# SPDX-License-Identifier: Apache-2.0
"""Prepare authored landscape geometry against the unchanged terrain/footprints.

Use the upstream Python environment, then build-visual-pilot.py in Blender.
All added paths and tree placements are illustrative art direction, not GIS claims.
"""
from pathlib import Path
import json
import random
import hashlib
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from geospatial3d.corridors import drape_surface

ROOT = Path(__file__).resolve().parents[1]
scene = ROOT/'apps/web-preview/public/scene'
manifest = json.loads((scene/'manifest.json').read_text(encoding='utf-8'))
field = json.loads((scene/manifest['heightfield_url']).read_text(encoding='utf-8'))
config = json.loads((ROOT/'configs/visual-pilot.json').read_text(encoding='utf-8'))
extent = box(*config['bounds_enu_m'])
buildings = unary_union([Polygon(b['footprint_enu_m']).buffer(1) for b in manifest['buildings']])
existing = unary_union([LineString(f['centerline_enu_m']).buffer(f['width_m']/2+0.8) for f in manifest['corridors']['features']])
paths = unary_union([LineString(p).buffer(2.3) for p in config['paths']])
plazas = unary_union([box(-588,-193,-530,-171),Point(-272,-47).buffer(24),box(-415,-26,-387,-13)])
paths = paths.union(plazas).intersection(extent).difference(buildings).difference(existing)
lawns = unary_union([box(*p) for p in config['lawns']]).difference(buildings.buffer(1)).difference(existing.buffer(1)).difference(paths.buffer(.15))
surfaces = []
for name, shape in [('lawn',lawns),('paving',paths)]:
    verts, faces = drape_surface(shape,field)
    surfaces.append({'kind':name,'vertices':verts,'faces':faces})
rng = random.Random(config['seed'])
sightline = LineString([manifest['spawn_enu_m'],[-255,-36]])
trees=[]
for i in range(20000):
    if len(trees)>=config['tree_target']:break
    x=rng.uniform(-640,-150);n=rng.uniform(-330,65)
    p=Point(x,n)
    if not lawns.contains(p) or buildings.distance(p)<5 or existing.distance(p)<4 or paths.distance(p)<3.5:continue
    if sightline.distance(p)<9:continue
    # Keep the center of Memorial Quad open and preserve landmark sightlines.
    if -574<x<-535 and -162<n<-24:continue
    if -414<x<-387 and -20<n<12:continue
    if any((x-a)**2+(n-b)**2<64 for a,b,*_ in trees):continue
    trees.append([round(x,3),round(n,3),round(rng.uniform(8,17),2),rng.random()<.23,rng.randrange(3)])
payload={'configuration':config,'surfaces':surfaces,'trees':trees,
         'manifest_sha256':hashlib.sha256((scene/'manifest.json').read_bytes()).hexdigest(),
         'heightfield_sha256':hashlib.sha256((scene/manifest['heightfield_url']).read_bytes()).hexdigest()}
out=ROOT/'artifacts/visual-pilot-input.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(payload),encoding='utf-8')
print(f'{len(trees)} trees; landscape triangles: {sum(len(s["faces"]) for s in surfaces)}; {out}')
