# Eleven exteriors around Emerald and Onyx

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `roof-9752966f` | 170729 | 1975–1981 Onyx. Yellow west frontage, projecting roof sections and an estimated north-door approach. |
| `onyx-1959-west` | 216805 | 1959 Onyx west building. Separate low wing and hipped main roof, with the screened street frontage approximated. |
| `roof-b1caff97` | 149485 | 1314 East 21st. Broad intersecting roofs, north garage wing and a narrow terrain apron under the south extension. |
| `roof-b7484145` | 171144 | 1959 Onyx alley building. Upper row of windows, three closed garage doors and an exterior stair at the south end of the alley face. |
| `emerald-alley-1946` | 216803 | 1946 Emerald Alley. Separate blue-gray lap-sided volume and low projecting canopy. |
| `emerald-alley-1940` | 216804 | 1940 Emerald Alley. New independent two-story exterior with offset gables and an upper alley-side balcony. |
| `roof-b36b0ddb` | 170768 | 1361 East 21st. Shallow gabled porch with a railing, east-side steps and an open area between posts. |
| `roof-c0e5df84` | 170774 | 2072 Emerald. Low west wing and distinct east garage and porch, with an estimated street approach. |
| `roof-90b1b81e` | 170761 | 1407 East 21st / 2087 Emerald. One stepped building with three west garage doors and upper window groups. |
| `roof-4ad5629d` | 170733 | 1405 East 20th. White two-story house seen clearly from the south, with grouped windows, red door, covered porch and chimney. |
| `east20-1425` | 170734 | 1425 East 20th. Independent low blue street frontage with a recessed door and higher rear roof. |

The two 1959 Onyx roofs are 14.908 m apart and use the same municipal address. The western roof is 0.422 m from 1975–1981 Onyx. The alley building is 1.356 m from 1946 Emerald Alley, which is 1.078 m from 1940 Emerald Alley. The earlier model overlaps 4.980 m² of 1940's 152.378 m² footprint. The city outlines at 1405 and 1425 East 20th leave a 0.936 m gap. The package uses county aerials dated 2017, 2021 and 2025 and 27 registered street and alley views. View bearings and materials for concealed facades remain estimates. [City footprints](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [County aerial service](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Editable parameters and evidence](../data/metadata/emerald-onyx-frontages-review.json).

The surveyed terrain and elevation sample grids stop at northing −1,000 m. The south end of 1314 East 21st continues another 8.69 m. Its roof and rear outline follow the aerials. An apron extrapolates the terrain edge beneath the building for visual continuity. A ray at `[-166.8, -1010]` hits that apron at 11.5413 m. The viewer's walking boundary stays at the surveyed edge.

| Model | 2013–15 paired median error | DOGAMI paired median error |
| --- | ---: | ---: |
| 1975–1981 Onyx | 1.0262 → 0.6676 m | 0.8991 → 0.5015 m |
| 1959 Onyx west | 1.1700 → 0.4882 m | 1.0457 → 0.9873 m |
| 1314 East 21st | 1.1931 → 0.6499 m | 1.0033 → 0.6765 m |
| 1959 Onyx alley | 1.3807 → 0.2636 m | 1.1550 → 1.0688 m |
| 1946 Emerald Alley | 1.2642 → 0.4192 m | 1.4635 → 0.3223 m |
| 1940 Emerald Alley | 3.1679 → 1.0324 m | 2.2389 → 3.2736 m |
| 1361 East 21st | 1.0499 → 0.3056 m | 1.2230 → 0.3028 m |
| 2072 Emerald | 0.5899 → 0.5354 m | 0.5346 → 0.3425 m |
| 1407 East 21st / 2087 Emerald | 0.9520 → 0.4236 m | 1.6728 → 0.5123 m |
| 1405 East 20th | 1.7455 → 0.5448 m | 1.7690 → 0.1613 m |
| 1425 East 20th | 1.5510 → 1.0855 m | 1.6619 → 0.4399 m |

Both useful surfaces hit all 2,768 samples. The 1,892 paired cells show improvement in 21 of 22 medians. At 1940 Emerald Alley, the earlier mesh covers only two grid cells per surface. Full new-surface median errors across 126 cells per surface are 0.5107 m and 0.2876 m. The 2017 USACE grid returned one isolated value of 113.0754 m at the 1959 Onyx alley building, around 97.7 m above the modeled roof at that point. The recorded result excludes that value from the paired summary.

Eighteen matched views and exact index and vertex-attribute comparisons confirm the replacement of 1,799 triangles and preserve 50 batch peers. The exporter checked 7,710 route edges. Desktop and phone select all eleven buildings, resolve both 1959 Onyx results, and pass 26 collision probes and 16 approach probes. Routes from Knight Library to 1975–1981 Onyx, 1405 and 1425 East 20th, and 2072 Emerald have 199, 228, 230 and 239 points respectively. A damaged GLB and an invalid last source anchor each restore all seven older shapes and their approaches, with 1940 Emerald Alley absent in both fallback cases. Staged, repeated, installed, built and served bytes match. The package remains local and uncommitted. [Exporter](../scripts/build-emerald-onyx-frontages-review.py).
