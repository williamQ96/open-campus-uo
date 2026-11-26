# Miller Theatre Complex exterior review

The local default scene adopts the registered exterior of the James F. Miller Theatre Complex (UO 031A, `roof-944fcd46`). It includes the Robinson fly tower and auditorium, the Hope and studio wing, the west glass lobby with three door pairs, three stepped flights and a lower east connection to Villard. The two halls and the theater keep their individual selectable identities. The site takes the place of the temporary connection from the earlier Heritage Core package. Failed validation of the expanded package restores that earlier package and the previous Miller model.

## Footprint and exterior

- The campus map fixes the wall offsets and connection with Villard. The model covers 99.83% of the mapped outline, up from 78.57% for the source theater footprint. The registered footprint is 2,015.61 m². It shares 23.26 m of boundary with Villard. The 2024 orthophoto and 2013–2015 first-return grid distinguish the west canopy, auditorium, fly tower and south wing. [UO Campus Map](https://map.uoregon.edu/) · [OSIP 2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [NOAA Digital Coast lidar](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html)
- The university survey and architect's photos document the plain concrete masses, tall fly tower, metal-framed glass lobby, planting and terraces. The model uses original geometry with simplified, opaque glazing. The activated west door approach lies on the modeled landing below the upper stairs. Flights, planters and the northern side of the theater join have collision. The viewer enters the shared interior preview from the modeled approach. Roof equipment, hidden west and east finishes, plant species and surveyed thresholds remain approximate. [UO Robinson Theatre survey, PDF pp. 1–4](https://cpfm.uoregon.edu/sites/default/files/2025-01/robinsontheatre_2025.pdf) · [Hacker project photography](https://www.hackerarchitects.com/education/miller-theatre-complex)

## Verification and level

The model was reviewed against the Knight Library L2 example for footprint, massing, principal façades, visible detailing, materials, editable source and scene integration. Every one of the 1,464 screened first-return cells hits the revised theater. The paired figures below use the 1,345 cells hit by both versions. The grid also informed registration. The east connection comparison includes the prior temporary joint geometry.

| Roof area | Paired cells | Prior median absolute difference | Revised median absolute difference |
| --- | ---: | ---: | ---: |
| Robinson fly tower | 177 | 12.486 m | 0.078 m |
| West lobby canopy | 79 | 2.944 m | 0.061 m |
| North lobby wing | 19 | 4.274 m | 0.036 m |
| Robinson auditorium | 403 | 1.166 m | 0.291 m |
| Hope and south studios | 601 | 0.656 m | 0.068 m |
| East connection | 66 | 1.403 m | 0.534 m |

The east connection retains the largest residual and the north lobby comparison has few paired samples. Ten paired views cover the west façade, stair approaches, other elevations and the joint. Those views retain their draw counts and add about 9,400 visible triangles. Positions, colors, normals and indices of the University and Villard Hall meshes match the preceding versions byte for byte. All 7,705 existing route edges were checked at a 0.42 m margin, with zero added conflicts. The browser checks cover the west landing and east join collision, west entry and return, theater selection and both levels of site fallback.

Run `python scripts/build-miller-theatre-site-review.py --audit <path-to-audit.json>` from the repository root. Source captures, roof sample coordinates, matched views and verification outputs are in the research worktree under `exterior-l2/miller-theatre-20261124/`. The package uses original CC BY 4.0 geometry. [Earlier Miller study](miller-west-study.md) · [Heritage Core adoption](heritage-core-exterior-review-2026-11-24.md)

[Editable registration](../data/metadata/miller-theatre-site-review.json) · [Builder](../scripts/build-miller-theatre-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/heritage-miller-review/site.json)
