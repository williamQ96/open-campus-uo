# Garden Avenue exteriors

Reviewed on 2026-11-24 for Open Campus: UO. The local default scene uses five original exteriors under the existing building IDs.

| Address | Scene ID | Exterior reviewed |
| --- | --- | --- |
| 1848 Garden Ave | `roof-3ac532c7` | Three levels, two shallow roof wings, a raised center roof, three front gable accents and a covered entry. |
| 1901 Garden Ave | `roof-9c95368e` | Riverview Business Park. Stepped hip roofs, horizontal facade bands, a west glazed entry, a ramp and an exterior stair. |
| 1976 Garden Ave | `roof-f2c952e3` | Two office levels, three roof sections, a glazed entry and two groups of solar panels. |
| 2001 Garden Ave | `roof-1a10907d` | Millrace Gardens South Building. Shorter form, three crossing gables, vertical siding and projecting upper window bays. |
| 2001 Garden Ave | `roof-e3c224a3` | Millrace Gardens North Building. Longer form, distinct roof ridges, upper window bays and a separate entry off the courtyard. |

The registration combines Oregon building outlines, Eugene address points, the 2024 orthophoto, and the 2013–15 and 2017 surface grids. The five footprint feature IDs, dated street observations, model dimensions and source hashes are recorded in the [model parameters](../data/metadata/garden-avenue-exterior-review.json). [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface](campus-surface-2017-2026-11-24.md).

The 1848 street image shows three facade gables and its covered entrance. The 1901 tenant photographs show the western approach and exterior stair. The orthophoto resolves two panel groups at 1976, modeled as four rows of 12 and four rows of 23 modules. The individual module dimensions are approximate. [1848 street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=vyxztA_oRYvdTySVyjbPnQ&heading=189) · [1901 tenant photographs](https://www.oregonhealingcollective.com/riverview-office) · [1976 street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=r36QVfUd34JYlfhnwFjrnQ&heading=210).

Millrace Gardens shares one postal address. State features 20-1073466 and 20-1073465 define the two footprints, and their model walls have a minimum 10.715 m separation. The property photograph supports the projecting bays, upper siding and ground-floor rails. The model uses representative dimensions and window spacing where trees obscure details. [Millrace Gardens property photographs](https://www.sunny.com/or/eugene/2001-garden-ave) · [Courtyard street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=4rbb2LAFCnvsAC2TRMzq2Q&heading=30).

The rear building at 1907 Garden Ave, scene ID `roof-c630f067` and state feature 20-1073434, remains L1. Its municipal address and outline agree. The available street view primarily shows the 1901 frontage, leaving the rear office's main facade and entrance unverified. [Site street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=6e2-KCd0mHaSUCLcQc7Gfg&heading=15).

## Verification

| Model | Shared roof cells | 2017 median absolute error, old → new |
| --- | ---: | ---: |
| 1848 | 618 | 0.795 → 0.055 m |
| 1901 | 377 | 1.087 → 0.199 m |
| 1976 | 536 | 1.005 → 0.127 m |
| Millrace Gardens South | 140 | 1.132 → 0.345 m |
| Millrace Gardens North | 184 | 0.973 → 0.245 m |

The table compares 1,855 one-meter cells with hits on both meshes. The new roofs have a hit at all 1,913 samples in the audited windows. The median error against the older surface also falls in all five cases. The 2017 90th-percentile North Building error is still 3.010 m where the study window includes residual canopy and edge returns. The 2017 returns on smaller newly covered edges of 1848 and 1901 are likewise variable.

- Eleven paired exterior and roof viewpoints cover the entries, panel layout and building separation. The two source batches remove 1,186 triangles and retain the exact surviving vertex attributes, indices and 19 neighboring members in the isolated check.
- Checked 7,710 route edges and registered five walkable entrances. The closest existing route is 14.203 m from the new collision geometry. The Millrace Gardens passage stays open and each of the two building interiors blocks outdoor walking.
- Desktop and mobile production checks cover selection by name and the five entries. Invalid source anchors, terrain hashes and damaged model bytes each restore the baseline. The local scene has 519 selectable buildings, 386 source-batch members and 13 separate roof treatments.
- The [outdoor ledger](asset-refinement-inventory.md) records 135 L2 exteriors, 384 independent L1 buildings, 13 L1 environment groups and 21 historical mappings.

[Editable builder](../scripts/build-garden-avenue-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/garden-avenue-exterior-review/site.json).

```powershell
python scripts/build-garden-avenue-exterior-review.py --audit D:/path/to/garden-avenue-audit.json
```

Add `--stage <directory>` for an isolated export. Stage and adopted output hashes match. The renderings and quantitative audit are in the research worktree at `exterior-l2/east-campus-20261124/garden-avenue-stage/`. The review uses public imagery as modeling reference and ships original geometry and materials. The change is local pending publication.
