# West study boundary exteriors at East 17th and East 19th

The local model splits the merged East 17th source candidate into three registered buildings. Eight municipal address points establish which addresses each polygon serves. The East 19th replacement retains its previous scene ID. All four meshes stay inside the current 2 km study area. [Editable geometry and source references](../data/metadata/west-boundary-exterior-review.json) · [Exporter](../scripts/build-west-boundary-exterior-review.py) · [City footprint layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

| Building | Scene ID | Level and visible work |
| --- | --- | --- |
| 625–627 East 17th Avenue | `roof-dcd48157` | L2. Street gable, two eyebrow vents, chimney, olive siding and open recessed porches. One estimated approach serves the visible west porch. |
| 630–632 East 16th Alley | `e16-alley-630-632` | L2. Separate nearly flat roof, stepped footprint, pale walls and the upper sash visible from the north. Side openings are approximations. |
| 634–640 East 16th Alley | `e16-alley-634-640` | L1. Independent outline and roof ridge. The main elevations remain screened in the registered views. |
| 631 East 19th Avenue East Building | `roof-4dff8a97` | L2. Two sloping roofs, red masonry base, siding, north clerestory and tower. Rear openings are modeled with approximate dimensions. |

The former church and education leasing material documents the site's prior use. The east building label is based on the registered outline. Public directions for Building B point toward the westerly courtyard building. The east building's current use remains open, so the model has no authored wayfinding gate. [Broker listing and flyer](https://www.cityfeet.com/cont/listing/631-e-19th-ave-eugene-or-97401/cs20806005) · [Building B address](https://healingattention.org/contact/) · [Public event directions](https://dailyeugene.com/or/eugene/events/evt_TJafgtTXv3za).

## Verification

The four roofs intercepted 1,622 of 1,726 sample rays. At the East 19th east edge, the 2024 aerial and DOGAMI support a narrower outline than the City polygon. The omitted 52 points per reference are at eastings −977.5 and −976.5 m. Their medians are 0.729 m in DOGAMI and 5.512 m in the 2013–15 surface. The west edge is clipped at −1,000 m. The roof comparison uses 1,534 paired cells.

| Exterior | 2013–15 before → after | DOGAMI before → after |
| --- | ---: | ---: |
| 625–627 East 17th | 0.7630 → 0.6516 m | 0.6660 → 0.2131 m |
| 630–632 East 16th Alley | 1.0602 → 0.0267 m | 0.9926 → 0.0213 m |
| 634–640 East 16th Alley | 1.6036 → 0.8178 m | 1.7053 → 0.0875 m |
| 631 East 19th east building | 1.1786 → 0.0612 m | 1.1168 → 0.3150 m |

Nine matched cameras cover the four exteriors. Exact geometry checks preserve 105 peers in two source batches while removing 573 source triangles. The exporter checks 7,710 route edges. The earlier Hilyard package and the new package reproduce their installed bytes.

Desktop and phone production both select the four buildings and verify nine collision probes, including the alley gap and the open portion of the porch. The route from Knight Library reaches the estimated south porch in 93 points. Independently corrupt GLB bytes and an invalid source anchor restore the two source candidates and their old approaches. The default local scene now has 526 selectable buildings, 267 batched buildings and 597 approaches.

Three exteriors pass the local L2 review. This revision is local and uncommitted.
