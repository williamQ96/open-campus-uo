# EMU Green and Knight Library pilot planting correction

The local default scene removes eighteen generated trees on EMU Green and four on the west side of Knight Library. Two generated shrubs paired with EMU tree indices 25 and 50 are part of the same correction. Compare [the default planting](http://127.0.0.1:5173/) with [the previous planting](http://127.0.0.1:5173/?exterior-review=tree-baseline) in the development viewer.

## Evidence for removal

- The 2022 campus plan identifies EMU Green as an open sunny gathering space. The 2024 aerial shows open grass inside its circular path, with the trees primarily outside the circle. The eighteen selected stem coordinates project onto the open green. Two earlier EMU corrections, indices 216 and 273, remain accounted for in the visible count. [University of Oregon Campus Plan, page 150](https://cpfm.uoregon.edu/sites/default/files/2023-12/principle-12-design-area-special-conditions_2022_23_.pdf), [Oregon 2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).
- Generated tree stems 10, 129, 187 and 245 west of Knight project onto walk surfaces or open low planting between visible crowns. The modeled tall trees physically intersect the exported library. The east group around tree 296 projects into continuous canopy, and the Gerlinger candidate 272 is also under a visible crown. Resolving those intersections needs enough evidence to place the stems and verify the wall positions. [Knight Library cultural resources survey, page 4](https://cpfm.uoregon.edu/sites/default/files/2025-01/knightlibrary_2025.pdf), [original pilot tree audit](vegetation-clearance-audit.md).
- Matched all 600 trees to triangle spans in the exported source mesh. The surface test used non-coplanar segment-to-triangle contacts against independent and batched building meshes, including the default Ford/Arena replacements and the eleven revised background roofs. The old tree 60 translation and earlier suppressions were included. Thirty distinct tree models contacted the tested building surfaces, including fourteen of the approved removals. Sixteen contact cases remain. The test screens surface intersections. Containment and individual decorative overlays require their own checks.

An approximate ellipse around EMU Green, traced from the aerial, has about 1,555 m² of area. The current EMU geometry above 7.5 scene metres projects onto about 746 m² of that ellipse, while the UO map outline for record 033 has zero overlap with it. This residual indicates where the modeled southern facade and lawn need a separate site correction. [Campus mapping](https://map.uoregon.edu/).

## Scene and validation

The editable list selects twenty-two indices from the original 300 pilot trees. Five mesh records identify ordered triangle spans for the bark, foliage and paired shrubs. The branch checks the source and recipe hashes and applies the complete correction together. The source generate-and-preserve step retains the recipe with the original art. Failed integrity checks keep the prior planting for those locations.

The shared art counts are 600 source trees and 576 visible after both earlier pilot corrections and the new twenty-two. The default site then removes two separate context trees in the Ford/Arena footprint clearance, yielding 574 visible trees, including 276 pilot trees and 298 context trees. The tree comparison view displays 596. The optional athletic block applies its own documented tree correction.

Chromium renderer comparisons checked 9,336 removed triangles across the five affected meshes. Every other index in those meshes and their position, normal and color arrays matched byte for byte. Draw counts matched in the four paired views. Browser interaction compared all 536 gate records for the 534 building IDs. The baseline and error fallback preserve the four model gates introduced with the Ford/Arena site. The project still records the pilot trees and understory groups at L1.

## EMU exterior follow-up

During the paired EMU scene review, the understory paired with tree 290 still occupied the circular lawn. The current recipe removes that third shrub group, bringing the verified removal total to 9,444 triangles. The visible tree counts are unchanged. [EMU exterior and lawn review](emu-green-exterior-2026-11-23.md).

## Editing and reproduction

Edit [the reviewed tree list](../data/metadata/pilot-tree-clearance.json) and regenerate the [runtime patch](../apps/web-preview/public/scene/pilot-green-tree-clearance.json) with `python scripts/build-pilot-tree-clearance.py --tree-input <visual-pilot-input.json> --audit <audit.json>`. The build checks the recorded tree input and GLB hashes. The existing input used here is under the original checkout's `artifacts/` folder.

Images, UO references, checked sample locations and numerical outputs stay in `D:/github/opencampus-interior-research-20261116/exterior-l2/tree-clearance-20261123/`. Run `acquire.py`, `mesh-screen.py` and `plot-review.py` there for the source review. Run `render.mjs` against the local development server to reproduce the paired screenshots and geometry audit.
