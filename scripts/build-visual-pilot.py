# SPDX-License-Identifier: Apache-2.0
"""Blender 4.5: --background --factory-startup --python this_file.

Original photo-informed art models, not measured facade reconstructions.
Run prepare-visual-pilot.py with the upstream Python environment first.
"""
import bpy
import bmesh
import json
import math
import hashlib
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT/'apps/web-preview/public/scene'
inp = json.loads((ROOT/'artifacts/visual-pilot-input.json').read_text(encoding='utf-8'))
manifest = json.loads((PUBLIC/'manifest.json').read_text(encoding='utf-8'))
field = json.loads((PUBLIC/manifest['heightfield_url']).read_text(encoding='utf-8'))
config = inp['configuration']
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def linear(c):
    return c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4

COLORS = {'brick':'B96F55','brick-dark':'9C5D4D','stone':'E4D6BB','roof':'A8ADB0',
          'glass':'608788','glass-light':'8FAEAE','grass':'91B66F','leaf':'658B54',
          'leaf-light':'829E59','evergreen':'385A45','paving':'CDBB9F','trunk':'77634F',
          'metal':'3F514B','path-edge':'ABA99A'}
mats={}
for name,h in COLORS.items():
    c=tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*c,1)
    node=mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*c,1);node.inputs['Roughness'].default_value=.87
    mats[name]=mat

parts={}
def mesh(key,verts,faces,mat):
    if key not in parts:parts[key]=[[],[],[]]
    vs,fs,ms=parts[key];offset=len(vs);vs.extend(verts)
    fs.extend([tuple(offset+i for i in f) for f in faces]);ms.extend([mat]*len(faces))

def cube(key,x,n,z,w,d,h,mat,angle=0):
    verts=[];c,s=math.cos(angle),math.sin(angle)
    for dz in [-h/2,h/2]:
        for dx,dn in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
            verts.append((x+c*dx-s*dn,n+s*dx+c*dn,z+dz))
    mesh(key,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def cylinder(key,x,n,z,r,h,mat,segments=10,top=None):
    top=r if top is None else top
    vs=[(x+rr*math.cos(i*math.tau/segments),n+rr*math.sin(i*math.tau/segments),zz)
        for rr,zz in [(r,z),(top,z+h)] for i in range(segments)]
    fs=[tuple(reversed(range(segments))),tuple(range(segments,segments*2))]
    fs += [(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
    mesh(key,vs,fs,mat)

def crown(key,x,n,z,rx,ry,rz,mat):
    vs=[];sides=9;rings=6
    for j in range(rings+1):
        a=math.pi*j/rings
        for i in range(sides):
            b=math.tau*i/sides+(j%2)*.12
            vs.append((x+rx*math.sin(a)*math.cos(b),n+ry*math.sin(a)*math.sin(b),z+rz*math.cos(a)))
    mesh(key,vs,[(j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i) for j in range(rings) for i in range(sides)],mat)

def ground(x,n):
    u=max(0,min(field['nx']-1.000001,(x-field['min_east_m'])/field['spacing_m']))
    v=max(0,min(field['ny']-1.000001,(n-field['min_north_m'])/field['spacing_m']))
    i,j=int(u),int(v);a,b=u-i,v-j
    at=lambda dx,dy:field['heights_m'][(j+dy)*field['nx']+i+dx]
    return at(0,0)+(at(1,0)-at(0,0))*a+(at(1,1)-at(1,0))*b if a>=b else at(0,0)+(at(1,1)-at(0,1))*a+(at(0,1)-at(0,0))*b

def prism(key,ring,z,h,mat):
    count=len(ring);vs=[(x,n,z+dz) for dz in [0,h] for x,n in ring]
    vectors=[Vector((x,n,z+h)) for x,n in ring];lookup={tuple(v):i for i,v in enumerate(vectors)}
    tris=[tuple(lookup[tuple(v)] if not isinstance(v,int) else v for v in tri) for tri in tessellate_polygon([vectors])]
    fs=[tuple(i+count for i in t) for t in tris]+[tuple(reversed(t)) for t in tris]
    fs +=[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh(key,vs,fs,mat)

def volume(key,x0,n0,x1,n1,b,h,mat='brick'):
    cube(key,(x0+x1)/2,(n0+n1)/2,b+h/2,x1-x0,n1-n0,h,mat)
    cube(key,(x0+x1)/2,(n0+n1)/2,b+h+.22,x1-x0+.6,n1-n0+.6,.44,'stone')
    cube(key,(x0+x1)/2,(n0+n1)/2,b+h+.48,x1-x0-.7,n1-n0-.7,.15,'roof')

def window(key,x,n,z,w=1.7,h=2.5,angle=0):
    cube(key,x,n,z,w+.25,.23,h+.25,'stone',angle)
    dx,dn=.14*math.sin(angle),-.14*math.cos(angle)
    cube(key,x+dx,n+dn,z,w,.08,h,'glass',angle)
    cube(key,x+dx*1.2,n+dn*1.2,z,.065,.09,h,'stone',angle)
    cube(key,x+dx*1.2,n+dn*1.2,z,w,.09,.065,'stone',angle)

def facade(key,x0,n0,x1,n1,b,h,spacing=4.5,rows=2):
    dx,dn=x1-x0,n1-n0;length=math.hypot(dx,dn)
    if length<5:return
    count=max(1,int(length/spacing));a=math.atan2(dn,dx)
    for row in range(rows):
        for i in range(count):
            t=(i+.5)/count
            window(key,x0+t*dx,n0+t*dn,b+2.7+row*(h-3.7)/rows,1.6,min(2.6,h/rows-1),a)

records={b['name']:b for b in manifest['buildings'] if b.get('name')}
names=['Knight Library','Johnson Hall','Erb Memorial Union','Jordan Schnitzer Museum of Art','Condon Hall','Chapman Hall','Gerlinger Hall','Hendricks Hall','Susan Campbell Hall','Collier House','Friendly Hall','Gerlinger Annex','Prince Lucien Campbell Hall']
names=[name for name in names if name in records]
for id in config.get('context_envelope_ids', []):
    b=next(b for b in manifest['buildings'] if b['id']==id)
    name='Pilot context '+id
    records[name]={**b,'name':name};names.append(name)

# Context refinements retain the historical footprint and roof-height envelope.
for name in names:
    if name in config['landmarks']:continue
    b=records[name];key=b['id'];ring=b['footprint_enu_m'];base=b['base_z_m'];height=b['height_m']
    prism(key,ring,base,height,'brick' if name!='Prince Lucien Campbell Hall' else 'stone')
    prism(key,ring,base+height,.38,'roof')
    signed=sum(x0*n1-x1*n0 for (x0,n0),(x1,n1) in zip(ring,ring[1:]+ring[:1]))
    for p,q in zip(ring,ring[1:]+ring[:1]):
        dx,dn=q[0]-p[0],q[1]-p[1];length=math.hypot(dx,dn)
        if length<7:continue
        ox,on=(dn/length*.16,-dx/length*.16) if signed>0 else (-dn/length*.16,dx/length*.16)
        # Window front is local -north; reverse the segment if its exterior is opposite.
        a,c=(p,q) if signed>0 else (q,p)
        facade(key,a[0]+ox,a[1]+on,c[0]+ox,c[1]+on,base,height,5, max(1,round(height/4.8)))

# Knight Library: historic north block, high windows, stone cornice and three balconies.
b=records['Knight Library'];key=b['id'];base=b['base_z_m']
volume(key,-612,-225,-509,-193,base,15.5)
volume(key,-612,-298,-583,-225,base,12.5)
volume(key,-535,-298,-509,-225,base,12.5)
volume(key,-602,-318,-518,-282,base,16,'brick-dark')
for i in range(7):
    x=-590+i*9.4
    window(key,x,-192.82,base+9.1,3.9,7.6,math.pi)
    cube(key,x,-192.55,base+14.1,5.8,.35,.65,'stone')
    window(key,x,-192.82,base+2.6,3.5,2.8,math.pi)
    if 2<=i<=4:
        cube(key,x,-191.6,base+5.3,5,2.4,.5,'stone')
        cube(key,x,-190.4,base+5.9,5,.3,1.1,'stone')
for x in [-605,-516]:
    window(key,x,-192.75,base+3,3.6,4.5,math.pi)
    cube(key,x,-191.8,base+.4,8,3,.8,'stone')
for n in range(-292,-226,6):
    for z in [base+3,base+8]:
        window(key,-612.15,n,z,2.6,2.7,-math.pi/2)
        window(key,-508.85,n,z,2.6,2.7,math.pi/2)
for x in [-610,-510]:
    cube(key,x,-192.6,base+8,1.3,.7,15.8,'stone')

# Johnson Hall: six-column north portico, two window levels and a broad stepped approach.
b=records['Johnson Hall'];key=b['id'];base=b['base_z_m']
volume(key,-418,-56,-384,-29,base,12.5)
cube(key,-401,-42.5,base+.9,35,28,1.8,'stone')
for x in [-414,-408.8,-403.6,-398.4,-393.2,-388]:
    cylinder(key,x,-25.7,base+1.3,.52,10.1,'stone',16,top=.45)
    cylinder(key,x,-25.7,base+1.1,.78,.4,'stone',16)
    cube(key,x,-25.7,base+11.6,1.35,1.3,.5,'stone')
cube(key,-401,-26,base+12.3,31,6,1.1,'stone')
cube(key,-401,-26,base+13,32,6.7,.35,'stone')
for i in range(7):cube(key,-401,-24+i*.7,base+.1+(6-i)*.15,30,5.2-i*.6,.2,'stone')
for x in [-414,-407.5,-394.5,-388]:
    for z in [base+3.6,base+8.6]:window(key,x,-28.8,z,2.7,3.5,math.pi)
window(key,-401,-28.6,base+3.3,3.2,4.6,math.pi)
facade(key,-418.15,-54,-418.15,-31,base,12.5,5,2)
facade(key,-383.85,-31,-383.85,-54,base,12.5,5,2)

# EMU: varied brick masses, glazed ground floor, curved Fishbowl and a shallow canopy.
b=records['Erb Memorial Union'];key=b['id'];base=b['base_z_m']
volume(key,-250,-66,-168,-33,base,13.8)
volume(key,-215,-96,-168,-66,base,9.3)
volume(key,-250,-96,-215,-66,base,7.4)
for x in range(-244,-171,6):
    window(key,x,-32.8,base+7.5,2.1,5,math.pi)
    window(key,x,-32.8,base+2.6,3.8,3.9,math.pi)
for n in [-37,-44,-51,-58]:
    window(key,-250.2,n,base+8.8,2.6,4.8,-math.pi/2)
    window(key,-250.2,n,base+2.6,4,3.9,-math.pi/2)
cube(key,-253,-48,base+5.5,9,24,.45,'stone')
for n in [-39,-48,-57]:cylinder(key,-256.5,n,base,.2,5.3,'metal',8)
for i in range(10):
    a=math.pi/2+i*math.pi/9;x=-235+19*math.cos(a);n=-78+15*math.sin(a)
    window(key,x,n,base+3,3.8,4.4,a+math.pi/2)
for i in range(3):cube(key,-265-i*3,-48,ground(-265-i*3,-48)+.12,3.1,32,.24,'paving')

# Terrain-draped lawn and illustrative paved connections (separate from Census geometry).
for surface in inp['surfaces']:
    verts=[(x,n,z+.03) for x,n,z in surface['vertices']]
    mesh('landscape-'+surface['kind'],verts,surface['faces'],'grass' if surface['kind']=='lawn' else 'paving')

for index,(x,n,height,conifer,tone) in enumerate(inp['trees']):
    z=ground(x,n);key='vegetation'
    cylinder(key,x,n,z,.22,height*.7,'trunk',7,top=.12)
    if conifer:
        for j in range(3):cylinder(key,x,n,z+height*(.24+j*.19),height*(.24-j*.045),height*.47,'evergreen',9,top=.05)
    else:
        leaf=['leaf','leaf-light','evergreen'][tone];r=height*.25
        for ox,on,oz,scale in [(0,0,.72,1),(-.55,.15,.65,.72),(.48,.28,.69,.75),(.1,-.45,.78,.65)]:
            crown(key,x+ox*r,n+on*r,z+height*oz,r*scale,r*scale*.93,r*scale*1.1,leaf)

# Low planting bands, benches, bollards and globe lamps provide a readable human scale.
for x in range(-590,-528,4):
    for n in [-173]:crown('planting',x,n,ground(x,n)+.8,2,1,.9,'leaf')
for i in range(24):
    a=i*math.tau/24;x=-401+5*math.cos(a);n=-12+3.3*math.sin(a)
    crown('planting',x,n,ground(x,n)+.6,.8,.6,.6,'leaf')
for x,n in [(-581,-58),(-581,-126),(-529,-100),(-449,-95),(-422,-180),(-380,-96),(-317,-120),(-279,-28),(-279,-66)]:
    z=ground(x,n)
    cube('furniture',x,n,z+.6,3,.8,.18,'trunk')
    cube('furniture',x,n+.4,z+1,3,.12,.65,'trunk')
    for dx in [-1.1,1.1]:cube('furniture',x+dx,n,z+.3,.12,.7,.6,'metal')
for x,n in [(-576,-170),(-530,-170),(-576,-100),(-530,-36),(-430,-85),(-360,-85),(-313,-30),(-280,-30),(-280,-65),(-420,-10),(-382,-10)]:
    z=ground(x,n);cylinder('furniture',x,n,z,.11,4.3,'metal',8)
    crown('furniture',x,n,z+4.4,.35,.35,.45,'stone')

objects=[]
for key,(verts,faces,material_names) in parts.items():
    data=bpy.data.meshes.new(key);data.from_pydata(verts,[],faces);data.update()
    names_used=list(dict.fromkeys(material_names))
    for name in names_used:data.materials.append(mats[name])
    slots={name:i for i,name in enumerate(names_used)}
    for poly,name in zip(data.polygons,material_names):poly.material_index=slots[name]
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(key,data);bpy.context.collection.objects.link(obj);objects.append(obj)
    if key.startswith('roof-'):
        obj['asset_kind']='building';obj['asset_id']=key;obj['reconstruction_status']='photo-informed-art-approximate'
        obj['display_name']=next(b['name'] for b in records.values() if b['id']==key)
    else:obj['asset_kind']='landscape-surface' if key.startswith('landscape-') else 'landscape-detail'
    obj['rights']='Original model contribution: CC BY 4.0; reference photographs not bundled'

scene=bpy.context.scene;scene.unit_settings.system='METRIC'
scene['art_status']=config['status'];scene['source_manifest_sha256']=inp['manifest_sha256']
scene['attribution']='Open Campus: UO — Zhongyi "William" Qiu and contributors — CC BY 4.0'
bpy.ops.object.light_add(type='SUN',location=(-600,-150,400));bpy.context.object.rotation_euler=(.4,-.5,-.5);bpy.context.object.data.energy=2.2
bpy.ops.object.camera_add(location=(-165,-600,450));camera=bpy.context.object
camera.rotation_euler=(Vector((-415,-140,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=610;scene.camera=camera
scene.world.color=(.6,.7,.65)
asset=ROOT/'assets/visual-pilot';asset.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(asset/'knight-emu-johnson.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(PUBLIC/'visual-pilot.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False,export_copyright=scene['attribution'])
presentation={
    'version':1,'id':config['id'],'asset_url':'visual-pilot.glb',
    'replaces_building_ids':[records[n]['id'] for n in names],
    'landmark_building_ids':[records[n]['id'] for n in config['landmarks']],
    'overview':config['overview'],'lighting':config['lighting'],
    'status':config['status'],'stats':{'trees':len(inp['trees']),'landmarkBuildings':3},
    'source_manifest_sha256':inp['manifest_sha256'],
    'heightfield_sha256':inp['heightfield_sha256'],
    'asset_sha256':hashlib.sha256((PUBLIC/'visual-pilot.glb').read_bytes()).hexdigest(),
    'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'credit':scene['attribution'],
}
(PUBLIC/'presentation.json').write_text(json.dumps(presentation,indent=2)+'\n',encoding='utf-8')
print('VISUAL PILOT EXPORTED',len(objects),'editable semantic meshes;',len(inp['trees']),'trees')
