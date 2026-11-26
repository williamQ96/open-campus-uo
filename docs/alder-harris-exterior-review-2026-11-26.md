# Six Alder, Harris and nearby residential exteriors

The local preview replaces six source meshes under their original scene IDs. Municipal footprints and the 2024 Oregon aerial establish the positions. Dated street views and site photographs constrain the principal elevations. The published inputs to the exporter are original geometry dimensions and source references. [Editable dimensions](../data/metadata/alder-harris-exterior-review.json) · [Exporter](../scripts/build-alder-harris-exterior-review.py) · [City building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

| Building and scene ID | Exterior reconstructed |
| --- | --- |
| Lorax Manner, 1648 Alder, `roof-71f4af04` | Rounded turret with a conical roof, arched windows, pale upper band, brick walls and gabled east porch |
| Campbell Club, 1670 Alder, `roof-0587b8ad` | Street and lower rear roofs, three green dormers and an open porch |
| Woodside Manor, 1810 Harris, `roof-80aadee0` | Five hip roofs, a low connector, four footprint openings, glass-block base, balcony rails and east stair |
| 1065–1079 East 19th, `roof-73a1a032` | Stepped gables and the visible yellow end door within one outline serving eight address points |
| 750 East 18th, `roof-1a3a0846` | Near-flat roof, red vertical facade panels, raised base and side windows |
| 746 East 19th, `roof-c7815e30` | North shed dormer and porch, stucco walls and alley-side stairs |

The co-op photos and historic survey show frontage details screened in the street views. The public 2023 listing photos confirm the north and alley elevations at 746. Wall details in screened areas, the Lorax turret height and the approach grades use estimated dimensions. Four estimated approaches are included in the scene. The 750 model has an empty approach list because private unit access remains unclear. [Students’ Cooperative Association](https://eugenesca.com/) · [Lorax Manner](https://eugenesca.com/loraxmanner/) · [Campbell Club photos](https://eugenesca.com/campbellclub/campbell-club-photo-album/) · [National Park Service survey](https://npgallery.nps.gov/NRHP/GetAsset/NRHP/64500505_text) · [Woodside Manor listing](https://www.rentcollegepads.com/city/eugene-or/listings/woodside-manor-41826) · [746 East 19th listing](https://www.redfin.com/OR/Eugene/746-E-19th-Ave-97401/home/26201447).

## Verification

New roofs intercepted all 5,332 available height rays in the two surfaces used for comparison. The table reports median absolute error across 5,084 cells with hits on both versions. The 2017 grid yielded one valid cell at Lorax and was excluded from the comparisons.

| Building | 2013–15 before → after | DOGAMI before → after |
| --- | ---: | ---: |
| Lorax Manner | 1.7037 → 1.1067 m | 1.6239 → 0.3954 m |
| Campbell Club | 1.1869 → 0.6614 m | 1.1909 → 0.1513 m |
| Woodside Manor | 1.0297 → 0.3321 m | 1.0260 → 0.1883 m |
| 1065–1079 East 19th | 0.7091 → 1.1532 m | 1.3609 → 0.1752 m |
| 750 East 18th | 1.0550 → 0.0226 m | 1.0364 → 0.0167 m |
| 746 East 19th | 1.1880 → 0.6748 m | 1.0563 → 0.2823 m |

At 1065–1079, the 2013–15 surface places the ridge farther east. The adopted roof follows the registered outline and 2024 aerial interpretation and improves the DOGAMI fit. The reason for the difference between the two reference surfaces remains unresolved.

Twelve matched views cover the visible exteriors. The package removes 1,149 original triangles and retains the indices and vertex attributes of 158 peer records across three batches. At the shared Campbell boundary, the source GLB hash and anchors constrain the replacement to original triangle range `[524, 712)`. The neighboring range `[3845, 4345)` remains intact. The exporter checks 7,710 route edges. Repeated export, installed and locally served asset bytes match.

Desktop and phone production previews each expose six original IDs, four walkable approaches and a 47-point route from Knight Library to Campbell Club. Eleven collision probes cover walls, porches and open space, including two Woodside courtyard interiors and an adjacent wall. The scene has 524 selectable buildings, 273 remaining batched buildings, two independent context roof refinements and 600 approaches. Independently invalid GLB bytes and an invalid source anchor each restore all six old meshes and their generic approaches.

All six exteriors are registered as L2. This revision is local and uncommitted.
