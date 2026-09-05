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
    pose=('The exact vial from the first reference lies flat on its side on top of it, horizontal, its whole length in contact with it, the label facing the camera, casting a small soft shadow onto it; the vial is not upright, not standing, not floating.' if p.get('pose')=='lie' else 'The exact vial from the first reference stands upright on it, its base in full contact with the surface, casting a small soft shadow onto it; it is not floating.')
    obj=p['plant']; lie=p.get('pose')=='lie'
    contact=("lies on its side nestled deep into it, half surrounded: parts of it rise in front of the glass and partly hide the cap, the shoulder and the lower body, the parts beneath are pressed flat under the vial's weight, its soft shadow falls onto it and onto the green, and the parts behind it are visible refracted through the clear empty glass" if lie else
             "stands on it and sinks slightly into it: parts of it rise in front of the base of the glass, the surface beneath is compressed under the vial's weight, its soft shadow falls onto it and onto the green, and the surface is visible through the clear empty glass at the base")
    prompt=(f"A page from a modern plant book, photographed flat from above in soft daylight. The background is one perfectly flat, uniform bright green, exactly the green of the second reference cover, edge to edge, no page edges, no spiral binding, no book visible. "
            f"{obj[0].upper()+obj[1:]} lies {p['orientation']} across the page, cut out cleanly on the green. The exact vial from the first reference, the same bottle with the same proportions, height and width, {contact}. Its label is exactly the reference label design: the lowercase serif wordmark meridian in forest green, a thin rule, then {name} in bold sans, {dose} beneath it, a second rule, {p.get('line','99% Purity and Research Use Only')}, and the small green M badge in the corner; every letter of the wordmark and the name fully visible: whatever crosses the vial crosses the glass, the cap or the shoulder, never the label. {('The vial itself is '+p['vial']+'. ') if p.get('vial') else ''}Exactly one vial in the picture, a single vial, never two. One photograph of real objects touching, not a vial placed on top: real photographic detail in the plant, natural imperfections, true soft shadows. Ultra sharp, no other text.")
    for attempt in range(2):
        vref=os.path.join(OUT,f"{p['slug']}-main.png") if p.get('vial') and os.path.exists(os.path.join(OUT,f"{p['slug']}-main.png")) else LABEL
        r=subprocess.run(['higgsfield','generate','create','nano_banana_2','--image',vref,'--image',COVER,'--aspect_ratio','3:2','--wait','--prompt',prompt],capture_output=True,text=True,timeout=600)
        m=re.search(r'https://\S+\.png',r.stdout+r.stderr)
        if m:
            subprocess.run(['curl','-s','-o',out,m.group(0)],timeout=120)
            if os.path.exists(out) and os.path.getsize(out)>100000: return p['slug'],'ok'
    return p['slug'],'FAILED: '+(r.stdout+r.stderr)[-200:]
want=sys.argv[1:] or [p['slug'] for p in prods]
todo=[p for p in prods if p['slug'] in want]
with ThreadPoolExecutor(5) as ex:
    for slug,st in ex.map(one,todo): print(slug,st,flush=True)
