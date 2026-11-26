# Northeast science complex exterior review

Seven selectable models meet the exterior L2 comparison used for [Knight Library](knight-library-registration-2026-11-23.md). They follow the university map and 2024 aerial with a common 1.13 m west and 0.43 m north registration. The surveys and project photography inform the visible entrances, raised connections and changes after the historical lidar. [University map](https://map.uoregon.edu/) · [2024 OSIP aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 source surface](campus-surface-2017-2026-11-24.md).

| Campus record | Selection ID | Registered outline | Modeled approaches |
| --- | --- | ---: | ---: |
| 037 Onyx Bridge with Cascade Annex West | `roof-a5a51275` | 1,763.398 m² | 3 |
| 028B Cascade Annex East | `roof-0f5fbbd5` | 489.569 m² | 1 |
| 038 Klamath Hall | `context-b0038` | 2,608.202 m² | 2 |
| 040 Huestis Hall | `context-b0040` | 1,550.343 m² | 2 |
| 044 Deschutes Hall | `roof-0ca67b60` | 1,026.554 m² | 2 |
| 045 Streisinger Hall | `context-b0045` | 1,559.851 m² | 2 |
| 046 Willamette Hall | `roof-34f891de` | 2,993.759 m² | 3 |

Onyx uses a raised glazed body with steel X-bracing, end links and separately collidable concrete piers. The two white-clad annexes have distinct ground envelopes beneath the upper volume. Cascade Annex West remains part of the Onyx selection, and Cascade Annex East uses its own original candidate ID with the campus identifier B0028B. The preserved opening has modeled clearance of 4.17–4.22 m at the three checked terrain points. [Onyx survey and site diagram](https://cpfm.uoregon.edu/sites/default/files/2025-01/onyxbridge_2025.pdf#page=4) · [Annex West survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/cascadeannexwest_2025.pdf#page=4) · [Annex East survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/cascadeannexeast_2025.pdf#page=4).

Klamath follows the tall concrete bays, flat mechanical deck and rooftop volumes. The new Huestis exterior includes the west elevator projection, light window framing, recessed south entrance and new roof penthouse. Its rooftop layout uses the later aerial and completed project photographs. The 17.78 m modeled penthouse datum and details of the later wall and roof work are approximate. [Klamath survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/klamathhall_2025.pdf#page=4) · [University Huestis comparison](https://bpb-us-e1.wpmucdn.com/blogs.uoregon.edu/dist/8/16874/files/2024/05/FL-Meeting-5_21_24.pdf#page=43) · [Huestis design architect](https://tvaarchitects.com/project/huestis-hall/).

Deschutes uses a west glazed bay, pitched north and south wings and a recessed green-facing approach. Streisinger includes the brick courtyard, arched lower windows and an elevated connection across the gap toward Klamath. Willamette models the south atrium court, glazed roof peak, separate flat decks, west skylit porch and octagonal corner tower. Window bands stop where the local roof changes height. Roof joins, glazing dimensions and hidden wall details remain approximate. [Project site plan and completion photographs](https://www.usmodernist.org/AR/AR-1991-11.pdf#page=48) · [Deschutes archive](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/deschutes-hall) · [Willamette archive](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/willamette-hall).

The former Willamette composite crossed Klamath, Huestis and Streisinger. The native Willamette ID now follows UO 046. Three redundant footprints enter the historical ledger: the former Pacific-labeled composite at Onyx, the second Willamette candidate and the north Deschutes candidate. Three anchored spans totaling 1,656 triangles are removed from a shared batch, including the East Annex range replaced by its independent model. The prior Lawrence review has to install the corrected Pacific identity before the new group can retire its former alias. If that predecessor fails to install, the original Pacific alias and the previous northeast exteriors remain available.

| Asset | Eligible 2017 points | Paired | Median before | Median after |
| --- | ---: | ---: | ---: | ---: |
| Onyx Bridge | 1,109 | 910 | 1.390 m | 0.222 m |
| Cascade Annex East | 158 | 152 | 0.754 m | 0.168 m |
| Klamath Hall | 2,496 | 2,493 | 1.062 m | 0.052 m |
| Deschutes Hall | 903 | 522 | 1.743 m | 0.745 m |
| Streisinger Hall | 1,352 | 1,272 | 0.999 m | 0.824 m |
| Willamette Hall | 2,727 | 2,098 | 2.942 m | 1.178 m |

The comparison uses a 0.83 m inset and building-specific roof-height limits. It measures agreement with the historical modeling raster. The revised geometry covers all 8,745 eligible points and 7,447 hit both versions. The Huestis roof is excluded from this comparison because of the subsequent renovation. Willamette has the largest remaining median difference.

Reviewed 25 paired view configurations in toon, PBR and campus context. A vertical ray confirms the actual Onyx soffit. The kept shared-batch vertex attributes and index order match the prior scene after excluding the three verified ranges. The 7,710 active route edges pass the modeled clearance screen. Desktop and mobile production checks cover 15 approaches, 14 collision points, seven selections and asset, terrain, batch and predecessor failure cases. The default has 518 selectable buildings, 444 in source batches, and 139 road segments.

The [editable specification](../data/metadata/northeast-science-site-review.json) and [builder](../scripts/build-northeast-science-site-review.py) reproduce the packaged model and descriptor. Run `python scripts/build-northeast-science-site-review.py --audit <audit.json>` from the project root. The research worktree under `exterior-l2/east-campus-20261124/` holds the source overlays, the facade photographs, paired images and runtime evidence.
