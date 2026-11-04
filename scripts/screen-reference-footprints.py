# SPDX-License-Identifier: Apache-2.0
"""Screen existing named campus candidates against an externally supplied GIS extract.

The extract is reference-only; do not infer identity from overlapping polygons.
"""
import argparse
import hashlib
import json
from pathlib import Path

from shapely.affinity import translate
from shapely.geometry import Polygon, shape

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'apps/web-preview/public/scene/manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def screen(manifest, data):
    if data.get('type') != 'FeatureCollection' or data.get('crs', {}).get('properties', {}).get('name') != 'EPSG:3740':
        raise ValueError('Expected an EPSG:3740 GeoJSON feature collection')
    if data.get('exceededTransferLimit'):
        raise ValueError('Incomplete feature collection')
    origin = manifest['coordinate_frame']['origin_projected_m']
    geoms = []
    for index, f in enumerate(data['features']):
        geom = translate(shape(f['geometry']), xoff=-origin[0], yoff=-origin[1])
        if not geom.is_valid:
            geom = geom.buffer(0)
        if geom.is_empty or geom.geom_type not in ('Polygon', 'MultiPolygon'):
            raise ValueError(f'Invalid polygon at source index {index}')
        prop = f.get('properties') or {}
        geoms.append((geom, prop))
    results = []
    for b in manifest['buildings']:
        if not b.get('name'):
            continue
        candidate = Polygon(b['footprint_enu_m'])
        if not candidate.is_valid:
            candidate = candidate.buffer(0)
        if candidate.is_empty or candidate.area <= 0:
            raise ValueError(f'Invalid project footprint: {b["id"]}')
        hits = []
        for p, prop in geoms:
            if not candidate.intersects(p):
                continue
            overlap = candidate.intersection(p).area
            if overlap < 1:
                continue
            hits.append({'source_object_id': prop.get('OBJECTID'), 'source_building_id': prop.get('ORBLD_ID'), 'contributor': prop.get('CONTRIBUTOR'), 'source_date': prop.get('SOURCE_DATE'), 'source_area_m2': round(p.area, 2), 'overlap_m2': round(overlap, 2), 'candidate_fraction': round(overlap / candidate.area, 4), 'source_fraction': round(overlap / p.area, 4)})
        hits.sort(key=lambda h: (-h['overlap_m2'], str(h['source_object_id'])))
        results.append({'id': b['id'], 'name': b['name'], 'name_match': b.get('name_match'), 'candidate_area_m2': round(candidate.area, 2), 'overlaps': hits})
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--geojson', type=Path, required=True, help='Reference extract; not copied into the report')
    ap.add_argument('--output', type=Path, required=True, help='New report path (never overwritten)')
    ap.add_argument('--expected-count', type=int, required=True, help='Count from a separate source count query')
    args = ap.parse_args()
    source_bytes = args.geojson.read_bytes()
    manifest_bytes = MANIFEST.read_bytes()
    source = json.loads(source_bytes)
    if len(source.get('features', [])) != args.expected_count:
        raise ValueError('Extract count differs from the independent source count')
    report = {'manifest_sha256': digest(manifest_bytes), 'reference_sha256': digest(source_bytes), 'reference_crs': 'EPSG:3740', 'reference_feature_count': args.expected_count, 'source': 'https://services8.arcgis.com/8PAo5HGmvRMlF2eU/arcgis/rest/services/Building_Footprints/FeatureServer/0', 'meaning': '2D intersections only; neither a registered survey nor an identity, mesh, height, current-condition or permission determination.', 'named_candidates': screen(json.loads(manifest_bytes), source)}
    with args.output.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"Screened {len(report['named_candidates'])} named candidates against {args.expected_count} reference features")


if __name__ == '__main__':
    main()
