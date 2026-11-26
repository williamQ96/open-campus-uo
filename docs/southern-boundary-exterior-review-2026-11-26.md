# Eight southern boundary exteriors

| Scene ID | City outline | Exterior model |
| --- | ---: | --- |
| `roof-6594bfe8` | 129687 | 2039 Harris. Raised porch and stair, adjacent garage frontage and interrupted retaining wall. |
| `harris-2061` | 129674 | 2061 Harris. Offset pale gables, west shutters, circular attic vent and chimney. |
| `roof-d44341e6` | 129644 | 1025 East 21st. Twin street gables, sheltered porch and two-bay garage elevation with a glazed upper row. |
| `roof-24910633` | 129427 | 2086 Potter. Offset roof masses, east board fence and closed metal gate under its own small gable. |
| `roof-8d87ddf2` | 129431 | 2089 Potter. Main street gable, lower wing, raised steps and retaining wall. |
| `roof-496beafd` | 129710 | 2000 University. Two broad roof masses with a low covered link and a raised east approach. |
| `roof-7873e057` | 129699 | 2028 University main house. The irregular registered outline retains the intersecting roof volumes and small northern cutout. |
| `university-2028-rear` | 129698 | 2028 University rear building. The adjacent roof remains a separate selectable hipped structure on the same parcel. |

The two measured roof gaps are 2.536 m between the Harris addresses and 0.722 m between the two University roofs. The 2017, 2021 and 2025 aerials and two elevation surfaces show the separate rear roof. The west street bearings are screened and leave the rear structure's use, finish and openings uncertain. It has no assigned independent address or modeled approach. The 2086 Potter gate is closed in the viewer. Landscaped areas, concealed details and approach heights use estimates. [City footprints](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Editable dimensions and source references](../data/metadata/southern-boundary-exterior-review.json).

| Model | 2013–15 paired median error | DOGAMI paired median error |
| --- | ---: | ---: |
| 2039 Harris | 0.7233 → 0.5599 m | 0.7577 → 0.3055 m |
| 2061 Harris | 0.8533 → 0.3745 m | 0.7577 → 0.4307 m |
| 1025 East 21st | 1.0723 → 0.3483 m | 0.9283 → 0.6903 m |
| 2086 Potter | 1.0625 → 0.7564 m | 1.4051 → 0.8553 m |
| 2089 Potter | 1.0174 → 0.3709 m | 0.9578 → 0.8343 m |
| 2000 University | 0.8594 → 0.1801 m | 0.9372 → 0.2410 m |
| 2028 University main | 1.5223 → 0.9603 m | 1.4175 → 0.4920 m |
| 2028 University rear | 1.4300 → 0.7911 m | 1.5185 → 0.3060 m |

All 3,462 available rays from the two useful surface grids hit, including 2,332 cells also covered by the old roofs. The 2017 USACE grid has no samples at these locations. Fourteen view pairs include both restored gaps, the linked volumes at 2000 University and the rear mass at 2028. Exactly 1,742 source triangles were removed from two batches. The retained index order and vertex attributes are unchanged for 106 batch peers. The exporter checks 7,710 route edges with minimum clearance 4.7206 m.

Desktop and phone select all eight models. They pass 18 collision probes and 24 clearance probes across six estimated approaches. From Knight Library, the six routes contain 152, 158, 166, 178, 186 and 192 points in table order, omitting the two exteriors without an authored approach. Both damaged model bytes and an invalid source anchor restore all six old meshes and approaches, and both split gap probes become blocked in the fallback. Stage, repeat, installed, built and served package bytes match. This package is local and uncommitted. [Exporter](../scripts/build-southern-boundary-exterior-review.py).
