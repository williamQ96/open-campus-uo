# SPDX-License-Identifier: Apache-2.0
import bpy,json,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];pub=ROOT/'apps/web-preview/public/scene';data=np.load(ROOT/'artifacts/phase13-landcover.npz')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mesh=bpy.data.meshes.new('Open inferred ground cover');mesh.from_pydata(data['vertices'].tolist(),[],data['faces'].tolist());mesh.update()
color=mesh.color_attributes.new(name='Col',type='FLOAT_COLOR',domain='POINT');rgb=data['colors'];linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);rgba=np.column_stack([linear,np.ones(len(rgb))]);color.data.foreach_set('color',rgba.ravel())
for p in mesh.polygons:p.use_smooth=True
mat=bpy.data.materials.new('Matte inferred campus and urban ground');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.98;node=mat.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='Col';mat.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color']);mesh.materials.append(mat)
o=bpy.data.objects.new('Ground cover foundation',mesh);bpy.context.collection.objects.link(o);o['asset_kind']='landscape-surface';o['surface_layer']='foundation';o['heightfield_offset_m']=.018;o['surface_grain']=.10;o['status']='Original stylized inferred surface colors guided by archived NAIP; no photographic texture';o.select_set(True);bpy.context.view_layer.objects.active=o
out=ROOT/'assets/landcover';out.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out/'eugene-ground.blend'))
bpy.ops.export_scene.gltf(filepath=str(pub/'landcover.next.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=False,export_copyright='Original ground art CC BY 4.0, Open Campus contributors; NAIP reference remains public-domain and separate')
(pub/'landcover.next.glb').replace(pub/'landcover.glb')
p=pub/'presentation.json';d=json.loads(p.read_text(encoding='utf-8'));d['landcover_url']='landcover.glb';d['landcover_sha256']=hashlib.sha256((pub/'landcover.glb').read_bytes()).hexdigest();d['landcover_status']='Full-extent inferred grass/concrete/asphalt foundation, guided by archived 2024 NAIP; not a land-use survey';d['reference_image_ids']=list(dict.fromkeys(d['reference_image_ids']+['naip-2024-main-campus-rgb']));p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('LANDCOVER',len(mesh.vertices),len(mesh.polygons),(pub/'landcover.glb').stat().st_size)
