# Eight Potter and University-area exteriors

| Scene ID | City outline | Model |
| --- | ---: | --- |
| `roof-c82780ef` | 171056 | **Central Lutheran Church**, 1857 Potter. The high sanctuary, brick plinth, wood screen, cross and inset colored glazing meet the lower wings. The two old source ranges become one connected building with an open central court and a covered east entry. |
| `roof-77b9b163` | 171061 | **1081–1083 East 19th**, two levels with horizontal siding, a band between the stories and the south entry projection. |
| `roof-09fb4f67` | 171062 | **1085–1089 East 19th**, lower intersecting hips, blue siding and yellow east doors. |
| `roof-b6ce8f92` | 171111 | **1136 East 19th**, two roof dormers, the north porch, steps and the interrupted street retaining wall. |
| `roof-b74469f2` | 171112 | **1910 University**, tall corner wing with east-facing dormers, pale chimney and an enclosed windowed frontage. |
| `university-1940` | 171117 | **1940 University**, low transverse roofs and side wing, porch and street steps. |
| `university-1960` | 171118 | **1960 University**, intersecting main roofs, lower rear wing and east steps. |
| `university-1976` | 171120 | **1976 University**, hip roof with a separate east gable and steps. |

The church keeps the primary source ID and absorbs `roof-7b05979c`. The municipal outline contains the 66.9 m² courtyard opening, which is preserved in rendering and collision. The four University Street houses occupy separate lots. Their adjacent roof gaps are 3.004, 0.894 and 2.327 m. Frontage colors, visible profiles and street steps use the dated imagery. Landscaped and obscured openings, courtyard planting and entrance elevations are approximate. Secondary City outline 216796 at 1136 East 19th remains a separate research item. [Church address](https://www.connecttocentral.org/) · [East entry reference](https://www.connecttocentral.org/about-6) · [City architectural survey](https://www.eugene-or.gov/DocumentCenter/View/24803/Eugene-Modernism-1935-65) · [Editable data and source links](../data/metadata/potter-university-exterior-review.json).

| Model | 2013–15 paired median roof error | DOGAMI paired median roof error |
| --- | ---: | ---: |
| Central Lutheran Church | 1.4213 → 0.2406 m | 1.3998 → 0.2031 m |
| 1081–1083 East 19th | 1.3345 → 0.6757 m | 1.2054 → 0.2844 m |
| 1085–1089 East 19th | 1.0482 → 0.9787 m | 1.1311 → 0.2802 m |
| 1136 East 19th | 1.1387 → 0.6211 m | 0.8912 → 0.5520 m |
| 1910 University | 2.1067 → 0.7700 m | 2.0677 → 0.4305 m |
| 1940 University | 1.9933 → 0.5574 m | 1.8231 → 0.2127 m |
| 1960 University | 0.9950 → 0.3373 m | 0.9007 → 0.4344 m |
| 1976 University | 1.6217 → 0.9521 m | 1.7385 → 0.4692 m |

The two useful height grids supplied 6,751 roof hits and 5,417 paired samples. The 2017 USACE grid supplied one unpaired cell at the church. Fifteen matched views cover the courtyard, both church fronts and the four independent University houses. The exporter removes 2,534 triangles, preserves the index order and vertex attributes of 51 source peers and checks 7,710 route edges with 7.1629 m minimum clearance.

Desktop and phone find and select all eight buildings. Both pass the courtyard and all three gap probes within 19 scene collision probes, plus 36 clearance probes across nine estimated approaches. Routes from Knight Library reach all eight building destinations in 127, 142, 141, 152, 166, 175, 177 and 180 points in table order. Damaged GLB bytes and an invalid last source anchor each restore all six legacy shapes and estimated approaches. Stage, repeat, installed, built and served asset bytes match. The package is local and uncommitted. [Exporter](../scripts/build-potter-university-exterior-review.py).
