# Friendly, Collier and McKenzie exterior review

Three registered exteriors retain their existing selection IDs and meet the exterior L2 criteria used for [Knight Library](knight-library-registration-2026-11-23.md). The wall outlines come from the campus map and were registered to the 2024 aerial. Roof heights use the 2017 historical surface, supplemented by dated surveys and photographs. [University map](https://map.uoregon.edu/) · [2024 OSIP aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 campus surface](campus-surface-2017-2026-11-24.md).

| Building | Campus and scene IDs | Map translation east/north | Wall envelope | Modeled entrances |
| --- | --- | ---: | ---: | ---: |
| Friendly Hall | 009 · `roof-556799cc` | −2.48 / +1.13 m | 1,006.317 m² | 3 |
| Collier House | 081 · `roof-e5accf83` | −1.70 / +0.85 m | 351.341 m² | 2 |
| McKenzie Hall | 030 · `roof-f61e9b20` | −2.30 / +1.20 m | 2,622.059 m² | 3 |

**Friendly Hall.** The model represents the pre-renovation exterior, with two west porticoes, a mansard roof, dormers, circular openings, south gables and lower east wings. The two west doors use separate approaches. The campus reports renovation underway, and the facilities assessment describes proposed changes to the later south stair. Portico ornament, dormer dimensions and individual openings are approximate. [Historic assessment](https://cpfm.uoregon.edu/sites/default/files/2024-06/friendly-hall_preliminary-hp-assessment_.pdf#page=10) · [Facilities assessment](https://cpfm.uoregon.edu/sites/default/files/2024-06/friendly-hall-assessment_final-rdcd_revmay2024.pdf) · [UO construction update](https://news.uoregon.edu/content/get-update-construction-activity-around-university-0).

**Collier House.** The main hipped roof, bracketed eaves, chimney stacks, polygonal window bays and painted horizontal siding distinguish the original house from its lower additions. The east porch has open circulation between posts and a white balustrade. The annex entry has its own approach. Bracket spacing, porch steps and annex detailing are approximate. [2025 Collier House survey](https://cpfm.uoregon.edu/sites/default/files/2025-03/collierhouse_2025.pdf#page=4).

**McKenzie Hall.** The exterior has three main roof levels around 7.3, 11.0 and 14.6 m, buff brick and concrete bands, and upper equipment volumes. The south approach crosses a wide stair under the recessed entrance. The east court retains its lower grade, open arcades, retaining walls, steps and paths. Its sampled ground is about 1.16 m below the east edge and the modeled paving at that point sits 0.085 m above the sampled grade. Glazing, furnishings and individual landscape dimensions are approximate. [McKenzie Hall assessment and courtyard photographs](https://cpfm.uoregon.edu/sites/default/files/2025-07/mckenzie-hall_preliminary-hp-assessment_2025_sm.pdf#page=54).

| Building | Eligible roof samples | Paired hits | Previous median absolute difference | L2 median absolute difference |
| --- | ---: | ---: | ---: | ---: |
| Friendly | 786 | 738 | 1.136 m | 0.369 m |
| Collier | 264 | 256 | 0.967 m | 0.406 m |
| McKenzie | 2,311 | 2,165 | 2.862 m | 0.042 m |

The roof comparison uses the same 2017 raster that guided construction, with a 0.99 m footprint inset and building-specific plausible height ranges. The updated exteriors cover all 3,361 eligible samples. The medians compare the 3,159 samples that hit both versions and measure agreement with the source raster.

Twenty paired views cover street and elevated views in toon and PBR, including the two porches and the McKenzie courtyard. Production desktop and mobile checks verified selection, eight walkable modeled approaches and twelve collision probes. All 7,710 active navigation edges passed the modeled clearance screen. Tests with damaged model bytes and an invalid terrain hash restored the preceding group. A representative neighboring batch retained identical position, normal, color and index buffers. The default scene has 524 selectable buildings, including 451 source-batch members, and 139 road segments.

The [editable specification](../data/metadata/friendly-collier-mckenzie-site-review.json) and [builder](../scripts/build-friendly-collier-mckenzie-site-review.py) generate the assets. Run `python scripts/build-friendly-collier-mckenzie-site-review.py --audit <audit.json>` from the project root. Registration overlays, dated references, paired views, roof samples and production verification are in the research worktree under `exterior-l2/east-campus-20261124/`.
