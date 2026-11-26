# East Campus housing exterior review

Reviewed on 2026-11-24 for Open Campus: UO. The local default scene uses six individual original meshes under the existing selection IDs and the campus building numbers.

| Address | UO | Scene ID | Exterior reviewed |
| --- | --- | --- | --- |
| 1841 E 15th Ave | B0620 | `roof-bef4cf29` | Dark horizontal siding, small south-facing gabled porch with brick bases and a perpendicular garage roof. |
| 1602 Villard St | B0548 | `roof-7dd08283` | Long main ridge steps down to the pale two-gable street elevation. |
| 1778 Villard St | B0609 | `roof-e086d515` | Three-part gabled dormer, supported front porch and detached garage. The garage is part of this selection and has separate ground collision. |
| 1795 Moss St | B0588 | `roof-9fdf719c` | Smaller supported porch gable in front of the main gable and a short side wing. |
| 1800 Columbia St | B0630 | `roof-fb6ac47a` | Broad front gable, tan vertical siding, asymmetric sash widths and a low north and west return. |
| 1848 Moss St | B0589 | `roof-6f41ba80` | Cross gable, pale chimney, blue-green porch trim and central stair. |

The 2025 university inventory and campus plan establish the addresses and building numbers. The model uses state footprints checked against the university outlines and the 2024 orthophoto. The roof planes were reconstructed from two historical elevation grids together with the dated views. Overhangs and steps were modeled as separate geometry. [Building inventory](https://cpfm.uoregon.edu/sites/default/files/2025-09/14_buildings_by_ownership_fy2025-1.pdf) · [Campus plan appendix](https://cpfm.uoregon.edu/cp2025appendices) · [State building outlines](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

The dated visual references are attached to the [model parameters](../data/metadata/east-campus-housing-exterior-review.json). Five frontages are legible in 2024 imagery, with an additional closer 2024 photograph for 1778 Villard. For 1848 Moss, the 2008 view shows the porch beneath the mature tree cover of the 2024 view. The materials and dimensions of obscured wall details, the garage door, and all entrance thresholds remain approximate. The 1778 model has a representative approach to its porch. The temporary fence shown in the 2024 photograph remains outside the reconstructed building geometry. [1778 Villard photograph](https://www.klcc.org/housing-homelessness/2024-06-11/the-graceful-edge-thats-marked-a-dividing-line-between-the-university-of-oregon-and-its-eastern-neighbors) · [1848 Moss historical image](https://www.google.com/maps/@?api=1&map_action=pano&pano=jXFYGt_pnYewgQCjNYpK3g&heading=270) · [1848 Moss July 2024 image](https://www.google.com/maps/@?api=1&map_action=pano&pano=u4H9z0kDBcEcQslNGPc_VQ&heading=270).

## Roof and placement checks

| Address | Shared cells per date | 2013–15 median absolute error, old → new | 2017 median absolute error, old → new |
| --- | ---: | ---: | ---: |
| 1841 E 15th Ave | 116 | 0.976 → 0.155 m | 0.955 → 0.262 m |
| 1602 Villard St | 93 | 0.847 → 0.052 m | 0.932 → 0.553 m |
| 1778 Villard St | 88 | 0.850 → 0.268 m | 0.855 → 0.563 m |
| 1795 Moss St | 101 | 0.840 → 0.282 m | 1.026 → 0.243 m |
| 1800 Columbia St | 101 | 0.151 → 0.118 m | 0.430 → 0.353 m |
| 1848 Moss St | 84 | 0.952 → 0.407 m | 0.621 → 0.496 m |

Both comparisons use the 583 common 1 m cells in visually clear roof windows. The same audit verifies a roof hit at all 642 sampled cells on the expanded outlines and summarizes the 59 cells outside the previous geometry. The dated surfaces support the modeled main roof forms. Present-day field dimensions and occluded roof edges remain to be measured. [2017 surface registration](campus-surface-2017-2026-11-24.md) · [Historical context roofs](context-roof-refinements-2026-11-23.md).

- Twelve paired street and roof views cover all six houses. The replacement removes 1,178 pinned source triangles across three batches and retains the index buffers, attributes and selection IDs of 54 neighbors.
- Checked 7,710 active route edges with 5.070 m minimum clearance to the new collision geometry. The six modeled approaches pass the clearance check. The 1778 Villard garage occupies a separate collision footprint.
- The local default scene counts 519 selections, 398 source-batch members, 13 separate roof treatments and 139 road segments. The [outdoor ledger](asset-refinement-inventory.md) records 123 L2 exteriors, 396 independent L1 buildings, 13 L1 environment groups and 21 historical mappings.
- Production desktop and mobile both verify search by name, the six walkable approaches, and the separate garage footprint. Invalid source anchors, terrain pins, or model bytes each restore the prior source records.

[Editable builder](../scripts/build-east-campus-housing-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/east-campus-housing-exterior-review/site.json).

```powershell
python scripts/build-east-campus-housing-exterior-review.py --audit D:/path/to/east-campus-housing-audit.json
```

Use `--stage <directory>` to build in isolation. Stage and adopted hashes match for the model and descriptor. The research worktree keeps comparison views, coordinate windows and verification output under `exterior-l2/east-campus-20261124/east-campus-housing-stage/`. All work is local pending publication.
