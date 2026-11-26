# Level and stepped context roofs

The [local default viewer](http://127.0.0.1:5173/) loads ten new single-level roofs and four two-level roofs. Together with the earlier corrections, 31 context IDs use revised roof geometry across ten existing mesh batches. [Original roofs in the development viewer](http://127.0.0.1:5173/?exterior-review=roof-baseline).

## Selection and measurements

The area-wide screen used the existing 534 IDs and excluded previously reconstructed roofs, authored named buildings, and ambiguous or undersampled footprints. Eligible candidates matched one state footprint reciprocally, with at least 74% overlap of each polygon. The constant roof screen returned 12 candidates, and the stepped screen returned four additional candidates whose two levels were supported by the elevation fits. Fitting, choosing the split and assessing the selected form used disjoint 2 m spatial blocks. Orthophoto review rejected a low-sloped roof and a building with separate eastern roof sections. Fourteen candidates were adopted. [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx), [NOAA Lane County lidar](https://www.fisheries.noaa.gov/inport/item/57407), [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

The table reports median absolute differences from historical 1 m first-return cells reserved for verification. Across all 1,541 cells in the table, the median of the per-building medians moved from 1.086 m to 0.035 m. This measures agreement with historic heights.

| Scene ID | Form | Reserved cells | Previous difference | Revised difference |
| --- | --- | ---: | ---: | ---: |
| `roof-5f1a5ce2` | Single level | 114 | 1.588 m | 0.020 m |
| `roof-f89a9211` | Single level | 77 | 1.330 m | 0.040 m |
| `roof-04683fef` | Single level | 98 | 1.273 m | 0.085 m |
| `roof-77a7eb6c` | Single level | 68 | 1.232 m | 0.030 m |
| `roof-8fea5de9` | Single level | 115 | 1.214 m | 0.080 m |
| `roof-aae8fc07` | Single level | 91 | 1.079 m | 0.060 m |
| `roof-31cf5cf8` | Single level | 23 | 0.910 m | 0.030 m |
| `roof-175d8088` | Single level | 119 | 0.824 m | 0.030 m |
| `roof-57cd5529` | Single level | 151 | 0.804 m | 0.030 m |
| `roof-4cb05afd` | Single level | 122 | 0.733 m | 0.030 m |
| `roof-e17be27c` | Two levels | 111 | 1.102 m | 0.150 m |
| `roof-5e7ce49c` | Two levels | 90 | 1.092 m | 0.010 m |
| `roof-2cbfcd06` | Two levels | 160 | 1.078 m | 0.040 m |
| `roof-efbfe809` | Two levels | 202 | 0.782 m | 0.080 m |

Two rows on the lower deck of `roof-e17be27c` depict the solar arrays visible in the aerial. Panel module count, inclination, roof trim heights, and fascia colors are approximate. The new roof geometry uses the original footprints. Existing walls and their openings are fitted to the revised eaves. Current facade and entrance detail, identities and heights after the historical acquisition remain open. All fourteen entries remain L1.

## Verification and rebuild

Chromium returned the original ID and expected surface height at all twenty inspection points, including the raised and lowered wings and both solar rows. The default-view browser checks cover collision on all fourteen new footprints. The ten affected batches retain 94,068 unchanged triangles in exact source order. Total triangles in those batches moved from 100,543 to 104,953. Draw calls matched across fourteen paired detail views and a PBR solar pair.

A stepped-roof correction shares a source mesh batch with an old Frohnmayer wing. The scene translates that wing's original triangle range after applying the roof corrections. The music review removes the wing while preserving 6,580 unrelated triangles in the same batch byte for byte, including the newly stepped roof. Seventeen earlier roof recipes were also compared and matched exactly.

The [editable parameters](../data/metadata/context-roof-refinements.json) feed `python scripts/build-context-roof-refinements.py <audit.json>`. The numerical screens, orthophoto acquisition metadata, checksums and decisions are in the `flat-roofs-20261123` and `stepped-roofs-20261123` folders under `D:/github/opencampus-interior-research-20261116/exterior-l2/`. The first folder also contains the matched render and integrity audit. The runtime bundle contains original geometry and color values. The aerial originals remain in the research archive.
