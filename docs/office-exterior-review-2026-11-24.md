# Annex, Rainier and three office exteriors

The local preview uses five new exterior models with their original selection IDs and university names. The editable file records plan registration, roof planes, window treatments, modeled exterior approaches, and source hashes. [Editable registration](../data/metadata/office-exterior-review.json) · [Builder](../scripts/build-office-exterior-review.py) · [Scene descriptor](../apps/web-preview/public/scene/office-exterior-review/site.json).

| Campus building and scene ID | Reconstructed features | Details estimated |
| --- | --- | --- |
| UO Annex B0082, `roof-17c233f0` | Two-story volume under a hipped roof, roof projections, and the north approach. | Frame profiles, materials and exact door position. |
| Rainier Building B0090, `roof-b8f94f8e` | Rotated rectangular envelope, inclined roof facets, and an elongated raised roof housing. | Function of the housing, details of its side panels, window spacing and position of the modeled south approach. |
| 1311 Franklin B0115, `roof-3c2b8bdc` | Low two-plane roof, pale roofing strips and paneled walls with a modeled south approach. | Finish, door position and details of the roof strips. |
| University Business Operations Center B0705, `roof-7c1c7fb1` | East 13th Avenue gable, projecting arched glazing, rectangular upper windows, green ground-floor glazing and lower rear roof. | Exact arch shape and opening dimensions, the rear wall, and finishes away from the photographed side. |
| 1715 Franklin B0726, `roof-bb20ea46` | Stepped north wing with a higher sloped roof around its lower deck, lower southern wings, open court, and east and court approaches. | Material palette, local roof transitions, exact door dimensions and court grade. |

UO's building inventory and campus map establish the identities. The Annex worksite outline and aerial support the main rectangle. The Rainier public address and alley directions confirm its street context. The aerial and historical returns constrain the two roof sizes and the location of the central raised volume. [UO inventory](https://cpfm.uoregon.edu/sites/default/files/uo_building_inventory_202102.pdf) · [Campus map](https://map.uoregon.edu/) · [Annex plan](https://gtff3544.net/steward-resources/worksite-maps/) · [Rainier directions](https://is.uoregon.edu/nts/contactus).

The UO Calendar photo of the former Thompson University Center shows the photographed north facade and the arch. The current Business Affairs page uses University Business Operations Center. The public 1715 Franklin outline confirms the open court and an east entrance. The models use original geometry and vertex colors. [UO facade photo](https://calendar.uoregon.edu/thompsons_university_center) · [Business Affairs](https://ba.uoregon.edu/) · [1715 Franklin plan](https://bpb-us-e1.wpmucdn.com/blogs.uoregon.edu/dist/2/14032/files/2022/11/1715.pdf).

## Integration and verification

The five pinned source spans remove 2,882 triangles. The comparison without roof recipes verified the surviving vertex attributes and index order in each affected batch. The layout tracks appended geometry so the office review works while the earlier Alder facade is active. A successful office package supersedes the 1311 Franklin roof recipe. The default scene has 29 earlier roof records and a fallback restores 30.

Reviewed 12 before-and-after camera pairs and tested the arch face and adjacent wall with separate rays. All 7,348 selected historical roof probes intersected the models. The 2017 median absolute roof differences were 0.17–0.32 m. The 2013–15 differences reached 0.80 m at the Annex and 1.11 m at the Business Operations Center, where the roof responses shift horizontally between acquisitions. The 2024 orthophoto and the more closely aligned 2017 grid guided their placement. At 1715 Franklin, the 2017 90th percentile is 1.59 m around the mixed roof. The elevation comparisons use the source grids that informed the model.

The route audit covered 7,710 edges. The production package is byte-identical to the draft and independent rebuild. Desktop and mobile checks cover six walkable modeled approaches, twelve collision probes, search by the five university names, and rollback for invalid mesh bytes, mismatched terrain and a late batch-anchor failure. The scene retains 515 selectable buildings with 423 source batch members, 139 road segments and 550 trees. The outdoor ledger has 94 L2 entries, 434 independent L1 entries and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).
