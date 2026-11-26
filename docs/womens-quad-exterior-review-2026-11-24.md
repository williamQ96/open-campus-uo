# Susan Campbell Hall and Hendricks Hall exterior review

The local default preview adopts the two rebuilt exteriors facing the Women's Memorial Quad. Susan Campbell Hall uses UO building 075 and `roof-fd061857`. Hendricks Hall uses UO 071 and `roof-e145c222` for both residential wings and the lower former refectory. The previously unnamed `roof-6cd16f5c` covered part of the same Hall and is retained in the inventory as a source record mapped to `roof-e145c222`. The runtime removes its 452 triangles from the shared context batch. The remaining triangle indices and member IDs match the original batch with only that wing removed. The previous scene and its three source records remain available if the package fails verification.

## Sources and exterior decisions

- The campus footprints register Susan Campbell's L-shaped body and Hendricks's north refectory. The 2024 orthophoto shows the roofs, wing junctions and the two approaches to the quad. The 2013–2015 lidar grid establishes the shared elevation frame. The official building footprints cover 544.95 m² and 785.22 m² in the adopted approximation. [UO Campus Map](https://map.uoregon.edu/) · [OSIP 2024 imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)
- Susan Campbell's east approach has a sloping deck and railings, while its west entrance has the restored portico form. The model uses the pictured brick parapets, oculi, metal balcony rails, two gambrel roof sections and north-side sash. [UO 2026 Susan Campbell assessment, PDF pp. 9–18](https://cpfm.uoregon.edu/sites/default/files/2026-02/susan-campbell-hall_preliminary-hp-assessment_2026_sm.pdf)
- Hendricks gains separate gambrel roof edges, two shed-dormer rows on the main bar, parapet caps, south-facing green awnings and the low refectory roof. The west entrance faces the quad and the east entry faces University Street. [UO 2025 Hendricks assessment, PDF pp. 8–22](https://cpfm.uoregon.edu/sites/default/files/2025-07/hendricks-hall_preliminary-hp-assessment_sm_0.pdf)

Both exteriors were reviewed individually against the project's Knight Library example and reach L2. The builder records the modeled proportions and source hashes. The glazing and masonry rhythms simplify the photographs. Parapet relief, dormer counts in partly obscured stretches, portal positions and measured threshold slopes remain approximate. The entrances provide game interactions with the shared interior preview. Normal scene trees still obscure some elevations, which were inspected with and without that vegetation for comparison. The package uses original CC BY 4.0 geometry and metadata.

Earlier models and evidence remain linked in the [Susan Campbell exterior history](susan-campbell-refinement.md) and [Hendricks placement audit](hendricks-exterior-audit.md).

## Verification

Median absolute vertical differences below compare roof rays against the same 2013–2015 lidar cells used to guide the roof profiles. Cells missed by either version were excluded from the paired statistic. Differences represent historical alignment in the sampled areas.

| Roof section | Paired cells | Prior | Revised |
| --- | ---: | ---: | ---: |
| Susan Campbell main bar | 56 | 0.644 m | 0.522 m |
| Susan Campbell north wing | 36 | 1.292 m | 0.360 m |
| Hendricks main bar | 74 | 0.894 m | 0.216 m |
| Hendricks north wing | 32 | 0.944 m | 0.249 m |
| Hendricks former refectory | 47 | 0.575 m | 0.298 m |

The revised geometry covers all 272 sampled positions, compared with 245 for the previous site. All 7,705 navigation edges were screened and reveal zero new conflicts after moving one dead-end node approximately 1.74 m back from Susan Campbell's registered south wall. The route node and its incident edge keep their original identities. Browser checks cover both building identities, entrance approaches, the amended route, the Susan east entrance round trip and the damaged-package fallback.

Build with `python scripts/build-womens-quad-site-review.py --audit <path-to-audit.json>`. The asset, descriptor and retained inspection traces are linked below. Source images, paired views and lidar comparison results are in the research worktree under `exterior-l2/womens-quad-20261124/`. Work remains local.

[Editable registration](../data/metadata/womens-quad-site-review.json) · [Builder](../scripts/build-womens-quad-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/womens-quad-review/site.json)
