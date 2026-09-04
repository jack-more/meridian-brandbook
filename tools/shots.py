#!/usr/bin/env python3
"""Per-product renders of the floating vial and the vial in the water — the real
label in real perspective, off the M-3 RT reference. Parallel, resumable."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL=os.path.join(ROOT,'img/ref/label-m3rt.png'); WATER=os.path.join(ROOT,'img/gen/hero-water-2.png')
SHADOW=os.path.join(ROOT,'img/gen/master-shadow-1.png'); CUBE=os.path.join(ROOT,'img/gen/master-cube-1.png')
OUT=os.path.join(ROOT,'img/products')
prods=[p for p in json.load(open(os.path.join(ROOT,'products.json'))) if p['slug']!='kubix']
def label(name,dose): return (f"the lowercase serif wordmark meridian in forest green, a thin rule, then {name} in bold sans, {dose} beneath it, a second rule, 99% Purity and Research Use Only, and the small green M badge in the corner; every letter of the name fully visible")
def gen(args,out):
    for attempt in range(2):
        r=subprocess.run(['higgsfield','generate','create','nano_banana_2']+args+['--wait'],capture_output=True,text=True,timeout=600)
        m=re.search(r'https://\S+\.png',r.stdout+r.stderr)
        if m:
            subprocess.run(['curl','-s','-o',out,m.group(0)],timeout=120)
            if os.path.exists(out) and os.path.getsize(out)>100000: return 'ok'
    return 'FAILED: '+(r.stdout+r.stderr)[-160:]
def one(job):
    p,kind=job; name=p['name'].replace('MRDN-','M-'); dose=p['dose']
    out=os.path.join(OUT,f"{p['slug']}-{kind}.png")
    if os.path.exists(out): return p['slug'],kind,'exists'
    if kind=='float':
        prompt=(f"Reproduce the reference exactly: the same clear glass vial at the same tilt, the same warm vanilla cap over a silver band, the same soft warm studio background and lighting. The label is exactly the reference label design with one change, the product name and dose: {label(name,dose)}. Ultra sharp, no other text.")
        args=['--image',LABEL,'--aspect_ratio','2:3','--prompt',prompt]
    elif kind=='main':
        prompt=(f"Reproduce the first reference exactly: the same clear glass vial standing upright with the same slight tilt, the same warm vanilla cap over a silver band, the same flat warm vanilla surface and seamless background, the same soft light and the same soft contact shadow. The label is exactly the second reference's label design with one change, the product name and dose: {label(name,dose)}. Ultra sharp, product-render precision, no other text.")
        args=['--image',SHADOW,'--image',LABEL,'--aspect_ratio','3:4','--prompt',prompt]
    elif kind=='cube':
        prompt=(f"Reproduce the first reference exactly: the same clear glass vial standing left of centre, the same small warm vanilla cube with the lowercase serif m pressed into it resting to the right, the same flat warm vanilla surface, seamless background, soft light and contact shadows. The vial's label is exactly the second reference's label design with one change, the product name and dose: {label(name,dose)}. Ultra sharp, product-render precision, no other text.")
        args=['--image',CUBE,'--image',LABEL,'--aspect_ratio','4:3','--prompt',prompt]
    else:
        prompt=(f"Reproduce the first reference exactly: the same still pond seen from above, the same warm pale vanilla water, the same concentric ripples, the same vial standing upright at the centre, the same lighting and reflection. The label is exactly the second reference's label design with one change, the product name and dose: {label(name,dose)}. Ultra sharp, no other text.")
        args=['--image',WATER,'--image',LABEL,'--aspect_ratio','16:9','--prompt',prompt]
    return p['slug'],kind,gen(args,out)
kinds=sys.argv[1:] or ['float','water']
jobs=[(p,k) for k in kinds for p in prods]
with ThreadPoolExecutor(int(os.environ.get('PAR','5'))) as ex:
    for slug,kind,st in ex.map(one,jobs): print(slug,kind,st,flush=True)
