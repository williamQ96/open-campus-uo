# Final neighborhood exterior review

| Exterior | Evidence and modeled features |
| --- | --- |
| Alpha Omega House, 1332 Kincaid Street | City 170536 and June 2024 street views support the stepped roof, east dormers, sided elevations and a covered entry. The front approach follows the visible path. |
| Fire Station 13, 1695 Agate Street | City 171536 and the municipal photo support the low office wing, brick front, two closed white apparatus doors, teal fascia and the public-facing University Station inscription. The gabled east roof and the low screened south extension follow the 2024 street views and the aerial outlines. |
| 2200–2210 Birch Lane | City 171367 and the July 2024 north and west views show two roof levels, two garage doors, the upper balcony, the external stair and the lower porch. |
| 1615 Fairmount Boulevard | City 169391 and the July 2024 Fairmount views show an independent house with a centered gable, brown siding and west steps. The new building ID is searchable independently of 2200–2210 Birch Lane. The closest modeled wall separation is 0.6853 m. |
| 2288 Birch Lane | City 158821 follows the multi-wing roof. The west and north siding and upper red-brown shutters follow the visible parts of the July 2024 view. The main ridge is fitted to the 2017 and DOGAMI profiles. |
| 634–640 East 16th Alley | City 226903 and the 2017, 2021 and 2025 roof outlines retain the clipped gabled footprint. The public 640 exterior photograph adds the two-story east gallery, vertical siding, dark balusters and a stair descending south. The other three West Boundary models retain their geometry and selection IDs. |

The former Patterson YMCA roof is stored as a historical mapping. The active tennis and pickleball hall lies south of the scene. The 2025 aerial puts its main roof about 12 m past the boundary and the small roof projection about 7 m past it. Within the current frame, the original 2,547 m² legacy building is replaced by the visible open ground and retained asphalt and concrete. Those surfaces are recorded under ENV-05. [YMCA site listing](https://www.eugeneymca.org/locations/hours-location) · [City building outlines](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County imagery](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer).

The facades, roof edges and stair dimensions are photo-based estimates. Vegetation screens part of 2288 Birch Lane. Its older surface has a visibly displaced ridge, while the two more recent paired median errors are 0.144 m and 0.145 m. The 16th Alley DOGAMI median increases from 0.0875 m to 0.129 m after repositioning the ridge against the recent aerials. The original reference photographs remain research sources. [Alpha Omega operator handbook](https://fbceugene.com/wp-content/uploads/AO-Handbook-26-27-1-2.pdf) · [Station photograph and address](https://www.eugene-or.gov/1999/Fire-Stations) · [640 East 16th Alley exterior photograph](https://www.zillow.com/b/640-e-16th-aly-eugene-or-CF2Vpk/).

Thirteen matched camera pairs, 3,542 inboard roof rays and 1,930 Patterson ground rays pass. In 16 of 17 dated comparisons the median roof-height error decreases. The exact source index audit removes 1,974 triangles and preserves 127 unaffected ranges within the four checked batches. The rerendered west group keeps the other three meshes and its approach ground byte-identical at the geometry-array level. The 7,710-edge graph check finds a minimum clearance of 3.474 m for the new neighborhood package.

Desktop and phone both expose the exact 610 L2 exterior IDs and can select the six reviewed exteriors through search. The on-screen route from Knight Library ends at the Alpha Omega House approach in 26 points. Three injected failures restore the expected older geometry and entrance records. The production build, 197 unit tests, 11 browser cases, 457 asset archive checks and 400 viewer hash checks passed. The published checkpoint remains c3dc42c.

- [Editable neighborhood metadata](../data/metadata/neighborhood-exterior-closeout-review.json)
- [Neighborhood exporter](../scripts/build-neighborhood-exterior-closeout-review.py)
- [West Boundary metadata](../data/metadata/west-boundary-exterior-review.json)
- [West Boundary exporter](../scripts/build-west-boundary-exterior-review.py)
