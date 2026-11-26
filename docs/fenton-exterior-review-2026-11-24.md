# Fenton Hall exterior review

The local preview uses the registered exterior for Fenton Hall (UO 019, `roof-4f0c798e`). It distinguishes the two-story original building and its hipped standing-seam roof, the balustraded east entrance, the elevator and stair tower, and the five-story western stacks with their lower flat roof and masonry parapet. The main façades include the broad eaves and brackets, quoin lines, arched and rectangular windows, stone foundation band and low windows, and the stacks' narrower window rows. The south entrance has nine modeled risers and flanking planters. The site package replaces the previous mass and façade overlays under the original selectable ID and falls back to the earlier version if its source checks fail.

## Sources and registration

- The campus map fixes the wall outline and the OSIP image locates the roof edges, ridge, east terrace, skylight, tower and stacks. The authored outline is 831.12 m² and covers 99.86% of the mapped outline. The original 813 m² model covered 85.44%. The map footprint itself has no stated survey tolerance. [UO Campus Map](https://map.uoregon.edu/) · [OSIP 2024 RGB orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)
- The UO survey and assessment differentiate the original building from the 1914–1924 stacks and tower. The assessment's photo, historic roof plan and 13th Avenue site drawings support the main entry surround and upper sash, east slope skylight and nine-step south entry. The south door was placed from the assessment's diagrams and the campus frontage. The precise sill and planter positions, step dimensions, tower details and lower and rear window spacing remain estimates. [UO historic survey, PDF pp. 1–4, 7](https://cpfm.uoregon.edu/sites/default/files/2025-01/fentonhall_2025.pdf) · [UO entries and skylight assessment, PDF pp. 1, 3–4, 18–20](https://cpfm.uoregon.edu/sites/default/files/fentonhall_entriesandskylightassessment_2016-01-20.pdf)
- The model uses original geometry and materials. The patch replaces three earlier approximate shrubs with planting set back inside the new south planters and retains Tykeson's independently generated planting. The existing route graph passes the footprint and stair clearance screen at 0.42 m. The viewer uses two explicit landing approaches below the modeled stairs to enter the shared interior preview. Model elevations and entrances remain approximate and the campus library publishes its own access directions. [UO Libraries accessibility](https://library.uoregon.edu/accessibility)

## Verification and level

Both model versions were ray-sampled at the same selected cells from the historical 2013–2015 first-return grid. The map and lidar informed the new geometry. The comparison omits perimeter cells, except in the narrow east terrace, and first returns outside the respective roof height ranges to limit tree contamination. [NOAA Digital Coast source dataset](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html)

| Roof region | Paired cells | Prior median absolute difference | Revised median absolute difference |
| --- | ---: | ---: | ---: |
| Original hipped roof | 481 | 2.714 m | 0.076 m |
| Western stacks | 101 | 2.054 m | 0.097 m |
| Connecting tower | 12 | 1.084 m | 0.260 m |
| East terrace | 6 | 0.398 m | 0.050 m |

All 631 selected cells intersect the new roofs. The tower and east terrace have limited paired evidence. The height of the east terrace's raised inner strip comes from the return profile and its detailed construction is inferred.

The individual review against the Knight Library L2 example covers registered massing, principal elevations, roof and entry detail, materials, and scene integration. Nine fixed-camera render pairs compare the two versions, including toon and PBR views. The paired renders use an equal number of draw calls or one fewer, with about 29,900 additional rendered triangles. All 7,705 navigation edges were checked for new conflicts and none were found. The browser checks cover both doors, collision at and below the stairs, Fenton selection, and the previous model fallback.

Rebuild with `python scripts/build-fenton-site-review.py --audit <path-to-audit.json>`. Source captures, sample positions, paired render images and runtime results are in the research worktree under `exterior-l2/fenton-20261124/`. The previous source and visual studies remain in the [Fenton overlay record](fenton-south-refinement.md). The L2 adoption is local.

[Editable registration](../data/metadata/fenton-site-review.json) · [Builder](../scripts/build-fenton-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/fenton-site-review/site.json)
