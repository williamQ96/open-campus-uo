# Fairmount Boulevard residential exteriors

Reviewed on 2026-11-24 for Open Campus: UO. Seven additional Fairmount Boulevard houses use registered L2 exteriors in the local default viewer.

| Address | Scene ID | Exterior modeled |
| --- | --- | --- |
| 1705 Fairmount Blvd | `roof-41f5448c` | Low cross gables, gray siding, dark garage door and inset wood entry. |
| 1799 Fairmount Blvd | `roof-57f699be` | Butterfly roof, 49 modeled solar modules, timber soffit and covered space below the upper deck. |
| 1834 Fairmount Blvd | `roof-8aa49f9b` | Dark lap siding, crossing gable, Walnut-side approach and attached garage. |
| 1892 Fairmount Blvd | `roof-e057643a` | Low street entrance cover, multi-part roof, timber balcony and lower alley garage. |
| 1925 Fairmount Blvd | `roof-7bb19f64` | Low front roof, broad windows and raised clerestory facing Fairmount. |
| 2055 Fairmount Blvd | `roof-72b4d323` | Tan split-level walls, two roof directions, front stairs and lower garage. |
| 2094 Fairmount Blvd | `roof-78a95ac1` | Gabled main frontage and lower north garage wing off Orchard. |

Municipal addresses align with the state outlines. The 2024 imagery distinguishes the roof slopes and the solar array at 1799. Dated street panoramas show its timber overhang and the raised 1892 alley balcony. 2025 exterior listing photographs resolve the garage and entrance at 1705 and 2055. The models use original geometry and material colors. Tree-obscured walls, thresholds, stair and guardrail dimensions and the solar module count are approximate. [Editable registration](../data/metadata/fairmount-residential-exterior-review.json) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [1799 street view](https://www.google.com/maps/@?api=1&map_action=pano&pano=RVc5Vy1Nm7y0WJ699beK-g&heading=124) · [1892 alley view](https://www.google.com/maps/@?api=1&map_action=pano&pano=JrqLKtKiYzxIYS4fbkW8jQ&heading=90) · [1705 listing photos](https://www.redfin.com/OR/Eugene/1705-Fairmount-Blvd-97403/home/25862409) · [2055 listing photos](https://www.redfin.com/OR/Eugene/2055-Fairmount-Blvd-97403/home/26259271).

1667 Fairmount stays L1. It is about 92 m behind the boulevard, and the nearer Rose Lane image shows a different frontage in the line of sight. Its roof remains identifiable in overhead imagery, with tree returns at the west edge of both footprint and surface evidence.

## Verification

| Address | Common cells | 2013–15 median absolute error, source → L2 | 2017 median absolute error, source → L2 |
| --- | ---: | ---: | ---: |
| 1705 | 196 | 0.729 → 0.547 m | 0.785 → 0.164 m |
| 1799 | 108 | 3.994 → 0.391 m | 3.594 → 0.077 m |
| 1834 | 93 | 0.911 → 0.383 m | 1.067 → 0.330 m |
| 1892 | 115 | 1.161 → 0.512 m | 1.046 → 0.203 m |
| 1925 | 104 | 1.545 → 0.234 m | 1.360 → 0.054 m |
| 2055 | 147 | 1.052 → 0.217 m | 0.908 → 0.137 m |
| 2094 | 122 | 1.379 → 0.756 m | 1.169 → 0.188 m |

Both surfaces cover all 969 sampled cells. The model and the source mesh both have roof hits at 885 cells. The older 90th-percentile errors rose at 1705 and 1925. At 2055, the 13 newly covered 2017 edge samples have a median error of 7.091 m. The overhead and paired surface views show tree returns near those added edges. The prior Fairmount package re-exported with the same GLB and descriptor bytes. [2017 surface provenance](campus-surface-2017-2026-11-24.md).

- Fifteen paired views cover seven houses. The isolated replacement removes 1,686 triangles in one source batch and preserves the original vertex data and indices for 50 other members.
- Static checks cover 7,710 route edges with a nearest clearance of 5.626 m. The seven homes retain their source IDs and register seven entrance approaches. Collisions leave space under the 1799 overhang and under the 1892 balcony, with the balcony supports marked solid.
- The production build, 195 JavaScript tests, 26 layer tests, 317 archive checks and 247 viewer hashes passed. Desktop and mobile production confirmed seven searchable entries, seven open-space samples and four blocking support samples in each mode. Source anchor, terrain and GLB failure checks restored the seven sources. The 36-case Playwright run passed 34 cases. After updating two fallback-census assertions, both affected files passed all four cases.

- The local preview has 519 selectable buildings, 350 source-batch members and 13 separate context roof treatments. The [outdoor ledger](asset-refinement-inventory.md) has 171 L2 buildings, 348 active L1 buildings, 13 L1 outdoor groups and 21 historical mappings.

[Builder](../scripts/build-fairmount-residential-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/fairmount-residential-exterior-review/site.json).

```powershell
python scripts/build-fairmount-residential-exterior-review.py --audit D:/path/to/fairmount-residential-audit.json
```

Add `--stage <directory>` for an isolated export. Stage and adopted asset bytes match. Renders and audits are in the research worktree under `exterior-l2/east-campus-20261124/fairmount-residential-stage/`. This change is local.
