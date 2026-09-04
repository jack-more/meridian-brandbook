#!/usr/bin/env python3
"""1:1 versions of the main shots: the vanilla ground extended on both sides
from the image's own edge columns, so the whole vial sits in a square."""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def square(src, dst, margin=0.06):
    im=Image.open(src).convert('RGB'); W,H=im.size
    side=int(H*(1+margin*2)); a=np.array(im).astype(float)
    out=np.zeros((side,side,3))
    # ground: each row is the edge column's colour, blended across; vertical gradient kept
    left=a[:,:24].mean(axis=1); right=a[:,-24:].mean(axis=1)
    rows=np.linspace(0,H-1,side).astype(int)
    for y in range(side):
        r=rows[y]; t=np.linspace(0,1,side)
        out[y]=left[r][None,:]*(1-t)[:,None]+right[r][None,:]*t[:,None]
    bg=Image.fromarray(np.clip(out,0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(6))
    # paste the original centred, with a feathered edge so the seam disappears
    ox=(side-W)//2; oy=int(H*margin)
    mask=Image.new('L',(W,H),255); m=np.array(mask).astype(float); f=40
    ramp=np.linspace(0,1,f); m[:, :f]*=ramp[None,:]; m[:, -f:]*=ramp[::-1][None,:]; m[:f,:]*=ramp[:,None]; m[-f:,:]*=ramp[::-1][:,None]
    bg.paste(im,(ox,oy),Image.fromarray(m.astype('uint8')))
    bg.save(dst,quality=94,subsampling=0); return side
if __name__=='__main__':
    prods=json.load(open(os.path.join(ROOT,'products.json'))); which=sys.argv[1:] or [p['slug'] for p in prods]
    for p in prods:
        if p['slug'] not in which: continue
        src=f"{ROOT}/img/products/{p['slug']}-main.png"
        if not os.path.exists(src): src=f"{ROOT}/img/products/{p['slug']}-main.jpg"
        side=square(src,f"{ROOT}/img/products/{p['slug']}-square.jpg"); print(p['slug'],side)
