# SPDX-License-Identifier: Apache-2.0
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('screen_reference', Path(__file__).with_name('screen-reference-footprints.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FootprintScreenTest(unittest.TestCase):
    def setUp(self):
        self.manifest = {'coordinate_frame': {'origin_projected_m': [100, 200, 0]}, 'buildings': [{'id': 'x', 'name': 'Example', 'footprint_enu_m': [[0,0], [10,0], [10,10], [0,10]]}]}
        self.data = {'type': 'FeatureCollection', 'crs': {'properties': {'name': 'EPSG:3740'}}, 'features': [{'type': 'Feature', 'geometry': {'type': 'Polygon', 'coordinates': [[[105,200],[115,200],[115,210],[105,210],[105,200]]]}, 'properties': {'OBJECTID': 1, 'ORBLD_ID': 'duplicate'}}]}
    def test_overlap_fractions_and_source_not_renamed(self):
        result = module.screen(self.manifest, self.data)[0]
        self.assertEqual(result['name'], 'Example')
        self.assertEqual(result['overlaps'][0]['overlap_m2'], 50)
        self.assertEqual(result['overlaps'][0]['candidate_fraction'], .5)
        self.assertEqual(result['overlaps'][0]['source_fraction'], .5)
        self.assertEqual(result['overlaps'][0]['source_object_id'], 1)
    def test_wrong_crs_and_truncated_results_rejected(self):
        self.data['crs']['properties']['name'] = 'EPSG:4326'
        with self.assertRaises(ValueError): module.screen(self.manifest, self.data)
        self.data['crs']['properties']['name'] = 'EPSG:3740'
        self.data['exceededTransferLimit'] = True
        with self.assertRaises(ValueError): module.screen(self.manifest, self.data)

if __name__ == '__main__': unittest.main()
