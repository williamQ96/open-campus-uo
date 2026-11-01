# SPDX-License-Identifier: Apache-2.0
"""Audit the complete inferred ground foundation against the original heightfield."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
ROOT=Path(__file__).resolve().parents[1];scene=ROOT/'apps/web-preview/public/scene'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=read(scene/'presentation.json');m=read(scene/'manifest.json');f=read(scene/m['heightfield_url'])
raw=(scene/p['landcover_url']).read_bytes();assert hashlib.sha256(raw).hexdigest()==p['landcover_sha256']
size=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+size]);binary=memoryview(raw)[28+size:]
assert not g.get('images') and not g.get('textures')
assert len(g['meshes'])==1
def accessor(index):
 a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
 assert 'byteStride' not in v
 width={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
 dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]
 return np.frombuffer(binary,dtype=dtype,count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],width)
prim=g['meshes'][0]['primitives'][0];pos=accessor(prim['attributes']['POSITION']);colors=accessor(prim['attributes']['COLOR_0']);indices=accessor(prim['indices'])
assert len(pos)==f['nx']*f['ny']==160801
assert len(indices)==(f['nx']-1)*(f['ny']-1)*6==960000
# glTF Y is up, -Z is north. The editable Blender source stores ENU.
x=f['min_east_m']+np.arange(f['nx'])*f['spacing_m'];north=f['min_north_m']+np.arange(f['ny'])*f['spacing_m'];xx,nn=np.meshgrid(x,north)
expected=np.column_stack([xx.ravel(),np.array(f['heights_m'])+.018,-nn.ravel()])
assert np.allclose(pos,expected,atol=0.00005,rtol=0)
assert np.isfinite(colors).all() and np.ptp(colors[:,:3],axis=0).min()>.1
assert all(mat['pbrMetallicRoughness']['roughnessFactor']>=.97 for mat in g['materials'])
ground=next(n for n in g['nodes'] if 'mesh' in n)['extras'];assert ground['surface_layer']=='foundation' and ground['heightfield_offset_m']==.018
assert (ROOT/'assets/landcover/eugene-ground.blend').is_file()
ref=read(ROOT/'data/metadata/naip-2024-main-campus-reference.json');assert hashlib.sha256((ROOT/'data/reference-images'/ref['archive_file']).read_bytes()).hexdigest()==ref['sha256']
summary=read(ROOT/'data/metadata/landcover-inference.json');assert summary['source_sha256']==ref['sha256']
assert sum(summary['class_vertices'].values())==len(pos) and all(n>0 for n in summary['class_vertices'].values())
print(json.dumps({'vertices':len(pos),'triangles':len(indices)//3,'runtime_bytes':len(raw),'embedded_images':0,'source_height_max_error_m':float(np.abs(pos-expected).max()),'surface_classes':summary['class_vertices'],'source_terrain_coordinates':'preserved'}))
