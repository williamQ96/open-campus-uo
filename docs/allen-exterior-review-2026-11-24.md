# Allen Hall exterior review

The local default scene uses the registered Allen Hall exterior (UO 017, `roof-7b7893d6`). The model distinguishes the 1954 limestone-and-brick west wing, the earlier Journalism wing, and the 2012–13 addition with its recessed glazed entrance and higher roof. The west facade has two continuous window bands, nine abstract relief plaques, a roof guard and a glazed end bay. East, west and south approach points connect to the shared interior preview. A failed package check restores the previous Allen block and west overlay.

## Registration and exterior details

The 1,740.03 m² model follows the campus-map outline, covering 99.94% of the mapped area. The previous source outline covered 52.84%. The orthophoto and historic lidar identify the campus roof offsets and vertical breaks. The 2025 survey and architect's photographs inform the contrasting wings, west plaques, curtain wall, south entrance and apron. The plaques are simplified original geometry. The roof equipment, exact plaque relief, window dimensions, south threshold and planting are approximate. The west retaining walls approximate the sunken areaway edge at the existing terrain grade. [UO Campus Map](https://map.uoregon.edu/) · [UO survey, PDF pp. 4–5](https://cpfm.uoregon.edu/sites/default/files/2025-01/allenhall_2025.pdf) · [YGH Architecture photo record](https://ygharch.squarespace.com/work-uoah) · [OSIP 2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)

Allen's prior model is independent of the merged Lawrence–Pacific–Columbia candidate. The paired exports confirm matching runtime position, normal, color and index data for the Lawrence mesh and the batch containing its detached eastern candidate. The separate identity audit records the remaining split. [Science complex registration audit](lawrence-science-exterior-crosswalk-2026-11-24.md)

## Verification and level

The model was reviewed against the Knight Library L2 example for massing, principal façades and entrances, material contrast, editable source and scene integration. The new roofs intersect all 1,156 admitted historical lidar cells. The table compares the 647 cells struck by both model versions. The original model misses all the selected cells on the south addition and on the upper atrium crown. The narrow east entry canopy has no admitted cells, and the north service block has four common cells. The lidar also informed the reconstruction. [NOAA Digital Coast historical lidar](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html)

| Roof area | Paired cells | Prior median absolute difference | Revised median absolute difference |
| --- | ---: | ---: | ---: |
| 1954 west wing | 301 | 0.323 m | 0.077 m |
| West atrium roof | 73 | 5.383 m | 0.093 m |
| East brick wing | 213 | 1.019 m | 0.048 m |
| 2013 east roof | 21 | 3.599 m | 0.024 m |
| Central junction | 35 | 2.463 m | 0.045 m |
| North service block | 4 | 4.513 m | 0.098 m |

Ten paired views cover the entrances, wings, north wall and roof in toon, PBR and campus context. Each view holds its previous draw count and adds about 19,300 visible triangles. The model and site collision add no conflicts across all 7,705 route edges. The runtime checks cover selection, all three round trips and a damaged-package fallback.

Reproduce the model with `python scripts/build-allen-site-review.py --audit <path-to-audit.json>`. Source hashes, camera pairs, sample coordinates and browser results are in the research worktree under `exterior-l2/allen-lawrence-20261124/`. The project ships original CC BY 4.0 geometry. [Previous Allen west overlay](allen-west-exterior-refinement.md)

[Editable registration](../data/metadata/allen-site-review.json) · [Builder](../scripts/build-allen-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/allen-site-review/site.json)
