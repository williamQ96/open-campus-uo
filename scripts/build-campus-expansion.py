# SPDX-License-Identifier: Apache-2.0
"""Blender: photo grammar + seeded low-poly context, keeping geographic envelopes."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ROOT=Path(__file__).resolve().parents[1];PUBLIC=ROOT/'apps/web-preview/public/scene'
source=json.loads((ROOT/'artifacts/campus-expansion-input.json').read_text(encoding='utf-8'));config=source['config'];baseline=source['baseline']
manifest=json.loads((PUBLIC/'manifest.json').read_text(encoding='utf-8'));field=json.loads((PUBLIC/manifest['heightfield_url']).read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(ROOT/config['source_blend']),link=False) as (data,loaded):
 loaded.objects=[name for name in data.objects if name in source['protected_ids'] or name in ['landscape-lawn','landscape-paving','vegetation','understory','planting','furniture']]
for obj in loaded.objects:
 if obj:
  bpy.context.collection.objects.link(obj)
  if obj.name in ['landscape-lawn','landscape-paving']:obj['heightfield_offset_m']=.07
objects=[o for o in loaded.objects if o];original_by_id={o.get('asset_id'):o for o in objects if o.get('asset_id')}
parts={};members=defaultdict(list);metadata={};window_counts={}
PALETTE={'brick':'B96F55','brick-dark':'9C5D4D','stone':'E4D6BB','roof':'929C9F','glass':'608788','metal':'3F514B','wood':'8E7154','cream':'EEE6D3','awning':'824B4D','grass':'9CB980','trunk':'77634F'}
def color(c):
 h=PALETTE.get(c,c);v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,)
def add(key,vertices,faces,c):
 if key not in parts:parts[key]=[[],[],[]]
 vs,fs,cs=parts[key];offset=len(vs);vs.extend(vertices);fs.extend([tuple(i+offset for i in f) for f in faces]);cs.extend([c]*len(faces))
def cube(key,x,n,z,w,d,h,c,angle=0):
 co,si=math.cos(angle),math.sin(angle);v=[]
 for dz in [-h/2,h/2]:
  for dx,dn in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:v.append((x+co*dx-si*dn,n+si*dx+co*dn,z+dz))
 add(key,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],c)
def face(key,points,c):
 vectors=[Vector(p) for p in points];lookup={tuple(v):i for i,v in enumerate(vectors)}
 faces=[tuple(v if isinstance(v,int) else lookup[tuple(v)] for v in tri) for tri in tessellate_polygon([vectors])]
 add(key,points,faces,c)
def prism(key,ring,z,h,c):
 count=len(ring);vs=[(x,n,z+dz) for dz in [0,h] for x,n in ring]
 add(key,vs,[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)],c)
 face(key,[(x,n,z+h) for x,n in ring],c)
def ground(x,n):
 u=max(0,min(field['nx']-1.00001,(x-field['min_east_m'])/field['spacing_m']));v=max(0,min(field['ny']-1.00001,(n-field['min_north_m'])/field['spacing_m']));i,j=int(u),int(v);a,b=u-i,v-j
 at=lambda dx,dy:field['heights_m'][(j+dy)*field['nx']+i+dx]
 return at(0,0)+(at(1,0)-at(0,0))*a+(at(1,1)-at(1,0))*b if a>=b else at(0,0)+(at(1,1)-at(0,1))*a+(at(0,1)-at(0,0))*b
def panel(key,x,n,z,w,h,c,angle=0,offset=0):
 co,si=math.cos(angle),math.sin(angle);ox,on=si*offset,-co*offset
 add(key,[(x-co*w/2+ox,n-si*w/2+on,z-h/2),(x+co*w/2+ox,n+si*w/2+on,z-h/2),(x+co*w/2+ox,n+si*w/2+on,z+h/2),(x-co*w/2+ox,n-si*w/2+on,z+h/2)],[(0,1,2,3)],c)
def window(key,x,n,z,w,h,angle=0,detailed=False):
 panel(key,x,n,z,w+.22,h+.24,'stone',angle,.08);panel(key,x,n,z,w,h,'glass',angle,.10)
 if detailed:
  panel(key,x,n,z,.06,h,'cream',angle,.12)
  for dz in [-h/4,0,h/4]:panel(key,x,n,z+dz,w,.055,'cream',angle,.125)
def arch(key,x,n,z,r,thickness,c,angle=0):
 co,si=math.cos(angle),math.sin(angle);v=[]
 for radius in [r,r+thickness]:
  for i in range(13):
   a=math.pi*i/12;dx=math.cos(a)*radius;v.append((x+co*dx,n+si*dx,z+math.sin(a)*radius))
 add(key,v,[(i,i+1,i+14,i+13) for i in range(12)],c)
def sphere(key,x,n,z,r,c,squash=1):
 v=[]
 for j in range(5):
  a=math.pi*j/4
  for i in range(8):
   b=math.tau*i/8;v.append((x+r*math.sin(a)*math.cos(b),n+r*math.sin(a)*math.sin(b),z+r*math.cos(a)*squash))
 add(key,v,[(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(4) for i in range(8)],c)

for item in source['plan']:
 ring=item['footprint_enu_m'];x=sum(p[0] for p in ring)/len(ring);n=sum(p[1] for p in ring)/len(ring)
 key=item['id'];metadata[key]=item
 if not item.get('name'):
  batch=f"context-{item['tier']}-{math.floor((x+1000)/500)}-{math.floor((n+1000)/500)}";members[batch].append(item['id'])
 base=item['base_z_m'];h=item['wall_height_m'];variant=item['variant'];campus=item['tier']!='background'
 walls=(['B96F55','AD7861','C1A37F','D4CCB9'] if campus else ['B9B8A8','B9BEB0','BFAE9B','AF9E8F'])[variant]
 roofs={'weathered-metal':'847854','muted-tile':'AA7055','dark-slate':'586A63','flat-parapet':'B3A282','flat-services':'98977B','flat-skylights':'A7967D'}[item['roof_style']]
 if item['tier']=='photo-grammar':walls='B96F55';roofs='586A63'
 prism(key,ring,base,h,walls)
 if item['roof_faces']:
  for roof in item['roof_faces']:
   # Two restrained tones make pitch readable under a three-band toon ramp.
   shade=1.0 if sum(p[1] for p in roof)/len(roof)>n else .80
   roof_tone=''.join(f'{round(int(roofs[i:i+2],16)*shade):02X}' for i in (0,2,4))
   face(key,roof,roof_tone)
   for rp,rq in zip(roof,roof[1:]+roof[:1]):
    if abs(rp[2]-item['roof_z_m'])<.001 and abs(rq[2]-item['roof_z_m'])<.001:
     length=math.dist(rp[:2],rq[:2])
     if length>.1:cube(key,(rp[0]+rq[0])/2,(rp[1]+rq[1])/2,item['roof_z_m']-.04,length,.16,.08,'metal',math.atan2(rq[1]-rp[1],rq[0]-rp[0]))
   # Fill gable ends only where roof-plane edges follow the original boundary.
   for p,q in zip(roof,roof[1:]+roof[:1]):
    mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
    on_edge=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
     dx,dn=b[0]-a[0],b[1]-a[1];ll=dx*dx+dn*dn
     if ll<.001:continue
     t=max(0,min(1,((mid[0]-a[0])*dx+(mid[1]-a[1])*dn)/ll))
     if math.hypot(mid[0]-a[0]-t*dx,mid[1]-a[1]-t*dn)<.01:on_edge=True;break
    if on_edge:add(key,[(p[0],p[1],base+h),(q[0],q[1],base+h),q,p],[(0,1,2,3)],walls)
 else:prism(key,ring,base+h-.12,.12,roofs)
 # Deliberately inferred roof grammar: no photographic textures or claim of exact equipment.
 for a,b in item['roof_seams']:
  cube(key,(a[0]+b[0])/2,(a[1]+b[1])/2,a[2],math.dist(a[:2],b[:2]),.055,.035,'8F896D' if item['roof']=='flat' else '615B48',math.atan2(b[1]-a[1],b[0]-a[0]))
 if item['roof']=='flat':
  for a,b in zip(ring,ring[1:]+ring[:1]):
   cube(key,(a[0]+b[0])/2,(a[1]+b[1])/2,item['roof_z_m']-.20,math.dist(a,b),.14,.40,'stone',math.atan2(b[1]-a[1],b[0]-a[0]))
  for rx,rn,rz,kind in item['roof_details']:
   cube(key,rx,rn,rz+.11,1.7,1.3,.22,'glass' if kind=='flat-skylights' else 'metal')
   cube(key,rx,rn,rz+.23,1.9,1.5,.04,'stone')
 signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]));edges=[]
 for p,q in zip(ring,ring[1:]+ring[:1]):
  if signed<0:p,q=q,p
  length=math.dist(p,q)
  if length<3:continue
  angle=math.atan2(q[1]-p[1],q[0]-p[0]);edges.append((length,p,q,angle))
  if campus:panel(key,(p[0]+q[0])/2,(p[1]+q[1])/2,base+h-.25,length,.35,'stone',angle,.06)
 budget=item['window_budget'];slots=[];floors=max(1,min(5,round(h/4.3)))
 for length,p,q,angle in edges:
  bays=max(1,min(18,int(length/(4.6 if campus else 5))))
  for row in range(floors):
   for i in range(bays):
    t=(i+.5)/bays;slots.append((p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t,base+min(h-1.3,2.1+row*h/floors),min(2.1,length/bays*.43),min(2.7,h/floors*.54),angle))
 stride=max(1,math.ceil(len(slots)/max(1,budget)));chosen=slots[::stride][:budget] if budget else []
 for values in chosen:window(key,*values,detailed=campus and bool(item.get('name')))
 window_counts[item['id']]=len(chosen)
 if edges and item.get('name') and item['tier']!='photo-grammar':
  length,p,q,angle=max(edges);window(key,(p[0]+q[0])/2,(p[1]+q[1])/2,base+1.6,2.3,3,angle,True)

# Gerlinger Hall: symmetric sash bays, awnings and central pediment from 2013 photo.
b=next(b for b in source['plan'] if b.get('name')=='Gerlinger Hall');key=b['id'];base=b['base_z_m']
for x in [-420,-411.5,-403,-394.5,-386]:
 for z in [base+3.1,base+8.5]:window(key,x,-200.6,z,2.8,3.8,math.pi,True)
 add(key,[(x-1.8,-200.3,base+5.3),(x+1.8,-200.3,base+5.3),(x+1.8,-198.6,base+4.3),(x-1.8,-198.6,base+4.3)],[(0,1,2,3)],'awning')
 for z in [base+5.8,base+11]:cube(key,x,-200.4,z,3.5,.5,.28,'stone')
add(key,[(x,n,base+z) for n in [-199.9,-200.4] for x,z in [(-424,12),(-382,12),(-403,15.5)]],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],'cream')
arch(key,-403,-200.25,base+13.2,.62,.18,'stone')
for x in [-408,-398]:cube(key,x,-199.8,base+2.0,.65,.7,4,'stone')
cube(key,-403,-199.8,base+4.25,11,1.1,.55,'stone');window(key,-403,-199.4,base+1.9,4.2,3.8,math.pi,True)
for x in [-438,-367]:cube(key,x,-210,base+14.2,1.7,1.7,3.4,'brick-dark')
window_counts[key]=11

# Gerlinger Annex: repeated arched sash bays, cream band, round accents and dormers.
b=next(b for b in source['plan'] if b.get('name')=='Gerlinger Annex');key=b['id'];base=b['base_z_m']
for side,angle,n in [('north',math.pi,-242.0),('south',0,-270.0)]:
 for i in range(11):
  x=-494+i*5.45
  panel(key,x,n,base+9.3,5.2,3.6,'cream',angle,.065)
  window(key,x,n,base+4.8,3.0,7.0,angle,True);arch(key,x,n+(.13 if side=='north' else -.13),base+8.3,1.5,.22,'stone')
  if i<10:arch(key,x+2.72,n+(.16 if side=='north' else -.16),base+9.2,.38,.13,'brick-dark')
  # Dormers stay within the historical footprint and source roof-height envelope.
  if side=='north':
   cube(key,x,-246.2,base+14.0,3.2,3.0,2.9,'stone');window(key,x,-244.6,base+14.0,2.4,2.5,math.pi,True)
   cube(key,x,-246.2,base+15.55,3.6,3.6,.22,'stone')
 cube(key,-466.8,n,base+10.95,63,.5,.32,'stone')
window_counts[key]=33

# Restrained additions to the preserved three landmark meshes, not a rebuild.
records={b['name']:b for b in manifest['buildings'] if b.get('name')}
b=records['Knight Library'];key=b['id'];base=b['base_z_m']
for x in [-599,-589,-579,-569,-559,-549,-539,-529,-519]:
 arch(key,x,-192.03,base+15.5,.42,.16,'stone')
b=records['Erb Memorial Union'];key=b['id'];base=b['base_z_m']
for x in range(-246,-170,4):cube(key,x,-32.35,base+5.1,.09,.35,3.8,'metal')
for x in [-241,-220,-199,-178]:cube(key,x,-32.0,base+5.25,13,2.2,.18,'stone')
b=records['Johnson Hall'];key=b['id'];base=b['base_z_m']
for x in [-414,-407.5,-394.5,-388]:cube(key,x,-28.32,base+1.4,3.8,.34,.25,'stone')

# Treat preserved landmark roof materials too; keep their authored silhouette intact.
for id,obj in original_by_id.items():
 roof_slots=[]
 for index,material in enumerate(obj.data.materials):
  if material and material.name.split('.')[0]=='roof':
   material=material.copy();material.name='Inferred weathered landmark roof';rgba=color('766C50');material.diffuse_color=rgba
   if material.use_nodes:material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=rgba
   obj.data.materials[index]=material;roof_slots.append(index)
 for polygon in list(obj.data.polygons):
  if polygon.material_index not in roof_slots or polygon.normal.z<.9 or polygon.area<20:continue
  vertices=[obj.matrix_world@obj.data.vertices[i].co for i in polygon.vertices]
  xmin,xmax=min(p.x for p in vertices),max(p.x for p in vertices);nmin,nmax=min(p.y for p in vertices),max(p.y for p in vertices);z=sum(p.z for p in vertices)/len(vertices)
  def inside(x,n):
   hit=False
   for a,b in zip(vertices,vertices[1:]+vertices[:1]):
    if (a.y>n)!=(b.y>n) and x<(b.x-a.x)*(n-a.y)/(b.y-a.y)+a.x:hit=not hit
   return hit
  for f in [.25,.5,.75]:
   rx=xmin+(xmax-xmin)*f;rn=(nmin+nmax)/2
   if all(inside(rx+dx,rn+dn) for dx,dn in [(-1,-.7),(1,-.7),(1,.7),(-1,.7)]):
    cube(id,rx,rn,z+.08,1.8,1.2,.12,'glass');cube(id,rx,rn,z+.16,2,1.4,.04,'stone')

# Extra landscape is explicitly inferred beyond the limited archived aerial crop.
lawn=source['lawn'];add('campus-lawn-extension',lawn['vertices'],lawn['faces'],'grass')
for i,(x,n,h,tone) in enumerate(source['trees']):
 z=ground(x,n);cube('campus-trees',x,n,z+h*.3,.3,.3,h*.6,'trunk')
 sphere('campus-trees',x,n,z+h*.7,h*.28,['67865B','81955E','4B7355','729367'][tone],1.25)

# A single vertex-color material per new semantic mesh keeps context inexpensive.
material=bpy.data.materials.new('Original low-poly vertex palette');material.use_nodes=True
node=material.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='Col';bsdf=material.node_tree.nodes.get('Principled BSDF');material.node_tree.links.new(node.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.9
for key,(vertices,faces,colors) in parts.items():
 data=bpy.data.meshes.new(key);data.from_pydata(vertices,[],faces);data.update();data.materials.append(material)
 if key=='campus-lawn-extension':
  for polygon in data.polygons:polygon.use_smooth=True
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 attribute=data.color_attributes.new(name='Col',type='FLOAT_COLOR',domain='CORNER')
 for polygon,c in zip(data.polygons,colors):
  rgba=color(c)
  for index in polygon.loop_indices:attribute.data[index].color=rgba
 obj=bpy.data.objects.new(key,data);bpy.context.collection.objects.link(obj)
 if key in original_by_id:
  original=original_by_id[key];bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);original.select_set(True);bpy.context.view_layer.objects.active=original;bpy.ops.object.join();continue
 if key in members:
  obj['asset_kind']='context-building-batch';obj['asset_ids']=members[key];obj['appearance_status']='Seeded types/palette; original coordinates and footprints retained'
 elif key in metadata:
  item=metadata[key];obj['asset_kind']='building';obj['asset_id']=key;obj['display_name']=item['name'] or 'Illustrative context '+item['id'];obj['detail_tier']=item['tier'];obj['appearance_status']=item['status'];obj['reference_ids']=[item['reference']] if item.get('reference') else []
 else:obj['asset_kind']='landscape-surface' if key=='campus-lawn-extension' else 'landscape-detail'
 if key=='campus-lawn-extension':obj['heightfield_offset_m']=.04
 obj['rights']='Original geometry: CC BY 4.0; source photo terms remain separate; no photographic textures';objects.append(obj)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene['art_status']=config['status'];scene['source_manifest_sha256']=source['source_manifest_sha256']
scene['method']='Photo grammar in focus; inexpensive geography-preserving context; spatial haze is a viewer effect'
source_blend=ROOT/config.get('output_source_blend','assets/campus-expansion/eugene-campus.blend');source_blend.parent.mkdir(parents=True,exist_ok=True)
# Keep every geographic identity editable in the Blender source. Merge copies
# only after saving, so delivery cost does not dictate authoring granularity.
by_id={o.get('asset_id'):o for o in objects if o.get('asset_id')}
assert len(by_id)==len(manifest['buildings'])
bpy.ops.wm.save_as_mainfile(filepath=str(source_blend))
anonymous={id for ids in members.values() for id in ids}
export_objects=[o for o in objects if o.get('asset_id') not in anonymous]
for batch,ids in members.items():
 copies=[]
 for id in ids:
  obj=by_id[id].copy();obj.data=obj.data.copy();bpy.context.collection.objects.link(obj);copies.append(obj)
 bpy.ops.object.select_all(action='DESELECT')
 for obj in copies:obj.select_set(True)
 combined=copies[0];bpy.context.view_layer.objects.active=combined;bpy.ops.object.join();combined.name=batch
 for key in ['asset_id','display_name','detail_tier','reference_ids']:
  if key in combined:del combined[key]
 combined['asset_kind']='context-building-batch';combined['asset_ids']=ids
 combined['appearance_status']='Seeded context appearance; original positions and footprints retained'
 export_objects.append(combined)
bpy.ops.object.select_all(action='DESELECT')
for obj in export_objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(PUBLIC/'campus-expanded.next.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_copyright='Open Campus contributors — Original model geometry CC BY 4.0; photographs remain separate')
(PUBLIC/'campus-expanded.next.glb').replace(PUBLIC/'campus-expanded.glb')
ids=[b['id'] for b in manifest['buildings']]
output={**baseline,'editable_source':str(source_blend.relative_to(ROOT)).replace('\\','/'),'roof_status':config['roof_status'],'roof_treatments':{**{p['id']:p['roof_style'] for p in source['plan']},**{id:'retained-landmark-weathered-roof' for id in original_by_id}},'id':config['id'],'asset_url':'campus-expanded.glb','replaces_building_ids':ids,'landmark_building_ids':baseline['landmark_building_ids']+[records[name]['id'] for name in config['photo_refinements']],'context_fog':config['context_fog'],'status':config['status'],'stats':{'trees':300+len(source['trees']),'landmarkBuildings':5,'contextBuildings':source['counts']['background'],'campusBuildings':len(ids)-source['counts']['background']},'inferred_landscape':{'extra_trees':len(source['trees']),'status':'Procedural campus planting and lawns beyond the limited archived aerial crop; not measured or image-extracted'},'reference_image_ids':baseline['reference_image_ids']+[p['reference'] for p in config['photo_refinements'].values()],'source_manifest_text_sha256':source['source_manifest_text_sha256'],'heightfield_text_sha256':source['source_heightfield_text_sha256'],'source_manifest_sha256':source['source_manifest_sha256'],'heightfield_sha256':source['source_heightfield_sha256'],'art_pipeline':source['art_pipeline'],'preserved_source_blend_sha256':config['source_blend_sha256'],'reference_manifest_sha256':hashlib.sha256((ROOT/'data/reference-images/manifest.json').read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'asset_sha256':hashlib.sha256((PUBLIC/'campus-expanded.glb').read_bytes()).hexdigest()}
(PUBLIC/'presentation.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
audit={'source_manifest_sha256':source['source_manifest_sha256'],'preserved_source_blend_sha256':config['source_blend_sha256'],'replaced_ids':ids,'protected_ids':source['protected_ids'],'appearance_plan':source['plan'],'window_counts':window_counts,'context_batches':dict(members),'extra_trees':len(source['trees']),'mesh_count':len(export_objects),'editable_source':str(source_blend.relative_to(ROOT)).replace('\\','/'),'roof_style_counts':dict(__import__('collections').Counter([p['roof_style'] for p in source['plan']])),'source_mesh_count':len(objects),'source_building_objects':len(by_id),'runtime_bytes':(PUBLIC/'campus-expanded.glb').stat().st_size,'method':'Randomize archetypes/palette only; original coordinates, footprints, heights and roads are fixed. Background geometry is an illustrative original open component library, not a surveyed building inventory.'}
(ROOT/'data/metadata/campus-expansion-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
print('EXPORTED',len(export_objects),'runtime meshes /',len(objects),'editable source meshes',len(ids),'building identities',len(members),'context batches',output['stats'])
