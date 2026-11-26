# Six southeast Fairmount exteriors at L2

The default scene rebuilds six hillside houses on Sunset Drive, Rose Lane and Birch Lane while keeping each existing scene ID. Municipal address points establish names. City outlines are available for 281 and 366 Sunset and 2275 Rose. The other three use the statewide outlines checked against the 2024 orthophoto. The editable register holds the individual roof planes, source references and principal facade geometry. [City GIS building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Editable register](../data/metadata/southeast-fairmount-exterior-review.json).

| Address | Scene ID | Modeled features |
| --- | --- | --- |
| 281 Sunset Dr | `roof-e0d560b4` | The shallow glazed gable, low garage and timber approach follow the visible elevation. The approach is a rendered approximation fitted to steep scene terrain. |
| 365 Sunset Dr | `roof-169a7b78` | A brown gable, visible rooftop solar array and lower garage wing follow the aerial and visible street edges. The principal doorway is screened. |
| 366 Sunset Dr | `roof-699d6c1e` | The long west balcony has a shallow overhang, wood rail and posts. Its recessed lower bay separates from the southern garage. |
| 2281 Rose Ln | `roof-22175da6` | The west brick elevation has green trim, three individual gabled dormers and a lower northern roof wing. The hedge screens the bottom of the approach. |
| 2275 Rose Ln | `roof-05727176` | A high southern gable meets a lower diagonal roof. Trees obscure much of the street elevation and its door position. |
| 2293 Birch Ln | `roof-b2800bfe` | The blue-gray street gable has white trim, an attic sash, lower window groups and a chimney. The timber frame next to it appears beyond the registered building outline. |

The 366 Sunset, 2281 Rose and 2293 Birch approaches are estimated. The 281 Sunset ramp is represented visually, and that building, 365 Sunset and 2275 Rose use empty gameplay entrance lists. Building bases follow the modeled hillside. Roof pitches, window dimensions, pavement and screened wall details remain approximate. 2110 Hamble and 2300 Parkside remain L1 while their exterior evidence is checked.

## Verification

- The six roofs intercepted all 4,083 archived surface samples used for the comparison. The original and revised roofs overlapped for 3,345 paired samples across the three surveys. Every building had a lower median absolute vertical residual in each survey. The lidar sets are historical and include canopy returns, so those values describe this paired model comparison.
- The builder checked 7,710 route edges. The closest retained edge to the checked model walls or supports was 6.316 m. The new package removes 1,150 targeted source triangles in two batches. Exact index and attribute comparisons verified the surviving data for 94 batch peers. The preceding Fairmount and Kincaid GLB was reproduced byte for byte.
- Desktop and phone production previews passed six address searches, six solid and three clear collision probes, and the 365-point route from 968 Alder to the west approach at 2281 Rose. The stage, installed files, production files and served bytes match. All six focused browser cases passed, including recovery when the last source anchor is invalid.
- This package uses the pinned default scene and is local and uncommitted. It contains original geometry and source references. Run `python scripts/build-southeast-fairmount-exterior-review.py --stage PATH --audit PATH` to export a separate review copy and use `/?exterior-review=southeast-fairmount-exterior-baseline` to view the six old batch shapes. [Packaged scene descriptor](../apps/web-preview/public/scene/southeast-fairmount-exterior-review/site.json).
