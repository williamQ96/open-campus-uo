# 1515 Hilyard and E 15th Avenue exteriors

The local scene replaces the merged `roof-9bdc0828` mesh with three independent L2 exteriors. 1515 Hilyard retains that scene ID. Treetop Apartments at 740 E 15th and the 1547–1549 Hilyard duplex have their own searchable IDs. The separate footprints come from the Eugene building and address layers and were checked against the 2024 OSIP orthophoto. [Municipal buildings](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Municipal address points](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0) · [Source pins and model dimensions](../data/metadata/hilyard-1515-exterior-review.json).

| Building | City footprint | Overlap with the former combined source | Restored features |
| --- | ---: | ---: | --- |
| 1515 Hilyard Apartments | 170382 | 789.06 m² | Light membrane roof, ventilated dark eaves, tall glazed north stair window, lower window row and west balcony. |
| Treetop Apartments, 740 E 15th | 170381 | 632.08 m² | Flat roof with a low raised strip, separate north and alley entry stairs and two open north parking recesses with braced covers. |
| 1547–1549 Hilyard Duplex | 170341 | 101.35 m² | Hip roof, red-brown vertical wood siding, west balcony, twin doors and a covered south door. |

June 2024 street views show the street faces and alley windows. A leasing photo attached to the duplex advert shows another building number. The model follows the registered Hilyard panorama for the duplex. The source imagery remains external. The exported models use original geometry and material colors. The hidden side details, recess depth, balcony dimensions and approach thresholds are estimates. [1515 north front](https://www.google.com/maps/@?api=1&map_action=pano&pano=vjc_u1i9lJ5bBahpB9F-HA&heading=180) · [740 north front](https://www.google.com/maps/@?api=1&map_action=pano&pano=qJQIH-RC8JG8uBfL1Z7E3A&heading=180) · [Apartment alley view](https://www.google.com/maps/@?api=1&map_action=pano&pano=J5qfyhb9EjmupoduHlPd_w&heading=0) · [Duplex west front](https://www.google.com/maps/@?api=1&map_action=pano&pano=tzm6yeZa1mAIwASykh5gyQ&heading=90).

## Roof verification

The table gives the before and after median absolute elevation difference on common 1 m cells. The model covers all 724, 666 and 153 buffered roof cells respectively, including portions missing from the old combined outline. The limited 2017 returns in this part of the study area had implausible heights. The DOGAMI grid has high outliers at Treetop's tree-screened north edge, where all-cell difference at the 90th percentile remains 8.45 m. Both datasets are historical. [NOAA Digital Coast LiDAR](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI surface mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

| Building | Common roof cells | NOAA 2013–2015 | DOGAMI Lane County |
| --- | ---: | ---: | ---: |
| 1515 Hilyard | 722 | 0.77 → 0.03 m | 0.74 → 0.03 m |
| 740 E 15th | 572 | 0.83 → 0.05 m | 0.82 → 0.05 m |
| 1547–1549 Hilyard | 97 | 1.09 → 0.30 m | 0.94 → 0.30 m |

## Scene integration

The registration removes 608 old triangles while preserving the other 51 members of the background batch and their surviving indices and mesh attributes. The ground footprints leave the gap between the two apartments and both front parking recesses open. The model blocks the central entry support at 740 separately from those bays. The nearest of 7,710 checked route edges is 3.1597 m away. The underlying outdoor route graph is unchanged.

Five before-and-after view pairs cover the three street faces, the alley and the roofs. Both desktop and phone production verified search, four walkable estimated approaches and seven collision probes. The default scene has 518 selectable buildings, 328 batched buildings and seven separate context roof treatments. A damaged batch anchor restores the original combined building and removes both split IDs. Formatting, 195 unit tests, eight focused browser tests, the production build, 333 open archive checks and 266 viewer pin checks passed. This local update is uncommitted. [Builder](../scripts/build-hilyard-1515-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/hilyard-fifteenth-exterior-review/site.json).
