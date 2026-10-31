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
          'metal':'3F514B','path-edge':'ABA99A','bronze':'796A49','wood':'8E7154',
          'cream':'EEE6D3','shrub':'577750'}
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

def beam(key,p,q,r,mat='metal'):
    p,q=Vector(p),Vector(q);direction=(q-p).normalized()
    side=direction.cross(Vector((0,0,1)))
    if side.length<.001:side=Vector((1,0,0))
    side.normalize();up=direction.cross(side).normalized()
    vs=[tuple(center+dx*side+dy*up) for center in [p,q] for dx,dy in [(-r,-r),(r,-r),(r,r),(-r,r)]]
    mesh(key,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def detailed_window(key,x,n,z,w,h,angle=math.pi,columns=2,rows=4):
    c,s=math.cos(angle),math.sin(angle);out=(s,-c)
    cube(key,x,n,z,w+.38,.30,h+.38,'stone',angle)
    cube(key,x+out[0]*.18,n+out[1]*.18,z,w,.12,h,'metal',angle)
    cube(key,x+out[0]*.25,n+out[1]*.25,z,w-.16,.06,h-.16,'glass',angle)
    for i in range(1,columns):
        dx=w*(i/columns-.5)
        cube(key,x+c*dx+out[0]*.30,n+s*dx+out[1]*.30,z,.055,.07,h,'metal',angle)
    for j in range(1,rows):
        cube(key,x+out[0]*.30,n+out[1]*.30,z+h*(j/rows-.5),w,.07,.055,'metal',angle)
    # A restrained, original colored-glass accent, with no photographic textures.
    dx=w*.30
    cube(key,x+c*dx+out[0]*.29,n+s*dx+out[1]*.29,z+h*.25,w*.17,.035,h*.28,'glass-light',angle)

def inscription(key,text,x,n,z,size=1,angle=math.pi):
    curve=bpy.data.curves.new('architectural lettering','FONT');curve.body=text
    curve.align_x='CENTER';curve.align_y='CENTER';curve.size=size;curve.extrude=.008;curve.resolution_u=3
    obj=bpy.data.objects.new('temporary lettering',curve);bpy.context.collection.objects.link(obj)
    obj.location=(x,n,z);obj.rotation_euler=(math.pi/2,0,angle)
    bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=evaluated.to_mesh()
    mesh(key,[tuple(obj.matrix_world@v.co) for v in data.vertices],[tuple(p.vertices) for p in data.polygons],'bronze')
    evaluated.to_mesh_clear();bpy.data.objects.remove(obj,do_unlink=True);bpy.data.curves.remove(curve)

def approach_steps(key,x,n,width,base,count=9,run=.72):
    bottom=ground(x,n);rise=(base-bottom)/count
    for i in range(count):
        top=bottom+(i+1)*rise
        cube(key,x,n-i*run,(bottom+top)/2,width,run+.03,max(.12,top-bottom),'stone')
    for dx in [-width/2+.5,width/2-.5]:
        for i in [0,count//2,count-1]:
            z=bottom+(i+1)*rise
            beam(key,(x+dx,n-i*run,z),(x+dx,n-i*run,z+1),.055)
        beam(key,(x+dx,n,bottom+rise+1),(x+dx,n-(count-1)*run,base+1),.055)

def historic_lantern(key,x,n,z):
    cube(key,x,n,z+.45,1.05,1.05,.9,'brick-dark')
    cube(key,x,n,z+.96,1.25,1.25,.16,'stone')
    cube(key,x,n,z+1.8,.62,.62,1.5,'bronze')
    for dx,dn in [(0,-.325),(0,.325),(-.325,0),(.325,0)]:
        cube(key,x+dx,n+dn,z+1.8,.47 if dx==0 else .025,.025 if dx==0 else .47,1.23,'cream')
    cube(key,x,n,z+2.62,.78,.78,.14,'bronze')

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

# Knight Library: archived north-facade and lantern photos; unseen elevations inferred.
b=records['Knight Library'];key=b['id'];base=b['base_z_m']
volume(key,-612,-225,-509,-193,base,15.5)
volume(key,-612,-298,-583,-225,base,12.5)
volume(key,-535,-298,-509,-225,base,12.5)
volume(key,-602,-318,-518,-282,base,16,'brick-dark')
pattern=config['facade_patterns']['knight-north']
for i,bay in enumerate(sorted(inp['facade_modules']['knight-north'],key=lambda bay:bay['east_m'])):
    x=bay['east_m']
    # Brick reveals, dark many-pane glazing and shallow framed frieze panels.
    cube(key,x,-192.84,base+9.1,4.9,.28,8.6,'brick-dark')
    detailed_window(key,x,bay['north_m'],bay['height_m'],*pattern['opening_m'],bay['yaw_rad'],pattern['pane_columns'],pattern['pane_rows'])
    cube(key,x,-192.53,base+14.0,5.8,.40,.72,'stone')
    cube(key,x,-192.27,base+14.0,5.2,.08,.40,'brick-dark')
    detailed_window(key,x,-192.6,base+2.5,3.5,2.5,columns=3,rows=3)
    if 2<=i<=4:
        cube(key,x,-191.6,base+5.3,5,2.4,.5,'stone')
        for dx in [-2.35,2.35]:cube(key,x+dx,-191.4,base+5.85,.22,2.2,1.05,'stone')
        beam(key,(x-2.35,-190.4,base+6.3),(x+2.35,-190.4,base+6.3),.07,'bronze')
        for dx in [-1.8,-1.2,-.6,0,.6,1.2,1.8]:
            beam(key,(x+dx,-190.4,base+5.5),(x+dx,-190.4,base+6.3),.035,'bronze')
for x in [-605,-516]:
    detailed_window(key,x,-192.5,base+2.7,3.6,4.5,columns=2,rows=3)
    approach_steps(key,x,-186,8,base+.45,6,.65)
    for dx in [-3.4,3.4]:historic_lantern(key,x+dx,-190.3,base+.45)
cube(key,-560.5,-192.55,base+.52,104,.5,1.04,'stone')
for z,w,d in [(15.0,104,.7),(15.45,105,1.05),(16.05,104,.7)]:
    cube(key,-560.5,-192.7,base+z,w,d,.32,'stone')
for x in range(-610,-510,2):
    cube(key,x,-192.15,base+15.62,.52,.60,.42,'stone')
for x in [-599.5,-590,-580.6,-571.2,-561.8,-552.4,-543,-533.6,-524.2]:
    crown(key,x,-192.5,base+16.4,.45,.18,.42,'stone')
inscription(key,'KNIGHT LIBRARY',-560.5,-192.15,base+14.08,.63)
for n in range(-292,-226,6):
    for z in [base+3,base+8]:
        window(key,-612.15,n,z,2.6,2.7,-math.pi/2)
        window(key,-508.85,n,z,2.6,2.7,math.pi/2)
for x in [-610,-510]:
    cube(key,x,-192.6,base+8,1.3,.7,15.8,'stone')
for x in [-599,-522]:
    for n in range(-281,-234,9):
        cube(key,x,n,base+13.1,4.5,5,.55,'roof')

# Johnson Hall: fluted colonnade, layered entablature, parapet, rear green awnings.
b=records['Johnson Hall'];key=b['id'];base=b['base_z_m']
volume(key,-418,-56,-384,-29,base,12.5)
cube(key,-401,-42.5,base+.9,35,28,1.8,'stone')
for bay in inp['facade_modules']['johnson-colonnade']:
    x=bay['east_m']
    cylinder(key,x,-25.7,base+1.3,.52,10.1,'stone',16,top=.45)
    cylinder(key,x,-25.7,base+1.1,.78,.4,'stone',16)
    cube(key,x,-25.7,base+11.6,1.35,1.3,.5,'stone')
    for i in range(12):
        a=i*math.tau/12
        cylinder(key,x+.48*math.cos(a),-25.7+.48*math.sin(a),base+1.75,.047,9.1,'cream',5)
    for dx in [-.49,.49]:crown(key,x+dx,-25.35,base+11.32,.26,.19,.24,'cream')
cube(key,-401,-26,base+12.3,31,6,1.1,'stone')
cube(key,-401,-26,base+13,32,6.7,.35,'stone')
cube(key,-401,-26,base+14.05,31,5.6,1.7,'brick')
for x in [-416,-409,-393,-386]:cube(key,x,-23.1,base+14.1,.65,.4,1.9,'stone')
for z in [13.3,14.9]:cube(key,-401,-23,base+z,31.6,.5,.24,'stone')
cube(key,-401,-22.84,base+12.35,19,.16,.95,'cream')
inscription(key,'JOHNSON HALL',-401,-22.72,base+12.35,.80)
crown(key,-401,-23.0,base+15.25,1.1,.3,1.1,'stone')
crown(key,-401,-22.68,base+15.25,.7,.08,.7,'bronze')
for x in range(-415,-386,2):cube(key,x,-22.8,base+12.91,.55,.55,.35,'stone')
approach_steps(key,-401,-16,29,base+1.1,10,.8)
for x in [-414,-407.5,-394.5,-388]:
    for z in [base+3.6,base+8.6]:detailed_window(key,x,-28.7,z,3.15,3.9,columns=2,rows=3)
cube(key,-401,-28.6,base+3.1,3.1,.28,4.4,'wood')
detailed_window(key,-401,-28.4,base+3.1,2.6,4.0,columns=2,rows=3)
for dx in [-.35,.35]:cube(key,-401+dx,-28.02,base+2.8,.07,.09,.75,'bronze')
facade(key,-418.15,-54,-418.15,-31,base,12.5,5,2)
facade(key,-383.85,-31,-383.85,-54,base,12.5,5,2)
for x in [-413,-406.8,-395.2,-389]:
    for z in [base+3.5,base+8.8]:
        detailed_window(key,x,-56.2,z,3.2,3.1,0,2,3)
        # Sloping green awnings simplified from the archived 2012 rear view.
        mesh(key,[(x-1.9,-56.4,z+1.7),(x+1.9,-56.4,z+1.7),(x+1.9,-57.9,z+.8),(x-1.9,-57.9,z+.8)],[(0,1,2,3)],'evergreen')
        cube(key,x,-57.9,z+.74,3.8,.12,.18,'evergreen')
for dx in [-12,12]:
    z=ground(-401+dx,-14);cylinder(key,-401+dx,-14,z,.09,3.4,'metal',8)
    crown(key,-401+dx,-14,z+3.55,.3,.3,.4,'cream')

# EMU: 2017 brick/glass/clerestory vocabulary and a historical Fishbowl motif.
# This is a plausible staged hybrid, not an assertion of one exact dated facade.
b=records['Erb Memorial Union'];key=b['id'];base=b['base_z_m']
volume(key,-250,-66,-168,-33,base,13.8)
volume(key,-215,-96,-168,-66,base,9.3)
volume(key,-250,-96,-215,-66,base,7.4)
for bay in inp['facade_modules']['emu-north']:
    upper=bay['height_m']>base+5
    detailed_window(key,bay['east_m'],bay['north_m'],bay['height_m'],2.3 if upper else 4.3,4.7 if upper else 3.9,bay['yaw_rad'],1 if upper else 2,2)
cube(key,-208,-32.6,base+5,77,.45,.30,'stone')
cube(key,-208,-32.7,base+12.7,77,.25,1.65,'glass-light')
for x in range(-246,-169,3):cube(key,x,-32.48,base+12.7,.08,.08,1.65,'metal')
# Stepped rooftop volumes are inferred from the photos and the aerial roof rhythm.
volume(key,-232,-57,-182,-39,base+14.3,2.0,'brick-dark')
for x in range(-230,-181,3):detailed_window(key,x,-38.8,base+15.2,2.7,1.2,columns=1,rows=1)
for x,n,w,d,h in [(-176,-76,10,19,3),(-198,-86,20,9,1.7),(-243,-39,8,9,2.1)]:
    cube(key,x,n,base+10+h/2,w,d,h,'roof')
for n in [-37,-44,-51,-58]:
    detailed_window(key,-250.2,n,base+8.8,2.6,4.8,-math.pi/2,2,4)
    detailed_window(key,-250.2,n,base+2.6,4,3.9,-math.pi/2,2,2)
cube(key,-253,-48,base+5.5,9,24,.45,'stone')
for n in [-39,-48,-57]:cylinder(key,-256.5,n,base,.2,5.3,'metal',8)
arc=[(-235+20*math.cos(math.pi/2+i*math.pi/16),-78+15*math.sin(math.pi/2+i*math.pi/16)) for i in range(17)]
ring=arc+[(-220,-93),(-220,-63)]
prism(key,ring,base,1.2,'brick-dark');prism(key,ring,base+6.7,.65,'stone')
for p,q in zip(arc,arc[1:]):
    x,n=(p[0]+q[0])/2,(p[1]+q[1])/2;a=math.atan2(q[1]-p[1],q[0]-p[0]);w=math.dist(p,q)
    cube(key,x,n,base+3.9,w,.12,5.5,'glass',a)
    cube(key,x,n,base+3.7,w,.16,.09,'metal',a)
    cylinder(key,p[0],p[1],base+1.1,.075,5.6,'metal',6)
inscription(key,'ERB MEMORIAL UNION',-250.45,-48,base+5.05,.72,-math.pi/2)
for i in range(4):
    x=-260-i*3.2;z=ground(x,-48)
    cube(key,x,-48,z+.18,3.3,31+i*2,.36,'paving')
    for n in [-32-i,-64+i]:cube(key,x,n,z+.65,3.1,.55,1.0,'brick-dark')
for n in [-34,-62]:
    z=ground(-270,n)
    for x in [-274,-270,-266]:beam(key,(x,n,z+.4),(x,n,z+1.3),.04)
    beam(key,(-274,n,z+1.3),(-266,n,z+1.3),.045)

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
        leaf=['leaf','leaf-light','evergreen'][tone];r=height*.28
        for direction in [-1,1]:
            beam(key,(x,n,z+height*.35),(x+direction*r*.5,n+r*.2,z+height*.67),.11,'trunk')
        for ox,on,oz,scale in [(0,0,.72,1),(-.55,.15,.65,.72),(.48,.28,.69,.75),(.1,-.45,.78,.65)]:
            crown(key,x+ox*r,n+on*r,z+height*oz,r*scale,r*scale*.93,r*scale*1.1,leaf)
    if index%5==0:
        crown('understory',x+1.1,n-.5,z+.7,1.7,1.2,.9,'shrub')

# Small shrubs/fern-like fans, inferred from the archived entrance photographs.
for x,n in [(-608,-186),(-598,-187),(-521,-187),(-511,-187),(-416,-17),(-386,-17),(-416,-59),(-386,-59),(-275,-64),(-270,-65),(-263,-65)]:
    z=ground(x,n);crown('understory',x,n,z+.6,1.8,1.4,.7,'shrub')
    for j in range(8):
        a=j*math.tau/8
        mesh('understory',[(x,n,z+.2),(x+1.5*math.cos(a-.2),n+1.5*math.sin(a-.2),z+.3),
                          (x+1.15*math.cos(a),n+1.15*math.sin(a),z+1.35)],[(0,1,2)],'leaf-light')

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
    obj['rights']='Original model contribution: CC BY 4.0; reference images retain their own terms and are archived separately, not embedded as textures'
    if key in [records[name]['id'] for name in config['landmarks']]:
        obj['method']='Geographic envelope + photo-informed modular facade grammar + plausible inference; no new manual measurements or photogrammetric solve'
        obj['reference_register']='https://github.com/williamQ96/open-campus-uo/tree/main/data/reference-images'

scene=bpy.context.scene;scene.unit_settings.system='METRIC'
scene['art_status']=config['status'];scene['source_manifest_sha256']=inp['manifest_sha256']
scene['attribution']='Open Campus: UO — Zhongyi "William" Qiu and contributors — CC BY 4.0'
scene['inference_policy']='Recognizable first pass; editable assumptions corrected over long-term maintenance'
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
    'reference_image_ids':config['reference_image_ids'],'aerial_reference':inp['aerial_reference'],
    'art_pipeline':inp['art_pipeline'],
    'inference_policy':scene['inference_policy'],
    'reference_manifest_sha256':hashlib.sha256((ROOT/'data/reference-images/manifest.json').read_bytes()).hexdigest(),
    'source_manifest_sha256':inp['manifest_sha256'],
    'heightfield_sha256':inp['heightfield_sha256'],
    'asset_sha256':hashlib.sha256((PUBLIC/'visual-pilot.glb').read_bytes()).hexdigest(),
    'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'credit':scene['attribution'],
}
(PUBLIC/'presentation.json').write_text(json.dumps(presentation,indent=2)+'\n',encoding='utf-8')
print('VISUAL PILOT EXPORTED',len(objects),'editable semantic meshes;',len(inp['trees']),'trees')
