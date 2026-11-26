# Parkside Place and three south neighborhood exteriors

Four original meshes replace the old context geometry under the same scene IDs. City building polygons and the 2024 Oregon aerial locate the roofs and structural outlines. June and July 2024 street views constrain the visible elevations. The model exporter uses editable dimensions and colors with source links. [Geometry specification](../data/metadata/hilyard-south-exterior-review.json) · [Exporter](../scripts/build-hilyard-south-exterior-review.py) · [City building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

| Exterior | What the local model restores |
| --- | --- |
| Parkside Place, 1448 Hilyard, `roof-f92cf968` | Three hip roofs and two connectors, upper east gabled bay, green siding, balcony rails and a recessed south garage approach with closed shutter |
| 1131 East 20th, `roof-10b438f6` | Higher and lower flat roofs, light gray upper cladding, tall vertical windows and a recessed timber-colored lower entry |
| 1039 East 21st, `roof-769d99e6` | Intersecting front and rear ridges, green front gable and projecting multipane bay window |
| 1145 East 21st, `roof-57ecbd31` | Cream front gable, bay window and vent, chimney, columned gabled porch and brick steps |

Parkside's 21-unit identity is confirmed by a city budget packet. Its visible garage frontage is fitted to the present terrain and kept closed. True ramp depth, parked-car levels and screened residential openings are approximate. The two walkable approaches use estimated stairs and thresholds. The models for 1131 and 1039 leave the scene entrance lists empty because trees screen the complete path and door location. [Parkside budget record](https://www.eugene-or.gov/Archive/ViewFile/Item/4782) · [1145 East 21st frontage photos](https://www.zillow.com/homedetails/1145-E-21st-Ave-Eugene-OR-97403/48409032_zpid/).

## Verification

The rebuilt roofs intercepted all 2,829 available sample rays. The 2,659 cells with observations from both model versions give the paired median absolute differences below. The 2017 comparison has 13 cells, all at Parkside Place.

| Exterior | 2013–15 before → after | DOGAMI before → after | 2017 before → after |
| --- | ---: | ---: | ---: |
| Parkside Place | 0.8337 → 0.8786 m | 0.8458 → 0.1215 m | 0.3752 → 0.1807 m |
| 1131 East 20th | 0.8567 → 0.0570 m | 0.8280 → 0.0487 m | |
| 1039 East 21st | 0.9300 → 0.6307 m | 0.9087 → 0.1814 m | |
| 1145 East 21st | 0.8757 → 0.5385 m | 0.6743 → 0.1561 m | |

The two longer reference surfaces differ in their positioning of the Parkside wing ridges and west connector. The old surface tracks the previous roof slightly more closely in the paired median. The adopted roof follows the aerial interpretation and the DOGAMI profile, with the documented difference carried forward for review.

Ten matched view pairs examine frontages, the closed garage approach and the new roofs. Exact geometry comparison across three source batches retains 160 peer records and removes 1,531 source triangles. The exporter checks 7,710 route edges. Repeat, installed, built and served assets match the staged bytes.

Desktop and phone verified four searchable buildings, two walkable approaches and ten solid/open collision probes. Routes from Knight Library finish at the Parkside pedestrian approach in 58 points and at the 1145 East 21st porch approach in 194 points. Independent bad model bytes and an invalid source anchor restore the old meshes and approaches. The default local scene has 524 selectable buildings, 269 batched buildings, two independent context roof treatments and 598 approaches.

All four exteriors are registered as L2. This revision is local and uncommitted.
