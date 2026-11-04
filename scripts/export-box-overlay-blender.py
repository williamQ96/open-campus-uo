# SPDX-License-Identifier: Apache-2.0
"""Build editable Blender snapshot and compact GLB of box-only runtime overlay.
Usage: blender -b --python export-box-overlay-blender.py -- input.json output.blend output.glb
Blender Z-up to glTF Y-up mapping preserves coordinates of the existing Three.js spec.
"""
import bpy, sys, json, hashlib, math
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]; assert len(args)==3
source,blend,glb=map(Path,args);raw=source.read_bytes();spec=json.loads(raw)
assert spec['version']==1 and spec['scope']=='environment' and spec['replace_building'] is False
items=spec['objects'];assert 0<len(items)<=500
assert all(o['kind']=='prop' and o['material']=='bench-wood' and o['shape']=='box' and 'rotation' not in o and len(o['position'])==3 and len(o['size'])==3 and all(math.isfinite(x) for x in o['position']+o['size']) and all(0<x<=100 for x in o['size']) for o in items)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def lin(v):
 v=v/255.0
 return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
mat=bpy.data.materials.new('bench-wood');mat.diffuse_color=tuple(lin(v) for v in (119,99,79))+(1,);mat.use_nodes=True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=0.9
for i,o in enumerate(items):
 x,y,z=o['position'];sx,sy,sz=o['size'];bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-z,y));b=bpy.context.object;b.name=f'bench_detail_{i:03d}';b.scale=(sx,sz,sy);b.data.materials.append(mat)
bpy.context.scene['source_overlay_sha256']=hashlib.sha256(raw).hexdigest();bpy.context.scene['base_asset_sha256']=spec['base_asset_sha256'];bpy.context.scene['description']='Editable detail overlay only; original benches and suppression are separate.'
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()))
# Join a temporary in-memory copy for a single mesh in the review GLB; blend remains editable.
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();joined=bpy.context.view_layer.objects.active;joined['source_overlay_sha256']=hashlib.sha256(raw).hexdigest();joined['base_asset_sha256']=spec['base_asset_sha256'];bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format='GLB',export_yup=True,export_extras=True)
print('BUILT_BOX_OVERLAY',len(items),hashlib.sha256(raw).hexdigest())
