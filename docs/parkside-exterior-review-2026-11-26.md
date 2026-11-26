# 2300 Parkside Lane exterior review

City of Eugene building object 159832 contains the municipal address point for 2300 Parkside Lane. The 2024 Oregon aerial and three historical elevation datasets locate its main roof and raised clerestory. The July 2026 RMLS listing attributes the house to D. Unthank and documents the uphill carport, the gate and the terraces on three exterior levels. The local scene retains the original ID `roof-6f59699a`. [City building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [RMLS listing](https://www.realtor.com/realestateandhomes-detail/2300-Parkside-Ln_Eugene_OR_97403_M26184-75479).

The new mesh follows the 174.30 m² registered outline. It includes the shallow roof and clerestory window band, brick chimney, open timber-post carport, horizontal slat gate, a driveway tied into the scene terrain, and three stacked levels with downhill glazing and timber decks. The deck dimensions, floor elevations and window divisions use approximate values. The gate is shown closed and the viewer offers no entrance marker for the private residence. The [editable dimensions](../data/metadata/parkside-exterior-review.json) drive the [exporter](../scripts/build-parkside-exterior-review.py). The archived mesh is vertex-colored original geometry.

## Verification

All 438 historical height rays hit the new geometry. The error comparison uses the 115 cells per surface covered by both versions, including points affected by trees. The 2017 surface supplied the approximate roof level and clerestory coordinates.

| Historical surface | Previous median absolute error | New median absolute error |
| --- | ---: | ---: |
| 2013–15 | 1.8215 m | 0.1934 m |
| 2017 USACE | 1.4052 m | 0.0427 m |
| DOGAMI Lane County | 1.3320 m | 0.1005 m |

Five matched camera pairs cover the uphill frontage, roof, both sides and downhill terraces. The source batch loses 186 original triangles and retains all surviving indices and vertex attributes for 56 peers. The exporter checks 7,710 route edges. Desktop and phone production load the same bytes as the independent staged exports, find the building by address and clear both the carport opening and selected driveway probe. The house and one carport post collide at their modeled positions. The local default scene has 524 selectable buildings, 282 batched buildings and 604 approaches. A damaged GLB restores the prior selectable batch entry and its generic approach.

The model meets the local L2 exterior review. The change is local and uncommitted.
