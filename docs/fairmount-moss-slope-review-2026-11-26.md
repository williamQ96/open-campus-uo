# Eleven hillside exteriors around Fairmount, Moss and McMorran

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `roof-b8fa3497` | 170488 | 1864 Moss Street. Low hipped shell, east entry roof and west alley windows. |
| `roof-6a4f93e6` | 170619 | 1926 Moss Street. Broad pale gable, lower garage and leveled approach apron. |
| `roof-100b2613` | 171181 | 1911 Moss Street and 1820 East 19th Avenue. One joined roof outline, with a lower east wing and a recessed wooden porch with a red side door. |
| `roof-136be56b` | 160495 | 2303 McMorran Avenue. Western shingled gable, triple window, eastern garage and a roofed connector open between the posts. |
| `roof-f6bcefaf` | 171179 | 2288 Fairmount Boulevard. High pale street gable, shutters, smaller gable and stepped porch. |
| `roof-5245ef5e` | 159886 | 2309 Fairmount Boulevard. Intersecting roof wings and pale painted siding, with partly estimated openings on the screened frontage. |
| `roof-daca02ed` | 159887 | 2323 Fairmount Boulevard. Tall pale downhill elevation, long raised balcony and lower rear wing. |
| `roof-d5a8b80c` | 181068 | 2275 Fairmount Boulevard. Intersecting roof masses and south garden apron, with estimates behind the tree cover. |
| `roof-b62a90ef` | 160492 | 2415 Fairmount Boulevard. Upper window band and deck, lower landing and stair, and an oval pool terrace. |
| `east19-1836` | 171180 | 1836 East 19th Avenue. Previously missing shingled exterior with a projecting red-trimmed north gable and estimated porch details. |
| `fairmount-2241` | 159884 | 2241 Fairmount Boulevard. Previously missing pale exterior with sharp front gable, dormer, doorway canopy and arched front glazing. |

The City outlines at 1836 East 19th and 2241 Fairmount have zero positive-area overlap with the earlier scene. They sit 2.9798 m from the 1911 Moss roof and 6.6745 m from the 2275 Fairmount roof. Both now have independent IDs. Both municipal addresses at 1911 Moss lie inside City outline 171181. The 2024 market photo establishes the timber surround and the recessed red door. The model keeps one exterior and leaves the address-specific doors unassigned. The photo for 2241 establishes the façade shape and window details. Its capture date is unknown. [City footprint service](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [1911 Moss listing photograph](https://photos.zillowstatic.com/fp/50af6f6c533b713a45a28b585ea8befd-uncropped_scaled_within_1536_1152.webp) · [2241 Fairmount listing photograph](https://photos.zillowstatic.com/fp/def2759e907c265478f134079e706d3f-uncropped_scaled_within_1536_1152.webp).

The 2024 southeast street bearing and 2026 agent photo both show the 2303 McMorran link between the main building and garage. It has two occupied ground footprints and three modeled support posts. At 2415, the oval pool in the county aerial establishes the pool-facing orientation for the two decks and exterior stair. Deck heights and the local grade are approximate. Part of the main roof extends 4.08 m south of the terrain edge. A short apron uses the last sampled ground line. The separate 63.4549 m² City roof on the 2415 parcel lies fully beyond that edge. Only 0.3604 m² of neighboring 2425 Fairmount falls inside the terrain. Both have zero roof grid hits and remain research candidates. The small 219453 roof next to 2309 has a separate unresolved identity. The 2024 estate images supply local material and patio evidence, and the 2309 and 2275 screened elevations retain inferred openings. Geometry, finishes and the pool are original work. [2303 agent listing](https://www.windermere.com/listing/OR/Eugene/2303-McMorran-Ave-97403/227246563) · [2415 agent listing](https://www.windermere.com/listing/OR/Eugene/2415-Fairmount-Blvd-97403/226963650) · [2309 event photos](https://estatesales.org/estate-sales/or/eugene/97403/estate-sale-by-pam-2312705/gallery) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Editable dimensions and source locations](../data/metadata/fairmount-moss-slope-review.json).

| Model | 2013–15 paired median error (m) | DOGAMI paired median error (m) |
| --- | ---: | ---: |
| 1864 Moss | 1.2253 → 0.5625 | 1.0947 → 0.6132 |
| 1926 Moss | 1.0098 → 0.9844 | 0.8352 → 0.7255 |
| 1911 Moss | 0.7705 → 0.6164 | 0.6867 → 0.2004 |
| 2303 McMorran | 0.9339 → 0.4240 | 1.0822 → 0.8802 |
| 2288 Fairmount | 1.0530 → 0.7770 | 0.6443 → 0.6025 |
| 2309 Fairmount | 1.0665 → 0.6391 | 1.0253 → 0.3508 |
| 2323 Fairmount | 0.8509 → 0.9369 | 0.7987 → 0.6862 |
| 2275 Fairmount | 1.3740 → 1.2159 | 1.3632 → 1.2565 |
| 2415 Fairmount | 0.7729 → 0.6256 | 0.8463 → 0.4379 |

The eleven roofs intersect all 5,245 usable cells. Nineteen of twenty medians decrease across 3,427 paired cells. The 2017 medians at 1864 and 1911 Moss decrease from 0.9526 m to 0.5675 m and 0.8797 m to 0.1781 m. The only 2017 sample at 2309 Fairmount is 175.0737 m above the scene origin, more than 147 m above the 27.8483 m roof intersection at that point. That record is kept in the raw audit and excluded from the usable statistics. At 1836 East 19th the unpaired medians are 0.5818, 0.7536 and 0.6086 m for 2013–15, DOGAMI and 2017. At 2241 Fairmount the two usable unpaired medians are 1.0049 and 0.8388 m.

Seventeen matched render pairs and exact index and attribute checks preserve 26 unmodified peers from the same batch. The package removes 2,258 original source triangles. One connector ray traverses the whole opening and the other reaches the far wall. The bottom ray reaches the underside at 28.7300 m. The 1911 porch rays hit the recessed wall and roof underside. The pool ray reaches the modeled water at 28.5900 m. The exporter checks 7,710 graph edges with at least 2.5051 m of clearance.

Desktop and phone select all eleven buildings and find 1911 Moss when searching for its second address. Both pass 30 collision probes and eight clearance probes. Directions from Knight Library reach the two estimated street approaches at 1864 Moss and 2288 Fairmount in 277 and 299 points. An invalid model and an invalid final source anchor both restore the nine old approaches, old collision and previous building counts. Both new IDs disappear on fallback. The staged, repeated, installed, built and served bytes agree. The package is local and uncommitted. [Exporter](../scripts/build-fairmount-moss-slope-review.py).
