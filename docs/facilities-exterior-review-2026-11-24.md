# North campus facilities and Romania exteriors

The local preview registers five campus exterior assets with their original selection IDs. The editable source records the UO plan, sampled roof sections, material and opening parameters, and modeled entrances. It pins the 2024 orthophotos, the roof evidence array and applicable documents. [Editable registration](../data/metadata/facilities-exterior-review.json) · [Builder](../scripts/build-facilities-exterior-review.py) · [Scene descriptor](../apps/web-preview/public/scene/facilities-exterior-review/site.json).

| Campus building and scene ID | Reconstructed exterior | Details still estimated |
| --- | --- | --- |
| CPFM Warehouse and Shops B0130, `roof-2975e487` | Broad long-axis ridge, south projection, dark roof strips seen in aerial imagery and a rhythm of loading bays. | Bay widths, door counts, finish and changes related to the 2026 work. |
| Facilities Services Miscellaneous Quonset B0131, `roof-3b3ed882` | L-shaped plan with a corrugated arch over the main volume and a low western wing. | Minor doors, finish and parts of the north edge near vegetation. |
| Facilities Services Recycling Quonset B0134, `roof-4c8ea72b` | Rounded metal roof and modeled end bays. | The two elevation grids put the arch crest about a meter apart. The roof follows the common aerial and elevation pattern. Current opening dimensions remain approximate. |
| CPFM Administration B0136, `roof-b5543048` | Refurbished Quonset with a long curved roof, lower north entrance, low side projections and modeled office windows. | Roof edge and exact entry placement and openings. |
| Romania Warehouse and Showroom B0180, `roof-0151b728` | Oval north pavilion with east and west roof tips, a 2.12 m modeled overhang, upper curtain wall above boarded lower panels, west steps and tiered warehouse roofs with blue garage doors. | Individual openings, current finishes, accessible ramp geometry and local warehouse roof junctions. The scene represents the documented existing building before the proposed redevelopment. |

UO's campus map establishes identity and plan. The 2019 warehouse plan locates the south projection. The architecture exhibit identifies the Administration building as a refurbished Quonset. The recent notice establishes work at the warehouse whose effects on the exterior remain unverified. [Campus map](https://map.uoregon.edu/) · [Warehouse plan](https://bpb-us-e1.wpmucdn.com/blogs.uoregon.edu/dist/2/14032/files/2019/11/Building-130-Construction-Project.pdf) · [Administration Quonset](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/campus-operations-office) · [October 2026 warehouse work](https://news.uoregon.edu/content/heat-will-be-cpfm-warehouse-during-project).

Pages 11–13 of the Romania assessment show the north pavilion, boarded glazing and warehouse doors in exterior photographs. The north-side plan and roof history establish the overhang and east–west roof rise. The capital plan discusses redevelopment and preservation of the showroom. The scene uses original geometry and colors. [2025 historic assessment](https://cpfm.uoregon.edu/sites/default/files/2025-07/romania_preliminary-hp-assessment_2025_.pdf) · [2025 capital plan](https://cpfm.uoregon.edu/sites/default/files/2026-01/2025-capital-plan-booklet-1.pdf).

## Integration and verification

Five spans totaling 2,070 triangles are replaced across three source batches. The source-range audit compares all surviving indices and vertex attributes before the separate roof recipe runs.

| Source batch | Original triangle spans, end exclusive |
| --- | --- |
| `context-campus-1-2` | 732–1172 |
| `context-background-1-2` | 0–220, 358–520, 676–850 |
| `context-background-3-1` | 0–1074 |

The full exterior packages install first using pinned source triangles. The context roof recipe then fits the remaining source ranges. A successful facilities package supersedes the earlier Recycling Quonset roof and leaves the other 30 roof records active. The earlier 31 roofs are available again if the facilities mesh, terrain pin or a late batch anchor fails validation.

Across 13 paired camera positions, the models were inspected from ground level and above. All 13,700 selected historic roof probes intersected the replacements. Median absolute differences against the sampled data used to fit the sections are 0.08–0.28 m across the buildings and dates. The Romania 90th percentile reaches 1.26 m, including roof transition zones.

The route audit covered 7,710 edges. Desktop and mobile production tests checked six modeled approaches, fourteen collision probes and the five search identities. The production, repeated and stage model files match byte for byte. The default scene has 515 selectable buildings, 428 source batch members, 139 road segments and 550 trees. The local outdoor ledger has 89 L2 entries, 439 independent L1 entries and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).
