# SPDX-License-Identifier: Apache-2.0
"""Prepare a portable, inferred ground-cover layer using archived public-domain NAIP cues."""
from pathlib import Path
import json,hashlib
import numpy as np
import rasterio
from scipy.ndimage import uniform_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import contains_xy
ROOT=Path(__file__).resolve().parents[1];pub=ROOT/'apps/web-preview/public/scene'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
m=read(pub/'manifest.json');f=read(pub/m['heightfield_url']);c=read(ROOT/'configs/campus-expansion.json');ref=read(ROOT/'data/metadata/naip-2024-main-campus-reference.json')
raw=(ROOT/'data/reference-images'/ref['archive_file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==ref['sha256']
with rasterio.open(ROOT/'data/reference-images'/ref['archive_file']) as src:image=np.moveaxis(src.read([1,2,3]),0,-1).astype(float)
smooth=uniform_filter(image,size=(17,17,1))
x=f['min_east_m']+np.arange(f['nx'])*f['spacing_m'];n=f['min_north_m']+np.arange(f['ny'])*f['spacing_m'];xx,nn=np.meshgrid(x,n)
origin=ref['local_origin_projected_m'];ext=ref['export_response']['extent'];u=np.clip(((xx+origin[0]-ext['xmin'])/(ext['xmax']-ext['xmin'])*(image.shape[1]-1)).astype(int),0,image.shape[1]-1);v=np.clip(((ext['ymax']-nn-origin[1])/(ext['ymax']-ext['ymin'])*(image.shape[0]-1)).astype(int),0,image.shape[0]-1)
r,g,b=[smooth[v,u,k] for k in range(3)];green=(2*g-r-b)/(r+g+b+1)
focus=contains_xy(Polygon(c['priority_polygon_enu_m']),xx,nn)
near=contains_xy(unary_union([Polygon(q['footprint_enu_m']).buffer(1.2) for q in m['buildings']]),xx,nn)
# Classes are stylized ground use, not pixel-accurate vegetation or access segmentation.
classes=np.full(xx.shape,2,dtype=np.int8)
classes[(green>.055)&(g>r*.94)]=1
classes[focus&((green>.015)|((r+g+b)/3<115))]=0
classes[focus&(classes==2)]=2
classes[near]=2
# Supporting urban context gets an explicit concrete/asphalt vocabulary, not placeholder gray.
lots=((np.floor(xx/32)+2*np.floor(nn/36)).astype(int)%5==0)&~focus&(classes==2)
classes[lots]=3
water=(nn>280)&(b>r*1.06)&(g>r*1.10)&(green<.115)&((r+g+b)/3<145)
classes[water]=4
classes[(~focus)&(classes==2)]=5
palette=np.array([[.63,.72,.46],[.57,.63,.47],[.70,.68,.60],[.35,.39,.38],[.42,.60,.58],[.60,.63,.63]])
colors=palette[classes];grain=np.sin(xx*12.9898+nn*78.233)*43758.5453;grain=grain-np.floor(grain)-.5;colors=np.clip(colors*(1+grain[:,:,None]*.025),0,1)
vertices=np.stack([xx,nn,np.array(f['heights_m']).reshape(xx.shape)+.018],axis=-1).reshape(-1,3)
faces=[]
for j in range(f['ny']-1):
 for i in range(f['nx']-1):
  a=j*f['nx']+i;b=a+1;d=a+f['nx']+1;e=a+f['nx'];faces.extend([[a,b,d],[a,d,e]])
(ROOT/'artifacts').mkdir(exist_ok=True)
np.savez_compressed(ROOT/'artifacts/phase13-landcover.npz',vertices=vertices,faces=np.asarray(faces,dtype=np.int32),colors=colors.reshape(-1,3),classes=classes)
summary={'source_id':'naip-2024-main-campus-rgb','source_sha256':ref['sha256'],'method':'Smoothed open aerial color cues plus inferred aprons, lawns and urban hardscape; not a measured land-use or access survey. No photographic texture is embedded.','coverage_m':2000,'vertices':len(vertices),'triangles':len(faces),'palette_srgb':palette.tolist(),'class_vertices':{k:int(np.sum(classes==i)) for i,k in enumerate(['campus-grass','context-planting','concrete','asphalt','water-cue','context-concrete'])},'height_offset_m':.018}
(ROOT/'data/metadata/landcover-inference.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(summary)
