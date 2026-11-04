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
 def test_unsafe_layer_paths_rejected(self):
  self.prev['landcover_url']='../ground.glb'
  with self.assertRaisesRegex(ValueError,'Unsafe'):module.carry_layers(self.prev,{'asset_sha256':'old'},self.scene)
if __name__=='__main__':unittest.main()
