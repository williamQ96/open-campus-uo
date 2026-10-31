# SPDX-License-Identifier: Apache-2.0
"""Editable CC0 Kenney student adaptation; no logos, original green/gold styling."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'data/asset-sources/kenney/animated-characters-3';out=ROOT/'apps/web-preview/public/characters';out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(source/'Model/characterMedium.fbx'))
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=next(o for o in bpy.context.scene.objects if o.type=='MESH')
def material(name,color,image=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=.88
 if image:
  texture=m.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(image));m.node_tree.links.new(texture.outputs['Color'],n.inputs['Base Color'])
 return m
materials=[material('Kenney original face and hands',(1,1,1),source/'Skins/humanMaleA.png'),material('Forest green sweatshirt',(.012,.17,.075)),material('Gold collar and sleeves',(.95,.62,.02)),material('Charcoal denim',(.045,.065,.09)),material('Cream sneakers',(.8,.82,.75)),material('Backpack',(.09,.14,.11))]
body.data.materials.clear()
for m in materials:body.data.materials.append(m)
for p in body.data.polygons:
 weights={}
 for index in p.vertices:
  for g in body.data.vertices[index].groups:weights[body.vertex_groups[g.group].name]=weights.get(body.vertex_groups[g.group].name,0)+g.weight
 name=max(weights,key=weights.get) if weights else ''
 z=sum((body.matrix_world@body.data.vertices[i].co).z for i in p.vertices)/len(p.vertices)
 if any(k in name for k in ['Head','Neck','Hand','ForeArm']):slot=0
 elif any(k in name for k in ['Spine','Chest','Shoulder','Arm']):slot=2 if z>2.35 else 1
 elif any(k in name for k in ['Foot','Toes']):slot=4
 else:slot=3
 p.material_index=slot
# A simple original backpack attached to the animated torso.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.30,2.07));pack=bpy.context.object;pack.name='Original campus backpack';pack.scale=(.54,.34,.75);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bevel=pack.modifiers.new('Soft edges','BEVEL');bevel.width=.07;bevel.segments=2;bpy.context.view_layer.objects.active=pack;bpy.ops.object.modifier_apply(modifier=bevel.name);pack.data.materials.append(materials[5])
world=pack.matrix_world.copy();pack.parent=arm;pack.parent_type='BONE';pack.parent_bone='Chest';bpy.context.view_layer.update();pack.matrix_world=world
original={o.name for o in bpy.context.scene.objects}
clips=[]
# FBX animation rigs use different rest poses from the skinned model. Bake
# world-space source poses into the target skeleton; copying actions gives T poses.
for file,keyword,label in [('idle.fbx','Idle','Idle'),('run.fbx','Run','Walk')]:
 before=set(bpy.data.actions);bpy.ops.import_scene.fbx(filepath=str(source/'Animations'/file))
 source_arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.name not in original)
 source_action=next(a for a in set(bpy.data.actions)-before if keyword in a.name)
 source_arm.animation_data.action=source_action;source_arm.animation_data.action_slot=source_action.slots[0]
 for t in source_arm.animation_data.nla_tracks:t.mute=True
 action=bpy.data.actions.new(label);arm.animation_data_create();arm.animation_data.action=action
 for frame in range(int(source_action.frame_range[0]),int(source_action.frame_range[1])+1):
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
  transform=arm.matrix_world.inverted()@source_arm.matrix_world
  for pb in arm.pose.bones:
   if pb.name not in source_arm.pose.bones:continue
   desired=transform@source_arm.pose.bones[pb.name].matrix
   parent_desired=transform@source_arm.pose.bones[pb.parent.name].matrix if pb.parent else None
   pb.matrix_basis=pb.bone.convert_local_to_pose(desired,pb.bone.matrix_local,parent_matrix=parent_desired if parent_desired is not None else __import__('mathutils').Matrix.Identity(4),parent_matrix_local=pb.parent.bone.matrix_local if pb.parent else __import__('mathutils').Matrix.Identity(4),invert=True)
   for path in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=path,frame=frame,group=pb.name)
 clips.append(action)
 for o in list(bpy.context.scene.objects):
  if o.name not in original:bpy.data.objects.remove(o,do_unlink=True)
arm.animation_data.action=None
for action in clips:
 track=arm.animation_data.nla_tracks.new();track.name=action.name;strip=track.strips.new(action.name,1,action)
 if hasattr(strip,'action_slot'):strip.action_slot=action.slots[0]
 track.mute=False
bpy.context.scene.frame_set(1)
for o in [arm,body,pack]:o['source_license']='CC0-1.0';o['source_author']='Kenney';o['adaptation']='Green/gold clothes and backpack; no university marks'
pack['source_license']='CC-BY-4.0';pack['source_author']='Open Campus contributors'
bpy.context.scene.render.fps=30
bpy.ops.file.pack_all()
asset=ROOT/'assets/characters';asset.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(asset/'campus-student.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in [arm,body,pack]:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'campus-student.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_extras=True,export_copyright='Kenney CC0; original Open Campus adaptation CC BY 4.0')
print('Exported rigged student',[(a.name,list(a.frame_range)) for a in clips])
