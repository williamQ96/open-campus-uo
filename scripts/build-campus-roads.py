"""Prepare a small, attributable Census road/path GeoJSON for this campus AOI.

Run with upstream Python plus pyshp (pip install pyshp==3.1.6). County ZIP is
cached outside git. Widths are display estimates, not measurements or road access.
"""
from collections import Counter
from pathlib import Path
import io
import json
import zipfile

from pyproj import CRS, Transformer
import shapefile
import shapely
from shapely.geometry import LineString, box

from geospatial3d.io import fetch_source, write_json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = {
    'id': 'us-census-tiger-2025-lane-roads',
    'provider': 'U.S. Census Bureau',
    'title': '2025 TIGER/Line® Shapefiles, Lane County, Oregon, All Roads',
    'url': 'https://www2.census.gov/geo/tiger/TIGER2025/ROADS/tl_2025_41039_roads.zip',
    'filename': 'tl_2025_41039_roads.zip',
    'sha256': '9ff7743ebd87d5fe3bed57f4555784e747aab25c96e72f2aac382da5d11bda2b',
    'license_url': 'https://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2025/TGRSHP2025_TechDoc.pdf',
    'license_note': 'U.S. Government work; technical documentation §1.2 permits reproduction with Census Bureau attribution. TIGER/Line is a registered trademark.',
    'source_crs': 'EPSG:4269 (NAD83), verified against source .prj',
    'vintage': '2025',
    'verified_on': '2026-10-31',
    'processing': 'County centerlines reprojected from NAD83 to WGS84, clipped to campus AOI plus 35 m. Original LINEARID, names and MTFCC retained; widths estimated by class. No bridge decks or lane geometry.',
}
# Conservative display widths in metres, not surveyed carriageways.
CLASSES = {'S1100': ('road', 16), 'S1200': ('road', 18), 'S1400': ('road', 9),
           'S1630': ('road', 7), 'S1640': ('road', 7), 'S1730': ('road', 4),
           'S1740': ('road', 5), 'S1780': ('road', 5),
           'S1710': ('path', 3), 'S1820': ('path', 4)}


def main():
    config = json.loads((ROOT/'configs/eugene-main-campus.json').read_text())
    target = config['aoi']['horizontal_epsg']
    origin = Transformer.from_crs(4326, target, always_xy=True).transform(*config['aoi']['center_lon_lat'])
    half = config['aoi']['size_m']/2 + 35
    extent = box(origin[0]-half, origin[1]-half, origin[0]+half, origin[1]+half)
    source_to_local = Transformer.from_crs(4269, target, always_xy=True)
    local_to_wgs = Transformer.from_crs(target, 4326, always_xy=True)
    features = []
    path = fetch_source(SOURCE, ROOT/'data/raw')
    with zipfile.ZipFile(path) as archive:
        stem = 'tl_2025_41039_roads'
        if CRS.from_wkt(archive.read(stem+'.prj').decode()).to_epsg() != 4269:
            raise ValueError('Unexpected road source CRS')
        reader = shapefile.Reader(**{suffix: io.BytesIO(archive.read(stem+'.'+suffix)) for suffix in ['shp','shx','dbf']})
        # Coarse geographic filter; exact projected clipping follows below.
        for row in reader.iterShapeRecords(bbox=(-123.09, 44.03, -123.05, 44.06)):
            props = row.record.as_dict()
            if props['MTFCC'] not in CLASSES:
                continue
            points = row.shape.points
            starts = list(row.shape.parts) + [len(points)]
            for index, (start, end) in enumerate(zip(starts, starts[1:])):
                line = shapely.transform(LineString(points[start:end]), source_to_local.transform, interleaved=False).intersection(extent)
                parts = [line] if line.geom_type == 'LineString' else list(getattr(line,'geoms', []))
                for part_index, part in enumerate(parts):
                    if part.geom_type != 'LineString' or part.length < 1:
                        continue
                    kind, width = CLASSES[props['MTFCC']]
                    wgs = shapely.transform(part, local_to_wgs.transform, interleaved=False)
                    features.append({'type': 'Feature', 'id': f"tiger-{props['LINEARID']}-{index}-{part_index}",
                                     'properties': {'name': props['FULLNAME'] or 'Unnamed '+kind,
                                                    'kind': kind, 'width_m': width, 'source_id': SOURCE['id'],
                                                    'mtfcc': props['MTFCC'], 'linearid': props['LINEARID']},
                                     'geometry': {'type': 'LineString', 'coordinates': [[round(x,9),round(y,9)] for x,y in wgs.coords]}})
    features.sort(key=lambda f: f['id'])
    write_json(ROOT/'data/metadata/campus-roads.geojson', {'type': 'FeatureCollection', 'sources': [SOURCE], 'features': features})
    print(json.dumps({'features': len(features), 'kinds': dict(Counter(f['properties']['kind'] for f in features))}, indent=2))


if __name__ == '__main__':
    main()
