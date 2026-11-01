# SPDX-License-Identifier: Apache-2.0
"""Compile movement habitats once from the actual authored paving/lawns and source roads."""
from pathlib import Path
import json,math,random
from shapely.geometry import Polygon,LineString,Point,box,mapping,shape
from shapely.ops import unary_union
from geospatial3d.activity import fixed_paths,line_parts
ROOT=Path(__file__).resolve().parents[1];PUBLIC=ROOT/'apps/web-preview/public/scene'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
m=read(PUBLIC/'manifest.json');field=read(PUBLIC/m['heightfield_url']);c=read(ROOT/'configs/visual-pilot.json')
config=read(ROOT/'configs/campus-life.json');obstacles=unary_union([Polygon(b['footprint_enu_m']) for b in m['buildings']])
roads=unary_union([LineString(f['centerline_enu_m']).buffer(f['width_m']/2+.8) for f in m['corridors']['features']])
extent=box(*c['bounds_enu_m']);building_exclusion=obstacles.buffer(1)
paving=unary_union([LineString(p).buffer(2.3) for p in c['paths']]).union(unary_union([box(-588,-193,-530,-171),Point(-272,-47).buffer(24),box(-415,-26,-387,-13)]))
paving=paving.intersection(extent).difference(building_exclusion).difference(roads)
vegetation=unary_union([box(*p) for p in c['lawns']]).difference(building_exclusion.buffer(1)).difference(roads.buffer(1)).difference(paving.buffer(.15))
def ground(x,n):
 u=max(0,min(field['nx']-1.000001,(x-field['min_east_m'])/field['spacing_m']));v=max(0,min(field['ny']-1.000001,(n-field['min_north_m'])/field['spacing_m']));i,j=int(u),int(v);a,b=u-i,v-j
 at=lambda dx,dy:field['heights_m'][(j+dy)*field['nx']+i+dx]
 return at(0,0)+(at(1,0)-at(0,0))*a+(at(1,1)-at(1,0))*b if a>=b else at(0,0)+(at(1,1)-at(0,1))*a+(at(0,1)-at(0,0))*b
paths=fixed_paths(c['paths'],paving,obstacles,'pedestrian',lambda x,n:ground(x,n)+.075,inset=1.05,clearance=1.05,prefix='sidewalk')
driving_features=[f for f in m['corridors']['features'] if f['name'] in config['driving_road_names']]
driving=unary_union([LineString(f['centerline_enu_m']).buffer(f['width_m']/2) for f in driving_features])
car_lines=[]
for f in driving_features:
 line=LineString(f['centerline_enu_m'])
 for sign in [-1,1]:car_lines.extend(line_parts(line.offset_curve(sign*min(1.8,f['width_m']*.18))))
paths+=fixed_paths(car_lines,driving,obstacles,'driving',lambda x,n:ground(x,n)+.08,inset=1.22,clearance=2.7,minimum_length=35,prefix='driving')
rng=random.Random(config['seed']);green_lines=[]
# Fixed grass routes are authored once, not randomly resampled every animation frame.
for region in getattr(vegetation,'geoms',[vegetation]):
 if region.area<100:continue
 minx,miny,maxx,maxy=region.bounds
 for _ in range(4):
  x=rng.uniform(minx,maxx);n=rng.uniform(miny,maxy);angle=rng.random()*math.tau;length=rng.uniform(12,26)
  green_lines.append(LineString([(x-math.cos(angle)*length/2,n-math.sin(angle)*length/2),(x+math.cos(angle)*length/2,n+math.sin(angle)*length/2)]))
paths+=fixed_paths(green_lines,vegetation,obstacles,'vegetation',lambda x,n:ground(x,n)+.075,inset=.5,clearance=.7,minimum_length=7,prefix='grass')
# Tree roots/height come from the retained authored pilot vegetation, not a new inventory.
trees=[]
for anchor in config['tree_anchors']:
 i=anchor['id'].split('-')[-1];x,n,h=anchor['east'],anchor['north'],anchor['height']
 if len(trees)>=8:break
 if not vegetation.buffer(-.65).covers(Point(x+.35,n)):continue
 trees.append({'id':f'tree-{i}','east':x,'north':n,'height':h})
 y=ground(x,n)+.075
 paths.append({'id':f'tree-climb-{i}','surface':'tree','tree_id':f'tree-{i}','points_enu_m':[[x+.35,n,y],[x+.35,n,y+h*.48],[x+.8,n,y+h*.56],[x+.35,n,y+h*.48],[x+.35,n,y]],'classification':'Illustrative climb/perch on an existing authored tree; not observed wildlife'})
slots=[]
for f in driving_features:
 line=LineString(f['centerline_enu_m'])
 for sign in [-1,1]:
  for curb in line_parts(line.offset_curve(sign*(f['width_m']/2+2.2))):
   for d in range(8,int(curb.length)-8,9):
    p=curb.interpolate(d);a=curb.interpolate(d-.5);b=curb.interpolate(d+.5)
    if obstacles.distance(p)<3 or paving.distance(p)<2 or vegetation.distance(p)<2:continue
    if any(math.hypot(p.x-s['east'],p.y-s['north'])<7 for s in slots):continue
    ux,uy=(b.x-a.x),(b.y-a.y);norm=math.hypot(ux,uy);ux,uy=ux/norm,uy/norm
    parking=Polygon([(p.x+ux*d-uy*w,p.y+uy*d+ux*w) for d,w in [(-2.8,-1.25),(2.8,-1.25),(2.8,1.25),(-2.8,1.25)]])
    if vegetation.intersects(parking) or paving.intersects(parking) or obstacles.buffer(.3).intersects(parking):continue
    slots.append({'id':f'parking-{len(slots)}','surface':'parking','east':round(p.x,4),'north':round(p.y,4),'height':round(ground(p.x,p.y)+.05,4),'yaw':math.atan2(b.x-a.x,-(b.y-a.y)),'footprint_enu_m':list(parking.exterior.coords),'classification':'Authored curbside prop slot; parking permission unverified'})
    if len(slots)>=20:break
   if len(slots)>=20:break
  if len(slots)>=20:break
 if len(slots)>=20:break
assert len(slots)>=14 and sum(p['surface']=='pedestrian' for p in paths)>=4 and sum(p['surface']=='vegetation' for p in paths)>=4
output={'pedestrian_regions':mapping(paving.buffer(-.45).difference(obstacles.buffer(.6))),'version':2,'seed':config['seed'],'status':'Compiled fixed semantic habitats and estimated curb slots; illustrative, not current access/traffic data','paths':paths,'prop_slots':slots,'trees':trees,'maximum_body_clearance_m':{'pedestrian':1.05,'driving_buildings':2.7,'driving_surface':1.22,'vegetation':.5}}
(PUBLIC/'activity.json').write_text(json.dumps(output,separators=(',',':'))+'\n')
zones={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'surface':name},'geometry':mapping(zone)} for name,zone in [('pedestrian',paving),('driving',driving),('vegetation',vegetation),('parking',unary_union([Polygon(slot['footprint_enu_m']) for slot in slots]))]]}
(ROOT/'data/metadata/activity-zones.geojson').write_text(json.dumps(zones,separators=(',',':'))+'\n')
print('Compiled',len(paths),'paths',len(slots),'prop slots',len(trees),'climb trees', {s:sum(p['surface']==s for p in paths) for s in ['pedestrian','driving','vegetation','tree']})
