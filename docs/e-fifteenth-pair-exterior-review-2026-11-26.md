# E 15th Avenue street and alley apartment exteriors

The local viewer registers two distinct L2 exterior geometries east of Treetop Apartments. The street building uses the original ID `roof-0c745864` and city outline 170401. The previously omitted alley building uses `east-fifteenth-alley-apartments` and city outline 170420. The 2024 aerial registers the roof separation and the 3.839 m gap between the municipal outlines. [Eugene building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Source pins and dimensions](../data/metadata/e-fifteenth-pair-exterior-review.json).

## Address evidence

Both models use location-based names. The northern street frontage shows a physical number 750 beside the central entry structure. The leasing photograph for 750 shows the same elevation. The municipal records put six 758 unit points in the northern taxlot, 1703323401901, and 12 unit points for 750 in the two southern lots, 1703323401900 and 1703323401902. The street number could mark access to the rear apartments. The E 15th Alley panorama shows the southern building and supplies a nearest-address label of 758. Building-number assignment remains unresolved. [Street panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=FkwxjAUh21jK_tTn9Wy-yw&heading=180) · [Alley panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=fwO4YT7IBNigdxtm6s8ftQ&heading=0) · [750 listing](https://www.apartments.com/750-e-15th-ave-eugene-or/m3zn9pj/) · [City address points](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0).

## Modeling and roof verification

The street building has two inward-rising roofs, vertical wall boards, a slatted cover over the stair bay, bridge landings and lower parking recesses. The model preserves the barrier where the June 2024 view shows a gate. The alley building has two small gables, horizontal siding, three window levels and an open switchback stair between its wings. Mesh and material colors are original. The references remain external. The stair runs, window sizes, parking depth and approach thresholds are approximate.

The roof audit ray-traces each wing after excluding the intentional stair gap from the sample masks. All 1,019 selected roof cells were hit. The street comparison uses cells common to both meshes. The alley originally had no dedicated roof model, so the last column shows the new median only. Tall surface returns near trees remain visible in the audit. The 90th-percentile residuals are 5.61 and 5.70 m for the street building and 6.45 and 0.74 m for the alley building. Isolated implausible 2017 values are outside the comparison. [NOAA LiDAR archive](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI elevation mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

| Historical surface | Street common cells and median absolute difference | Alley count and median absolute difference |
| --- | ---: | ---: |
| NOAA 2013–2015 | 366 cells, 1.66 → 0.71 m | 97 cells, 0.33 m |
| DOGAMI Lane County | 366 cells, 1.24 → 0.16 m | 109 cells, 0.39 m |

## Verification

Four before-and-after render pairs show the street face, alley face, inter-building court and roof separation. The review removes 174 triangles from the previous street candidate and preserves the surviving indices and attributes for the other 51 members of its batch. The nearest of 7,710 checked route edges is 10.1875 m from the revised collision footprint. The test checks both parking recesses, the court, the closed gate and the independent alley approach. The approaches terminate outside the modeled gate or stair.

Desktop and phone production verified both searches, both estimated walkable approaches and nine collision samples. A changed source anchor restores the old street candidate and removes the added alley selection. Re-exporting the adjacent Hilyard review with the shared stair builder reproduces its previous GLB and descriptor byte for byte. Formatting, 195 unit tests, six focused browser tests, production build, 337 open archive checks and 270 viewer pins passed. The default scene contains 520 selectable buildings, 325 batched members and six independent context roof treatments. This batch is local and uncommitted. [Builder](../scripts/build-e-fifteenth-pair-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/e-fifteenth-pair-exterior-review/site.json).
