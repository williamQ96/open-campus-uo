# SPDX-License-Identifier: Apache-2.0
"""Create an editable Blender and review GLB from an unrotated box facade overlay.
Usage: blender -b --factory-startup --python-exit-code 1 --python SCRIPT -- input.json output.blend output.glb
"""
import bpy,sys,json,hashlib,math
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];assert len(args)==3
source,blend,glb=map(Path,args);raw=source.read_bytes();spec=json.loads(raw)
palette={'station-cladding':'d5ddda','station-wall':'526f6d','glass':'608788'}
assert spec['version']==1 and spec['replace_building'] is False and isinstance(spec.get('building_id'),str)
items=spec['objects'];assert 0<len(items)<=500
assert all(o['kind']=='building' and o['material'] in palette and o['shape']=='box' and 'rotation' not in o and len(o['position'])==3 and len(o['size'])==3 and all(math.isfinite(v) for v in o['position']+o['size']) and all(0<v<=100 for v in o['size']) for o in items)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def lin(v):
 v=v/255
 return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
materials={}
for name,h in palette.items():
 c=tuple(lin(int(h[i:i+2],16)) for i in (0,2,4))+(1,);m=bpy.data.materials.new(name);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=c;p.inputs['Roughness'].default_value=.87;materials[name]=m
for i,o in enumerate(items):
 x,y,z=o['position'];sx,sy,sz=o['size'];bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-z,y));b=bpy.context.object;b.name=f'facade_{i:03d}';b.scale=(sx,sz,sy);b.data.materials.append(materials[o['material']])
hash=hashlib.sha256(raw).hexdigest();bpy.context.scene['source_overlay_sha256']=hash;bpy.context.scene['base_asset_sha256']=spec['base_asset_sha256'];bpy.context.scene['building_id']=spec['building_id'];bpy.context.scene['description']='Facade overlay only; source building and collision metadata are separate.'
bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()));bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join();o=bpy.context.view_layer.objects.active;o['source_overlay_sha256']=hash;o['base_asset_sha256']=spec['base_asset_sha256'];o['building_id']=spec['building_id'];bpy.ops.export_scene.gltf(filepath=str(glb.resolve()),export_format='GLB',export_yup=True,export_extras=True)
print('BUILT_FACADE_BOXES',len(items),'source_sha256',hash)
