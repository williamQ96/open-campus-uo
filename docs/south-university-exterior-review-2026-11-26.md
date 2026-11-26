# Three South University exteriors

| Scene ID | Model and visible details |
| --- | --- |
| `roof-b048deca` | **Sigma Nu Chapter House, 1851 Onyx Street.** Four full-height west columns, a recessed double entrance, intersecting roof ridges and the screened rear deck. |
| `roof-82ccbe9b` | **1306 East 18th Avenue.** Sage vertical siding, shallow stepped roofs, the open west canopy and a rear exterior stair. |
| `roof-e0385ede` | **1874 Emerald Street.** Blue siding, two rows of openings, a hip roof and the small east porch. |

The City outlines are 170645, 170643 and 170642. County captures from 2017, 2021 and 2025 provide the outline and roof context. July 2024 street views establish the front elevations and the two chapter-area rear features. The University IFC lists Sigma Nu at 1851 Onyx. The 1306 model uses the street address because current occupancy was not verified. The roof equipment, screened openings, rear stair dimensions and three entrances use approximate measurements. [City footprint layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Sigma Nu chapter listing](https://uoifc.com/alpha-tau-omega/) · [University records index for 1306](https://publicrecords.uoregon.edu/correspondence-73).

| Building | 2013–15 median error | DOGAMI median error |
| --- | ---: | ---: |
| Sigma Nu | 0.9682 → 0.6853 m | 0.7623 → 0.1792 m |
| 1306 East 18th | 1.4965 → 0.2970 m | 1.5781 → 0.1501 m |
| 1874 Emerald | 1.3887 → 0.5740 m | 1.4399 → 0.2250 m |

The model roofs hit all 2,239 rays in those two grids. The comparisons use 2,043 paired cells. The 2017 USACE surface contributes one cell at Sigma Nu with a 43.90 m model residual. It is excluded from the paired grid summary.

Ten matched views cover the main elevations, entries, rear features and roofs. Exact removal of 692 source triangles preserves the attributes and index order of 54 batch peers. The exporter checked 7,710 route edges with a minimum clearance of 11.5762 m. On desktop and phone the three original IDs are selectable by their registered names, 13 collision probes pass and the routes from Knight Library reach the three approaches in 175, 175 and 200 points. Failed GLB integrity and an invalid source anchor independently restore all three original models and their generic approaches.

Staged, repeated, installed, built and served bytes match. Formatting, 197 unit tests, seven related browser cases, production build, inventory structure, 397 archived files and 340 viewer hashes passed. This revision is local and uncommitted. [Editable source and dated references](../data/metadata/south-university-exterior-review.json) · [Exporter](../scripts/build-south-university-exterior-review.py).
