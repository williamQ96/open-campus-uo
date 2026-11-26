# East Broadway and Orchard exterior review

Reviewed on 2026-11-24 for Open Campus: UO. Nine source IDs now use L2 exteriors in the local default preview.

| Address | Scene ID | Exterior modeled |
| --- | --- | --- |
| 652 E Broadway | `roof-b40f786d` | Purple storefront, yellow cover and low street fascia with raised ends. |
| 659 E Broadway | `roof-f8b27077` | Stepped parapets, brick accents, pale covers, glazed parking-side entry and exterior drive-through lane. |
| 686 E Broadway | `roof-060ab58a` | Two tiers of glazing in red and dark framing, green cover along Hilyard, and the stepped rear roof. |
| 782 E Broadway | `roof-6c97d6b4` | Hip and front gable, chimney, octagonal vent, pale siding and brick skirt. |
| 1432 Orchard St | `roof-b3252193` | Flat upper floor over the open frontage, blue fascia, column supports and exterior stair. |
| 1468–1476 Orchard Aly | `roof-bb9ee65a` | One connected roof above three municipal addresses, raised east wall and four modeled posts around the covered parking. |
| 1505 Orchard St | `roof-a8a115d2` | Four stepped wings and a planted courtyard with a walkable gap. The courtyard facing includes one approximate entrance. |
| 1838 Orchard St | `roof-846446eb` | Lower rear roof, higher hip, muted green siding, broad east window and red entry. |
| 2059 Orchard St | `roof-8eff0cee` | Intersecting roof slopes, pale siding and entry stairs with rails. |

The footprints and municipal points register each building. The 2024 orthophoto defines the main outlines, wings and the courtyard gap, while the 2013–15 and 2017 surfaces constrain the roof fits. Dated storefront views identify the purple and yellow 652 storefront, the 659 awnings, the glazed former brewery, and the hip and chimney at 782. The adoption uses address names and the June and July 2024 facade conditions. The export uses original geometry and material colors. [Editable registration](../data/metadata/broadway-orchard-exterior-review.json) · [Address points](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0) · [2024 Oregon imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface review](campus-surface-2017-2026-11-24.md).

The 1432 street view shows the animal hospital's lower entry and upper stair. The 2020 Orchard Alley panoramas show the continuous parking-side beam, siding and stall posts. The 1505 street-side and alley views show the two exterior levels. The open courtyard uses the 2024 footprint and ortho crop, with approximate planting beds and interior-facing entrance. Door, stair and equipment dimensions, canopy post positions and tree-obscured details at 1838 and 2059 remain approximate. [Lane County clinic directory](https://www.lanecounty.org/government/county_departments/public_works/general_services/animal_services/lost_a_pet_/lane_county_veterinary_clinics) · [1432 frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=cir1V30KUJdPfCvchO-spw&heading=270) · [Orchard Alley parking frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=ZwmVzMjUb0bBZiX4ztiMEw&heading=220) · [1505 west frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=yf-x46fWtDmEcnabhDyX2w&heading=89).

## Verification

| Address | Shared roof cells | 2013–15 median absolute error, source → L2 | 2017 median absolute error, source → L2 |
| --- | ---: | ---: | ---: |
| 652 E Broadway | 276 | 0.854 → 0.275 m | 0.848 → 0.140 m |
| 659 E Broadway | 228 | 0.996 → 0.516 m | 1.056 → 0.075 m |
| 686 E Broadway | 201 | 0.861 → 0.180 m | 0.859 → 0.132 m |
| 782 E Broadway | 317 | 0.884 → 0.335 m | 0.823 → 0.237 m |
| 1432 Orchard | 416 | 0.936 → 0.056 m | 1.003 → 0.024 m |
| 1468–1476 Orchard Alley | 191 | 1.502 → 0.790 m | 1.302 → 0.168 m |
| 1505 Orchard | 903 | 0.716 → 0.200 m | 0.611 → 0.147 m |
| 1838 Orchard | 184 | 1.017 → 0.356 m | 1.208 → 0.076 m |
| 2059 Orchard | 166 | 0.996 → 0.461 m | 0.974 → 0.115 m |

Both dated surfaces cover all 3,057 sampled cells. The 2,882 shared cells hit both source and replacement. Old returns at the newly covered 1468–1476 edges have a 90th-percentile difference of 4.014 m. New 2017 cells at 652 have 3.674 m at the 90th percentile across five samples.

- Nineteen paired views cover the nine buildings, including one courtyard view at 1505. The isolated replacement removes 1,948 triangles from four source batches and preserves all surviving vertex data and indices for 135 retained members.
- The static check covers 7,710 route edges. The nearest existing route lies 5.820 m from the new collision outlines.
- The production build, 195 JavaScript tests, 26 layer tests, 315 archive checks, 245 viewer hashes and 34 selected Playwright cases passed. Desktop and mobile production checks confirmed all nine addresses and entrance approaches, seven clear passage samples and ten blocking support or wall samples in each mode. Independent source-anchor, terrain and GLB failures returned all nine source members.
- The default preview has 519 selectable buildings, 357 source-batch members and 13 separate context roof treatments. The outdoor ledger tracks 164 L2 buildings, 355 independent L1 buildings, 13 L1 outdoor groups and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).

[Builder](../scripts/build-broadway-orchard-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/broadway-orchard-exterior-review/site.json).

```powershell
python scripts/build-broadway-orchard-exterior-review.py --audit D:/path/to/broadway-orchard-audit.json
```

Add `--stage <directory>` for an isolated export. Stage and adopted GLB and descriptor bytes match. The earlier Franklin Complex and Villard–Garden packages remained byte-identical on re-export. The paired views and audit files are in the research worktree under `exterior-l2/east-campus-20261124/broadway-orchard-stage/`. Changes are local pending publication.
