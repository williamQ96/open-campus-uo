import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
args=sys.argv[sys.argv.index('--')+1:];source,glb=map(Path,args);raw=source.read_bytes();spec=json.loads(raw)
assert bpy.context.scene['source_overlay_sha256']==hashlib.sha256(raw).hexdigest();objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==len(spec['objects'])==180
expected=[]
for i,(o,d) in enumerate(zip(sorted(objs,key=lambda x:x.name),spec['objects'])):
 assert o.name==f'bench_detail_{i:03d}';x,y,z=d['position'];sx,sy,sz=d['size']; assert (o.location-Vector((x,-z,y))).length<.0001 and (o.scale-Vector((sx,sz,sy))).length<.0001
 for dx in (-.5,.5):
  for dy in (-.5,.5):
   for dz in (-.5,.5):expected.append(Vector((x+dx*sx,-z+dy*sz,y+dz*sy)))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(glb.resolve()));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1;assert meshes[0]['source_overlay_sha256']==hashlib.sha256(raw).hexdigest();assert meshes[0]['base_asset_sha256']==spec['base_asset_sha256']
actual=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
def tree(points):
 t=KDTree(len(points))
 for i,p in enumerate(points):t.insert(p,i)
 t.balance();return t
at,et=tree(actual),tree(expected);err1=max(at.find(v)[2] for v in expected);err2=max(et.find(v)[2] for v in actual);assert max(err1,err2)<.00015,(err1,err2)
print('VERIFIED_BOX_OVERLAY boxes=',len(objs),'glb_meshes=',len(meshes),'glb_vertices=',len(actual),'max_error_m=',max(err1,err2),'source_sha256=',hashlib.sha256(raw).hexdigest())
