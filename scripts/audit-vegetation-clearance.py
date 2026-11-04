# SPDX-License-Identifier: Apache-2.0
"""Conservative tree-to-footprint screening; does not modify or certify geometry."""
import argparse, hashlib, json
from pathlib import Path
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();root=args.root
 manifest=root/'apps/web-preview/public/scene/manifest.json'; records=read(manifest)['buildings']; ids=[]; polygons=[]
 for rec in records:
  if len(rec['footprint_enu_m'])<3:continue
  shape=Polygon(rec['footprint_enu_m'])
  if not shape.is_valid:raise ValueError('Invalid footprint: '+rec['id'])
  ids.append(rec['id']);polygons.append(shape)
 index=STRtree(polygons);groups=[]
 for name,kind in [('visual-pilot-input.json','pilot'),('campus-expansion-input.json','expansion')]:
  src=root/'artifacts'/name; trees=read(src)['trees']; hits=[]; inside=0
  for i,t in enumerate(trees):
   x,n,h=t[:3];point=Point(x,n);radius=h*(.36 if kind=='pilot' else .35)
   for j in index.query(point.buffer(radius)):
    distance=polygons[j].distance(point)
    if distance==0:inside+=1
    if distance<radius:
     hits.append({'tree_index':i,'east_m':x,'north_m':n,'height_m':h,'screen_radius_m':round(radius,3),'building_id':ids[j],'footprint_distance_m':round(distance,3)})
  groups.append({'input':str(src.relative_to(root)).replace('\\','/'),'input_sha256':digest(src),'tree_count':len(trees),'trunk_inside_pair_count':inside,'candidate_tree_count':len({h['tree_index'] for h in hits}),'candidate_pairs':hits})
 report={'method':'Conservative 2D crown-radius versus historical candidate footprint screening; 0.36 * pilot height and 0.35 * expansion height; no vertical, leaf, or custom building-geometry intersection test. Input snapshot may not prove current exported mesh correspondence. Inspect each candidate before edits.', 'manifest_sha256':digest(manifest),'groups':groups}
 args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps([{'input':g['input'],'trees':g['tree_count'],'trunk_inside_pairs':g['trunk_inside_pair_count'],'candidate_trees':g['candidate_tree_count']} for g in groups]))
if __name__=='__main__':main()
