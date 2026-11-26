# Pilot tree registration against the UO inventory

2026-11-23. Local Open Campus: UO preview.

The default planting review paired the 2024 Oregon orthophoto with living and removed tree records from the UO public inventory. A read-only query within the two-kilometre scene returned 4,897 living-layer points and 1,790 removal-layer points. WGS84 points were projected using the project's EPSG:3740 campus origin. This follows the registration used by the campus building comparison. The recorded tree sizes are dated observations. [UO Campus Trees](https://cpfm.uoregon.edu/trees), [UO tree map](https://map.uoregon.edu/trees/main), [CampusTrees data service](https://fass-ig-web1.uoregon.edu/arcgis/rest/services/DistributedEdit/CampusTrees/FeatureServer), [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

| Source tree index | UO tree number | Site | Recorded height × spread |
| --- | --- | --- | --- |
| 114 | 4102 | Southwest garden near Knight Library | 2.44 × 1.83 m |
| 130 | 6371 | Planting strip east of the EMU Green | 2.44 × 1.22 m |
| 175 | 3421 | East planting row near Knight Library | 1.22 × 1.83 m |
| 254 | 819 | North end of the southeast planting group near Knight Library | 7.32 × 3.05 m |
| 272 | 6446 | Planting strip north of Gerlinger Hall | 2.44 × 1.22 m |

The five fits move the existing trunk and crown together, sample the exported terrain at the new stem and scale height and maximum horizontal crown span to the recorded dimensions. Crown shape, branching and material still use the original procedural geometry. The default viewer removes one further tree, index 176, whose stem falls on pavement. Its closest inventoried living tree was 7.67 m away. The five moved trees and one removed tree came from the 16 prior surface-contact cases. The repeat screen found 10 individual trees and 17 tree-part/building contacts across 85 reviewed building meshes, down from 16 and 25 respectively. These counts cover intersecting surfaces, including foliage, and do not establish pedestrian clearance.

All ten remaining cases are against the authored Knight Library mesh. The review deferred four proposed fits. Mapped stem coordinates for 26, 91 and 256 fall below existing Knight surfaces in the local model. Fit 164 still places the crown against the mesh. The other cases include overlapping crowns in the dense east planting and stems without a confident match. Reconcile the authored wall, step and overhang placement with registered evidence before adjusting those trees. The inventory and aerial checks leave both planting groups at L1.

The in-scene fit is pinned to the exact art GLB and its own recipe digest. It verifies the expected vertices before transforming positions and normals, and uses the existing vegetation batches. The removal data control triangle indices independently. Missing or mismatched fit bytes leave original tree placement in the preview. The default local build currently has 573 visible trees from 600 source trees, including the two exclusions at Ford/Arena. The development comparison is available at `/?exterior-review=tree-baseline`.

Two browser scene loads with the same removal data verified 4,770 transformed tree vertices and 231,930 unchanged vertices in the pilot batches. Tree triangle indices, draw calls and drawn triangle counts match before and after the fit. The default-route browser check also verified that all 534 existing building approaches were retained and that both recipes fall back independently.

## Reproduction

- [Fit input](../data/metadata/registered-pilot-trees.json) records the adopted tree IDs, stem coordinates, dimensions and source hashes. [Clearance input](../data/metadata/pilot-tree-clearance.json) records the pavement removal. The public runtime contains derived project geometry edits. The queried inventory, imagery crops and rendered comparisons are in the local research folder `exterior-l2/campus-tree-registration-20261123`.
- From the project root, run `python scripts/build-registered-pilot-trees.py --tree-input <original-pilot-input.json>`. Run `python scripts/build-pilot-tree-clearance.py --tree-input <original-pilot-input.json> --audit <audit.json>` for the removal recipe. Both use the original visual-pilot generation input pinned by the source metadata.

The later Knight Library exterior review added fit 171 to the default recipe. It places the southwest Shogetsu cherry at UO tree 3967, at a recorded height of 6.10 m and crown spread of 4.57 m. The fit clears the southwest tower of the candidate exterior. [Knight exterior and latest planting checks](knight-library-registration-2026-11-23.md).

On 2026-11-24 the default EMU revision added fits 142 and 209 for the southeast elm and birch, respectively UO trees 6354 and 6370, and removed procedural tree 299 from the open lawn edge. The default now displays 572 trees and applies eight source-pinned fits. The final building-mesh screen found four unique tree contacts across the 84 reviewed building mesh groups, three around Knight Library and one east of EMU. [EMU adoption](emu-green-exterior-2026-11-23.md#default-adoption-and-exterior-review-2026-11-24).
