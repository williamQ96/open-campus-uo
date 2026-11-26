# Five campus building exteriors

The local preview uses five new exterior models. The existing scene IDs are retained and four previously unnamed exterior entries now use the university's building names. The editable registration contains footprints, roof planes, facade segments and six exterior approaches. [Registration](../data/metadata/campus-frontage-review.json) · [Builder](../scripts/build-campus-frontage-review.py) · [Scene descriptor](../apps/web-preview/public/scene/campus-frontage-review/site.json).

The plans align campus outlines with Oregon's 2024 orthophoto and use dated elevation samples where they cover the visible roof. Those samples predate the Health Services expansion. Source photographs informed the exterior geometry and colors. The scene uses original meshes and materials. [UO campus map](https://map.uoregon.edu/) · [Oregon orthophoto service](https://imagery.oregonexplorer.info/arcgis/rest/services/) · [DOGAMI lidar catalog](https://www.oregongeology.org/lidar/).

| Campus building and scene ID | Adopted exterior | Remaining uncertainties |
| --- | --- | --- |
| University Health Services B0014, `roof-29dae856` | Three-story brick west addition, lower east and south roofs, two open courtyards, and west and north approaches. | West roof height is estimated from completed views. Window spacing and entry thresholds are approximate. |
| Central Power Station B0032, `roof-2518e2a2` | Main volume with five roof zones, light upper block, darker window bays and a separate low north annex. | The relationship between the photographed facade and east view is inferred. Openings and rooftop boxes are simplified. |
| Riley Hall B0086, `roof-5fd54bd8` | Lower brick, light precast bands, sunken open courtyard, small raised roof volume and east approach. | The courtyard grade, bands and minor openings are approximate. About 15 m of the west envelope lies outside the walkable scene. |
| Student Tennis Center B0139, `roof-a55aea46` | Two parallel roof ridges, shallow roof planes and the west approach. | The wall panel treatment and exact entry position are estimated. |
| Alder Building B0200, `roof-ee63827c` | T-shaped roof, six light porch columns, open passage behind them, semicircular door surround, and oval windows. | Column and trim profiles, side openings and exact door proportions are approximate. |

The Health Services addition is documented in the university survey, architect's project record and completed exterior photograph. [2025 UO survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/univhealthcenter_2025.pdf) · [Architect's record](https://www.ckarch.com/projects/uo-student-health-center/) · [Completed exterior](https://health.uoregon.edu/sites/default/files/home-update-sept2021.jpg).

The power plant records document the visible side wall and roof volumes. The outlines and aerial place the low annex and distinguish the neighboring chiller and switch house. [2013 exterior, Visitor7, CC BY-SA 3.0](https://commons.wikimedia.org/wiki/File:Central_Power_Station.jpg) · [2026 exterior photograph, KLCC](https://www.klcc.org/environment/2026-06-29/university-oregon-sets-aside-15-million-student-building-fees-replace-natural-gas-boiler).

The Riley survey shows the court on page 4 and provides a facade photograph. The tennis facility's construction record and the 2013–15 roof returns locate both ridges. Alder's entry photograph shows the columns and window shapes. [Riley survey](https://cpfm.uoregon.edu/sites/default/files/2025-04/rileyhall_2025.pdf) · [Tennis construction record](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/student-tennis-center) · [Athletics facility record](https://goducks.com/facilities/student-tennis-center/31) · [Alder architectural record](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/alder-building) · [Alder entry](https://humanities.uoregon.edu/creative-writing/graduate-program).

## Scene integration

The loader checks the presentation, base model, terrain and new exterior hashes and verifies original triangle anchors. On successful installation it replaces the following ranges, expressed in the original triangle order with an exclusive end.

| Building | Source batch | Range | Triangles |
| --- | --- | ---: | ---: |
| Health Services | `context-campus-2-1` | 5142–6146 | 1,004 |
| Riley Hall | `context-background-0-2` | 4618–5208 | 590 |
| Student Tennis Center | `context-campus-1-1` | 860–1208 | 348 |
| Alder Building | `context-background-0-1` | 16684–17004 | 320 |

Central Power Station replaces its individually rendered mesh. A failed replacement restores the earlier buildings and keeps the older facade treatments available. When a late rejection prevents the deferred Alder facade merge after the context roofs have loaded, the facade remains visible as a separate mesh.

The exterior ledger records 84 L2 entries, 444 independent L1 entries and 21 historical mappings across 549 outdoor records. The local default scene has 515 selectable buildings, 433 source batch members, 139 road segments and 550 trees. [Outdoor ledger](asset-refinement-inventory.md).

## Verification

The 15 camera positions were rendered in paired clear and context views. All 7,768 roof probes returned a modeled surface. Median absolute differences from the selected historic cells are 0.34 m for the retained Health Services roof, 0.42 m for Central Power Station, 0.09 m for Riley, 0.13 m for the tennis center and 0.39 m for Alder. The Health Services sample omits the area of the new west wing. These are comparisons against the elevation data used to help establish the roof planes.

The geometry audit checked 7,710 navigation edges and recorded 3.8281 m as the minimum clearance on screened nearby edges. Production checks covered desktop and mobile search, six walkable modeled approaches, twelve collision points, and rollback for invalid mesh bytes, a mismatched terrain hash and a late source anchor mismatch. The four source batches retained their other vertex attributes and index order. Repeated exports and the production copies matched the scene files byte for byte.
