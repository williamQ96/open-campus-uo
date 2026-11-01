# SPDX-License-Identifier: Apache-2.0
"""Keep source geography fixed; prepare an editable, tiered appearance overlay."""
from pathlib import Path
import json,hashlib,random
from collections import Counter
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from geospatial3d.context_appearance import appearance_plan,pitched_roof_faces
from geospatial3d.corridors import drape_surface
from geospatial3d.io import revision,text_sha256
import geospatial3d.context_appearance as method

ROOT=Path(__file__).resolve().parents[1];public=ROOT/'apps/web-preview/public/scene'
config=json.loads((ROOT/'configs/campus-expansion.json').read_text(encoding='utf-8'))
manifest=json.loads((public/'manifest.json').read_text(encoding='utf-8'));field=json.loads((public/manifest['heightfield_url']).read_text())
baseline=json.loads((ROOT/config['source_presentation']).read_text(encoding='utf-8'))
assert hashlib.sha256((ROOT/config['source_blend']).read_bytes()).hexdigest()==config['source_blend_sha256']
refresh={b['id'] for b in manifest['buildings'] if b.get('name') in config['photo_refinements']}
protected=[id for id in baseline['replaces_building_ids'] if id not in refresh]
plan=appearance_plan(manifest['buildings'],config['priority_polygon_enu_m'],config['seed'],protected)
for item in plan:
 if item.get('name') in config['photo_refinements']:
  item['tier']='photo-grammar';item['roof']='gable';item['window_budget']=0;item['reference']=config['photo_refinements'][item['name']]['reference']
 rise=min(3.6,item['height_m']*.25)
 item['wall_height_m']=item['height_m']-rise if item['roof']=='gable' else item['height_m']
 item['roof_faces']=pitched_roof_faces(item['footprint_enu_m'],item['base_z_m']+item['wall_height_m'],item['roof_z_m']) if item['roof']=='gable' else []
focus=Polygon(config['priority_polygon_enu_m'])
occupied=unary_union([Polygon(b['footprint_enu_m']).buffer(2.5) for b in manifest['buildings']])
roads=unary_union([LineString(f['centerline_enu_m']).buffer(f['width_m']/2+2) for f in manifest['corridors']['features']])
pilot=box(-655,-345,-135,80)
lawns=focus.buffer(-6).difference(occupied).difference(roads).difference(pilot)
vertices,faces=drape_surface(lawns,field)
rng=random.Random(config['seed']+203);trees=[]
for _ in range(30000):
 if len(trees)>=config['extra_tree_target']:break
 x=rng.uniform(-700,450);n=rng.uniform(-600,350);p=Point(x,n)
 if not lawns.contains(p) or occupied.distance(p)<4 or roads.distance(p)<5:continue
 if any((x-a)**2+(n-b)**2<144 for a,b,*_ in trees):continue
 trees.append([round(x,3),round(n,3),round(rng.uniform(7,15),2),rng.randrange(4)])
counts=Counter(item['tier'] for item in plan)
payload={'config':config,'baseline':baseline,'protected_ids':protected,'plan':plan,'lawn':{'vertices':vertices,'faces':faces},'trees':trees,'counts':dict(counts),'source_manifest_text_sha256':text_sha256(public/'manifest.json'),'source_heightfield_text_sha256':text_sha256(public/manifest['heightfield_url']),'source_manifest_sha256':hashlib.sha256((public/'manifest.json').read_bytes()).hexdigest(),'source_heightfield_sha256':hashlib.sha256((public/manifest['heightfield_url']).read_bytes()).hexdigest(),'art_pipeline':{**revision(),'module':'context_appearance.py','module_text_sha256':text_sha256(Path(method.__file__)),'module_sha256':hashlib.sha256(Path(method.__file__).read_bytes()).hexdigest()}}
(ROOT/'artifacts/campus-expansion-input.json').write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8')
print(dict(counts),'protected',len(protected),'trees',len(trees),'lawn triangles',len(faces))
