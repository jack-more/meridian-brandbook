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
    # a vertical colour profile from each edge, smoothed hard so no streak survives
    def profile(cols):
        prof=cols.mean(axis=1)                                     # H x 3
        k=np.exp(-np.linspace(-3,3,121)**2/2); k/=k.sum()
        return np.stack([np.convolve(np.pad(prof[:,c],60,mode='edge'),k,mode='valid') for c in range(3)],axis=1)
    left=profile(a[:,:80]); right=profile(a[:,-80:])
    rows=np.linspace(0,H-1,side).astype(int); t=np.linspace(0,1,side)
    out=left[rows][:,None,:]*(1-t)[None,:,None]+right[rows][:,None,:]*t[None,:,None]
    # grain matched to the photograph's own flat area
    flat=a[int(H*0.05):int(H*0.2), int(W*0.05):int(W*0.2)]
    sigma=float((flat-flat.mean(axis=(0,1))).std())
    rng=np.random.default_rng(7); out+=rng.normal(0,sigma,out.shape)
    bg=Image.fromarray(np.clip(out,0,255).astype('uint8'))
    ox=(side-W)//2; oy=int(H*margin)
    f=int(W*0.18)
    m=np.ones((H,W)); ramp=np.linspace(0,1,f)
    m[:, :f]*=ramp[None,:]; m[:, -f:]*=ramp[::-1][None,:]
    fy=int(H*0.06); rampy=np.linspace(0,1,fy); m[:fy,:]*=rampy[:,None]; m[-fy:,:]*=rampy[::-1][:,None]
    bg.paste(im,(ox,oy),Image.fromarray((m*255).astype('uint8')))
    bg.save(dst,quality=94,subsampling=0); return side
if __name__=='__main__':
    prods=json.load(open(os.path.join(ROOT,'products.json'))); which=sys.argv[1:] or [p['slug'] for p in prods]
    for p in prods:
        if p['slug'] not in which: continue
        src=f"{ROOT}/img/products/{p['slug']}-main.png"
        if not os.path.exists(src): src=f"{ROOT}/img/products/{p['slug']}-main.jpg"
        side=square(src,f"{ROOT}/img/products/{p['slug']}-square.jpg"); print(p['slug'],side)
