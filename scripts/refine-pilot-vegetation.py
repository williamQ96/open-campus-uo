# SPDX-License-Identifier: Apache-2.0
"""Export an isolated pilot vegetation layer; relocate one inferred tree."""
import bpy,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=R/'apps/web-preview/public/scene';source=R/'assets/roof-refinement/eugene-campus.blend';inp=R/'artifacts/visual-pilot-input.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(source)!='06b211f88256b028631e568b2b8401e11e0772e8604b9e454b92001e76187b86' or sha(inp)!='ea262a2dc98b77c22940b5f4928ba1ccf7ff37d5bf7947129684a6b24bd05254':raise ValueError('Source changed; revalidate tree selection')
m=json.loads((S/'manifest.json').read_text(encoding='utf-8'));f=json.loads((S/m['heightfield_url']).read_text(encoding='utf-8'));trees=json.loads(inp.read_text(encoding='utf-8'))['trees']
def ground(x,n):
 u=max(0,min(f['nx']-1.000001,(x-f['min_east_m'])/f['spacing_m']));v=max(0,min(f['ny']-1.000001,(n-f['min_north_m'])/f['spacing_m']));i,j=int(u),int(v);a,b=u-i,v-j;at=lambda dx,dy:f['heights_m'][(j+dy)*f['nx']+i+dx]
 return at(0,0)+(at(1,0)-at(0,0))*a+(at(1,1)-at(1,0))*b if a>=b else at(0,0)+(at(1,1)-at(0,1))*a+(at(0,1)-at(0,0))*b
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(source),link=False) as (data,loaded):
 if not {'vegetation','understory'}.issubset(data.objects):raise ValueError('Missing vegetation or understory')
 loaded.objects=['vegetation','understory']
obj,understory=loaded.objects
for o in loaded.objects:bpy.context.collection.objects.link(o)
if not obj.matrix_world.is_identity:raise ValueError('Unexpected transform')
x,n,h,con,tone=trees[60]
if [x,n,h,con,tone]!=[-603.521,-186.55,16.98,True,0]:raise ValueError('Tree identity changed')
z=ground(x,n);expected=[]
for radius,height,top,base,segs in [(.22,h*.7,.12,z,7)]+[(h*(.24-j*.045),h*.47,.05,z+h*(.24+j*.19),9) for j in range(3)]:
 for rr,zz in [(radius,base),(top,base+height)]:
  for k in range(segs):expected.append((x+rr*math.cos(k*math.tau/segs),n+rr*math.sin(k*math.tau/segs),zz))
selected=[v for v in obj.data.vertices if any((v.co.x-a)**2+(v.co.y-b)**2+(v.co.z-c)**2<1e-8 for a,b,c in expected)]
if len(selected)!=68:raise ValueError(f'Expected 68 vertices, got {len(selected)}')
nx,nn=-619.,-188.;delta=(nx-x,nn-n,ground(nx,nn)-z)
for v in selected:v.co.x+=delta[0];v.co.y+=delta[1];v.co.z+=delta[2]
obj.data.update();obj['status']='Inferred pilot trees; one conifer relocated for illustrative stair clearance, not a survey';obj['source_sha256']=sha(source)
if not understory.matrix_world.is_identity:raise ValueError('Unexpected understory transform')
shrub=[]
for j in range(7):
 a=math.pi*j/6
 for i in range(9):
  b=math.tau*i/9+(j%2)*.12;shrub.append((x+1.1+1.7*math.sin(a)*math.cos(b),n-.5+1.2*math.sin(a)*math.sin(b),z+.7+.9*math.cos(a)))
chosen=[v for v in understory.data.vertices if any((v.co.x-a)**2+(v.co.y-b)**2+(v.co.z-c)**2<1e-8 for a,b,c in shrub)]
if len(chosen)!=63:raise ValueError(f'Expected 63 shrub vertices, got {len(chosen)}')
for v in chosen:v.co.x+=delta[0];v.co.y+=delta[1];v.co.z+=delta[2]
understory.data.update();understory['status']='Inferred understory; one shrub moved with its paired conifer, not a survey'

# Tree 273 is procedural, overlaps the authored EMU, and its center lies on
# open lawn/paving in the dated archived NAIP view. Suppress rather than move it.
tree_index=273;tx,tn,th,tcon,ttone=trees[tree_index]
if [tx,tn,th,tcon,ttone]!=[-181.887,-72.478,20.47,False,1]:raise ValueError('Tree 273 identity changed')
first=sum(68 if t[3] else 282 for t in trees[:tree_index]);last=first+282
tree273_unique=[]
for v in obj.data.vertices[first:last]:
 pos=[v.co.x,v.co.z,-v.co.y]
 if not any(sum((a-b)**2 for a,b in zip(pos,q))<1e-8 for q in tree273_unique):tree273_unique.append(pos)
if len(tree273_unique)!=218:raise ValueError(f'Tree 273 expected 218 tree273_unique positions, got {len(tree273_unique)}')
# Ensure the same coordinates do not identify vertices belonging to another tree.
for v in obj.data.vertices:
 if first<=v.index<last:continue
 pos=(v.co.x,v.co.z,-v.co.y)
 if any(sum((a-b)**2 for a,b in zip(pos,q))<1e-8 for q in tree273_unique):raise ValueError('Tree 273 coordinate shared by another tree')
collapse=(tx,tn,ground(tx,tn))
for v in obj.data.vertices[first:last]:v.co=collapse
obj.data.update()
out=R/'assets/vegetation-refinement';out.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out/'pilot-vegetation.blend'))

patch={'version':1,'base_asset_sha256':'29f22c38eb5737fba2c8b3ab9618e049443c052e169e175f19428e66174ae896','target_name':'vegetation','expected_matches':204,'positions_gltf':[[a,c,-b] for a,b,c in expected],'delta_gltf':[delta[0],delta[2],-delta[1]],'tolerance_m':0.0001,'description':'One illustrative conifer moved clear of Knight stair; not a surveyed location'}
(S/'pilot-vegetation-patch.json').write_text(json.dumps(patch,indent=2)+'\n',encoding='utf-8')
print('VEGETATION_PATCH',len(obj.data.vertices),'changed',len(selected),'delta',delta,'sha',sha(S/'pilot-vegetation-patch.json'))

unique=[]
for a,b,c in shrub:
 p=[a,c,-b]
 if not any(sum((v-q)**2 for v,q in zip(p,other))<1e-8 for other in unique):unique.append(p)
shrub_patch={'version':1,'base_asset_sha256':patch['base_asset_sha256'],'target_name':'understory','expected_matches':216,'positions_gltf':unique,'delta_gltf':patch['delta_gltf'],'tolerance_m':0.0001,'description':'Paired illustrative shrub moved with conifer; not a surveyed location'}
(S/'pilot-understory-patch.json').write_text(json.dumps(shrub_patch,indent=2)+'\n',encoding='utf-8')
print('UNDERSTORY_PATCH',len(chosen),'unique positions',len(unique),'sha',sha(S/'pilot-understory-patch.json'))

suppression={'version':1,'base_asset_sha256':patch['base_asset_sha256'],'target_name':'vegetation','expected_matches':954,'positions_gltf':tree273_unique,'collapse_gltf':[collapse[0],collapse[2],-collapse[1]],'tolerance_m':0.0001,'suppressed_trees':1,'tree_index':273,'description':'Suppress one inferred tree from dated open lawn/paving; not a surveyed location'}
(S/'pilot-tree-273-suppression.json').write_text(json.dumps(suppression,indent=2)+'\n',encoding='utf-8')
print('TREE_273_SUPPRESSION',last-first,'unique',len(tree273_unique),'sha',sha(S/'pilot-tree-273-suppression.json'))
