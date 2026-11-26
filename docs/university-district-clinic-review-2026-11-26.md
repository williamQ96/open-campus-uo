# University District clinic, garage and office exterior review

The local scene splits the two source records at 1200 Hilyard and 677 E 12th into three independently selectable L2 exteriors. The 2024 Oregon orthophoto establishes the roof boundaries. The owner, operator and listing references document the six-story clinic, attached South Garage and separate North Building. [2024 Oregon ortho](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [1200 Hilyard sale and attachment](https://www.jll.com/en-us/newsroom/jll-completes-monetization-of-1200-hilyard-st-in-eugene) · [Owner photograph](https://montecitomac.com/news/montecito-medical-acquires-peacehealth-outpatient-asset/) · [North Building listing](https://invest.jll.com/us/en/listings/office/university-district) · [Operator site map](https://www.peacehealth.org/sites/default/files/2022-03/Sacred-Heart-University-District_campus.pdf).

| Address | Scene ID | Modeled details |
| --- | --- | --- |
| PeaceHealth University District Clinic, 1200 Hilyard St | `roof-4c79682d` | Main block and low north wing, pale piers and blue window bands, recessed Hilyard entrance and roof equipment. The north wing leaves the existing East 12th route clear underneath its modeled overhang. |
| University District South Parking Garage, 650 E 12th Ave | `university-district-650-e-12th-garage` | Lower parking deck with open bays, roof markings, elevator core and short enclosed connection to the clinic. Added as a split from `roof-4c79682d`. |
| University District North Building, 677 E 12th Ave | `roof-4a7d9b5a` | Complete stepped footprint, masonry wall panels, continuous horizontal glazing, canopy and differentiated rooftop mechanical housings. |

## Historical height comparison

Median absolute errors in meters use the cells covered by both the earlier combined source geometry and the new model. The two source ranges are combined for comparison, including the area split out as the garage.

| Exterior | Paired cells | 2013–15 archive, source → L2 | USACE 2017, source → L2 | DOGAMI Lane County, source → L2 |
| --- | ---: | ---: | ---: | ---: |
| 1200 Hilyard | 3,121–3,122 | 4.439 → 0.187 | 4.340 → 0.122 | 4.371 → 0.142 |
| 650 E 12th | 2,910 | 12.101 → 0.084 | 12.170 → 0.046 | 12.140 → 0.064 |
| 677 E 12th | 1,045 | 1.921 → 0.222 | 1.750 → 0.123 | 1.921 → 0.110 |

The 677 model has larger errors at some roof steps. Its 2017 90th-percentile error is 3.528 m on the shared cells, compared with 2.246 m for the earlier surface. A further 207 modeled cells have a 2017 median error of 0.098 m. At the clinic, the 215 newly covered locations include a low wing and joining edges that differ among the dated surfaces. The garage roof extends about 17.75 m west of the source terrain. Its apron and roof elevation use an extrapolated grade there. The connector and overhang have simplified dimensions, and the below-grade levels and operations are outside this exterior review.

## Scene verification

- Seven paired render views cover the three exteriors, roof steps and entrance canopies. The source footprints share an edge, which causes a buffered query to catch some faces from both members. The builder pins the 1,902- and 324-triangle ranges in the original batch. A raw-batch check verifies the original vertex arrays and surviving indices for the other 36 members.
- Static checks cover 7,710 active route edges. The closest is 1.237 m from checked ground walls and supports. Desktop and mobile production each reached the three models by building name and verified three walkable approaches, four clear samples under the portico and overhang, and six blocking samples. A corrupted source anchor restores both earlier candidates and removes the additional garage selection. Default census is 520 selectable buildings, 335 source-batch members and seven independent roof treatments.
- The [descriptor](../apps/web-preview/public/scene/university-district-clinic-review/site.json) and [GLB](../apps/web-preview/public/scene/university-district-clinic-review/site.glb) match the independently staged export byte for byte. The [editable registration](../data/metadata/university-district-clinic-review.json) and [builder](../scripts/build-university-district-clinic-review.py) preserve the geometry and reference provenance. This batch is local.

```powershell
python scripts/build-university-district-clinic-review.py --stage D:/path/to/preview-assets --audit D:/path/to/audit.json
```
