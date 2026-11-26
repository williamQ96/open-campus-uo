import importlib.util,json,unittest,tempfile,shutil,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('layers',root/'scripts/preserve_environment_layers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=Path.cwd());self.scene=Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
  def put(name,data):
   b=data if isinstance(data,bytes) else (json.dumps(data)+'\n').encode();(self.scene/name).write_bytes(b);return hashlib.sha256(b).hexdigest()
  self.ground=put('ground.glb',b'ground');self.patch=put('trees.json',{'base_asset_sha256':'old'})
  self.prev={'asset_sha256':'old','landcover_url':'ground.glb','landcover_sha256':self.ground,'landcover_status':'inferred','vegetation_patch_url':'trees.json','vegetation_patch_sha256':self.patch,'reference_image_ids':['naip-2024-main-campus-rgb']}
 def test_paired_site_requires_unchanged_source_and_mesh_bytes(self):
  def put(name,content):
   path=self.scene/name
   path.write_bytes(content)
   return hashlib.sha256(content).hexdigest()
  model=put('campus.glb',b'model')
  terrain=put('heightfield.json',b'heightfield')
  put('manifest.json',json.dumps({'model':{'url':'campus.glb','sha256':model},'heightfield_url':'heightfield.json'}).encode())
  (self.scene/'ford-arena-review').mkdir()
  assets=[]
  for name in ['ford-alumni-site','matthew-knight-arena-site','frontage-ground']:
   url=f'ford-arena-review/{name}.glb'
   assets.append({'url':url,'sha256':put(url,name.encode())})
  site={
   'source_presentation_sha256':'old',
   'source_landcover_sha256':self.ground,
   'source_model_sha256':model,
   'source_heightfield_sha256':terrain,
   'buildings':assets[:2],
   'frontage_ground':assets[2],
  }
  url='ford-arena-review/site.json'
  self.prev['ford_arena_site']={'url':url,'sha256':put(url,json.dumps(site).encode())}
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.assertEqual(result['ford_arena_site'],self.prev['ford_arena_site'])
  with self.assertRaisesRegex(ValueError,'does not match rebuilt presentation'):
   module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  put(assets[1]['url'],b'tampered')
  with self.assertRaisesRegex(ValueError,'site mesh missing or hash changed'):
   module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_cascade_site_checks_terrain_and_candidate_hashes(self):
  directory=self.scene/'cascade-volcanology-review'
  directory.mkdir()
  def put(path,data):
   path.write_bytes(data)
   return hashlib.sha256(data).hexdigest()
  field=self.scene/'terrain.json'
  manifest={'model':{'sha256':'base'},'heightfield_url':field.name}
  put(self.scene/'manifest.json',json.dumps(manifest).encode())
  site={'source_presentation_sha256':'old','source_base_model_sha256':'base',
        'source_heightfield_sha256':put(field,b'terrain'),'url':'cascade-volcanology-review/site.glb',
        'sha256':put(directory/'site.glb',b'candidate')}
  entry={'url':'cascade-volcanology-review/site.json','sha256':put(directory/'site.json',json.dumps(site).encode())}
  self.prev['cascade_volcanology_site']=entry
  self.assertEqual(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['cascade_volcanology_site'],entry)
  put(directory/'site.glb',b'changed')
  with self.assertRaisesRegex(ValueError,'site mesh missing or hash changed'):
   module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  put(field,b'changed')
  with self.assertRaisesRegex(ValueError,'terrain missing or hash changed'):
   module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_adopted_sites_survive_presentation_rebuild(self):
  scene=root/'apps/web-preview/public/scene'
  previous=json.loads((scene/'presentation.json').read_bytes())
  rebuilt={'asset_sha256':previous['asset_sha256']}
  for key in ('museum_site_review','gerlinger_site_review','womens_quad_site','memorial_quad_site','fenton_site_review','allen_site_review','lawrence_science_site','straub_earl_site','kalapuya_site','longhouse_site','global_scholars_site','moss_street_site','vivian_olum_site','graduate_village_site','knight_law_site','bean_unthank_site','cedar_yasui_site','carson_llc_site','oregon_jaqua_site','lillis_complex_site','friendly_collier_mckenzie_site','plc_lokey_tykeson_site','northeast_science_site','knight_campus_site','northsite_millrace_site','heritage_core_site','heritage_miller_site'):
   with self.subTest(key=key):
    result=module.carry_layers({key:previous[key]},rebuilt,scene)
    self.assertEqual(result[key],previous[key])
  key='public_building_exterior_site'
  self.assertEqual(module.carry_layers({key:previous[key]},rebuilt,scene)[key],previous[key])
  for key in ('hayward_exterior_site','campus_frontage_site','facilities_exterior_site','office_exterior_site','residential_exterior_site','campus_neighbor_exterior_site','chapter_house_exterior_site','villard_garden_exterior_site','alder_millrace_exterior_site','east_campus_housing_exterior_site','fairmount_boulevard_exterior_site','garden_avenue_exterior_site','villard_street_exterior_site','hilyard_west_exterior_site','treated_roof_exterior_site','fairmount_residential_exterior_site','broadway_orchard_exterior_site','franklin_complex_exterior_site','franklin_boulevard_exterior_site','bardell_avenue_exterior_site'):
   with self.subTest(key=key):
    self.assertEqual(module.carry_layers({key:previous[key]},rebuilt,scene)[key],previous[key])
 def test_trunk_variation_requires_valid_base_and_source(self):
  data={'base_asset_sha256':'old','target_name':'campus-trees'};b=(json.dumps(data)+'\n').encode();(self.scene/'context.json').write_bytes(b);(self.scene/'variation.json').write_bytes(b);digest=hashlib.sha256(b).hexdigest()
  self.prev.update({'context_trunks_url':'context.json','context_trunks_sha256':digest,'context_trunk_variation_url':'variation.json','context_trunk_variation_sha256':digest})
  self.assertEqual(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['context_trunk_variation_sha256'],digest)
  with self.assertRaisesRegex(ValueError,'rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  (self.scene/'variation.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.prev.pop('context_trunks_url')
  with self.assertRaisesRegex(ValueError,'requires context trunks'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_batch_palette_preserves_pins_and_rejects_mismatch(self):
  data={'base_asset_sha256':'old','building_id':'roof-test','target_name':'batch'};b=(json.dumps(data)+'\n').encode();(self.scene/'palette.json').write_bytes(b)
  entry={'url':'palette.json','sha256':hashlib.sha256(b).hexdigest()};self.prev['batch_palette_patches']=[entry]
  self.assertEqual(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['batch_palette_patches'],[entry])
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  self.prev['batch_palette_patches']=[entry,entry]
  with self.assertRaisesRegex(ValueError,'Duplicate'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.prev['batch_palette_patches']=[entry];(self.scene/'palette.json').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_building_roof_patch_is_preserved_and_rejects_mismatch(self):
  self.prev.pop('vegetation_patch_url');self.prev.pop('vegetation_patch_sha256')
  data={'base_asset_sha256':'old','building_id':'roof-test'};b=(json.dumps(data)+'\n').encode();(self.scene/'roof.json').write_bytes(b)
  entry={'url':'roof.json','sha256':hashlib.sha256(b).hexdigest()};self.prev['building_roof_patches']=[entry]
  self.assertEqual(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['building_roof_patches'],[entry])
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  self.prev['building_roof_patches']=[entry,entry]
  with self.assertRaisesRegex(ValueError,'Duplicate'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.prev['building_roof_patches']=[entry];(self.scene/'roof.json').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_context_roofs_are_pinned_to_the_batch_source(self):
  path=self.scene/'context-roof-refinements.json'
  payload=json.dumps({'version':1,'source_presentation_sha256':'old'}).encode()
  path.write_bytes(payload)
  entry={'url':path.name,'sha256':hashlib.sha256(payload).hexdigest()}
  self.prev.update({'verify_source_sha256':True,'context_roof_refinements':entry})
  self.assertEqual(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['context_roof_refinements'],entry)
  with self.assertRaisesRegex(ValueError,'Context roof refinements do not match'):
   module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  path.write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'Context roof refinement missing or hash changed'):
   module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_furniture_patch_is_preserved_only_for_exact_source_and_hash(self):
  data={'base_asset_sha256':'old'}; b=(json.dumps(data)+'\n').encode(); (self.scene/'furniture.json').write_bytes(b)
  self.prev.pop('vegetation_patch_url'); self.prev.pop('vegetation_patch_sha256')
  self.prev.update({'furniture_patch_url':'furniture.json','furniture_patch_sha256':hashlib.sha256(b).hexdigest()})
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.assertEqual(result['furniture_patch_sha256'],self.prev['furniture_patch_sha256'])
  with self.assertRaisesRegex(ValueError,'furniture_patch does not match'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  (self.scene/'furniture.json').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'furniture_patch missing'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_fern_patch_preserved_and_rejects_changed_source_or_bytes(self):
  self.prev.pop('vegetation_patch_url');self.prev.pop('vegetation_patch_sha256')
  data={'base_asset_sha256':'old'};b=(json.dumps(data)+'\n').encode();(self.scene/'fern.json').write_bytes(b)
  self.prev.update({'fern_patch_url':'fern.json','fern_patch_sha256':hashlib.sha256(b).hexdigest()})
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.assertEqual(result['fern_patch_sha256'],self.prev['fern_patch_sha256'])
  with self.assertRaisesRegex(ValueError,'fern_patch does not match'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  (self.scene/'fern.json').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'fern_patch missing'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_additional_environment_patch_is_source_pinned_and_unique(self):
  self.prev.pop('vegetation_patch_url');self.prev.pop('vegetation_patch_sha256')
  data={'base_asset_sha256':'old','target_name':'understory'};b=(json.dumps(data)+'\n').encode();(self.scene/'plaza.json').write_bytes(b)
  entry={'url':'plaza.json','sha256':hashlib.sha256(b).hexdigest()};self.prev['additional_environment_patches']=[entry]
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene);self.assertEqual(result['additional_environment_patches'],[entry])
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  self.prev['additional_environment_patches']=[entry,entry]
  with self.assertRaisesRegex(ValueError,'Duplicate'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.prev['additional_environment_patches']=[entry];(self.scene/'plaza.json').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_planting_variation_preserved_only_for_matching_source(self):
  b=(json.dumps({'base_asset_sha256':'old','target_name':'planting'})+'\n').encode();(self.scene/'shrubs.json').write_bytes(b)
  self.prev['planting_variation_url']='shrubs.json';self.prev['planting_variation_sha256']=hashlib.sha256(b).hexdigest()
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene);self.assertEqual(result['planting_variation_url'],'shrubs.json')
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'changed'},self.scene)
  (self.scene/'shrubs.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_context_trunks_preserved_only_for_matching_source(self):
  b=(json.dumps({'base_asset_sha256':'old','target_name':'campus-trees'})+'\n').encode();(self.scene/'trunks.json').write_bytes(b)
  self.prev['context_trunks_url']='trunks.json';self.prev['context_trunks_sha256']=hashlib.sha256(b).hexdigest()
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene);self.assertEqual(result['context_trunks_url'],'trunks.json')
  with self.assertRaisesRegex(ValueError,'do not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'changed'},self.scene)
  (self.scene/'trunks.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_lawn_tone_preserved_only_for_matching_source(self):
  b=(json.dumps({'base_asset_sha256':'old','target_name':'landscape-lawn'})+'\n').encode();(self.scene/'lawn.json').write_bytes(b)
  self.prev['lawn_tone_url']='lawn.json';self.prev['lawn_tone_sha256']=hashlib.sha256(b).hexdigest()
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene);self.assertEqual(result['lawn_tone_url'],'lawn.json')
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'changed'},self.scene)
  (self.scene/'lawn.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_paving_joints_preserved_only_for_matching_source(self):
  b=(json.dumps({'base_asset_sha256':'old','target_name':'landscape-paving'})+'\n').encode();(self.scene/'paving.json').write_bytes(b)
  self.prev['paving_joints_url']='paving.json';self.prev['paving_joints_sha256']=hashlib.sha256(b).hexdigest()
  result=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene);self.assertEqual(result['paving_joints_url'],'paving.json')
  with self.assertRaisesRegex(ValueError,'do not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'changed'},self.scene)
  (self.scene/'paving.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_wall_color_patch_preserved_and_checked(self):
  b=(json.dumps({'base_asset_sha256':'old'})+'\n').encode();(self.scene/'wall.json').write_bytes(b)
  entry={'url':'wall.json','sha256':hashlib.sha256(b).hexdigest()};self.prev['wall_color_patches']=[entry]
  self.assertEqual(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['wall_color_patches'],[entry])
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  self.prev['wall_color_patches']=[entry,entry]
  with self.assertRaisesRegex(ValueError,'Duplicate'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.prev['wall_color_patches']=[entry];(self.scene/'wall.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_preserves_verified_layers(self):
  out=module.carry_layers(self.prev,{'asset_sha256':'old','reference_image_ids':['other']},self.scene)
  self.assertEqual(out['vegetation_patch_sha256'],self.patch);self.assertEqual(out['landcover_sha256'],self.ground);self.assertEqual(out['reference_image_ids'],['other','naip-2024-main-campus-rgb'])
 def test_changed_glb_fails_before_any_writes(self):
  before={p.name:p.read_bytes() for p in self.scene.iterdir()}
  with self.assertRaisesRegex(ValueError,'does not match rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.scene.iterdir()})
 def test_ground_or_patch_tampering_rejected(self):
  (self.scene/'ground.glb').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'ground layer'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_patch_tampering_rejected(self):
  (self.scene/'trees.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'vegetation_patch missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_suppression_is_preserved_with_visible_count(self):
  b=(json.dumps({'base_asset_sha256':'old','suppressed_trees':1})+'\n').encode();(self.scene/'hide.json').write_bytes(b)
  self.prev.update({'tree_suppression_url':'hide.json','tree_suppression_sha256':hashlib.sha256(b).hexdigest(),'stats':{'sourceTrees':600,'trees':599}})
  out=module.carry_layers(self.prev,{'asset_sha256':'old','stats':{'trees':600}},self.scene)
  self.assertEqual(out['stats'],{'sourceTrees':600,'trees':599});self.assertEqual(out['tree_suppression_url'],'hide.json')
  self.prev['stats']['trees']=600
  with self.assertRaisesRegex(ValueError,'statistics changed'):module.carry_layers(self.prev,{'asset_sha256':'old','stats':{'trees':600}},self.scene)
 def test_exterior_detail_is_preserved_and_pinned(self):
  b=(json.dumps({'base_asset_sha256':'old'})+'\n').encode();(self.scene/'detail.json').write_bytes(b)
  self.prev.update({'exterior_detail_url':'detail.json','exterior_detail_sha256':hashlib.sha256(b).hexdigest(),'exterior_detail_status':'inferred'})
  out=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.assertEqual(out['exterior_detail_url'],'detail.json')
  with self.assertRaisesRegex(ValueError,'exterior detail does not match'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  (self.scene/'detail.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'exterior detail missing'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_multiple_exterior_details_preserved_and_checked(self):
  b=(json.dumps({'base_asset_sha256':'old'})+'\n').encode();(self.scene/'detail2.json').write_bytes(b)
  self.prev['exterior_details']=[{'url':'detail2.json','sha256':hashlib.sha256(b).hexdigest(),'status':'inferred'}]
  out=module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.assertEqual(out['exterior_details'],self.prev['exterior_details'])
  with self.assertRaisesRegex(ValueError,'exterior detail does not match'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
  self.prev['exterior_details'].append(dict(self.prev['exterior_details'][0]))
  with self.assertRaisesRegex(ValueError,'Duplicate'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_additional_tree_suppression_preserves_counts_and_hashes(self):
  b=(json.dumps({'base_asset_sha256':'old','suppressed_trees':1})+'\n').encode()
  for name in ('hide1.json','hide2.json'):(self.scene/name).write_bytes(b)
  digest=hashlib.sha256(b).hexdigest()
  self.prev.update({'tree_suppression_url':'hide1.json','tree_suppression_sha256':digest,'additional_tree_suppressions':[{'url':'hide2.json','sha256':digest}],'stats':{'sourceTrees':600,'trees':598}})
  out=module.carry_layers(self.prev,{'asset_sha256':'old','stats':{'trees':600}},self.scene)
  self.assertEqual(out['stats']['trees'],598);self.assertEqual(len(out['additional_tree_suppressions']),1)
  (self.scene/'hide2.json').write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'Additional tree suppression missing'):module.carry_layers(self.prev,{'asset_sha256':'old','stats':{'trees':600}},self.scene)
 def test_registered_tree_fits_follow_verified_source(self):
  b=json.dumps({'version':1,'operation':'registered-pilot-tree-fit-v1','base_asset_sha256':'old','trees':[{'index':114}]}).encode()
  path=self.scene/'fitted-trees.json';path.write_bytes(b)
  entry={'url':path.name,'sha256':hashlib.sha256(b).hexdigest(),'trees':1}
  self.prev.update({'registered_pilot_trees':entry,'verify_source_sha256':True})
  out=module.carry_layers(self.prev,{'asset_sha256':'old','stats':{'trees':600}},self.scene)
  self.assertEqual(out['registered_pilot_trees'],entry)
  self.assertEqual(out['stats']['trees'],600)
  entry['trees']=2
  with self.assertRaisesRegex(ValueError,'registration metadata'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  path.write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'registration missing or hash changed'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
 def test_triangle_patch_requires_verified_source_and_survives_rebuild(self):
  data={'base_asset_sha256':'old','building_id':'roof-test','source_triangle_patch':{'triangles':[]}}
  b=(json.dumps(data)+'\n').encode();(self.scene/'detail.json').write_bytes(b)
  self.prev['exterior_details']=[{'url':'detail.json','sha256':hashlib.sha256(b).hexdigest()}]
  with self.assertRaisesRegex(ValueError,'requires source hash verification'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
  self.prev['verify_source_sha256']=True
  self.assertIs(module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)['verify_source_sha256'],True)
  with self.assertRaisesRegex(ValueError,'rebuilt GLB'):module.carry_layers(self.prev,{'asset_sha256':'new'},self.scene)
 def test_unsafe_layer_paths_rejected(self):
  self.prev['landcover_url']='../ground.glb'
  with self.assertRaisesRegex(ValueError,'Unsafe'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
if __name__=='__main__':unittest.main()
