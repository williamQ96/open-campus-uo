# Thirteen hillside exteriors on Fairmount, Summit, Hamble and Hubbard

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `roof-0b345e8f` | 159897 | 2081 Fairmount Boulevard. Craftsman roof with two gabled dormers and a capped brick chimney. Raised porch has square columns and a brick approach. |
| `roof-3d7a4503` | 159873 | 2091 Fairmount Boulevard. Two shallow roof directions and a pale recessed street wall. |
| `roof-61b268c3` | 159874 | 2095 Fairmount Boulevard. Low ranch with a light street gable and double garage. |
| `roof-d709354e` | 159875 | 2105 Fairmount Boulevard. Dark renovated roof, light siding, recessed door bay under the cross gable and two curved brick terrace walls. |
| `roof-8d4cf396` | 159876 | 2125 Fairmount Boulevard. Long shallow roof, tall downhill window band and street-side garage. |
| `roof-3466a919` | 159881 | 2209 Fairmount Boulevard. Stepped roof sections follow the rotating footprint with estimated wall openings. |
| `roof-b8804a72` | 159852 | 2130 Summit Avenue. Two roof levels, including a pale low roof. |
| `roof-efd79ec7` | 159837 | 2195 Summit Avenue. Separate low roof sections follow the City outline. |
| `roof-d25e3df8` | 159838 | 2197 Summit Avenue. Stepped roof and high glazing on the south elevation visible in 2024. |
| `roof-636f0355` | 159869 | 2110 Hamble Avenue. Independently modeled intersecting roof planes. |
| `roof-b2bced50` | 159868 | 2140 Hamble Avenue. Separate shaped roof and clear driveway. |
| `roof-99cda8af` | 159854 | 2171 Hamble Avenue. Two low roof sections and an estimated east-facing wall finish. |
| `roof-f5434b03` | 159855 | 2010 Hubbard Lane. Long west wall and angled roof sections, with estimated finish. |

The models use City outlines, Lane County aerials from 2017, 2021 and 2025, historical elevation samples and 24 distinct street frames. The 2020 and 2022 views support the porch, dormers and chimney at 2081. The 2025 listing supports the light gable and two-bay garage at 2095. The 2026 listing at 2105 gives the post-renovation roof and wall finish, recessed entry and curved terrace walls. The 2105 and 2125 outlines reach about 8.48 m and 0.04 m beyond the terrain's southern edge. Short modeled terrain aprons extend the local grade below those footprints. Both pedestrian approaches, brace and stair dimensions, and terrace grades are approximate. [City outline service](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [2095 listing](https://whipplehomes.com/homes-for-sale-sold-details/2095-FAIRMOUNT-BLVD-EUGENE-OR-97403/722191207/54/) · [2105 agency photos](https://dcfinehomesre.com/home-search/listings/2466272594170022694-2105-FAIRMOUNT-BLVD) · [2105 renovation chronology](https://www.realtor.com/realestateandhomes-detail/2105-Fairmount-Blvd_Eugene_OR_97403_M28397-06870).

The selected street bearings yielded no useful images for 2130 and 2195 Summit or 2110 and 2140 Hamble. Entrances remain unassigned at these four and seven other models with screened or unverified approaches. Views at 2171 Hamble and 2010 Hubbard are heavily screened. The 2197 Summit photos document the south side. Its principal entrance location remains unverified. The published assets use original geometry and material colors. [Editable model input](../data/metadata/fairmount-summit-hamble-review.json).

All 8,774 vertical survey rays hit an adopted roof. Across 6,743 paired cells, 32 of 35 median absolute errors decrease. The 2197 Summit median increases from 0.8854 to 0.8865 m in the 2017 survey and from 1.0202 to 1.0647 m in DOGAMI. Its 2013–15 median decreases to 0.7898 m. At 2110 Hamble the 2013–15 median increases from 0.9600 to 1.2617 m, while the two other medians decrease to 0.3343 and 0.3534 m.

Eighteen paired views and exact attribute and index comparisons preserve 79 source peers across two batches after removing 3,780 source triangles. The exporter checks 7,710 graph edges with at least 7.0251 m clearance. Horizontal rays through the 2105 entry reach the rear wall, while upward rays verify the porch underside and 2081 chimney. Terrace rays hit both west brick walls. Desktop and phone select all thirteen models, pass 32 collision checks and route to the two estimated approaches. Invalid GLB bytes and an invalid final anchor restore the thirteen predecessor meshes and approaches. Repeated, installed, built and served assets have identical hashes. [Exporter](../scripts/build-fairmount-summit-hamble-review.py).
