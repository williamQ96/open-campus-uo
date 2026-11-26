# Bean and Unthank Hall exterior review

The local default scene uses two registered exteriors for Justice Robert Sharp Bean Hall (UO 068, `roof-0de7fadb`) and DeNorval Unthank Jr. Hall (UO 207, `context-oc-unthank`). The models retain the two scene identities, the surrounding terrain, and the existing campus route graph.

| Building | Registered wall footprint | Look and layout |
| --- | ---: | --- |
| Bean Hall | 6,567.840 m² | Two three-story brick rings with flat roofs, black panel rhythm, open landscaped courts, a lower commons link and north wing, and a glazed south stair hall |
| Unthank Hall | 4,125.814 m² | Three seven-story residential wings around a lower market and welcome-center podium, skylights, brick and vertical metal cladding, and glazed entries beneath projecting canopies |

The Bean courtyard holes cover 1,337.529 m² and 1,351.991 m². The corrected wall envelopes are 9.743 m apart at their nearest points. The old Unthank placeholder intersected the raw Bean map by 92.862 m². Registering both buildings lets the collision layer preserve two open courts and the actual north–south passage. The two own outlines shifted west by 2.40 m and 2.08 m and north by 0.12 m and 0.38 m to align with the 2024 aerial. [University map](https://map.uoregon.edu/) · [2024 OSIP aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2024 campus height comparison and oblique photo, p. 23](https://cpfm.uoregon.edu/sites/default/files/2024-10/2024-10-01_cpc_final_reduced_.pdf#page=23).

The main Bean roof fields follow the 2017 historical surface. The northwest addition, southern entrance and altered commons follow the later aerial, the 2019 reopening account and the 2025 survey. Pane spacing, door and equipment dimensions use visual estimates. Unthank's model uses the current campus outline and first-floor entrance layer, the 2024 aerial, and design-team and housing photographs. Its podium and upper roof elevations, cladding module widths and entrance thresholds remain estimates. The 2023 lidar sample at Autzen Stadium has no returns over these halls. [UO Bean renovation](https://news.uoregon.edu/content/uo-celebrates-renovation-justice-robert-sharp-bean-hall) · [Bean survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/beancomplex_2025.pdf) · [Bean housing photo](https://housing.uoregon.edu/bean) · [Unthank Hall and Welcome Center photographs](https://housing.uoregon.edu/unthank) · [Architect's Unthank exterior photos](https://rowellbrokaw.com/blog/2021/9/27/unthank-hall-vignettes) · [Autzen sample metadata](https://pointcloud.org/datasets/autzen-2023/).

| Historic Bean roof samples | Paired cells | Median absolute difference before | Median absolute difference after |
| --- | ---: | ---: | ---: |
| West ring | 1,746 | 0.760 m | 0.102 m |
| East ring | 1,930 | 0.780 m | 0.112 m |
| Combined | 3,676 | 0.770 m | 0.112 m |

The 2017 comparison used 3,747 cells at least 1.05 m inside the two residential roof regions, with historical heights between 10 and 14.5 m. The replacement hit every eligible cell. These checks compare against the same source that informed the fitted historic roof elevations. The 17 paired rendered views cover both Bean courtyards, the entrances, the reopened passage, and Unthank's wings and podium. The tested neighbor batch retained its positions, normals, colors and indices. All 7,710 active route edges clear the paired building and support footprints. Six entrances are walkable in the local preview. Desktop and mobile selection, courtyard and passage collision, and two paired fallbacks on an invalid GLB or a mismatched source passed.

Both exteriors were reviewed at L2 against [Knight Library](knight-library-registration-2026-11-23.md). The runtime package contains original geometry and colors, with no reference photography embedded. The [editable layout](../data/metadata/bean-unthank-site-review.json) and [generator](../scripts/build-bean-unthank-site-review.py) reproduce the GLB and descriptor. Run `python scripts/build-bean-unthank-site-review.py --audit <audit.json>` from the repository root. Paired renders, the raster sample list, current outline registration and the production smoke results are in the research worktree under `exterior-l2/east-campus-20261124/`.
