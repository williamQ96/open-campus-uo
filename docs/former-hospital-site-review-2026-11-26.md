# Former Sacred Heart hospital site and The Mark Eugene Phase 1

The local viewer shows the old hospital site after demolition, with the early Phase 1 construction visible on October 17, 2026. The southern parcel includes graded ground, a first-floor timber frame with window openings and temporary braces, perimeter fencing, a tower crane and a protected sidewalk along East 13th. The northern parcel shows an inferred interim ground surface and the footprint of earlier site disturbance. The L2 rating applies to the dated outdoor site group ENV-08.

## Parcel registration and evidence

- Lane County's parcel service separates the 10,606 m² southern lot, `1703323104701`, from the 13,154 m² northern lot, `1703323104702`. The original parcel was 791 E 13th Avenue. City file PF-26-0002 records the two-lot partition in May 2026. The parcel coordinates are transformed from EPSG:3740 into the project's local ENU frame using the same registration as the 2024 OSIP view. [Parcel service](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/arcgis/rest/services/EugTaxlots/FeatureServer/0) · [Recorded partition](https://pdd.eugene-or.gov/LandUse/SearchApplicationDocuments?file=PF-26-0002).
- The developer identifies Phase 1 at 1290 Alder and announced its September 2026 start. The October 17 ground photo shows an open timber frame, diagonal bracing, a chain-link perimeter and a tower crane on the south lot. The city records document separate proposals for the south and north lots. The model geometry is original and the photograph is linked as observational evidence. [Developer announcement](https://www.landmarkproperties.com/the-mark-eugene-breaks-ground-donates-10k-to-local-nonprofit/) · [October ground observation](https://sworegonarchitect.blogspot.com/2026/10/missing-mark.html) · [Phase 1 file](https://pdd.eugene-or.gov/LandUse/ApplicationReport?file=ARA-25-0023&pdf=True) · [Phase 2 file](https://pdd.eugene-or.gov/LandUse/SearchApplicationDocuments?file=ARA-26-0003).
- The November 23–27 road bulletin provides a separate dated basis for the east-side Hilyard closures in the viewer. The west Hilyard, south East 13th and Alder approaches stay available. These are scene representations for the dated window. [City road work advisories](https://www.eugene-or.gov/1191/Road-Work-Advisories).

The approximate timber extent, varying soil surfaces, north lot treatment, crane height and base, fence offsets and exact sidewalk edges are modeling decisions. Refresh the dated state when newer ground evidence establishes material changes. The editable inputs, references and measurement values are in [the site registration](../data/metadata/former-hospital-site-review.json), and the [builder](../scripts/build-former-hospital-site-review.py) exports the [runtime descriptor](../apps/web-preview/public/scene/former-hospital-site-review/site.json) and GLB.

## Historical candidates and runtime

| Source ID | Source footprint (m²) | Overlap with visible 2024 hospital roof (m²) |
| --- | ---: | ---: |
| `roof-a3f76ab6` | 4,856.0 | 3,977.13 |
| `roof-eb5ba9b8` | 1,771.5 | 0 |
| `roof-8caa7792` | 183.5 | 0 |
| `roof-6d2ad952` | 473.0 | 0 |
| `roof-8e0e504c` | 3,767.0 | 0 |

The four zero-overlap candidates sit on visible lawn, parking or paths in the 2024 acquisition. The first ID overlaps 81.9% of its source footprint and represents the demolished hospital. All five retain their original source records and L1 historical ledger entries. The active viewer removes 5,474 source triangles from a single batch and preserves the raw vertex data and surviving indices for the other 33 batch members. The site mesh contributes 39,283 triangles. Four bounded closures feed player collision and routing. A failed source or bounds check restores the earlier meshes, selections and walking area.

## Verification

Five paired renders cover both street corners, south frontage, the overall site and the former north lot. The route audit scanned 7,710 graph edges and found zero intersections with the closure boxes buffered by 0.5 m. Three nearby public transects have minimum clearance of 2.24 m from those buffered boxes. The focused Playwright tests checked the default census of 515 selectable buildings, 330 batched buildings and seven separate roof treatments, a public route from East 13th to East 11th, and full fallback from invalid closure bounds. The six combined former-hospital and University District tests passed. Desktop and mobile production served the source-pinned bytes and each verified three adjacent entrances, nine collision samples and a 51-point public route around the closure. Formatting, 195 unit tests, production build, 327 archive hashes and 259 viewer pins passed. This change is local and uncommitted.

- [Asset refinement inventory](asset-refinement-inventory.md)
- [Adjacent University District clinic and garage review](university-district-clinic-review-2026-11-26.md)
