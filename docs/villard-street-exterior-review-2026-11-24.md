# Villard Street exterior review

Reviewed on 2026-11-24 for Open Campus: UO. Six buildings keep their scene IDs and register their Eugene addresses in the local default preview.

| Address | Scene ID | Exterior reviewed |
| --- | --- | --- |
| 1401 Villard St | `roof-efd78630` | Low commercial building with a screened west end, flat main roof, raised parapet, roof housings and an approach along the south wall. |
| 1599 Villard St | `roof-d3e38b75` | Hipped front roof and red doorway, pale shed-roof addition, rear upper cladding and separate garage doors toward Orchard Alley. |
| 1637 Villard St | `roof-bb028710` | Wide front gable with three upper lights, a picture window, and a recessed south porch under the lower roof. |
| 1801 Villard St | `roof-5f1e62f1` | Raised entry, sage cladding, a lower front gable and crossing ridges on the taller main roof. |
| 1969 Villard St | `roof-45158580` | Open, full-width front porch with a central stair, upper sash under the gable, and a lower back addition. |
| 1979 Villard St | `roof-c2d79893` | Two overlapping front gables, a recessed stoop, a brighter rear roof section and a lower east wing. |

The six municipal address points fall within their state building outlines and original scene footprints. The 2024 orthophoto resolves the roof sections and light and dark roof finishes. The 2013–15 and 2017 elevation grids provide dated height checks. The [editable registration](../data/metadata/villard-street-exterior-review.json) includes source hashes, state feature IDs, material colors, roof planes, footprint outlines and entrance hints. [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface](campus-surface-2017-2026-11-24.md).

The 1401 street and alley views show different ends of the shallow block. The wall and roof fit use the address-level identity because the operator and its signage may change. The 1599 garage doors and upper slope are visible from Orchard Alley in 2020. Historical frontage views from May 2018 and November 2020 clarify openings, entry cover and wall treatment at 1599, 1637 and 1801 where the newer summer images contain more vegetation or glare. [1401 street](https://www.google.com/maps/@?api=1&map_action=pano&pano=QD7oKo7rXZf28dh943C8Fw&heading=61) · [1401 alley](https://www.google.com/maps/@?api=1&map_action=pano&pano=7rAMC9KMAVZCL3B7D4Wa6Q&heading=270) · [1599 front](https://www.google.com/maps/@?api=1&map_action=pano&pano=PWTfFn58--Pt86x0_8q8eQ&heading=93) · [1599 alley](https://www.google.com/maps/@?api=1&map_action=pano&pano=h2OljjOjMTGyva75FYiDPg&heading=270) · [1637](https://www.google.com/maps/@?api=1&map_action=pano&pano=HeV6vZG17yQ2BWYF8QAtwA&heading=98) · [1801](https://www.google.com/maps/@?api=1&map_action=pano&pano=ve4NLBtr3yoNFsNSmzKs8w&heading=90).

The 1969 street view and 2026 broker listing both show the broad porch. The detached carport falls outside the adopted house outline and remains outside this replacement. The 1979 street view supports the two front gables and upper sash. Roof edge details, stairs, concealed sides and window dimensions use approximations. [1969 street](https://www.google.com/maps/@?api=1&map_action=pano&pano=SUAmMU8cMoM4xn-GTHv2EA&heading=90) · [1969 RMLS gallery](https://www.realtor.com/realestateandhomes-detail/1969-Villard-St_Eugene_OR_97403_M28388-49753) · [1979 street](https://www.google.com/maps/@?api=1&map_action=pano&pano=BbhWayZiDP0h_ZyAykxZ9Q&heading=90).

## Verification

| Building | Shared roof cells | 2017 median absolute error, old → new |
| --- | ---: | ---: |
| 1401 | 214 | 0.611 → 0.097 m |
| 1599 | 212 | 1.113 → 0.109 m |
| 1637 | 97 | 1.030 → 0.379 m |
| 1801 | 95 | 1.190 → 0.174 m |
| 1969 | 177 | 0.857 → 0.071 m |
| 1979 | 151 | 0.901 → 0.145 m |

The table compares the 946 cells with hits on both meshes. The new meshes have a hit at all 1,021 samples in the audit windows. All six medians also improve against the 2013–15 surface. For 1979 the older shared-cell 90th percentile changes from 1.226 m to 1.317 m while the 2017 value improves to 0.561 m from 1.121 m. At newly covered 1599 edges with tree returns, the 2017 90th-percentile error reaches 3.497 m.

- Fifteen pairs of street, alley and roof viewpoints cover the distinguishing features. The source overlays replace 1,576 triangles across two batches. In the isolated render test all 94 neighboring members and their surviving vertex attributes and indices agree with the source.
- The static check covers 7,710 route edges. The closest existing route is 12.206 m from the new collision outlines. The front porch at 1969 becomes walkable in the model while the house wall behind it remains solid.
- The local outdoor ledger tracks 141 L2 models, 378 independent L1 buildings, 13 L1 outdoor asset groups and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).

[Exterior builder](../scripts/build-villard-street-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/villard-street-exterior-review/site.json).

```powershell
python scripts/build-villard-street-exterior-review.py --audit D:/path/to/villard-street-audit.json
```

Add `--stage <directory>` for an isolated export. Stage and adopted bytes match. The research worktree stores the source plots, model renderings and audit under `exterior-l2/east-campus-20261124/villard-street-stage/`. The package ships original geometry and colors. The changes are local pending publication.
