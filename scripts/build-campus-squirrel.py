# SPDX-License-Identifier: Apache-2.0
import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'data/asset-sources/campus-life/tree-squirrel.glb'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];print('SOURCE',[(o.name,len(o.data.polygons),list(o.dimensions)) for o in objs])
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Reduce the CC0 source to a flat-color low-poly campus wildlife silhouette.
modifier=o.modifiers.new('Low-poly campus silhouette','DECIMATE');modifier.ratio=min(1,900/max(1,len(o.data.polygons)));bpy.ops.object.modifier_apply(modifier=modifier.name)
bounds=[o.matrix_world@Vector(c) for c in o.bound_box];lo=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bounds) for i in range(3)))
o.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));scale=.55/max(hi.x-lo.x,hi.y-lo.y,hi.z-lo.z);o.scale*=scale;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
material=bpy.data.materials.new('Warm squirrel brown');material.use_nodes=True;material.diffuse_color=(.24,.12,.055,1);material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.24,.12,.055,1);material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.93
o.data.materials.clear();o.data.materials.append(material)
for p in o.data.polygons:p.material_index=0;p.use_smooth=False
o.name='Campus squirrel - CC0 source';o['source']='https://www.innerscene.com/tools/library/3d-parts/tree-squirrel-6499352e';o['source_license']='CC0-1.0';o['adaptation']='Decimated, normalized size, flat warm-brown material; source retained separately'
(root/'assets/animals').mkdir(parents=True,exist_ok=True);(root/'apps/web-preview/public/animals').mkdir(parents=True,exist_ok=True)
# Drop unused imported source materials/images from the editable adaptation.
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'assets/animals/campus-squirrel.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'apps/web-preview/public/animals/campus-squirrel.glb'),export_format='GLB',use_selection=True,export_extras=True,export_copyright='Innerscene CC0 source; Open Campus low-poly adaptation, CC BY 4.0')
# Inspect the adapted silhouette without modifying any source image.
(root/'artifacts').mkdir(parents=True,exist_ok=True)
bpy.ops.object.camera_add(location=(.85,-.85,.65));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.22))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.85;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.color_type='MATERIAL';scene.render.resolution_x=480;scene.render.resolution_y=480;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'artifacts/squirrel-inspection.png');bpy.ops.render.render(write_still=True)
print('ADAPTED',len(o.data.polygons),'faces')
