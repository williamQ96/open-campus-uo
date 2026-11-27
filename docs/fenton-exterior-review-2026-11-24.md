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

## Class of 1913 Fountain and Hello Walk

The 2025 Fenton Hall survey identifies the fountain north of the hall and records the missing spout. The 2007 landscape survey shows the stepped basin and round bowl with four sloped supports. The 2017, 2021 and 2025 orthophotos locate the 3.00 × 4.42 m outline. The local scene shows the drained basin. Vertical dimensions and the finish are estimates. [UO Library fountain record](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/class-of-1913-fountain) · [2025 Fenton survey, PDF pp. 4 and 6](https://cpfm.uoregon.edu/sites/default/files/2025-01/fentonhall_2025.pdf) · [Old Campus Quad survey, PDF p. 3](https://scholarsbank.uoregon.edu/server/api/core/bitstreams/58d8e085-01f4-4416-b48b-e8c98d7285a1/content).

The path follows three aerial dates from the E 13th approach past Fenton's east side and the fountain to the bend south of University Hall. The scene adds 242.80 m² of paving and 17 connected navigation edges. Desktop and phone returned the same 105.19 m route from the existing E 13th graph anchor to the north bend. The strip width and links beneath foliage are estimates. The next section of Hello Walk reaches the [University and Villard Hall courtyard](heritage-courtyard-landscape-review-2026-11-27.md) around both sides of University Hall. [Lane County orthophotos](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer).

Independent exports matched byte for byte. The Fenton exterior mesh vertices, faces and colors match the published building. Local paired views and browser checks covered the exposed basin, solid perimeter, clear walkway, its standing height and both prior entry approaches. The expanded landscape is local on top of `63263a9`.

## Class of 1920 drinking bubbler

The 2025 building survey locates the gift east of Fenton. The site preservation plan and Rick Obst's photograph show the fluted base, four curved arms and four individual bowls. The model adds a cast-metal finish, four steel nozzles and a concrete pad near the east edge of Hello Walk. The position and dimensions are estimates from the survey diagram and photographs. Both exports reproduce, and the default desktop and phone previews detect the fixture while keeping Hello Walk open. [Fenton survey, PDF pp. 4 and 6](https://cpfm.uoregon.edu/sites/default/files/2025-01/fentonhall_2025.pdf) · [Site preservation plan, PDF p. 75](https://cpfm.uoregon.edu/sites/default/files/2.0sitespecplansfull.pdf) · [2013 photograph by Rick Obst, CC BY 4.0](https://www.flickr.com/photos/discoveroregon/10499330663/).
