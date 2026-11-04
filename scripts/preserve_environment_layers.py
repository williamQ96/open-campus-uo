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
   if spec.get('source_triangle_patch') is not None and previous.get('verify_source_sha256') is not True:raise ValueError('Source triangle patch requires source hash verification')
  if previous.get('verify_source_sha256') is True:result['verify_source_sha256']=True
  result['exterior_details']=[dict(entry) for entry in details]
 if 'batch_palette_patches' in previous:
  patches=previous['batch_palette_patches']
  if not isinstance(patches,list):raise ValueError('Invalid batch palette patches')
  seen=set()
  for entry in patches:
   if not isinstance(entry,dict):raise ValueError('Invalid batch palette entry')
   path=safe_path(entry.get('url'))
   if path.name in seen:raise ValueError('Duplicate batch palette patch')
   seen.add(path.name)
   if not path.is_file() or sha(path)!=entry.get('sha256'):raise ValueError('Batch palette missing or hash changed')
   spec=json.loads(path.read_text(encoding='utf-8'))
   if spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Batch palette does not match rebuilt GLB')
   if not isinstance(spec.get('building_id'),str) or not spec['building_id'] or not isinstance(spec.get('target_name'),str) or not spec['target_name']:raise ValueError('Invalid batch palette target')
  result['batch_palette_patches']=[dict(entry) for entry in patches]
 if 'building_roof_patches' in previous:
  patches=previous['building_roof_patches']
  if not isinstance(patches,list):raise ValueError('Invalid building roof patches')
  seen=set()
  for entry in patches:
   if not isinstance(entry,dict):raise ValueError('Invalid building roof patch')
   path=safe_path(entry.get('url'))
   if path.name in seen:raise ValueError('Duplicate building roof patch')
   seen.add(path.name)
   if not path.is_file() or sha(path)!=entry.get('sha256'):raise ValueError('Building roof patch missing or hash changed')
   spec=json.loads(path.read_text(encoding='utf-8'))
   if not isinstance(spec.get('building_id'),str) or not spec['building_id']:raise ValueError('Invalid building roof identity')
   if spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Building roof patch does not match rebuilt GLB')
  result['building_roof_patches']=[dict(entry) for entry in patches]
 if previous.get('planting_variation_url'):
  path=safe_path(previous['planting_variation_url'])
  if not path.is_file() or sha(path)!=previous.get('planting_variation_sha256'):raise ValueError('Planting variation missing or hash changed')
  spec=json.loads(path.read_text(encoding='utf-8'))
  if spec.get('target_name')!='planting' or spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Planting variation does not match rebuilt GLB')
  result['planting_variation_url']=previous['planting_variation_url']
  result['planting_variation_sha256']=previous['planting_variation_sha256']
 if previous.get('context_trunks_url'):
  path=safe_path(previous['context_trunks_url'])
  if not path.is_file() or sha(path)!=previous.get('context_trunks_sha256'):raise ValueError('Context trunks missing or hash changed')
  spec=json.loads(path.read_text(encoding='utf-8'))
  if spec.get('target_name')!='campus-trees' or spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Context trunks do not match rebuilt GLB')
  result['context_trunks_url']=previous['context_trunks_url']
  result['context_trunks_sha256']=previous['context_trunks_sha256']
 if previous.get('context_trunk_variation_url'):
  if not previous.get('context_trunks_url'):raise ValueError('Trunk variation requires context trunks')
  path=safe_path(previous['context_trunk_variation_url'])
  if not path.is_file() or sha(path)!=previous.get('context_trunk_variation_sha256'):raise ValueError('Trunk variation missing or hash changed')
  spec=json.loads(path.read_text(encoding='utf-8'))
  if spec.get('target_name')!='campus-trees' or spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Trunk variation does not match rebuilt GLB')
  result['context_trunk_variation_url']=previous['context_trunk_variation_url']
  result['context_trunk_variation_sha256']=previous['context_trunk_variation_sha256']
 if previous.get('lawn_tone_url'):
  path=safe_path(previous['lawn_tone_url'])
  if not path.is_file() or sha(path)!=previous.get('lawn_tone_sha256'):raise ValueError('Lawn tone missing or hash changed')
  spec=json.loads(path.read_text(encoding='utf-8'))
  if spec.get('target_name')!='landscape-lawn' or spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Lawn tone does not match rebuilt GLB')
  result['lawn_tone_url']=previous['lawn_tone_url']
  result['lawn_tone_sha256']=previous['lawn_tone_sha256']
 if previous.get('paving_joints_url'):
  path=safe_path(previous['paving_joints_url'])
  if not path.is_file() or sha(path)!=previous.get('paving_joints_sha256'):raise ValueError('Paving joints missing or hash changed')
  spec=json.loads(path.read_text(encoding='utf-8'))
  if spec.get('target_name')!='landscape-paving' or spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Paving joints do not match rebuilt GLB')
  result['paving_joints_url']=previous['paving_joints_url']
  result['paving_joints_sha256']=previous['paving_joints_sha256']
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
