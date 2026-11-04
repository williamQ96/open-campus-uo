# SPDX-License-Identifier: Apache-2.0
"""Read-only mesh overlap screen for the existing pilot-tree audit candidates.

Run in Blender with --python-exit-code 1 --python this_script -- --root PROJECT --output REPORT.
This tests surface intersections, not containment, survey accuracy or access.
"""
import bpy, json, sys, hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
args=sys.argv[sys.argv.index('--')+1:];root=Path(args[args.index('--root')+1]);out=Path(args[args.index('--output')+1]);source=root/'assets/roof-refinement/eugene-campus.blend';candidate=root/'assets/vegetation-refinement/pilot-vegetation.blend';inp=root/'artifacts/visual-pilot-input.json';audit=root/'data/metadata/vegetation-clearance-audit-2026-11-03.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads(audit.read_text(encoding='utf-8')); group=report['groups'][0]
if sha(inp)!=group['input_sha256']:raise ValueError('Tree input differs from screened snapshot')
trees=json.loads(inp.read_text(encoding='utf-8'))['trees'];pairs=[(v['tree_index'],v['building_id']) for v in group['candidate_pairs']]+[(60,'roof-6684e091')]
names={'vegetation'}|{id for _,id in pairs}
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.objects=[name for name in a.objects if name in names]
objects={o.name:o for o in b.objects}
if set(objects)!=names:raise ValueError('A required semantic mesh is missing')
def tree_bvh(mesh,index):
 start=sum(68 if t[3] else 282 for t in trees[:index]);end=start+(68 if trees[index][3] else 282)
 coords=[v.co.copy() for v in mesh.vertices[start:end]];faces=[[i-start for i in f.vertices] for f in mesh.polygons if all(start<=i<end for i in f.vertices)]
 if len(coords)!=(68 if trees[index][3] else 282) or len(faces)!=(42 if trees[index][3] else 237):raise ValueError('Unexpected tree mesh layout')
 return BVHTree.FromPolygons(coords,faces)
def building_bvh(obj):return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(f.vertices) for f in obj.data.polygons])
mesh=objects['vegetation'].data;results=[]
for index,id in pairs:
 count=len(tree_bvh(mesh,index).overlap(building_bvh(objects[id])))
 results.append({'tree_index':index,'building_id':id,'surface_face_pairs':count,'interpretation':'surface intersections detected' if count else 'no surface intersections detected; containment not tested'})
with bpy.data.libraries.load(str(candidate),link=False) as (a,b):b.objects=['vegetation']
if not b.objects[0]:raise ValueError('Candidate vegetation missing')
after=len(tree_bvh(b.objects[0].data,60).overlap(building_bvh(objects['roof-6684e091'])))
start273=sum(68 if t[3] else 282 for t in trees[:273]);v273=[v.co.copy() for v in b.objects[0].data.vertices[start273:start273+282]]
collapsed=len(v273)==282 and all((v-v273[0]).length<0.0001 for v in v273)
if not collapsed:raise ValueError('Tree 273 is not collapsed in candidate')
result={'source_sha256':sha(source),'candidate_sha256':sha(candidate),'tree_input_sha256':sha(inp),'method':'BVH surface mesh overlap between per-tree vertex slices and corresponding authored building meshes; no containment, runtime patch, or survey proof. Numbers are mesh face pairs, not object counts.','original_pairs':results,'tree_60_candidate_surface_face_pairs':after,'tree_273_candidate_vertices_collapsed':collapsed}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
