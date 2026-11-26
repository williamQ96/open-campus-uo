# Fairmount Boulevard residential exteriors

Reviewed on 2026-11-24 for Open Campus: UO. Seven houses use original exterior geometry in the local default scene. Their municipal addresses are registered under the existing scene IDs.

| Address | Scene ID | Exterior reviewed |
| --- | --- | --- |
| 1610 Fairmount Blvd | `roof-41959677` | Pale siding, crossing roof sections, glazed front entry and light porch rails. |
| 1720 Fairmount Blvd | `roof-4c44850e` | Long main roof, lower south wing and a north driveway gable over the garage. |
| 1740 Fairmount Blvd | `roof-c60174af` | Warm low hip roofs, wide divided sash, pale siding and brick chimney. |
| 1780 Fairmount Blvd | `roof-333eb38f` | Sage siding, long eave, two chimneys and an open garage bay under a front cross gable. |
| 1800 Fairmount Blvd | `roof-8d9a1132` | Pale exterior, broad hips, brick chimney and front garage. |
| 1820 Fairmount Blvd | `roof-29f81172` | Long eave, recessed porch with light posts, dark lap siding and stepped rear mass. |
| 1956 Fairmount Blvd | `roof-9cf9957b` | Two differently pitched low roof sections, broad eaves, a south clerestory strip and garage. |

The registration uses state building outlines, Eugene address points, the 2024 orthophoto, and the 2013–15 and 2017 elevation grids. Each roof plane was fitted or adjusted against the dated surfaces and the visible silhouette. The 1956 frontage uses the clearer November 2020 street view and the 2024 overhead shape. Each public reference and orthophoto hash is stored in the [model parameters](../data/metadata/fairmount-boulevard-exterior-review.json). [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface](campus-surface-2017-2026-11-24.md).

The street references show the open garage gable at 1780, the long roof and light posts at 1820, and the stepped shallow roofs of 1956. Entrance thresholds, garage interiors within the recesses, and partly screened wall details use approximate dimensions. [1780 street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=vXdIbO3sKxt9wO1wV8FS6g&heading=299) · [1820 street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=v8_kVlHKOjrGxV9xWMXkFg&heading=315) · [1956 street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=xe8VWxu4PuXAQIMdDNZfFQ&heading=280).

## Verification

| House | Shared roof cells | 2017 median absolute error, old → new |
| --- | ---: | ---: |
| 1610 | 123 | 1.081 → 0.195 m |
| 1720 | 212 | 1.101 → 0.222 m |
| 1740 | 147 | 1.112 → 0.344 m |
| 1780 | 137 | 0.986 → 0.067 m |
| 1800 | 108 | 1.197 → 0.112 m |
| 1820 | 115 | 1.538 → 0.077 m |
| 1956 | 128 | 1.163 → 0.030 m |

The table compares the 970 cells with roof hits in both versions. The new mesh has a roof hit at all 1,081 samples in the audited windows. All seven medians also improved against the older surface. The 2013–15 90th-percentile error for 1820 increased from 2.797 m to 3.160 m, while the corresponding 2017 error fell from 1.950 m to 0.693 m. The older returns at several roof edges and expanded positions remain uncertain.

- Fourteen paired street and roof views cover the seven houses. The replacement removes 1,089 source triangles on two batches. The 93 retained members preserve their indices, vertex attributes and selection IDs.
- Checked 7,710 route edges and registered seven walkable approaches. The closest route is 12.486 m from the new collision geometry. The covered bay at 1780 allows passage through the entrance while the house behind it remains solid.
- Desktop and mobile production checks passed, including name-based search and the open garage collision. Invalid source anchors, terrain pins and damaged model bytes each restore the baseline. All 20 targeted browser tests passed.
- The local scene has 519 selectable buildings, 391 source-batch members and 13 separate roof treatments. The [outdoor ledger](asset-refinement-inventory.md) records 130 L2 exteriors, 389 independent L1 buildings, 13 L1 outdoor environment groups and 21 historical mappings.

[Editable builder](../scripts/build-fairmount-boulevard-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/fairmount-boulevard-exterior-review/site.json).

```powershell
python scripts/build-fairmount-boulevard-exterior-review.py --audit D:/path/to/fairmount-audit.json
```

Add `--stage <directory>` for an isolated export. Stage and adopted output hashes match. The optional roof clipping grid used by these rotated footprints also passed repeat-export checks for the Villard–Garden and East Campus housing packages. Renderings and the comparison audit are in the research worktree at `exterior-l2/east-campus-20261124/fairmount-boulevard-stage/`. The changes are local pending publication.
