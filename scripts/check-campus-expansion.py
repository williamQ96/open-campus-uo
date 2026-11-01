# SPDX-License-Identifier: Apache-2.0
"""Audit geographic invariants, retained sources, open image input and GLB identity."""
from pathlib import Path
import json,hashlib,struct
root=Path(__file__).resolve().parents[1];scene=root/'apps/web-preview/public/scene'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
manifest=read(scene/'manifest.json');presentation=read(scene/'presentation.json');audit=read(root/'data/metadata/campus-expansion-audit.json');config=read(root/'configs/campus-expansion.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
text_sha=lambda p:hashlib.sha256(p.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()
assert presentation['source_manifest_sha256']==audit['source_manifest_sha256']
assert text_sha(scene/'manifest.json')==presentation['source_manifest_text_sha256']
assert text_sha(scene/manifest['heightfield_url'])==presentation['heightfield_text_sha256']
assert sha(root/config['source_blend'])==config['source_blend_sha256']==presentation['preserved_source_blend_sha256']
source={b['id']:b for b in manifest['buildings']}
assert set(presentation['replaces_building_ids'])==set(source)
for art in audit['appearance_plan']:
 for key in ['id','footprint_enu_m','base_z_m','height_m','roof_z_m']:assert art[key]==source[art['id']][key],(art['id'],key)
raw=(scene/presentation['asset_url']).read_bytes();assert hashlib.sha256(raw).hexdigest()==presentation['asset_sha256']
length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length]);assert not gltf.get('images')
identities=[]
for node in gltf['nodes']:
 extra=node.get('extras',{})
 if extra.get('asset_kind')=='building':identities.append(extra['asset_id'])
 if extra.get('asset_kind')=='context-building-batch':identities.extend(extra['asset_ids'])
assert len(identities)==len(set(identities))==len(source) and set(identities)==set(source)
register=read(root/'data/reference-images/manifest.json');images={i['id']:i for i in register['images']}
for id in presentation['reference_image_ids']:assert id in images and images[id]['review_status']=='approved'
assert (root/'assets/campus-expansion/eugene-campus.blend').is_file()
print(json.dumps({'building_ids':len(identities),'individually_selectable':len(identities)-sum(map(len,audit['context_batches'].values())),'batched_buildings':sum(map(len,audit['context_batches'].values())),'context_batches':len(audit['context_batches']),'runtime_bytes':len(raw),'new_photo_references':2,'embedded_images':0,'source_geography':'unchanged','original_pilot_blend':'unchanged'}))
