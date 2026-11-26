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
 if 'ford_arena_site' in previous:
  entry=previous['ford_arena_site']
  if not isinstance(entry,dict) or entry.get('url')!='ford-arena-review/site.json':
   raise ValueError('Invalid Ford/Arena site descriptor')
  path=scene/entry['url']
  if not path.is_file() or sha(path)!=entry.get('sha256'):
   raise ValueError('Ford/Arena site missing or hash changed')
  site=json.loads(path.read_text(encoding='utf-8'))
  if site.get('source_presentation_sha256')!=output.get('asset_sha256') or site.get('source_landcover_sha256')!=result.get('landcover_sha256'):
   raise ValueError('Ford/Arena site does not match rebuilt presentation')
  manifest=json.loads(safe_path('manifest.json').read_text(encoding='utf-8'))
  if manifest['model'].get('sha256')!=site['source_model_sha256']:
   raise ValueError('Ford/Arena site does not match base scene')
  for name,digest in [(manifest['model']['url'],site['source_model_sha256']),
                      (manifest['heightfield_url'],site['source_heightfield_sha256'])]:
   source=safe_path(name)
   if not source.is_file() or sha(source)!=digest:
    raise ValueError('Ford/Arena site does not match base scene')
  for asset in [*site['buildings'],site['frontage_ground']]:
   name=asset.get('url')
   if not isinstance(name,str) or not re.fullmatch(r'ford-arena-review/[a-z-]+\.glb',name):
    raise ValueError('Invalid Ford/Arena asset path')
   asset_path=scene/name
   if not asset_path.is_file() or sha(asset_path)!=asset.get('sha256'):
    raise ValueError('Ford/Arena site mesh missing or hash changed')
  result['ford_arena_site']=dict(entry)
 for key,directory,label in [('cascade_volcanology_site','cascade-volcanology-review','Cascade'),
                             ('hedco_site_review','hedco-exterior-review','HEDCO'),
                             ('athletic_site_review','athletic-exterior-review','Athletic block'),
                             ('emu_green_site','emu-green-review','EMU Green'),
                             ('frohnmayer_site','frohnmayer-exterior-review','Frohnmayer'),
                             ('museum_site_review','museum-exterior-review','Museum'),
                             ('gerlinger_site_review','gerlinger-site-review','Gerlinger'),
                             ('womens_quad_site','womens-quad-review','Women’s Memorial Quad'),
                             ('memorial_quad_site','memorial-quad-review','Memorial Quad'),
                             ('fenton_site_review','fenton-site-review','Fenton Hall'),
                             ('allen_site_review','allen-site-review','Allen Hall'),
                             ('lawrence_science_site','lawrence-science-review','Lawrence science complex'),
                             ('straub_earl_site','straub-earl-review','Straub and Earl'),
                             ('kalapuya_site','kalapuya-review','Kalapuya Ilihi'),
                             ('longhouse_site','longhouse-review','Many Nations Longhouse'),
                             ('global_scholars_site','global-scholars-review','Global Scholars Hall'),
                             ('moss_street_site','moss-street-review','Moss Street Children’s Center'),
                             ('vivian_olum_site','vivian-olum-review','Vivian Olum'),
                             ('graduate_village_site','graduate-village-review','East Campus Graduate Village'),
                             ('knight_law_site','knight-law-review','Knight Law Center'),
                             ('bean_unthank_site','bean-unthank-review','Bean and Unthank'),
                             ('cedar_yasui_site','cedar-yasui-review','Cedar and Yasui'),
                             ('carson_llc_site','carson-llc-review','Carson and Living-Learning Center'),
                             ('oregon_jaqua_site','oregon-jaqua-review','Oregon Hall and Jaqua'),
                             ('lillis_complex_site','lillis-complex-review','Lillis complex and Computing Center'),
                             ('friendly_collier_mckenzie_site','friendly-collier-mckenzie-review','Friendly, Collier and McKenzie'),
                             ('plc_lokey_tykeson_site','plc-lokey-tykeson-review','PLC, Lokey Education and Tykeson'),
                             ('northeast_science_site','northeast-science-review','Northeast science complex'),
                             ('knight_campus_site','knight-campus-review','Knight Campus Buildings 1 and 2'),
                             ('northsite_millrace_site','northsite-millrace-review','Fine Arts Studios and 1600 Millrace Drive'),
                             ('public_building_exterior_site','public-building-exterior-review','Clinical Services, Museum, Barn and Agate Hall'),
                             ('hayward_exterior_site','hayward-exterior-review','Hayward Field'),
                             ('campus_frontage_site','campus-frontage-review','Campus public building frontages'),
                             ('facilities_exterior_site','facilities-exterior-review','UO facilities and Romania'),
                             ('office_exterior_site','office-exterior-review','Annex, Rainier and UO offices'),
                             ('residential_exterior_site','residential-exterior-review','Registered off-campus residences'),
                             ('campus_neighbor_exterior_site','campus-neighbor-exterior-review','Registered campus neighbors'),
                             ('chapter_house_exterior_site','chapter-house-exterior-review','Separately registered chapter houses'),
                             ('villard_garden_exterior_site','villard-garden-exterior-review','Split Villard and Garden residential exteriors'),
                             ('alder_millrace_exterior_site','alder-millrace-exterior-review','Registered Alder and Millrace apartment exteriors'),
                             ('east_campus_housing_exterior_site','east-campus-housing-exterior-review','Registered East Campus housing exteriors'),
                             ('hilyard_west_exterior_site','hilyard-west-exterior-review','Four registered Hilyard and West University exteriors'),
                             ('treated_roof_exterior_site','treated-roof-exterior-review','Six street-verified exteriors with prior context roofs'),
                             ('fairmount_residential_exterior_site','fairmount-residential-exterior-review','Seven additional Fairmount Boulevard residential exteriors'),
                             ('broadway_orchard_exterior_site','broadway-orchard-exterior-review','East Broadway and Orchard registered building exteriors'),
                             ('franklin_complex_exterior_site','franklin-complex-exterior-review','Womack Hall and connected Franklin Boulevard storefronts'),
                             ('franklin_boulevard_exterior_site','franklin-boulevard-exterior-review','Registered Franklin Boulevard commercial exteriors'),
                             ('bardell_avenue_exterior_site','bardell-avenue-exterior-review','Registered Bardell Avenue building exteriors'),
                             ('villard_street_exterior_site','villard-street-exterior-review','Registered Villard Street building exteriors'),
                             ('garden_avenue_exterior_site','garden-avenue-exterior-review','Registered Garden Avenue building exteriors'),
                             ('fairmount_boulevard_exterior_site','fairmount-boulevard-exterior-review','Registered Fairmount Boulevard house exteriors'),
                             ('heritage_core_site','heritage-core-review','Heritage Core'),
                             ('heritage_miller_site','heritage-miller-review','Heritage Core and Miller Theatre'),
                             ('knight_library_site','knight-library-review','Knight Library')]:
  if key not in previous:continue
  entry=previous[key]
  site_dir=scene/directory
  if not isinstance(entry,dict) or entry.get('url')!=f'{directory}/site.json':
   raise ValueError(f'Invalid {label} site descriptor')
  site_path=site_dir/'site.json'
  if not site_path.is_file() or sha(site_path)!=entry.get('sha256'):
   raise ValueError(f'{label} site missing or hash changed')
  site=json.loads(site_path.read_text(encoding='utf-8'))
  manifest=json.loads(safe_path('manifest.json').read_text(encoding='utf-8'))
  if site.get('source_presentation_sha256')!=output.get('asset_sha256') or site.get('source_base_model_sha256')!=manifest['model'].get('sha256'):
   raise ValueError(f'{label} site does not match rebuilt presentation or base scene')
  field=safe_path(manifest['heightfield_url'])
  if not field.is_file() or sha(field)!=site.get('source_heightfield_sha256'):
   raise ValueError(f'{label} site terrain missing or hash changed')
  mesh=site_dir/'site.glb'
  if site.get('url')!=f'{directory}/site.glb' or not mesh.is_file() or sha(mesh)!=site.get('sha256'):
   raise ValueError(f'{label} site mesh missing or hash changed')
  result[key]=dict(entry)
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
 if 'context_roof_refinements' in previous:
  entry=previous['context_roof_refinements']
  if not isinstance(entry,dict) or entry.get('url')!='context-roof-refinements.json':
   raise ValueError('Invalid context roof refinement link')
  recipe=safe_path(entry['url'])
  if not recipe.is_file() or sha(recipe)!=entry.get('sha256'):
   raise ValueError('Context roof refinement missing or hash changed')
  data=json.loads(recipe.read_text(encoding='utf-8'))
  if data.get('version')!=1 or data.get('source_presentation_sha256')!=output.get('asset_sha256'):
   raise ValueError('Context roof refinements do not match rebuilt scene')
  if previous.get('verify_source_sha256') is not True:
   raise ValueError('Context roof refinement requires source hash verification')
  result['verify_source_sha256']=True
  result['context_roof_refinements']=dict(entry)
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
   pilot_operation='pilot-tree-triangle-suppression-v1'
   if pilot_operation in (entry.get('operation'),data.get('operation')):
    if (entry.get('operation')!=pilot_operation or data.get('operation')!=pilot_operation or
        data.get('version')!=1 or entry.get('suppressed_trees')!=count or previous.get('verify_source_sha256') is not True):
     raise ValueError('Invalid pilot tree clearance metadata')
   extra_suppressed+=count
  result['additional_tree_suppressions']=[dict(entry) for entry in patches]
 if 'registered_pilot_trees' in previous:
  entry=previous['registered_pilot_trees']
  if not isinstance(entry,dict) or previous.get('verify_source_sha256') is not True:raise ValueError('Invalid pilot tree registration')
  path=safe_path(entry.get('url'))
  if not path.is_file() or sha(path)!=entry.get('sha256'):raise ValueError('Pilot tree registration missing or hash changed')
  spec=json.loads(path.read_text(encoding='utf-8'))
  if spec.get('base_asset_sha256')!=previous.get('asset_sha256') or spec.get('base_asset_sha256')!=output.get('asset_sha256'):raise ValueError('Pilot tree registration does not match rebuilt GLB')
  trees=spec.get('trees')
  if spec.get('operation')!='registered-pilot-tree-fit-v1' or spec.get('version')!=1 or not isinstance(trees,list) or not trees or len(trees)!=entry.get('trees'):raise ValueError('Invalid pilot tree registration metadata')
  result['registered_pilot_trees']=dict(entry)
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
