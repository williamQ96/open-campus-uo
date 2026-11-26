# Fine Arts Studios and 1600 Millrace Drive exterior review

Four existing selections meet the exterior L2 comparison used for [Knight Library](knight-library-registration-2026-11-23.md). The registered outlines use the university map and 2024 OSIP aerial. The historical 2017 surface verifies the main roof shapes. Photos and the dated site plan inform the visible exterior details and approaches. [University map](https://map.uoregon.edu/) · [2024 OSIP aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 roof-surface evidence](campus-surface-2017-2026-11-24.md).

| University record | Original scene ID | Registered footprint |
| --- | --- | ---: |
| 125A Fine Arts Studios Sculpture | `roof-f37c4e05` | 534.03 m² |
| 125B Fine Arts Studios Ceramics | `roof-1f65a447` | 596.42 m² |
| 125C Fine Arts Studios Metalsmith/Jewelry | `roof-4071cebd` | 543.32 m² |
| 750 1600 Millrace Drive | `roof-37a3afa0` | 1,964.37 m² |

The three studios use timber panel walls, shallow north-rising roofs and four glazed monitors per roof. The studio outlines share a 2.06 m west and 1.20 m north registration. The 1968 plan and later aerial both show the two courts and the covered passages along Gallery Way. The low Ceramics additions follow the later aerial. The adjoining Kiln shelter has a separate gabled roof and collidable timber posts in the Ceramics mesh. Its ground remains open between the posts. The three studio selections use their original IDs, and there is no separate recorded Kiln selection in this stage. Later window divisions, fence details and thresholds remain approximate. [University site plan and photographs](https://design.uoregon.edu/1980s-millrace-and-northsite-complex-active-hub) · [UO Libraries architectural record](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/millrace-studios) · [UO yard and portico notice](https://blogs.uoregon.edu/cpfmnotifications/category/demolition/page/2/).

1600 Millrace Drive uses its two masonry wings, horizontal brick and pale bands, the curved glazed entrance tower, and paired equipment groups on the flat roof. The roof outlines are registered 0.48 m west and 0.52 m north. The office entrance lawn and walk follow the mapped approach area. Glazing modules, garden door dimensions and minor equipment locations remain approximate. [University exterior photograph, PDF page 17](https://pages.uoregon.edu/psi/AR_FINAL_2015.pdf#page=17) · [University landscape survey](https://cpfm.uoregon.edu/sites/default/files/03_north_campus_riverfront_research_park-rfs.pdf#page=9).

| Asset | Eligible 2017 points | Paired | Median before | Median after |
| --- | ---: | ---: | ---: | ---: |
| Sculpture | 373 | 329 | 0.843 m | 0.027 m |
| Ceramics | 429 | 353 | 0.904 m | 0.022 m |
| Metalsmith/Jewelry | 447 | 376 | 0.840 m | 0.038 m |
| 1600 Millrace | 1,711 | 1,678 | 0.724 m | 0.225 m |

The comparison uses a 0.83 m roof inset and elevation limits to screen edge and canopy returns. The new geometry hits all 2,960 eligible points, with 2,736 common before-and-after hits against the modeling raster. Separate rays hit the monitors in each studio. The studio values measure agreement with the historical roof data used to fit the planes.

All four original IDs are now named independent selections. Four source ranges totaling 1,444 triangles are removed across three batches. The kept vertex attributes and exact index order match the previous scene, including the earlier changes in overlapping batches. Reviewed 22 paired views and 7,710 route edges. Production checks cover six walkable approaches, nine collision points, desktop and mobile search, and asset, terrain and late batch-anchor failure cases. The default scene has 517 selections, 439 remaining source-batch members and 139 road segments. Three repeat exports match the model and descriptor byte for byte.

The [editable specification](../data/metadata/northsite-millrace-site-review.json) and [builder](../scripts/build-northsite-millrace-site-review.py) reproduce the packaged geometry. Run `python scripts/build-northsite-millrace-site-review.py --audit <audit.json>` from the project root. The research worktree holds the dated sources, registration traces, comparison images and runtime checks.
