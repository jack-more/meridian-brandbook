#!/usr/bin/env python3
"""Ecophilia pages, one per product, its own plant. Runs the CLI in parallel and downloads."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL=os.path.join(ROOT,'img/ref/label-m3rt.png'); COVER=os.path.join(ROOT,'img/ref/ecophilia-cover.jpg')
OUT=os.path.join(ROOT,'img/products'); os.makedirs(OUT,exist_ok=True)
prods=json.load(open(os.path.join(ROOT,'products.json')))
def one(p):
    out=os.path.join(OUT,f"{p['slug']}-plant.png")
    if os.path.exists(out): return p['slug'],'exists'
    name=p['name'].replace('MRDN-','M-'); dose=p['dose']
    prompt=(f"A page from a modern plant book, photographed flat. The background is one perfectly flat, uniform bright green, exactly the green of the second reference book cover, edge to edge, no page edges, no border. "
            f"{p['plant'][0].upper()+p['plant'][1:]} lies {p['orientation']} across the page, cut out cleanly on the green. Resting on it, standing upright, is the exact vial from the first reference with the same label design, but the product name reads {name} and the dose reads {dose}: "
            f"meridian wordmark, rule, {name} in bold sans, {dose}, rule, 99% Purity, Research Use Only, the small green M badge bottom right; vanilla cap over a silver band. Every letter of the name fully visible. Nothing else on the page, no other text. Ultra sharp, flat, graphic.")
    for attempt in range(2):
        r=subprocess.run(['higgsfield','generate','create','nano_banana_2','--image',LABEL,'--image',COVER,'--aspect_ratio','3:2','--wait','--prompt',prompt],capture_output=True,text=True,timeout=600)
        m=re.search(r'https://\S+\.png',r.stdout+r.stderr)
        if m:
            subprocess.run(['curl','-s','-o',out,m.group(0)],timeout=120)
            if os.path.exists(out) and os.path.getsize(out)>100000: return p['slug'],'ok'
    return p['slug'],'FAILED: '+(r.stdout+r.stderr)[-200:]
want=sys.argv[1:] or [p['slug'] for p in prods]
todo=[p for p in prods if p['slug'] in want]
with ThreadPoolExecutor(5) as ex:
    for slug,st in ex.map(one,todo): print(slug,st,flush=True)
