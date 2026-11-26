# University District exterior review

The local production build adopts three L2 exteriors under the original scene IDs and connects the existing 722 E 11th Avenue model to its neighbor.

| Exterior | Scene ID | Modeled details |
| --- | --- | --- |
| Bushnell University, 770 E 11th Avenue | `roof-62a81026` | Four-story main block with banded glazing and rooftop equipment, a low east wing with an open recess, a south entry canopy and the glazed third-floor bridge to 722. |
| 633 E 12th Avenue Parking Garage | `roof-19858777` | Complete deck envelope with the west portion restored, split rooftop grades, open concrete screening, parapets and stair cores. |
| 666 E 13th Avenue Parking Garage & Retail | `roof-bdbcb4fc` | Open deck bays on a stepped footprint, a sloped roof deck, stair cores, and storefront bands on 13th and Hilyard. |

The roof and wall footprints use the 2024 Oregon ortho and compare to the state outline and municipal points. The current documents confirm the 770 identity and retention of the 722–770 bridge, the independent 633 garage and the planned reuse of the 666 deck. The building fabric follows the 2024 aerial phase. The bridge follows the retained third-floor segment between the two Bushnell buildings. The 722 source package supplies its west endpoint. The original model geometry uses vertex colors. [Oregon 2024 ortho](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Bushnell acquisition](https://bushnell.edu/news/bushnell-university-closes-on-university-district-hospital-properties/) · [Bushnell bridge and photograph](https://bushnell.edu/news/the-register-guard-see-inside-bushnells-university-district-campus-renovation/) · [633 listing](https://invest.jll.com/us/en/listings/office/university-district) · [Sale plans, pages 6 and 8](https://res.cloudinary.com/jll-global-cmg/image/upload/v1740167326/Prod/DealX/Doc/be8e7d68-eba7-4679-9ebc-a4d1c17d3f04/University_District_Flyer.pdf) · [Landmark development](https://www.landmarkproperties.com/the-mark-eugene-breaks-ground-donates-10k-to-local-nonprofit/).

## Roof and scene verification

Median absolute height error on cells in each historic surface covered by both the old and new meshes.

| Exterior | Paired cells | 2013–15 archive, source → L2 | USACE 2017, source → L2 | DOGAMI Lane County, source → L2 |
| --- | ---: | ---: | ---: | ---: |
| 770 E 11th | 1,519 | 0.949 → 0.187 m | 0.880 → 0.131 m | 0.889 → 0.144 m |
| 633 E 12th | 805 | 0.848 → 0.268 m | 0.679 → 0.125 m | 0.831 → 0.189 m |
| 666 E 13th | 1,667–1,669 | 0.754 → 0.181 m | 0.705 → 0.198 m | 0.726 → 0.195 m |

The 633 building extends 17.9 m west of the source terrain. The exterior uses the measured roof footprint there and an extrapolated deck elevation over a small modeled apron. The height comparison covers the portion inside the source grid. Newly included 770 and 666 footprint edges have larger disagreements across the historical surfaces, especially around the low roof and tree-shaded perimeter. Roof equipment dimensions, bridge supports, deck markings and storefront spacing are approximate. The modeled bridge roof is 10.51 m ENU across 312 ray samples in the open gap. Bridge interior and parking operations are outside the exterior review.

Seven paired views cover roof shapes, bridge clearance, street elevations and retail frontage. The two affected batches replace 1,506 source triangles, retaining identical vertex arrays and surviving indices for 83 members. All 7,710 active route edges were checked. The nearest route is 2.653 m from the checked ground footprint and supports.

Desktop and mobile production each verified four searchable names, four walkable approaches, four clear samples and seven solid samples including four bridge supports. With the district mesh request failed, the three original source members and the independently refined 722 model remain available. If the 722 package fails, the dependent district pack also falls back. The census is 519 selectable buildings, 337 batch members and seven independent roof treatments.

The registration and original geometry are editable in the [registration JSON](../data/metadata/university-district-exterior-review.json) and the [Python builder](../scripts/build-university-district-exterior-review.py). The [deployed-layout descriptor](../apps/web-preview/public/scene/university-district-exterior-review/site.json) and [GLB](../apps/web-preview/public/scene/university-district-exterior-review/site.glb) match the independent staged export byte for byte. The research directory `exterior-l2/east-campus-20261124/university-district-stage` retains the render, measurement and browser records. This batch is local.
