# SPDX-License-Identifier: Apache-2.0
"""Preserve explicitly adopted environment layers during a staged campus rebuild."""
from pathlib import Path
import hashlib,json,re

def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def carry_layers(previous, output, scene):
 """Validate existing layer bytes and copy metadata; never rewrite assets or patches.

 A patch is source-pinned: a byte-different rebuilt GLB must be reviewed and
 regenerated deliberately. A failed check occurs before live files are replaced.
 """
 result=dict(output);scene=Path(scene)
 def safe_path(name):
  if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or name in ('.','..'):raise ValueError('Unsafe layer path')
  return scene/name
 if previous.get('landcover_url'):
  asset=safe_path(previous['landcover_url'])
  if not asset.is_file() or sha(asset)!=previous.get('landcover_sha256'):raise ValueError('Existing ground layer missing or hash changed')
  for k in ('landcover_url','landcover_sha256','landcover_status'):
   if k in previous:result[k]=previous[k]
  if 'naip-2024-main-campus-rgb' in previous.get('reference_image_ids',[]):
   result['reference_image_ids']=list(dict.fromkeys(result.get('reference_image_ids',[])+['naip-2024-main-campus-rgb']))
 if previous.get('exterior_detail_url'):
  path=safe_path(previous['exterior_detail_url'])
  if not path.is_file() or sha(path)!=previous.get('exterior_detail_sha256'):raise ValueError('exterior detail missing or hash changed')
  detail=json.loads(path.read_text(encoding='utf-8'))
  if detail.get('base_asset_sha256')!=previous.get('asset_sha256') or detail.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('exterior detail does not match rebuilt GLB; preserve current files and revalidate')
  for suffix in ('_url','_sha256','_status'):
   key='exterior_detail'+suffix
   if key in previous:result[key]=previous[key]
 if 'exterior_details' in previous:
  details=previous['exterior_details']
  if not isinstance(details,list):raise ValueError('Invalid exterior details')
  seen=set()
  for detail in details:
   if not isinstance(detail,dict):raise ValueError('Invalid exterior detail entry')
   path=safe_path(detail.get('url'))
   if path.name in seen or path.name==previous.get('exterior_detail_url'):raise ValueError('Duplicate exterior detail')
   seen.add(path.name)
   if not path.is_file() or sha(path)!=detail.get('sha256'):raise ValueError('exterior detail missing or hash changed')
   spec=json.loads(path.read_text(encoding='utf-8'))
   if spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('exterior detail does not match rebuilt GLB; preserve current files and revalidate')
  result['exterior_details']=[dict(entry) for entry in details]
 if 'wall_color_patches' in previous:
  patches=previous['wall_color_patches']
  if not isinstance(patches,list):raise ValueError('Invalid wall color patches')
  seen=set()
  for entry in patches:
   if not isinstance(entry,dict):raise ValueError('Invalid wall color patch entry')
   path=safe_path(entry.get('url'))
   if path.name in seen:raise ValueError('Duplicate wall color patch')
   seen.add(path.name)
   if not path.is_file() or sha(path)!=entry.get('sha256'):raise ValueError('Wall color patch missing or hash changed')
   patch=json.loads(path.read_text(encoding='utf-8'))
   if patch.get('base_asset_sha256')!=previous.get('asset_sha256') or patch.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Wall color patch does not match rebuilt GLB')
  result['wall_color_patches']=[dict(entry) for entry in patches]
 if 'additional_environment_patches' in previous:
  patches=previous['additional_environment_patches']
  if not isinstance(patches,list):raise ValueError('Invalid additional environment patches')
  seen=set()
  for entry in patches:
   if not isinstance(entry,dict):raise ValueError('Invalid additional environment patch')
   path=safe_path(entry.get('url'))
   if path.name in seen:raise ValueError('Duplicate additional environment patch')
   seen.add(path.name)
   if not path.is_file() or sha(path)!=entry.get('sha256'):raise ValueError('Additional environment patch missing or hash changed')
   spec=json.loads(path.read_text(encoding='utf-8'))
   if spec.get('target_name') not in ('understory','vegetation','furniture'):raise ValueError('Invalid additional environment patch target')
   if spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Additional environment patch does not match rebuilt GLB')
  result['additional_environment_patches']=[dict(entry) for entry in patches]
 extra_suppressed=0
 if 'additional_tree_suppressions' in previous:
  patches=previous['additional_tree_suppressions']
  if not isinstance(patches,list) or not previous.get('tree_suppression_url'):raise ValueError('Invalid additional tree suppressions')
  seen={previous['tree_suppression_url']}
  for entry in patches:
   if not isinstance(entry,dict):raise ValueError('Invalid tree suppression entry')
   path=safe_path(entry.get('url'))
   if path.name in seen:raise ValueError('Duplicate tree suppression')
   seen.add(path.name)
   if not path.is_file() or sha(path)!=entry.get('sha256'):raise ValueError('Additional tree suppression missing or hash changed')
   data=json.loads(path.read_text(encoding='utf-8'))
   if data.get('base_asset_sha256')!=previous.get('asset_sha256') or data.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Additional tree suppression does not match rebuilt GLB')
   count=data.get('suppressed_trees')
   if not isinstance(count,int) or isinstance(count,bool) or count<1:raise ValueError('Invalid additional suppressed count')
   extra_suppressed+=count
  result['additional_tree_suppressions']=[dict(entry) for entry in patches]
 for prefix in ('vegetation_patch','understory_patch','furniture_patch','fern_patch','tree_suppression'):
  if not previous.get(prefix+'_url'):continue
  path=safe_path(previous[prefix+'_url'])
  if not path.is_file() or sha(path)!=previous.get(prefix+'_sha256'):raise ValueError(prefix+' missing or hash changed')
  patch=json.loads(path.read_text(encoding='utf-8'))
  if patch.get('base_asset_sha256')!=previous.get('asset_sha256'):raise ValueError(prefix+' is not pinned to the current asset')
  if patch.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError(prefix+' does not match rebuilt GLB; preserve current files and revalidate the patch')
  for suffix in ('_url','_sha256','_status'):
   key=prefix+suffix
   if key in previous:result[key]=previous[key]
  if prefix=='tree_suppression':
   count=patch.get('suppressed_trees');stats=dict(result.get('stats',{}));source=stats.get('trees')
   if not isinstance(count,int) or isinstance(count,bool) or count<1 or not isinstance(source,int) or source<count:raise ValueError('Invalid suppressed tree count')
   old=previous.get('stats',{})
   if source<count+extra_suppressed or old.get('sourceTrees')!=source or old.get('trees')!=source-count-extra_suppressed:raise ValueError('Suppressed tree statistics changed; revalidate')
   stats['sourceTrees']=source;stats['trees']=source-count-extra_suppressed;result['stats']=stats
 return result
