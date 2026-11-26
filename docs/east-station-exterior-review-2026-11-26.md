# UO East Station exterior review

The local viewer replaces the main East Station building and both annexes under their original scene IDs. UO lists them as B0187L, B0188L and B0189L. City outlines 170834, 170833 and 170835 overlap their preceding scene footprints by 313.619 m², 264.478 m² and 479.685 m², respectively. The state footprints and 2024 Oregon orthophoto agree with the separate city outlines. [UO building inventory](https://cpfm.uoregon.edu/sites/default/files/uo_building_inventory_published.pdf) · [City buildings](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Editable registration and source hashes](../data/metadata/east-station-exterior-review.json).

- **UO Police Department East Station, 2141 E 15th Ave**, restores the four-slope blue-gray standing-seam roof, pale vertical siding, south windows and the small gabled entrance cover. UO identifies the south door as the public lobby entrance. The modeled canopy dimensions, exact threshold and screened openings are approximate. [UO contact page](https://police.uoregon.edu/contact-us) · [Public lobby description](https://clery.uoregon.edu/reports/crime-log) · [July 2024 street view](https://www.google.com/maps/@?api=1&map_action=pano&pano=lz9A9cjGUqIcvBvYznsRhg&heading=352).
- **UOPD East Station Annex A, 2191 E 15th Ave**, uses an east–west gabled roof with the visible south ribbon of small windows and upper siding. **UOPD East Station Annex B, 2141 E 15th Ave**, uses the long, angled gable visible from Franklin Boulevard and its roof vents. Some openings screened by distance or vegetation, roof vent dimensions and both modeled annex approaches are estimates. [July 2024 Annex A view](https://www.google.com/maps/@?api=1&map_action=pano&pano=lz9A9cjGUqIcvBvYznsRhg&heading=34) · [July 2024 Annex B view](https://www.google.com/maps/@?api=1&map_action=pano&pano=qPX655pGQ4FMPtpI01aPSg&heading=180).

## Roof and scene verification

All 3,525 selected historical cells intersect the new meshes. The median absolute differences below are in meters and use only cells that hit both meshes. Each grid has 287 common cells on the main building, 264 on Annex A and 439 on Annex B. The revised main roof follows the 2024 metal hip silhouette and fits the 2017 surface more closely. The main building's oldest-grid median rises by 0.094 m. [NOAA LiDAR archive](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI elevation mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

| Historical surface | Main building | Annex A | Annex B |
| --- | ---: | ---: | ---: |
| NOAA 2013–2015 | 0.768 → 0.862 | 1.117 → 0.604 | 0.775 → 0.240 |
| NOAA 2017 | 1.121 → 0.042 | 0.987 → 0.037 | 0.801 → 0.046 |
| DOGAMI Lane County | 1.029 → 0.171 | 0.995 → 0.212 | 0.700 → 0.161 |

Five visual pairs cover the main south and east elevations, both annexes and the roof profiles. Removing 922 source triangles preserves the surviving indices, vertex attributes and 40 other IDs in the original batch. A 7,710-edge route scan finds no added conflicts. The nearest checked route edge is 16.1714 m from the revised collision polygons.

Desktop and phone production previews verify three searches, three walkable modeled approaches and eight collision points. The entrance canopy post blocks its footprint, and the checked space between the supports remains clear. A damaged third source anchor restores all three old volumes. The repeat export, stage, installed and served model and descriptor bytes match.

Formatting, 197 unit tests, four focused browser tests, the production build, 349 open archive hashes and 282 viewer pins passed. This batch uses original geometry and remains local and uncommitted. [Builder](../scripts/build-east-station-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/east-station-exterior-review/site.json).
