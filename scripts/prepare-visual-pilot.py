# SPDX-License-Identifier: Apache-2.0
"""Prepare authored landscape geometry against the unchanged terrain/footprints.

Use the upstream Python environment, then build-visual-pilot.py in Blender.
NAIP RGB canopy cues guide illustrative trees; heights/species remain inferred.
"""
from pathlib import Path
import json
import random
import hashlib
import warnings
from dataclasses import asdict
import rasterio
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from geospatial3d.corridors import drape_surface
from geospatial3d.architectural import facade_modules
from geospatial3d.canopy_cues import canopy_probability, sample_north_up
from geospatial3d import __version__
from geospatial3d.io import revision
import geospatial3d.architectural as architectural
import geospatial3d.canopy_cues as canopy_cues

ROOT = Path(__file__).resolve().parents[1]
scene = ROOT/'apps/web-preview/public/scene'
manifest = json.loads((scene/'manifest.json').read_text(encoding='utf-8'))
field = json.loads((scene/manifest['heightfield_url']).read_text(encoding='utf-8'))
config = json.loads((ROOT/'configs/visual-pilot.json').read_text(encoding='utf-8'))
aerial_record = json.loads((ROOT/'data/metadata/naip-2024-reference.json').read_text(encoding='utf-8'))
aerial_path = ROOT/'data/reference-images'/aerial_record['archive_file']
if hashlib.sha256(aerial_path.read_bytes()).hexdigest() != aerial_record['sha256']:
    raise ValueError('Archived aerial image checksum mismatch')
with warnings.catch_warnings():
    # The archived PNG's exact georeference is supplied by the export record.
    warnings.simplefilter('ignore',rasterio.errors.NotGeoreferencedWarning)
    with rasterio.open(aerial_path) as raster:
        canopy = canopy_probability(raster.read([1,2,3]))
aerial_extent = aerial_record['export_response']['extent']
origin = aerial_record['local_origin_projected_m']
local_bounds=[aerial_extent['xmin']-origin[0],aerial_extent['ymin']-origin[1],
              aerial_extent['xmax']-origin[0],aerial_extent['ymax']-origin[1]]
def canopy_at(x,n):
    return sample_north_up(canopy,local_bounds,x,n)
records={b['name']:b for b in manifest['buildings'] if b.get('name')}
modules={}
for name,pattern in config['facade_patterns'].items():
    base=records[pattern['building']]['base_z_m']
    modules[name]=[asdict(bay) for bay in facade_modules(pattern['start_enu_m'],pattern['end_enu_m'],pattern['count'],
                  [base+z for z in pattern['levels_above_base_m']])]
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
for i in range(80000):
    if len(trees)>=config['tree_target']:break
    x=rng.uniform(-640,-150);n=rng.uniform(-330,65)
    p=Point(x,n)
    if not lawns.contains(p) or buildings.distance(p)<5 or existing.distance(p)<4 or paths.distance(p)<3.5:continue
    if sightline.distance(p)<9:continue
    # Keep the center of Memorial Quad open and preserve landmark sightlines.
    if -574<x<-535 and -162<n<-24:continue
    if -414<x<-387 and -20<n<12:continue
    cue=canopy_at(x,n)
    if cue<.28 or rng.random()>min(1,cue*1.8):continue
    if any((x-a)**2+(n-b)**2<49 for a,b,*_ in trees):continue
    trees.append([round(x,3),round(n,3),round(rng.uniform(10,21),2),rng.random()<.20,rng.randrange(3)])
payload={'configuration':config,'surfaces':surfaces,'trees':trees,'facade_modules':modules,
         'art_pipeline':{'version':__version__,**revision(),
                         'module_sha256':{Path(module.__file__).name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                                          for module in [architectural,canopy_cues]}},
         'aerial_reference':{'id':'naip-2024-pilot-rgb','captured_at':'2024-06-08','sha256':aerial_record['sha256'],
                             'method':'Smoothed dark/textured-green RGB cue plus curated setbacks, open lawns and sightlines; seeded heights/species are inferred, not a tree inventory'},
         'manifest_sha256':hashlib.sha256((scene/'manifest.json').read_bytes()).hexdigest(),
         'heightfield_sha256':hashlib.sha256((scene/manifest['heightfield_url']).read_bytes()).hexdigest()}
out=ROOT/'artifacts/visual-pilot-input.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(payload),encoding='utf-8')
print(f'{len(trees)} trees; landscape triangles: {sum(len(s["faces"]) for s in surfaces)}; {out}')
