# Hilyard Apartments at 957, 971 and 975 Hilyard Street

Three independently modeled exteriors replace the combined 957/971 roof and the approximate 975 volume. 957 retains `roof-9feed235`, 971 uses `hilyard-apartments-971` and 975 retains `roof-eab27ea2`. The city address points agree with footprints 149932, 178620 and 170820 respectively. The municipal outlines for 957 and 971 overlap the old 957/971 candidate by 238.85 m² and 140.57 m². The 1993 apartment advert lists 957 and 971 together and identifies 973 as their management address. 975 is registered by its street address. [Municipal footprint layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Archived advert](https://oregonnews.uoregon.edu/lccn/2004260239/1993-05-25/ed-1/seq-7.pdf) · [Source pins and measurements](../data/metadata/hilyard-central-exterior-review.json).

The November 2020 view from Alder Alley shows three different forms. The north building at 957 has a gray end wall and two green exterior galleries with open stairs. The central 971 building has two rows of windows in a brick end wall and its own compact hip. The southern 975 building has a tan end wall and a single upper gallery and stair. The footprints and roof separations agree with the 2024 orthophoto. June 2024 views from Hilyard confirm their setback behind 973 and show some of the courtyard access. Courtyard-facing window counts, stair and gallery dimensions, some materials and all thresholds are estimates. The 971 north point is a simulated approach without a modeled door. Panorama pixels are external references. All exported geometry and material colors are original. [Alder Alley panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=oj-FXKPaxVd5Aw6HqJqi9g&heading=270) · [North driveway from Hilyard](https://www.google.com/maps/@?api=1&map_action=pano&pano=lseZZJSDv4wjhvFS9itHsQ&heading=90) · [South driveway from Hilyard](https://www.google.com/maps/@?api=1&map_action=pano&pano=HZelz5IYnWT2XS99nv0QZA&heading=82).

## Roof comparison

The final meshes cover all 1,783 usable roof samples in the three historical surfaces. The values below are median absolute differences on cells hit by both the earlier and revised mesh. The 975 baseline includes its previous context hip treatment. The revised 975 improves on two historical surfaces. Its median difference in the oldest grid rises by 0.16 m. [NOAA LiDAR archive](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI elevation mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

| Address | 2013–2015 | 2017 | DOGAMI Lane |
| --- | ---: | ---: | ---: |
| 957 | 1.25 → 0.22 m (216 cells) | 1.06 → 0.08 m (216) | 1.11 → 0.17 m (213) |
| 971 | 0.73 → 0.52 m (123) | 0.66 → 0.11 m (125) | 0.79 → 0.26 m (125) |
| 975 | 0.13 → 0.29 m (220) | 0.27 → 0.06 m (224) | 0.42 → 0.15 m (224) |

## Runtime and verification

The model replaces 642 source triangles and preserves the surviving indices and vertex attributes of 36 other batch members. The two gaps between the three buildings remain clear at the tested points, and the independent 973 approach and collision remain usable. The nearest of 7,710 checked route edges lies 7.7555 m from the revised footprint or support. The raw route graph is unchanged.

Four paired renders show the roof separation, two galleries and brick east facade. Desktop and phone production verified three searches, three estimated walkable approaches and six collision probes. A damaged anchor for the second source restores both old volumes and the preceding 975 roof treatment. Formatting, 195 unit tests, six focused browser tests, production build, 335 open archive checks and 268 viewer pins passed. The default scene now contains 519 selectable buildings, 326 batch members and six independent context roof treatments. The update is local and uncommitted. [Builder](../scripts/build-hilyard-central-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/hilyard-central-exterior-review/site.json).
