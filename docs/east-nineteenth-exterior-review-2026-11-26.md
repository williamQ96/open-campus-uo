# Three East 19th Avenue exterior reviews

The local preview uses three original building models under the existing scene IDs. City of Eugene footprints, address points and the 2024 Oregon aerial locate the three buildings. Public exterior photos inform the openings and materials. The archived mesh contains original vertex-colored geometry. The [editable dimensions](../data/metadata/east-nineteenth-exterior-review.json) drive the [exporter](../scripts/build-east-nineteenth-exterior-review.py). [City building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

| Address and scene ID | Exterior restored |
| --- | --- |
| Sigma Chi at 1440 East 19th, `roof-600a0bef` | Three roof ridges, dark columns, facade panels, an upper courtyard walk and the east entrance canopy |
| 1456 and 1458 East 19th, `roof-a8318b83` | Stoop, brick piers, porch gable, sloped front roof and low rear roof |
| 1355 East 19th, `roof-028770d6` | Two stepped gable sections, raised west walk and open lower parking bays |

The IFC directory confirms the chapter house address. The city modernism survey dates the building to 1964. The July 2024 north street view and the IFC courtyard photograph show the facade and railings. The November 2020 east view shows the canopy. The new entrance position and dimensions are estimated. [Chapter directory and courtyard photo](https://uoifc.com/sigma-chi/) · [City modernism survey](https://www.eugene-or.gov/DocumentCenter/View/24803/Eugene-Modernism-1935-65).

The 1456 and 1458 address points share City object 170739. A north street view shows the common porch. The model includes the porch stairs and piers. Address-specific doors remain unverified. The 1355 address points fall in City object 170639. A 2009 city agenda attachment lists 14 units at the matching tax lot. The July 2024 views show the south parking opening, stepped west balcony and vertical facade panel joints. The roof and balcony elevations, parking depths and screened side details are approximations. The viewer lists the east canopy approach at Sigma Chi. [City address information](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer) · [City agenda attachment](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/3?fileID=10).

## Verification

The new meshes intercepted 2,824 of 2,888 height rays. The 1355 model's narrower east eave follows the visible edge in the 2024 aerial and the DOGAMI surface break. This excludes 32 eastern cells per date. At the excluded cells, the 2013–15 and DOGAMI heights differ. The following comparison uses 2,716 cells covered by both versions. The 2017 grid has no observations at these locations.

| Building | Surface | Previous median absolute error | New median absolute error |
| --- | --- | ---: | ---: |
| Sigma Chi | 2013–15 | 0.8422 m | 0.4328 m |
| Sigma Chi | DOGAMI | 0.8575 m | 0.0603 m |
| 1456 / 1458 | 2013–15 | 0.8369 m | 0.0462 m |
| 1456 / 1458 | DOGAMI | 0.8012 m | 0.0311 m |
| 1355 | 2013–15 | 1.5924 m | 1.0339 m |
| 1355 | DOGAMI | 1.3686 m | 0.2393 m |

Nine camera pairs cover the three frontages, their roof forms and the chapter courtyard. The two source batches lose 678 original triangles and retain all other indices and vertex attributes for 89 peer records. The exporter checks 7,710 route edges. Exported, independently repeated, installed and served bytes match.

Desktop and phone select the three original IDs via four search queries. Both follow 221 route points from Knight Library to the Sigma Chi east approach. Seven collision probes cover the courtyard, porch, parking bay, support post and occupied walls. The local scene has 524 selectable buildings, 279 batched buildings and 602 approaches. Simulated invalid GLB bytes restore all three source records and their estimated approaches.

All three models pass the local L2 exterior review. This revision is local and uncommitted.
