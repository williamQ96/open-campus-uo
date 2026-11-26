# Hilyard Apartments at 973 Hilyard Street

The local viewer includes the previously missing 973 Hilyard building as the standalone L2 exterior `hilyard-apartments-973`. The model includes the stepped hip and lean-to roof, brick bands, two window rows, recessed glazing and blue west entrance awning. The surrounding building IDs and context roof treatments remain in the scene.

## Registration and sources

| Address | Municipal footprint | Source scene finding |
| --- | ---: | --- |
| 957 Hilyard | 149932 | Part of the merged candidate `roof-9feed235`, with 238.85 m² of overlap. |
| 971 Hilyard | 178620 | Part of the same candidate, with 140.57 m² of overlap. |
| 973 Hilyard | 170822 | The 206.70 m² municipal outline had no matching source model. Five 973 address points fall in or along this separate outline on taxlot 1703322402700. |
| 975 Hilyard | 170820 | 247.32 m² overlaps the separate `roof-eab27ea2` candidate. |
| 978 Hilyard | 170348 | Catherine Cornwall Townhouses is across the street and already uses its reviewed L2 model `roof-a3d5625f`. |

The city polygons for 973 and 975 are 1.203 m apart. The previous 975 approximation extended 0.159 m² into the municipal 973 outline. The new 973 wall line is set back 0.30 m from the roof envelope, leaving separate collision footprints. The OSIP 2024 image shows the gray roofs and different building placements. The leasing gallery is filed under 957 and includes an image marked 973, with brick and a blue covered entrance. The 1993 listing connects the 957–971 property to the management entrance at 973. [Municipal building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Municipal addresses](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0) · [Leasing gallery](https://www.apartments.com/hilyard-apartments-eugene-or/ejhh6lm/) · [1993 archived advertisement](https://oregonnews.uoregon.edu/lccn/2004260239/1993-05-25/ed-1/seq-7.pdf).

The new silhouette combines the municipal and aerial boundaries with the three historical elevation rasters. The entrance location along the west wall, canopy depth, individual window divisions and courtyard-side details are estimates. The source facade photograph has no verified capture date. The original geometry uses material colors and modeled features. Source acquisition links, coordinates, elevation plane inputs and hashes are in the [editable site registration](../data/metadata/hilyard-apartments-exterior-review.json).

## Roof comparison

The exported roof hit all 163 1 m cells inside the buffered municipal outline.

| Source surface | Samples | Median absolute difference | 90th percentile |
| --- | ---: | ---: | ---: |
| 2013–2015 | 163 | 0.439 m | 3.656 m |
| 2017 | 163 | 0.138 m | 0.484 m |
| DOGAMI Lane County | 163 | 0.275 m | 1.399 m |

In the 2013–2015 surface, 13 cells are at or below 0 m ENU within the polygon. Using its 150 above-grade cells yields 0.397 m median difference and 3.354 m at the 90th percentile. The historical surfaces disagree most along the lower annex.

## Runtime and validation

The builder verified the city-based wall footprint against all original candidate footprints and checked 7,710 outdoor graph edges. The closest graph edge is 20.7445 m away. An exterior register with a declared new ID accepts the site model or restores the preceding scene if the descriptor is malformed. Three paired renders show the west entrance, southwest view and roof. The graphics audit compared unchanged position, normal and color arrays from 11 unaffected background batches.

Desktop and phone production each showed 516 selectable buildings, 330 batched buildings and seven context roof treatments. The 973 search selected its own model. The route from Bushnell at 770 E 11th reached the west approach in 40 points. A separate cross-street route from 978 did not connect because its nearest source route nodes are on disconnected components. Both local entry points were walkable in the viewer.

Formatting, 195 unit tests, four final focused browser cases, the production build, the asset inventory structure, 329 archive hashes and 262 viewer pins passed. The preceding Hilyard West and former hospital suites also passed during the local integration. The [builder](../scripts/build-hilyard-apartments-exterior-review.py) produces the [runtime descriptor](../apps/web-preview/public/scene/hilyard-apartments-exterior-review/site.json) and GLB. This batch is local and uncommitted.
