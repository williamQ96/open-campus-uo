# Eight exteriors around Agate and Emerald

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `roof-a40877e3` | 149611 | The Studies at 19th, 1370 East 19th. One continuous building with three gabled north bays, two roof courts, open west-side parking and an estimated north stair. |
| `roof-a7890474` | 170742 | Tom's Market, 1490 East 19th. Low pitched roof, east covered entrance, glazed storefront, open canopy and blue wall finish as seen in July 2024. |
| `roof-aba1513b` | 170751 | 1442 East 20th. Low north frontage, narrow central roof and taller rear gable. |
| `roof-28502c01` | 170753 | 1460 East 20th. Low side roof, small projecting north gable, red door and estimated approach. |
| `east20-1470` | 170752 | 1470 East 20th. Separate roof with north dormer, recessed porch and lower garage wing. |
| `roof-06636962` | 214549 | 1473 East 20th. Two-story south-facing wall, shallow roof and deep eaves, rear wing and east drive. |
| `roof-58d0ebc7` | 170759 | 1495 East 21st / 2092 Agate. One stepped roof with a projecting upstairs bay over the south garage. |
| `roof-5a32e480` | 149481 | 1370 East 21st. Pale stepped frontage, projecting north canopy and a small apron beneath the south extent. |

The Studies city outline covers 1,761.513 m². The former east and west fragments intersect 155.695 m² and 124.917 m² of that outline respectively. The unified model keeps the east ID and records the former west ID `roof-879f17f5` as a historical mapping. Its open courts measure 108.69 m² and 144.28 m² in the city registration. Roof rays pass through both centers to modeled paving at 10.472 m. Three horizontal parking rays traverse open space to the rear wall, and vertical rays hit the soffit at 12.790 m. The nine columns and rear wall have collision. The north stair and courtyard surface heights are estimates. [City footprint service](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer).

The paired East 20th roofs have a 1.929 m gap. The 1370 East 21st outline extends 0.84 m beyond the local survey edge, and the apron follows terrain height at the edge. The viewer's walking bounds still end at the survey edge. Tom's Market represents the 2024 photographed period. The package uses original geometry and flat blue wall color, with the mural artwork pending a reusable source. Tree cover limits parts of 1442 and 1473 East 20th. [2024 Oregon storefront register](https://www.oregon.gov/dor/programs/businesses/Documents/7-10-24_Tobacco%20Retailers%20Currently%20Licensed%20by%20the%20State%20of%20Oregon.pdf#page=104) · [The Studies address listing](https://www.apartments.com/the-studies-at-19th-eugene-or/gps9lty/) · [Editable dimensions and public evidence](../data/metadata/agate-emerald-frontages-review.json).

| Model | 2013–15 paired median error | DOGAMI paired median error |
| --- | ---: | ---: |
| The Studies at 19th | 6.1512 → 0.5588 m | 6.6454 → 0.3007 m |
| Tom's Market | 0.8041 → 0.4353 m | 0.8989 → 0.4750 m |
| 1442 East 20th | 0.9992 → 0.6982 m | 1.4924 → 0.6664 m |
| 1460 East 20th | 0.7050 → 0.4124 m | 0.5258 → 0.2897 m |
| 1470 East 20th | 1.4662 → 0.5150 m | 1.6720 → 0.5277 m |
| 1473 East 20th | 1.6460 → 0.7034 m | 1.2756 → 0.4604 m |
| 1495 East 21st / 2092 Agate | 1.0497 → 0.6550 m | 0.7906 → 0.3428 m |
| 1370 East 21st | 1.4390 → 0.4624 m | 1.2128 → 0.2520 m |

The two useful surveys hit all 5,194 roof samples, including 2,150 paired with the old roofs. The 2017 USACE grid supplied no samples at these outlines. Sixteen matched views and exact vertex attribute and index comparisons preserve 84 peers in two batches, with 1,618 source triangles removed. The exporter checks 7,710 route edges with a minimum clearance of 2.4641 m. Thirty-one modeled stair surface samples show contiguous treads with a largest observed height step of 0.153 m.

Desktop and phone production select all eight buildings, find the alternate 2092 Agate address, and pass 25 collision and 20 approach probes. Routes from Knight Library to The Studies, Tom's Market, 1460 East 20th, 1470 East 20th and 1370 East 21st contain 203, 233, 239, 240 and 239 points respectively. Damaged model bytes and an invalid last source anchor restore both old apartment fragments, the earlier combined East 20th volume and all eight legacy gates. Stage, repeat, installed, built and served model bytes agree. The package is local and uncommitted. [Exporter](../scripts/build-agate-emerald-frontages-review.py).
