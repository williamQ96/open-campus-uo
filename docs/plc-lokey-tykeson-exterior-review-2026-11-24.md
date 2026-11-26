# PLC, Lokey Education and Tykeson exterior review

Four registered exteriors meet the L2 comparison documented for [Knight Library](knight-library-registration-2026-11-23.md). The models use university outlines, 2024 OSIP aerials, public campus-map entrances and dated exterior references. The historical roof samples help shape PLC and Lokey Education. [University map](https://map.uoregon.edu/) · [2024 OSIP imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 campus surface](campus-surface-2017-2026-11-24.md).

| Campus record | Selection ID | Map shift east/north | Wall envelope | Modeled entrances |
| --- | --- | ---: | ---: | ---: |
| 008 Prince Lucien Campbell Hall | `roof-8f611273` | −1.20 / +0.48 m | 1,968.798 m² | 4 |
| 007 Lokey Education A/B | `roof-74ecc113` | −1.55 / +0.85 m | 2,450.848 m² | 3 |
| 041 Lokey Education C | `roof-5bbb5fd1` | −1.20 / +0.90 m | 828.808 m² | 2 |
| 103 Tykeson Hall | `context-b0103` | 0.00 / +0.35 m | 1,323.289 m² | 4 |

PLC combines the nine-story tower, one-story auditorium and four-story wing. The tower has concrete banding and fins, dark tile-colored spandrels and brick end walls. The east and south courts follow the existing terrain, whose sampled points differ by about 3.4 m. Court approaches, paving and low edge walls are modeled. The roof topography guides the primary slabs and equipment volumes. [PLC campus survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/plccampbell_2025.pdf#page=4) · [University archive](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/prince-lucien-campbell-hall).

Lokey A/B retains two pitched historic volumes, grouped windows and the lower link along Scholar's Walk. Lokey C follows its separate campus record and the later south-wing proportions, with the recessed south porch and north approach. The C south court uses brick-colored paving. Threshold details, some roof transitions and individual openings are approximated from the available views. [Education building history](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/education-buildings) · [Southwest campus survey and photos](https://cpfm.uoregon.edu/southwest-campus-diagnosis).

Tykeson combines the brick classroom wing, striped terra-cotta portion and glazed Commons. The glazed west wing has a canopy and a terrace behind its guardrail. The north and south portals are recessed and the upper floor steps back. The high roof datum of 20.00 m in the scene frame is an estimate from the architecture study section, plan proportions and completed views. The 2013–15 and 2017 roof grids predate Tykeson. Glazing, terrace details and equipment dimensions are approximate. [Design architect project record](https://www.office-52.com/work/tykeson-hall-university-of-oregon/) · [Existing-building study](https://scholarsbank.uoregon.edu/server/api/core/bitstreams/0e61e8f4-5159-4bba-9f17-b3a02e649b94/content#page=30) · [UO west terrace](https://news.uoregon.edu/content/tykeson-hall-west-lawn-becomes-informal-learning-space).

PLC absorbs `roof-30574cc0` and `roof-4f014745`, with 89.54% and 84.09% of the old footprints within UO 008. Lokey A/B absorbs `roof-9346417e` at 85.94% inside UO 007. The former unnamed C mesh has 88.45% of its footprint inside UO 041 and keeps its ID with the registered name. The replacement removes four anchored spans totaling 2,274 triangles from `context-campus-0-1`. The retained index sequence and the position, normal and color data were verified in the before-and-after scenes. The three absorbed IDs stay in the inventory as historical records.

| Model and surface | Eligible points | Paired roof hits | Median before | Median after |
| --- | ---: | ---: | ---: | ---: |
| PLC, 2017 | 1,628 | 1,354 | 0.625 m | 0.058 m |
| Lokey A/B, 2013–15 | 1,996 | 1,912 | 1.268 m | 0.818 m |
| Lokey C, 2013–15 | 553 | 499 | 1.151 m | 0.319 m |

The comparison uses a 0.97 m interior inset and plausible roof-height bounds. The new roofs cover all 4,177 eligible points. The median absolute differences describe agreement with the same historical data used to guide the models. The 3,765 paired samples include the pieces consolidated into PLC and Lokey A/B.

Reviewed 24 paired renders including toon and PBR. The production scene kept 139 road segments and 7,710 active route edges passed the geometry screen. The desktop and mobile previews verified 13 modeled approaches, 14 collision probes and selection of all four IDs. The three invalid-asset, terrain-hash and source-anchor cases restored the prior scene. The new default has 521 selectable buildings including 447 source-batch members.

The [editable specification](../data/metadata/plc-lokey-tykeson-site-review.json) and [builder](../scripts/build-plc-lokey-tykeson-site-review.py) reproduce the GLB and descriptor. Run `python scripts/build-plc-lokey-tykeson-site-review.py --audit <audit.json>` from the project root. The research worktree at `exterior-l2/east-campus-20261124/` holds georeferenced overlays, source records, render pairs, roof rays and production results.
