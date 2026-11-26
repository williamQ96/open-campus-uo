# Chapman Hall and Condon Hall exterior review

The local preview uses registered exteriors for Chapman Hall (UO 006, `roof-f5cea51d`) and Condon Hall (UO 004, `roof-7ffcf31b`). Chapman uses the stepped perimeter, west triplet of arched windows, a terracotta frieze and arched west and north entrances. Condon uses the related east entrance composition, the lower west stair tower and the three-story concrete frame of the 1967 south addition. Both keep their building IDs. If the package fails its source checks, the preview falls back to the two earlier exteriors and their overlays.

## Registration and exterior details

- Campus footprints determine the wall offsets and the irregular south addition. The orthophoto identifies the flat membrane roofs, stepped parapets and Condon's roof levels. The historic lidar grid supplies an elevation reference. [UO Campus Map](https://map.uoregon.edu/) · [OSIP 2024 RGB orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)
- The Chapman survey and assessment show the west steps and arched window group, pale terracotta cornice, brick bands, north doors and steel sash. The 2018 project record describes retention of the original exterior character. The north entrance is placed near the western part of the north wall based on the assessment. [UO Chapman survey, PDF p. 4](https://cpfm.uoregon.edu/sites/default/files/2025-01/chapmanhall_2025.pdf) · [UO Chapman assessment, PDF pp. 29–36](https://cpfm.uoregon.edu/sites/default/files/chapmanhall_historicassessment_2016-01-20.pdf) · [2018 renovation record](https://news.uoregon.edu/content/chapman-hall-renovation-garners-historic-preservation-award)
- The Condon survey documents the east arch and curved stair cheeks, the contrast between the original north block and the south addition, and the later west stair tower. The grid across the east side of the modern wing follows the concrete-and-brick construction shown in the survey. The arch trim, basket-weave brick panels, iron sash and parapets are simplified original geometry. [UO Condon survey, PDF pp. 1, 4–5](https://cpfm.uoregon.edu/sites/default/files/2025-01/condonhall_2025.pdf)

The registered footprints are 622.04 m² for Chapman and 1,233.60 m² for Condon. The two main entrance interactions start below the modeled stairs. The steps have collision, while the invisible selection surface follows the raised door threshold. The north Chapman interaction follows the smaller modeled approach. All three lead to the shared interior preview. The stairs, field elevations, precise entry positions, masonry relief and hidden window details remain approximate. The package contains original CC BY 4.0 geometry. The older overlays and proof remain documented. [Chapman west overlay](chapman-west-refinement.md) · [Condon east overlay](condon-east-refinement.md)

## Verification and level

Both models were reviewed individually against the Knight Library L2 example. The camera pairs check the main elevations, roof edges and the modern addition. The source checks also compare Peterson's planting vertices in the old combined mesh and the retained separate mesh.

The table reports median absolute differences from the historical 2013–2015 lidar first returns at the same locations, using ray intersections on both versions. These data also informed the registration.

| Roof region | Paired cells | Prior | Revised |
| --- | ---: | ---: | ---: |
| Chapman main roof | 125 | 0.096 m | 0.091 m |
| Condon historic block | 128 | 0.315 m | 0.170 m |
| Condon south addition | 105 | 1.075 m | 0.032 m |
| Condon west stair tower | 6 | 1.500 m | 1.033 m |

The tower sample is small and its height is less certain. All 392 sample positions hit the revised roofs. The previous models cover 364 of those positions. The clearance scan compares all 7,705 route edges with both footprints and the new stair collision and finds zero new conflicts. The runtime checks cover all three approaches, building selection, Chapman west entry and return, and damaged-package fallback.

Run `python scripts/build-memorial-quad-site-review.py --audit <path-to-audit.json>` from the repository root. The source captures and before-and-after views, the roof fit and production smoke results are in the external research worktree under `exterior-l2/memorial-quad-20261124/`. Work remains local.

[Editable site registration and source hashes](../data/metadata/memorial-quad-site-review.json) · [Builder](../scripts/build-memorial-quad-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/memorial-quad-review/site.json)
