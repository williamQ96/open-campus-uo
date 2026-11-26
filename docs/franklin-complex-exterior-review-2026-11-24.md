# Womack Hall and Franklin Boulevard connected storefronts

Reviewed on 2026-11-24 for Open Campus: UO. Womack Hall and the connected Franklin retail property use L2 exteriors in the local default preview. The retail property has four public approaches under one scene ID.

| Address | Scene ID | Oregon outline | Exterior modeled |
| --- | --- | --- | --- |
| 850 Franklin Blvd, Womack Hall | `roof-b59639cc` | 20-1073454 | Four-level residence, paired facade windows, raised central roof, transverse gables, lower lobby and wing, and a two-pier drive canopy. |
| 1920–1960 Franklin Blvd | `roof-fc0fcc2e` | 20-1073488 | Joined shop wing and market with stepped roof decks and two raised storefronts. The four entrances serve Subway, Cafe Seoul, Hirons and Market of Choice. |

The state outlines and municipal points register the two buildings. The 2024 OSIP orthophoto shows the connected roof of the retail property and Womack's two low north projections. The two dated surface grids distinguish the Womack main ridge from its raised center and the retail west deck from the taller market and loading-side strip. Both models use original geometry and color. [Editable registration](../data/metadata/franklin-complex-exterior-review.json) · [Eugene municipal points](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0) · [OSIP imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface review](campus-surface-2017-2026-11-24.md).

The university's 2026 photo shows Womack's north lobby, the paired windows above its lower roof, and the square columns around the open approach. The 2024 views distinguish the north canopy from the enclosed lobby and show the east return. Glazing dimensions and the low side wing's materials are approximate. [University exterior photograph](https://bushnell.edu/wp-content/uploads/2026/07/bushnell-womack-hall-dorm-exterior.jpg) · [North view](https://www.google.com/maps/@?api=1&map_action=pano&pano=Ihjph2g-fCCtqi-UxKOecA&heading=142) · [East return](https://www.google.com/maps/@?api=1&map_action=pano&pano=pNdX7naZGGPdf2ovJLxrgQ&heading=240).

The city-filed owner letter names all four stores on the connected property. The July 2024 imagery shows the west corner's green base and short covers, and the two raised main entries with curved metal covers. The model uses the west-side positions for the two small doors, with approximate thresholds and dimensions. [Owner letter in city records](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/11?fileID=22) · [Hirons frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=4Gfb3sIQ0oYwqlIf97oeIw&heading=172) · [Villard corner](https://www.google.com/maps/@?api=1&map_action=pano&pano=n26YNPnxHIwqO2YW_OVvzA&heading=160) · [Market entrance](https://www.google.com/maps/@?api=1&map_action=pano&pano=640jAaA3rQM23wF_clbncQ&heading=210).

## Verification

| Building | Shared 2017 roof cells | 2013–15 median absolute error, source → L2 | 2017 median absolute error, source → L2 |
| --- | ---: | ---: | ---: |
| Womack Hall | 1,559 | 1.370 → 0.536 m | 1.191 → 0.171 m |
| 1920–1960 Franklin | 2,622 | 1.186 → 0.101 m | 1.149 → 0.125 m |

The 2017 grid covers 4,385 roof cells, of which 4,181 are shared by source and replacement. The 2013–15 grid covers 4,384 roof cells, with 4,180 shared. Newly covered cells along the Womack boundary have a 10.323 m 90th-percentile discrepancy in the older grid. The 188 newly covered retail cells have a 2017 median discrepancy of 1.143 m, with 4.128 m at the 90th percentile.

- Compared five pairs of street, corner and roof views. The two affected source batches omit 1,372 triangles and retain the same vertex attributes and indices for 79 members in the isolated overlay.
- Checked 7,710 navigation edges. The nearest active edge is 7.697 m from the modeled collision outlines.
- Desktop and mobile production checks verified both search names, five independent approaches, thresholds, the open canopy lane and support collision. Both source ranges returned after an invalid source anchor, terrain hash mismatch or correctly hashed mesh parse failure. All 31 selected Playwright cases passed.
- The default preview has 519 selectable buildings, 366 source-batch members and 13 separate roof treatments. The outdoor ledger records 155 L2 buildings, 364 active L1 buildings, 13 L1 outdoor groups and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).

[Builder](../scripts/build-franklin-complex-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/franklin-complex-exterior-review/site.json).

```powershell
python scripts/build-franklin-complex-exterior-review.py --audit D:/path/to/franklin-complex-audit.json
```

The stage and adopted descriptor and GLB match byte for byte. The earlier Franklin Boulevard and Bardell Avenue packages also matched their previous outputs on re-export. Render pairs, roof reports and the visual audit are in the research worktree under `exterior-l2/east-campus-20261124/franklin-complex-stage/`. Changes are local pending publication.
