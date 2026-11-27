# Franklin Boulevard and Riverfront parking exterior review

| Model | Evidence and features |
| --- | --- |
| 959 Franklin, City 219112 | The municipal outline measures 3,052.59 m². June 2024 street panoramas place the western cornice around 39–40 m and the podium around 10–11 m above the scene datum. The model has a four-level garage and glazed base, facade bands, a stepped east side and a roof deck. The pool and spa are separate water surfaces. |
| Hayward Inn, Franklin Building, City 170533 | The northern wing follows the roof visible in 2025. The east side has two balcony levels and an arcade over partly open parking. The old southern roof is over an exposed lot. Its paved surface and stall markings are included in the site export. |
| Best Western New Oregon, Court and Lobby, City 224680 | An open courtyard, stepped lobby and hipped vehicle canopy replace the older solid outline. Two previously refined front roofs remain independently selectable. |
| Best Western New Oregon, West Wing, City 226752 | The 1,351.67 m² outline follows the gabled wing around an open court. The canopy belongs to the lobby model. A smaller municipal polygon, City 226753, remains under observation because the aerial imagery does not show a separate roof there. |
| Riverfront lot west of 959 Franklin | The 2017, 2021 and 2025 orthophotos show pavement or vegetation over the large legacy footprint and over the separate 80.66 m² City polygon 220801. The old building range is retired, and the site export restores paving and stall markings along the southern frontage. |

The roof and canopy elevations, door dimensions, facade bays and pavement markings are estimates. The source inputs document outline and photo alignment. The exported meshes and materials are original. [959 Franklin landscape architect](https://www.satregroup.com/project/959-franklin/) · [959 Franklin operator](https://www.americancampus.com/student-apartments/or/eugene/959-franklin/) · [City corridor report](https://www.eugene-or.gov/DocumentCenter/View/71081/Franklin-Corridor-Report-2023) · [Hayward Inn photos](https://haywardinneugene.com/hotel-rooms-hayward-inn/) · [Best Western property overview](https://www.bestwestern.com/en-us/book/hotel/eugene/best-western-new-oregon/38013).

Two byte-identical exports and ten paired views verify removal of five ranges totaling 2,276 triangles. The remaining 44 members and position buffers in the two source batches are preserved. Collision probes verified the garage mouth, the hotel arcade and the vehicle canopy at approximately 2.72 m, 2.84 m and 2.78 m of modeled clearance, respectively. Four solid probes and five clear probes passed on desktop and phone. A 7,710-edge graph screen found a minimum separation of 4.2748 m from the modeled solid footprints. Knight Library routes reached 959 Franklin and the Best Western lobby in 134 and 171 points. Corrupt asset and shifted-anchor tests both restored all five original ranges.

The local viewer has 610 selectable sites, seven retained batch buildings, two isolated roof treatments and 461 entrance records. The build, formatting, 197 unit tests, seven browser cases and 455 asset archive checks passed. The public checkpoint is c3dc42c.

- [Editable model input](../data/metadata/franklin-riverfront-closeout-review.json)
- [Deterministic exporter](../scripts/build-franklin-riverfront-closeout-review.py)
- [Runtime site descriptor](../apps/web-preview/public/scene/franklin-riverfront-closeout-review/site.json)
