# Zebrafish International Resource Center exterior

The local L2 model registers the completed west addition at 1307 Franklin Boulevard and retains the earlier east building under scene ID `roof-f0cd697a` and UO facility code `B0101`. The west side has a gray concrete masonry base and lower wing, dark vertical metal cladding, two roof levels and a sidewalk. The retained south and east walls use pale siding, a brick base and copper-colored roofs. A small gabled canopy marks the south approach. [UO building history](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/zebrafish-international-resource-center) · [Fortis completion photograph](https://fortisconstruction.com/project/university-of-oregon-zebrafish-international-resource-center/).

## Registration and evidence

The Eugene building layer's footprint 169880 covers 1,107.4 m² and supports registration of the older east layout. The stitched roof envelope has 1,459.69 m². It combines the retained outline with three west polygons traced from the 2024 OSIP orthophoto. Model walls are inset 0.35 m from this envelope and cover 1,387.027 m². The university's reported 5,769 square feet is a gross floor-area update. [Municipal building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [UO space report](https://cpfm.uoregon.edu/sites/default/files/2026-02/fact_sheet_2yr_summary_2024-25_rev.pdf).

The pre-addition photo shows the east cross-gables, brick base and former entrance canopy. The contractor completion image confirms the newer cladding and stepped west volumes. The architect's design image supports approximate north glazing placement where the completion photo has no coverage. The roof, walls and material details use original geometry derived from the observations. Some opening positions, canopy dimensions and the approach threshold are estimated. The newer west roof heights use photo and shadow estimates, pending a post-addition elevation source. The south approach is an estimated walkable point in the viewer. [2019 capital plan, p. 10](https://cpfm.uoregon.edu/sites/default/files/2019_capital_plan_compiled_masterv2.pdf#page=10) · [Rowell Brokaw design image](https://rowellbrokaw.com/blog/2022/3/4/zebrafish-international-resource-center-expansion-featured-in-the-register-guard) · [Coordinates and source pins](../data/metadata/zirc-exterior-review.json).

## Roof verification

The adopted mesh covers all 1,317 buffered roof sample cells. Three historical 1 m surfaces support a before-and-after comparison on the retained roof. The table gives the median absolute elevation difference in meters across common cells.

| Surface | Light roof, 437 cells | East copper-colored roof, 92 cells |
| --- | ---: | ---: |
| 2013–2015 | 0.520 → 0.142 | 2.029 → 0.251 |
| 2017 | 0.407 → 0.057 | 2.157 → 0.364 |
| DOGAMI Lane County | 0.446 → 0.032 | 1.913 → 0.518 |

## Runtime verification

Four paired views show the west expansion, retained south canopy, complete roof and north wing. Registration removes 408 old building triangles from the context batch while preserving the surviving mesh arrays and indices for 11 neighbors. The nearest of 7,710 route edges is 12.3037 m from the adopted footprint. The viewer blocks the three tested building probes and leaves the tested west and south exterior points clear.

Desktop and phone production both verified the named search result, the walkable south approach and a count of 516 selectable buildings, 329 batched buildings and seven independent context roof treatments. An invalid source anchor restores the old exterior. Formatting, 195 unit tests, six focused browser tests and the production build passed. The archive and viewer hash checks passed. The model is local and uncommitted. [Builder](../scripts/build-zirc-exterior-review.py) · [Adopted descriptor](../apps/web-preview/public/scene/zirc-exterior-review/site.json).
