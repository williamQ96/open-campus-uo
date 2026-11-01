# SPDX-License-Identifier: Apache-2.0
"""Offline habitat/placement audit of the committed activity file; no extra dependencies."""
from pathlib import Path
import json
import math
import hashlib

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
activity = read(ROOT / 'apps/web-preview/public/scene/activity.json')
zones = read(ROOT / 'data/metadata/activity-zones.geojson')

def ring_contains(point, ring):
    x, y = point
    hit = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            hit = not hit
    return hit

def contains(point, geometry):
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    return any(ring_contains(point, rings[0]) and not any(ring_contains(point, hole) for hole in rings[1:]) for rings in polygons)

surfaces = {f['properties']['surface']: f['geometry'] for f in zones['features']}
trees = {tree['id']: tree for tree in activity['trees']}
assert activity['version'] == 2
assert len(set(p['id'] for p in activity['paths'])) == len(activity['paths'])
for path in activity['paths']:
    assert path['surface'] in {'pedestrian', 'driving', 'vegetation', 'tree'}
    points = path['points_enu_m']
    assert len(points) >= 2 and all(len(p) == 3 and all(math.isfinite(v) for v in p) for p in points)
    if path['surface'] == 'tree':
        tree = trees[path['tree_id']]
        assert contains([tree['east'] + .35, tree['north']], surfaces['vegetation'])
        assert all(math.hypot(p[0] - tree['east'], p[1] - tree['north']) < 1 for p in points)
        continue
    geometry = surfaces[path['surface']]
    for a, b in zip(points, points[1:]):
        count = max(1, math.ceil(math.dist(a[:2], b[:2]) / .4))
        for i in range(count + 1):
            assert contains([a[k] + (b[k] - a[k]) * i / count for k in (0, 1)], geometry), path['id']
assert len(activity['prop_slots']) >= 14
for slot in activity['prop_slots']:
    point = [slot['east'], slot['north']]
    assert slot['surface'] == 'parking' and contains(point, surfaces['parking'])
    assert not contains(point, surfaces['vegetation']) and not contains(point, surfaces['pedestrian'])
print(json.dumps({'version': 2, 'paths': len(activity['paths']), 'parking_slots': len(activity['prop_slots']),
                  'tree_routes': len(trees), 'semantic_samples': 'all classified; no cross-surface fallback'}))
