#!/usr/bin/env python3
"""
LABEL COMPOSITOR — one master, every product.

The master is a render of the vial with a blank band on the label between
the two rules. Each product's name and dose are set in the label's own
frame (origin at the left end of the upper rule, u along the rule, v down
the label) and multiplied into the paper so the grain shows through.
Geometry is measured once per master and kept in MASTERS below.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DM   = '/private/tmp/claude-501/-Users-jackmorello-Desktop-jackmorellodotcom/9b9d2682-1414-4894-9f14-980ce9fe0866/scratchpad/fonts/DMSans-Bold.ttf'
INTER= '/Users/jackmorello/sko-brand-build/desk/SKO_Creator_Deck_WIP/fonts/Inter-var.ttf'
FOREST = (42, 58, 46)

MASTERS = {
    'blank':  dict(src='img/gen/master-blank-1.png',  origin=(572, 1192), angle=12.3, width=640,
                   name_v=128, dose_v=212, name_px=118, dose_px=60, u0=22),
    'shadow': dict(src='img/gen/master-shadow-1.png', origin=(568, 1188), angle=15.9, width=660,
                   name_v=130, dose_v=216, name_px=118, dose_px=60, u0=22),
    'cube':   dict(src='img/gen/master-cube-1.png',   origin=(750, 899),  angle=17.7, width=400,
                   name_v=80,  dose_v=133, name_px=72, dose_px=37, u0=14, two_line_drop=20),
}

def font(path, px, wt=None):
    f = ImageFont.truetype(path, px)
    if wt:
        try: f.set_variation_by_axes([wt])
        except Exception: pass
    return f

def set_text(layer, text, f, u, v, angle, origin, fill):
    """draw text upright on a scratch layer, rotate it into the label frame,
    and place it so its top-left sits at (u, v) in that frame"""
    d = ImageDraw.Draw(layer); w = d.textlength(text, font=f)
    pad = 60; tw, th = int(w) + pad * 2, int(f.size * 1.5) + pad * 2
    scratch = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(scratch).text((pad, pad), text, font=f, fill=fill + (255,))
    rot = scratch.rotate(-angle, resample=Image.BICUBIC, expand=True)
    a = math.radians(angle)
    cx = origin[0] + u * math.cos(a) - v * math.sin(a); cy = origin[1] + u * math.sin(a) + v * math.cos(a)
    ox, oy = tw / 2 - pad, th / 2 - pad
    rx = ox * math.cos(a) - oy * math.sin(a); ry = ox * math.sin(a) + oy * math.cos(a)
    layer.alpha_composite(rot, (int(round(cx + rx - rot.width / 2)), int(round(cy + ry - rot.height / 2))))
    return w

def render(master, name, dose, out_path):
    M = MASTERS[master]
    base = Image.open(os.path.join(ROOT, M['src'])).convert('RGB')
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    px = M['name_px']; lines = [name]
    fits = lambda: all(d.textlength(l, font=font(DM, px, 700)) <= M['width'] for l in lines)
    while px > int(M['name_px'] * 0.5) and not fits(): px -= 4
    if not fits():
        for sep in [' + ', ' (', '/']:
            if sep in name:
                a_, b_ = name.split(sep, 1)
                lines = [a_.strip(), (sep.strip() + (' ' if sep == ' + ' else '') + b_).strip() if sep != '/' else b_.strip()]; break
        px = int(M['name_px'] * 0.74)
        while px > 44 and not fits(): px -= 4
    f = font(DM, px, 700)
    v = M['name_v'] + (M.get('two_line_drop', 34) if len(lines) == 2 else 0) - (px * 0.55 if len(lines) == 2 else 0)
    for l in lines:
        set_text(layer, l, f, M['u0'], v - px * 0.8, M['angle'], M['origin'], FOREST); v += px * 1.0
    fd = font(INTER, M['dose_px'], 500)
    dv = M['dose_v'] if len(lines) == 1 else max(M['dose_v'], v + M['dose_px'] * 0.15)
    set_text(layer, dose, fd, M['u0'] + 2, dv - M['dose_px'] * 0.8, M['angle'], M['origin'], FOREST)
    b = np.array(base).astype(float); L = np.array(layer).astype(float)
    a = L[..., 3:4] / 255.0; ink = L[..., :3] / 255.0
    out = b * (1 - a) + b * ink * a
    Image.fromarray(np.clip(out, 0, 255).astype('uint8')).save(out_path, quality=94, subsampling=0)

if __name__ == '__main__':
    prods = json.load(open(os.path.join(ROOT, 'products.json')))
    which = sys.argv[1:] or [p['slug'] for p in prods]
    for p in prods:
        if p['slug'] not in which: continue
        name = p['name'].replace('MRDN-', 'M-')
        render('shadow', name, p['dose'], os.path.join(ROOT, f"img/products/{p['slug']}-main.jpg"))
        render('cube',   name, p['dose'], os.path.join(ROOT, f"img/products/{p['slug']}-cube.jpg"))
        print('wrote', p['slug'], '→', name, p['dose'])
