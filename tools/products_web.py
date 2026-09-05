#!/usr/bin/env python3
"""Web-weight product plates and the product gallery page for the book."""
import json, os
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
prods=json.load(open(os.path.join(ROOT,'products.json')))
W=os.path.join(ROOT,'img/products/web'); os.makedirs(W,exist_ok=True)
F=os.path.join(ROOT,'img/products/full'); os.makedirs(F,exist_ok=True)
def full(s_,k):
    src=f'{ROOT}/img/products/{s_}-{k}.png'
    if not os.path.exists(src): src=f'{ROOT}/img/products/{s_}-{k}.jpg'
    if not os.path.exists(src): return False
    dst=f'{F}/{s_}-{k}.jpg'
    if os.path.exists(dst) and os.path.getmtime(dst)>=os.path.getmtime(src): return True
    im=Image.open(src).convert('RGB'); w=min(2000,im.width); im.resize((w,int(w*im.height/im.width)),Image.LANCZOS).save(dst,quality=92,subsampling=0); return True
def web(src,dst,w):
    if not os.path.exists(src): return False
    if os.path.exists(dst) and os.path.getmtime(dst)>=os.path.getmtime(src): return True
    im=Image.open(src).convert('RGB'); im.resize((w,int(w*im.height/im.width)),Image.LANCZOS).save(dst,quality=88,subsampling=0); return True
have={}
for p in prods:
    s=p['slug']; have[s]={}
    # generated PNGs win over the composite JPGs once they exist
    mp=f'{ROOT}/img/products/{s}-main.png'; cp=f'{ROOT}/img/products/{s}-cube.png'
    have[s]['main']=web(mp if os.path.exists(mp) else f'{ROOT}/img/products/{s}-main.jpg',f'{W}/{s}-main.jpg',1000)
    have[s]['cube']=web(cp if os.path.exists(cp) else f'{ROOT}/img/products/{s}-cube.jpg',f'{W}/{s}-cube.jpg',1000)
    have[s]['plant']=web(f'{ROOT}/img/products/{s}-plant.png',f'{W}/{s}-plant.jpg',1000)
    sq=f'{ROOT}/img/products/{s}-square.png'
    have[s]['square']=web(sq if os.path.exists(sq) else f'{ROOT}/img/products/{s}-square.jpg',f'{W}/{s}-square.jpg',1200)
    have[s]['moss']=web(f'{ROOT}/img/products/{s}-moss.png',f'{W}/{s}-moss.jpg',1400)
    for k in ['main','square','cube','plant','float','water','moss']: full(s,k)
    have[s]['float']=web(f'{ROOT}/img/products/{s}-float.png',f'{W}/{s}-float.jpg',1000)
    have[s]['water']=web(f'{ROOT}/img/products/{s}-water.png',f'{W}/{s}-water.jpg',1400)
# the gallery page
rows=[]
for p in prods:
    s=p['slug']; name=p['name'].replace('MRDN-','M-'); h=have[s]
    cells=''
    for k,label,ext in [('square','Main · 1:1','jpg'),('main','Main · 3:4','jpg'),('float','Floating','png'),('water','In the water','png'),('moss','On the moss','png'),('plant','Ecophilia','png'),('cube','With the cube','jpg')]:
        if k in ('float','water','cube','moss') and s=='kubix': continue
        if h[k]:
            cells+=f'<a class="shot" href="../img/products/full/{s}-{k}.jpg" download><img loading="lazy" src="../img/products/web/{s}-{k}.jpg" alt="{name} — {label}"><span>{label} · download</span></a>'
        else:
            cells+=f'<div class="shot pending"><span>{label} · rendering</span></div>'
    rows.append(f'<section id="{s}"><h2>{name}<i>{p["dose"]}</i></h2><div class="shots">{cells}</div></section>')
html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>meridian — Products</title>
<link rel="icon" type="image/png" href="../img/web/favicon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400&display=swap">
<style>
:root{{--vanilla:#F4EADB;--paper:#FBF6EE;--ink:#2F3D30;--mid:#7A6F63;--line:rgba(42,38,34,.14);--caramel:#A8763E}}
*{{box-sizing:border-box;margin:0}} body{{background:var(--vanilla);color:var(--ink);font-family:Inter,system-ui,sans-serif;padding:28px 0}}
.wrap{{width:min(1400px,94vw);margin:0 auto}}
header{{background:var(--paper);border:1px solid var(--line);padding:36px 46px;margin-bottom:26px;display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap}}
header h1{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:40px;letter-spacing:-.01em;line-height:1}}
header p{{font-size:12px;line-height:1.6;color:var(--mid);max-width:60ch;margin-top:10px}}
header a{{font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.14em;color:var(--caramel);text-decoration:none}}
section{{background:var(--paper);border:1px solid var(--line);padding:22px 26px 26px;margin-bottom:14px}}
section h2{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:26px;letter-spacing:-.01em;margin-bottom:12px;display:flex;align-items:baseline;gap:12px}}
section h2 i{{font-style:normal;font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.12em;color:var(--mid)}}
.shots{{display:grid;grid-template-columns:repeat(7,1fr);gap:12px}}
@media (max-width:1100px){{.shots{{grid-template-columns:repeat(2,1fr)}}}}
.shot{{position:relative;display:block;aspect-ratio:4/3;background:var(--vanilla);overflow:hidden;text-decoration:none;color:inherit}}
.shot img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.shot span{{position:absolute;left:10px;bottom:8px;font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.1em;color:var(--ink);background:rgba(251,246,238,.85);padding:3px 6px}}
.shot:hover{{box-shadow:0 0 0 2px var(--caramel)}}
.shot.pending span{{color:var(--mid)}}
@media (max-width:800px){{.shots{{grid-template-columns:1fr}}header{{padding:26px 22px}}}}
</style></head><body><div class="wrap">
<header><div><h1>Products</h1><p>Every offering, seven ways: the main shot on the shadow master, square and 3:4, on the moss branch, the floating vial, the vial standing in the water, its Ecophilia page on its own plant, and the vial beside the cube. Names and doses are composited from one master, so every product carries the same light. Click any plate to download it at 2000 px.</p></div><a href="../">&larr; BRAND BOOK</a></header>
{''.join(rows)}
</div></body></html>'''
os.makedirs(os.path.join(ROOT,'products'),exist_ok=True); open(os.path.join(ROOT,'products/index.html'),'w').write(html)
done=sum(1 for s in have if have[s]['plant']); print('gallery written; plants ready', done, '/', len(prods))

# the plant grid on the book's Products page: every product, its own plant
idx=os.path.join(ROOT,'index.html'); h=open(idx).read()
import re
tiles=''.join(f'<a class="tile" style="background:#44B24B" href="products/#{p["slug"]}"><img class="fill" src="img/products/web/{p["slug"]}-plant.jpg" alt="{p["name"]} on its plant"></a>' for p in prods if have[p['slug']]['plant'])
h2=re.sub(r'(<div class="tiles" id="plantgrid"[^>]*>).*?(</div>)', lambda m: m.group(1)+tiles+m.group(2), h, flags=re.S)
open(idx,'w').write(h2); print('plant grid:', sum(1 for p in prods if have[p['slug']]['plant']), 'tiles')

GH='https://jack-more.github.io/meridian-brandbook/img/products/'
car={}
for p in prods:
    s_=p['slug']; order=[('square','jpg'),('float','jpg'),('water','jpg'),('moss','png'),('plant','png'),('cube','jpg')]
    car[s_]={'name':p['name'],'images':[f'{GH}web/{s_}-{k}.jpg' for k,ext in order if have[s_].get(k)]}
json.dump(car,open(os.path.join(ROOT,'products/carousel.json'),'w'),indent=1); print('carousel.json', len(car))
