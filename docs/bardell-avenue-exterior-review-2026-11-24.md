# Bardell Avenue exterior review

Reviewed on 2026-11-24 for Open Campus: UO. Six Bardell Avenue houses use L2 exteriors in the local default preview under their existing scene IDs and Eugene addresses.

| Address | Scene ID | State outline | Exterior reviewed |
| --- | --- | --- | --- |
| 3324 Bardell Ave | `roof-3415fe97` | 20-1073205 | Long gray roof with a central cross roof, a raised gabled entry with broad stone piers and glazing, and single and double garage doors with window strips. |
| 3330 Bardell Ave | `roof-119eb630` | 20-1073180 | Dark main ridge, lower hip over the projecting garage, two pale garage doors with brick piers, and a recessed entry. |
| 3336 Bardell Ave | `roof-892a3891` | 20-1073206 | Long shallow hip with light roofing on the west, a lower intersecting hip on the east, and light masonry toward the street. |
| 3344 Bardell Ave | `roof-57234f59` | 20-1052444 | A main ridge, a lower western return and a transverse gable with pale cladding over the double garage. Square masonry piers frame the entry. |
| 3345 Bardell Ave | `roof-045d51bb` | 20-1052452 | A compound hip with a lower garage wing, three pale garage doors separated by masonry, and a red entry door. |
| 3355 Bardell Ave | `roof-6b824894` | 20-1052447 | Crossing ridges with a lower driveway hip, brick and pale siding, an arched entry transom, and curved heads over the garage panels. |

The six municipal address points lie inside both the original scene footprints and the state outlines. The 2024 orthophoto shows the ridges, finish breaks and driveway alignments. The 2017 and 2013–15 surface grids constrain roof heights where the roof is visible. The editable registration records the source hashes, state features, roof sections, finish colors and approach hints. [Editable registration](../data/metadata/bardell-avenue-exterior-review.json) · [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface](campus-surface-2017-2026-11-24.md).

The 2015 listing for 3324 clarifies the entry and garage doors beneath tree cover. Two street views resolve the garage bays at 3330. The camera position on the opposite side of Bardell helps identify the 3336 and 3344 frontages. The paved approach at 3336 supports an approximate entry, while the garage door position and count remain unverified. [3324 listing](https://www.redfin.com/OR/Eugene/3324-Bardell-Ave-97401/home/26112348) · [3330 frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=2jBw2fx1L1TGZKiq-4GMUA&heading=272) · [3336 frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=cnPnU8LD8-YsmtpS0qlhzA&heading=267) · [3344 frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=2VDDO45o4YnpP4bUtnex-Q&heading=251).

The 3345 gallery shows the three pale garage doors and the red entrance. The 3355 broker gallery shows the curved garage panels and entry transom. Across the six houses, foliage obscures some roof seams, eaves and rear walls. The entry locations, thresholds and opening dimensions use approximations where the photographs and orthophoto do not resolve them. [3345 listing](https://www.trulia.com/home/3345-bardell-ave-eugene-or-97401-48459262) · [3355 listing](https://www.zillow.com/homedetails/3355-Bardell-Ave-Eugene-OR-97401/48459263_zpid/) · [3355 frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=xfsH0iFh2wogpoCVd42UpA&heading=80).

## Verification

| Building | Shared roof cells | 2013–15 median absolute error, old → new | 2017 median absolute error, old → new |
| --- | ---: | ---: | ---: |
| 3324 | 453 | 0.867 → 0.507 m | 0.774 → 0.092 m |
| 3330 | 243 | 0.993 → 0.632 m | 0.910 → 0.207 m |
| 3336 | 252 | 1.182 → 0.793 m | 0.909 → 0.074 m |
| 3344 | 257 | 1.005 → 0.336 m | 0.802 → 0.235 m |
| 3345 | 190 | 1.319 → 0.460 m | 1.133 → 0.265 m |
| 3355 | 213 | 1.049 → 0.494 m | 1.216 → 0.192 m |

The 1,608 shared cells had a roof hit in both the source and the staged replacement. The new roofs cover all 1,866 sampled cells in the audit windows. At 3324, tree returns on newly covered edges raise the 90th-percentile error to 7.535 m against the 2017 surface and 11.634 m against the 2013–15 surface.

- Twelve paired street and roof viewpoints cover the six houses. The isolated overlay removes 2,438 triangles from `context-background-3-3` and preserves the source vertex attributes and indices of the 19 retained neighbors.
- The static collision check covers 7,710 route edges. The nearest existing route is 13.586 m from the new collision outlines.
- Desktop and mobile production checks verified all six addresses in search, their entrance thresholds and approach points, ordinary facade snapping and collision at the porch piers. The original meshes and entries returned with a shifted source anchor, a mismatched heightfield hash or an invalid GLB with a valid hash.
- All 26 selected Playwright tests passed, including both Bardell cases. The run took 4.2 minutes with a 120-second timeout per test.
- The default preview has 519 selectable buildings, with 374 source-batch members and 13 separate roof treatments. The outdoor ledger records 147 L2 buildings, 372 independent L1 buildings, 13 L1 outdoor asset groups and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).

[Exterior builder](../scripts/build-bardell-avenue-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/bardell-avenue-exterior-review/site.json).

```powershell
python scripts/build-bardell-avenue-exterior-review.py --audit D:/path/to/bardell-avenue-audit.json
```

Add `--stage <directory>` for an isolated export. The staged descriptor and GLB match the adopted files byte for byte. The research worktree stores the render pairs and roof metrics under `exterior-l2/east-campus-20261124/bardell-avenue-stage/`. The export uses original geometry and colors. The changes are local pending publication.
