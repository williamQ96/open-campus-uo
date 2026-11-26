# Six street-verified exteriors with earlier roof treatments

Reviewed on 2026-11-24 for Open Campus: UO. Each replacement keeps its existing scene ID and uses original, editable geometry.

| Building | Scene ID | Exterior modeled |
| --- | --- | --- |
| 1951 Onyx Alley | `roof-76af1329` | Tall main roof, lower east wing, shake over lap siding, alley garage and side approach. |
| 1772 Hilyard St | `roof-f447a8a6` | Gabled roof and small south bays, vertical siding, north walk and open west parking below the upper floor. |
| Spencer Apartments, 735 E 19th Alley | `roof-57dfe898` | Crossed gables, sage siding, window bays and a supported exterior gallery. |
| Eugene Institute of Religion, 768 E 16th Ave | `roof-efbfe809` | Staggered flat roofs, buff masonry and recessed glazed entrance with canopy. |
| 1010–1020 E 18th Ave | `roof-aae8fc07` | Continuous brick wall, two separate street entrances and open parking under the west end. |
| 1010 E 20th Ave | `roof-f1651047` | Pale siding, gabled street front, exterior stairs and open east carport. |

Municipal address points and state footprints associate the six records with the modeled outlines. The 2024 orthophoto resolves where roof wings and parking covers meet the main volumes. Street views from 2019–24 and public property photos support the visible façade elements. The model thresholds, obscured openings, support dimensions and lower parking clearance are approximate. The Onyx side entry uses an estimated threshold and position. [Editable registration](../data/metadata/treated-roof-exterior-review.json) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Onyx street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=FLNu36Rq9MnjObrB3ospQQ&heading=50) · [Hilyard parking image](https://www.google.com/maps/@?api=1&map_action=pano&pano=qbbUrlbsl57iZVsooDtZKA&heading=90) · [Spencer listing photo](https://www.rentcollegepads.com/city/eugene-or/listings/spencer-apartments-735-e-19th-alley-21677) · [Institute operator directory](https://local.churchofjesuschrist.org/en/us/or/eugene) · [E 18th entrances](https://www.google.com/maps/@?api=1&map_action=pano&pano=jIkI8-hNc_SQE4CubvtjPQ&heading=180) · [E 20th frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=bXNUTWpCQWunY54XRFjlcQ&heading=180).

## Roof checks

Both historical surfaces cover all 1,883 sampled cells. The prior roof treatment and the new roof both intersect 1,862 samples. Values are median absolute error on those common cells.

| Building | Common cells | DOGAMI Lane County, prior → L2 | 2013–15 archive, prior → L2 |
| --- | ---: | ---: | ---: |
| 1951 Onyx Alley | 105 | 0.929 → 0.522 m | 0.154 → 0.552 m |
| 1772 Hilyard | 373 | 0.553 → 0.313 m | 0.121 → 0.312 m |
| Spencer Apartments | 169 | 1.109 → 0.542 m | 0.162 → 0.729 m |
| Institute of Religion | 692 | 0.082 → 0.078 m | 0.075 → 0.073 m |
| 1010–1020 E 18th | 360 | 0.062 → 0.031 m | 0.055 → 0.061 m |
| 1010 E 20th | 163 | 0.472 → 0.350 m | 0.156 → 0.301 m |

The Lane County medians improved at all six roofs, and the 2013–15 archive medians increased at five. At Spencer and 1772 Hilyard, the roof registrations balance residuals across the two surfaces while retaining the roof forms visible from the ground. The products may overlap in acquisition date. The strongest usable evidence for the heights remains historical. Newly covered edges at the Institute and E 20th have several high Lane County returns. [DOGAMI surface service](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer) · [Lane County acquisition report](https://pubs.oregon.gov/dogami/ldq/reports/2013_2014_OLC_Lane_County_Delivery_2_4.pdf).

## Viewer checks

- Fourteen paired views show the street fronts, roofs and west parking ends. Three batches omit 1,238 source triangles and preserve the original vertex arrays and indices for 158 other members.
- The packages checked 7,710 route edges and cleared the nearest edge by 3.357 m. The default production viewer retains 519 selectable buildings, 344 source-batch members and seven independent context roof treatments.
- Desktop and mobile production each found the six names, seven walkable entrances, three open parking samples and 12 solid support samples. Source anchor, terrain and GLB failure checks each restored all six source ranges and prior roof treatments. All 44 selected Playwright cases passed, including lookup of both E 18th addresses.
- The local [outdoor ledger](asset-refinement-inventory.md) has 177 L2 buildings, 342 active L1 buildings, 13 L1 outdoor groups and 21 historical mappings. Five other context roof candidates retain L1 and have individual evidence gaps documented in the research worktree.

[Builder](../scripts/build-treated-roof-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/treated-roof-exterior-review/site.json).

Use `--stage <directory>` for an isolated export. The staged and adopted assets match byte for byte. The research worktree holds the paired views and the elevation and viewer audits in `exterior-l2/east-campus-20261124/treated-roof-stage/`.

```powershell
python scripts/build-treated-roof-exterior-review.py --audit D:/path/to/treated-roof-audit.json
```

This change is local.
