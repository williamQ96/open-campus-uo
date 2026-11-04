# SPDX-License-Identifier: Apache-2.0
"""Visualize generated tree centers against archived NAIP; not a stem survey."""
import argparse,hashlib,json
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=a.root
meta=json.loads((r/'data/metadata/naip-2024-reference.json').read_text(encoding='utf-8'));photo=r/'data/reference-images'/meta['archive_file'];digest=hashlib.sha256(photo.read_bytes()).hexdigest()
if digest!=meta['sha256']:raise ValueError('Archived NAIP image hash changed')
trees=json.loads((r/'artifacts/visual-pilot-input.json').read_text(encoding='utf-8'))['trees'];e=meta['export_response']['extent'];origin=meta['local_origin_projected_m'];bounds=[e['xmin']-origin[0],e['xmax']-origin[0],e['ymin']-origin[1],e['ymax']-origin[1]]
fig,axes=plt.subplots(2,2,figsize=(12,10),layout='constrained');image=Image.open(photo)
for ax in axes.flat:ax.imshow(image,extent=bounds,origin='upper');ax.set_xlabel('East (m)');ax.set_ylabel('North (m)')
for i in [129,296,273]:
 x,n=trees[i][:2];axes[0,0].scatter([x],[n],s=55,c='#e83c39',edgecolors='white');axes[0,0].annotate(str(i),(x,n),xytext=(5,5),textcoords='offset points',color='white',bbox={'facecolor':'black','alpha':.75})
axes[0,0].set_title('Pilot reference and candidate centers')
for ax,i in zip([axes[0,1],axes[1,0],axes[1,1]],[129,296,273]):
 x,n=trees[i][:2];ax.scatter([x],[n],s=80,c='#e83c39',edgecolors='white');ax.set_xlim(x-30,x+30);ax.set_ylim(n-30,n+30);ax.set_title(f'Generated tree {i}: 60 m context')
fig.suptitle('Generated centers on dated aerial imagery — not surveyed tree stems',fontsize=13)
fig.text(.5,-.01,'USDA FPAC-BC/GEO NAIP 2024-06-08 • public domain • 0.6 m/px archived subset; markers are project-generated coordinates',ha='center',fontsize=8)
fig.savefig(a.output,dpi=160,bbox_inches='tight');print('NAIP reference sha256',digest,'output',a.output)
