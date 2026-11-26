# University Hall and Villard Hall exterior review

The [registered Miller exterior](miller-exterior-review-2026-11-24.md) now supplies the permanent theater-side volume and the connection to Villard. The notes below describe the earlier two-hall package, which remains the fallback.

The local default scene adopts registered exteriors for University Hall (UO 005, `roof-9017feee`) and Villard Hall (UO 031, `roof-399c648e`). Both keep their individual selection IDs and fall back together if the package fails its source checks. The neighboring Miller Theatre Complex remains a separate building.

## University Hall

The roof follows the stepped form of the campus plan, with two higher end towers, mansard slopes, chimneys, dormers and iron-colored crests. The brick exterior includes pilaster strips, arches, bracketed cornices and the partially exposed base level. Concrete wing walls, flights of stairs and planted beds frame the east and west entries. Both entries have explicit interaction points below the steps. UO outline coverage goes from 69.92% to 99.83%. Window counts on partly obscured elevations, chimney dimensions, landscaping and field grades remain approximate. [UO historic architecture exhibit](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/university-hall) · [Campus Planning 2026 University Hall photo](https://cpfm.uoregon.edu/sites/default/files/2026-08/img_3015.JPEG)

## Villard Hall and the theater connection

The registered exterior has four corner mansards, cresting, molded window surrounds, rusticated corners and the east entry's three oculi and rectangular central panel. The main door opens to the modeled steps and planters. The west connection fills the former visual and collision gap to the existing theater mass. The campus map assigns the connector area to the theater side, and the connector mesh is packaged with the common site geometry. The project architect documents a glazed lobby connecting the two buildings. The modeled connector's membrane grade and side openings are estimates. UO outline coverage goes from 70.68% to 99.49%. The theater stays at L1. [Villard 2025 historic survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/villardhall_2025.pdf) · [Campus Planning 2026 Villard Hall photo](https://cpfm.uoregon.edu/sites/default/files/2026-08/img_3020.JPEG) · [UO Campus Map](https://map.uoregon.edu/) · [Hacker project description](https://www.hackerarchitects.com/education/miller-theatre-complex)

The Campus Planning gallery documents the post-restoration appearance. The orthophoto predates completion and informs roof and site registration. Doorway thresholds, stair and planting dimensions and the theater seam are approximate. The three entries open the shared classroom preview. [Campus Planning gallery](https://cpfm.uoregon.edu/academic-center-historic-core-diagnosis) · [2025 reopening report](https://news.uoregon.edu/content/historic-halls-reopen-modern-amenities-and-more) · [OSIP 2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)

## Verification and level

Each exterior was reviewed against the Knight Library L2 example for massing, identifiable façades and roofs, material contrast, editable source and scene integration. Model heights were compared at the same screened first-return cells in the 2013–2015 historical lidar grid. The grid also informed the new geometry. There are 1,035 screened cells, all covered by the new roofs. The table uses the 901 cells hit by both versions. Tower pairs cover fewer locations. [NOAA Digital Coast lidar source](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html)

| Building and roof area | Paired cells | Prior median absolute difference | Revised median absolute difference |
| --- | ---: | ---: | ---: |
| University main roof | 402 | 5.868 m | 0.128 m |
| University towers | 27 | 5.582 m | 0.337 m |
| Villard main roof | 433 | 3.330 m | 0.049 m |
| Villard towers | 39 | 4.390 m | 0.682 m |

Twelve matched render pairs cover the main façades, ends, roof and theater seam. Scene draw calls change by zero to two per view. The adopted stair, planter and theater-connection collision introduces zero new conflicts across all 7,705 route edges at a 0.42 m margin. The browser checks exercise the three stair approaches, independent building selection and fallback on a damaged model.

Run `python scripts/build-heritage-core-site-review.py --audit <path-to-audit.json>` from the repository root. The external research worktree stores post-renovation references, source hashes, roof sample masks, paired renders and runtime checks under `exterior-l2/heritage-core-20261124/`. The package contains original CC BY 4.0 geometry. [University Hall history](university-hall-refinement.md) · [Villard Hall history](villard-east-refinement.md)

[Editable registration](../data/metadata/heritage-core-site-review.json) · [Builder](../scripts/build-heritage-core-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/heritage-core-review/site.json)
