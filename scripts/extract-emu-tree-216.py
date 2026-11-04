# SPDX-License-Identifier: Apache-2.0
"""Generate a source-pinned EMU tree 216 suppression; run inside Blender.

blender --background --factory-startup --python-exit-code 1 --python scripts/extract-emu-tree-216.py -- --root PROJECT --output PATCH
The browser patch validator separately verifies all 954 exported matches before mutation.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=a.root
source=r/'assets/roof-refinement/eugene-campus.blend';inp=r/'artifacts/visual-pilot-input.json';glb=r/'apps/web-preview/public/scene/campus-expanded.glb'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source)=='06b211f88256b028631e568b2b8401e11e0772e8604b9e454b92001e76187b86'
assert sha(inp)=='ea262a2dc98b77c22940b5f4928ba1ccf7ff37d5bf7947129684a6b24bd05254'
base='29f22c38eb5737fba2c8b3ab9618e049443c052e169e175f19428e66174ae896';assert sha(glb)==base
trees=json.loads(inp.read_text(encoding='utf8'))['trees'];i=216;x,n,h,con,tone=trees[i]
assert [x,n,h,con,tone]==[-190.089,-10.77,14.16,False,2]
with bpy.data.libraries.load(str(source),link=False) as (data,loaded):loaded.objects=['vegetation']
obj=loaded.objects[0];bpy.context.collection.objects.link(obj);assert obj.matrix_world.is_identity
first=sum(68 if t[3] else 282 for t in trees[:i]);last=first+282;unique=[]
for v in obj.data.vertices[first:last]:
 point=[v.co.x,v.co.z,-v.co.y]
 if not any(sum((x-y)**2 for x,y in zip(point,q))<1e-8 for q in unique):unique.append(point)
assert len(unique)==218
for v in obj.data.vertices:
 if first<=v.index<last:continue
 point=(v.co.x,v.co.z,-v.co.y)
 if any(sum((x-y)**2 for x,y in zip(point,q))<1e-8 for q in unique):raise ValueError('Tree vertex also belongs to another tree')
patch={'version':1,'base_asset_sha256':base,'target_name':'vegetation','expected_matches':954,'positions_gltf':unique,'collapse_gltf':[x,unique[0][1],-n],'tolerance_m':.0001,'suppressed_trees':1,'tree_index':i,'description':'Suppress one procedural tree whose center is on open light surface in 2024 NAIP near EMU; not a present-day tree survey'}
a.output.write_text(json.dumps(patch,indent=2)+'\n',encoding='utf8');print('Wrote',a.output,'source tree vertices',last-first,'unique positions',len(unique))
