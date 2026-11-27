# Twenty-four East 12th–15th block exteriors

| Scene ID | City roof | Modeled exterior |
| --- | ---: | --- |
| `roof-31f7e9f1` | 170377 | 1360 Alder north wing. Open carport, red galleries and a shallow gable. |
| `alder-1360-south` | 170378 | Independent 1360 Alder south wing. Open parking and a ridge to the north of the centerline. |
| `east15-670` | 171230 | 670 East 15th. Separate low flat roof and side gallery. |
| `roof-9d174b26` | 171231 | 640 East 15th. Four roof runs around an open inner court. |
| `kincaid-1214` | 170132 | 1214 Kincaid. High gabled roof, lower street volume and porch. |
| `roof-9cc440db` | 170328 | 1236 Kincaid. Lower overlapping roof sections and east gallery. |
| `roof-a392e59a` | 182504 | 740 / 750 East 13th. Six visible levels, street storefront and recessed alley parking grille. |
| `hilyard-1477` | 170380 | 1477 Hilyard. Flat roof and a horizontal slat screen facing Hilyard. |
| `east15-733` | 170419 | 733 East 15th. Offset gabled wings and south galleries. |
| `roof-d798dc2a` | 170784 | 745 East 15th. Flat roof around an open courtyard. |
| `roof-ada23895` | 170787 | 810 / 830 East 13th. Low storefront roof and raised rear section. |
| `roof-5e74c2bc` | 170788 | 840 / 844 East 13th. Two storefronts, dark street fascia and flat roof. |
| `east13-854-860` | 170786 | 854 / 860 East 13th. Adjacent storefronts with separate entries under a red-brown fascia. |
| `east13-866-872` | 170537 | 866 / 868 / 870 / 872 East 13th. Raised storefront and upper window bays. |
| `east13-880-894` | 170546, 170826 | 880 / 884 / 894 East 13th. Connected corner building with a pitched frontage and windows on two streets. |
| `roof-60066458` | 170367 | 775 East 15th. Shallow roof and a stair to the north gallery. |
| `roof-54ce4ba0` | 170785 | 791 East 15th. Stepped roof and south arch band. |
| `east15-766` | 170433 | 766 East 15th. Separate slender roof with a through-drive and street gallery. |
| `roof-4058a38b` | 170493 | Campus Court at 1544 Alder. Three roof wings, two exposed gaps, exterior galleries and blue cladding. |
| `roof-6a85a0c3` | 171222 | 631 East 15th. Main gable, lower street gable and side gallery. |
| `roof-8b243212` | 171225 | 1480 / 1490 Hilyard. Shared cross-gabled roof. |
| `roof-03784b41` | 170431 | 821 East 15th. Hipped roof, dormers, south porch and estimated street approach. |
| `roof-f9516e15` | 170399 | 812 East 14th. U-shaped plan, open rear court, brick tones and projecting timber detail. |
| `roof-ac86161b` | 170782 | 850 East 14th. Street-facing gables, brick tones and timber detail. |

Sixteen prior ranges yield twenty-four selectable roofs, including nine separately registered splits. City roof 170493 intersects the original 1544 Alder ranges by 701.125 and 401.458 m². The two ranges meet in the source batch and each is removed through a pinned triangle range. The secondary ID `roof-321413cf` remains in the ledger as a historical mapping to Campus Court. City roof 170433 is the independent neighbor at 766 East 15th. City records 170546 and 170826 share a physical seam along the corner storefront and use one selection. County orthophotos, the DOGAMI lidar surface and 2024 street imagery establish volume and visible features. Roof junctions, wall openings, access heights and parts obscured by trees or adjacent roofs use approximate dimensions. Reference imagery remains in the research workspace. [City roof layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [County imagery](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Editable dimensions and dated evidence](../data/metadata/northwest-blocks-review.json).

All 11,010 sampled rays inside the adopted roofs hit. Of the 24 medians, 22 drop across 9,212 paired DOGAMI cells. The median at 670 East 15th rises from 0.0328 to 0.0366 m, and the median at 812 East 14th rises from 0.8005 to 0.9276 m. Thirty matched views and exact batch index and vertex comparisons preserve 53 neighboring mesh ranges. The renderer confirms the separated 1360 Alder wings, the exposed slots at Campus Court, the 766 through-drive, the recessed 740 / 750 grille, three open courts and the lower street roof at 810 / 830 East 13th. The exporter checks 7,710 route edges with 2.6306 m minimum clearance. [Exporter](../scripts/build-northwest-blocks-review.py).

Desktop and phone select all 24 buildings, resolve six aliases, pass 32 collision and four approach probes, and reach the estimated street entrance at 821 East 15th. Both an invalid GLB and a failing source anchor restore all sixteen previous meshes and approaches. The staged, repeated, installed, built and served bytes match. The package is local and uncommitted. The published checkpoint remains c3dc42c.
