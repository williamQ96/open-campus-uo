# Ten Harris, Potter and East 20th exteriors

| Scene ID | City outline | Exterior model |
| --- | ---: | --- |
| `roof-5be21a96` | 171103 | 1926 Potter. Intersecting roof volumes and the east porch. |
| `potter-1938` | 171105 | 1938 Potter. Dominant east gable, arched entrance surround and dormer. |
| `potter-1976` | 171108 | 1976 Potter. White east gable, chimney and lower rear section. |
| `roof-b0798c1b` | 171109 | 1992 and 1994 Potter. Both addresses share the model. The roof volumes follow the complete registered outline. |
| `roof-ae77fb78` | 171100 | 1045 East 20th. Stepped north and south roof volumes and a south wooden screen. |
| `roof-da8142c0` | 129711 | 1096 East 20th. Pale siding, front gable and a raised north landing. |
| `harris-1911` | 171094 | 1911 Harris. Transverse gables, lateral red garage door and siding. |
| `roof-84ccdaf5` | 171095 | 1925 Harris. Low and raised flat roofs, narrow panel bays, green fascia and a covered west approach. |
| `harris-1941` | 171096 | 1941 Harris. Low crossing roof sections and a small west porch. |
| `roof-7e72b4ca` | 171097 | 1959 Harris. Wide dormer and porch, street stair and interrupted retaining wall. |

Six older source IDs are retained. The four independently registered additions preserve roof gaps of 4.081 and 1.341 m on Potter and 1.739 and 1.385 m on Harris. The profiles use the 2017, 2021 and 2025 Lane County aerials and dated street views. Approximation remains in the concealed window and wall placement, screened siding and entrance grades. The 1045 East 20th and 1992–1994 Potter models have no authored pedestrian entry because the street views leave their door locations uncertain. [Municipal footprints](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerial service](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Editable data and verified source links](../data/metadata/harris-potter-exterior-review.json).

| Model | 2013–15 paired median error | DOGAMI paired median error |
| --- | ---: | ---: |
| 1926 Potter | 1.1127 → 0.7247 m | 0.7454 → 0.5430 m |
| 1938 Potter | 1.6991 → 0.8665 m | 1.8147 → 0.6984 m |
| 1976 Potter | 0.8813 → 0.7107 m | 0.6604 → 0.3480 m |
| 1992–1994 Potter | 1.6487 → 0.5832 m | 1.4469 → 0.4783 m |
| 1045 East 20th | 1.3260 → 1.2138 m | 1.1885 → 0.1906 m |
| 1096 East 20th | 1.2340 → 0.3509 m | 0.9454 → 0.1776 m |
| 1911 Harris | 0.7857 → 0.4376 m | 0.5818 → 0.5323 m |
| 1925 Harris | 0.8357 → 0.0410 m | 0.8272 → 0.0455 m |
| 1941 Harris | 0.6267 → 0.5821 m | 0.8569 → 0.4109 m |
| 1959 Harris | 1.0867 → 0.7141 m | 0.8782 → 0.5993 m |

All 3,196 available rays on the two useful grids hit the new roofs. The medians use 2,684 paired samples. There is no 2017 USACE coverage at these sites. Sixteen matched views compare the street elevations and the gaps. The exporter removes 2,019 triangles in two source batches, preserving the indices and vertex attributes for 106 unaffected batch members. It checks 7,710 route edges and reports a minimum clearance of 4.7368 m.

Desktop and phone select all ten buildings and route to the eight authored approaches. They pass 20 collision and 32 approach probes, including all four gaps, the 1925 covered approach and the 1959 stair and retaining wall. Corrupt model bytes and an invalid source anchor each restore all six old shapes and estimated entrances. Stage, repeat, installed, built and served assets match. This package is local and uncommitted. [Exporter](../scripts/build-harris-potter-exterior-review.py).
