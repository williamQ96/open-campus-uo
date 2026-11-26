# Trinity House and seven Onyx-area exteriors

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `roof-14401667` | 171143 | Trinity House, 1987 University. Brick west face, name panel, intersecting roof heights and lower east wing. |
| `east20-1256` | 129707 | 1256 East 20th. An independent gabled house with lower roof sections and a north window bay. |
| `roof-e01f1a78` | 129708 | 1276 East 20th / 2008 Onyx. One municipal outline for both addresses, with a hip, shallow dormer, lower connecting roof and north wood fence. |
| `roof-a1c68f4b` | 129642 | 1237 East 21st. Stepped roof, recessed porch, upper south windows, west drive and stone retaining bank. |
| `roof-df1012d3` | 214547 | 2066 University. Steep main roof, shallow south section, east drive and square canopy columns. |
| `roof-bece0173` | 129705 | 1136 East 20th. Blue north frontage with two projecting upper windows, gables and an estimated stair approach. |
| `east19-1262` | 171130 | 1262 East 19th. Stacked arched door and upper opening with a small balcony. The stairs interrupt the retaining bank. |
| `roof-96f32dee` | 171132 | 1931 Onyx Alley. Upper story spans an open west parking level. The rear wall and three columns have ground collision. |

The city outline pairs leave separate roof gaps of 2.182 m on East 20th and 2.235 m between East 19th and Onyx Alley. The old mesh IDs stay with the two larger overlaps. City footprints, parcel and address points, aerials from 2017, 2021 and 2025, and 16 street and alley views from November 2020 and July 2024 anchor the review. The mesh uses original materials and geometry. Rear openings under tree cover, the precise parking column spacing and height, and the heights of both estimated approaches remain approximate. A pedestrian approach is assigned at 1136 East 20th and 1262 East 19th. At 1237 East 21st the visible recessed doorway and the retaining wall are modeled, and the street connection remains unverified. [City outlines](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Trinity House address](https://fbceugene.com/wp-content/uploads/TRINITY-Handbook-26-27-.docx-1.pdf) · [Editable dimensions and evidence](../data/metadata/onyx-university-frontages-review.json).

| Model | 2013–15 paired median error | DOGAMI paired median error |
| --- | ---: | ---: |
| Trinity House | 1.7143 → 0.4443 m | 1.4969 → 0.1805 m |
| 1256 East 20th | 1.3922 → 0.5846 m | 0.9880 → 0.2057 m |
| 1276 East 20th / 2008 Onyx | 0.9372 → 0.6344 m | 0.5700 → 0.4622 m |
| 1237 East 21st | 0.8995 → 0.2016 m | 1.0999 → 0.2991 m |
| 2066 University | 1.5197 → 0.8797 m | 1.3992 → 0.2364 m |
| 1136 East 20th | 1.3084 → 0.6847 m | 1.1953 → 0.1532 m |
| 1262 East 19th | 1.2613 → 0.1444 m | 1.1094 → 0.0386 m |
| 1931 Onyx Alley | 1.1755 → 0.2747 m | 0.7777 → 0.5135 m |

Both useful surveys hit all 2,866 samples, including 2,016 cells also covered by the old roofs. The 2017 USACE grid has no samples at these outlines. The review compares 16 matched views and removes 1,511 source triangles. Vertex attributes and retained indices agree exactly for all 51 surviving batch members. The exporter checks 7,710 route edges with minimum clearance 3.0229 m.

Desktop and phone production select all eight models and find 2008 Onyx under its alternate address. Both viewers pass 20 collision probes including the two connectors removed from the source shapes, three open parking samples, three parking columns and the rear wall. Eight approach probes pass. The routes from Knight Library to 1136 East 20th and 1262 East 19th contain 171 and 178 points respectively. Damaged GLB bytes and an invalid final source anchor each restore the six source meshes and original entrance estimates, including the two old connectors and the solid parking footprint. Staged, repeated, installed, built and served asset bytes match. The package remains local and uncommitted. [Exporter](../scripts/build-onyx-university-frontages-review.py).
