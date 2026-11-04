# SPDX-License-Identifier: Apache-2.0
"""Verify editable facade and reimported GLB corners against runtime JSON."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
args=sys.argv[sys.argv.index('--')+1:];source,glb=map(Path,args);raw=source.read_bytes();spec=json.loads(raw);sha=hashlib.sha256(raw).hexdigest();assert bpy.context.scene['source_overlay_sha256']==sha and bpy.context.scene['building_id']==spec['building_id']
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==len(spec['objects']);expected=[]
for i,(o,d) in enumerate(zip(sorted(objs,key=lambda x:x.name),spec['objects'])):
 assert o.name==f'facade_{i:03d}' and o.data.materials[0].name==d['material'];x,y,z=d['position'];sx,sy,sz=d['size'];assert (o.location-Vector((x,-z,y))).length<.0001 and (o.scale-Vector((sx,sz,sy))).length<.0001
 for dx in (-.5,.5):
  for dy in (-.5,.5):
   for dz in (-.5,.5):expected.append(Vector((x+dx*sx,-z+dy*sz,y+dz*sy)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(glb.resolve()));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1 and meshes[0]['source_overlay_sha256']==sha and meshes[0]['building_id']==spec['building_id'];assert {m.name.rsplit('.',1)[0] if m.name.rsplit('.',1)[-1].isdigit() else m.name for m in meshes[0].data.materials}=={o['material'] for o in spec['objects']};actual=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
def tree(points):
 t=KDTree(len(points))
 for i,p in enumerate(points):t.insert(p,i)
 t.balance();return t
at,et=tree(actual),tree(expected);e=max(max(at.find(v)[2] for v in expected),max(et.find(v)[2] for v in actual));assert e<.00015,e
print('VERIFIED_FACADE_BOXES',len(objs),'glb_meshes',len(meshes),'max_error_m',e,'source_sha256',sha)
