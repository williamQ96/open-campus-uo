# Fairmount and Kincaid exterior review

Eight exteriors retain their existing scene IDs. Municipal addresses establish the six houses and the university directory confirms both chapter houses. The 1671 Walnut outline follows City feature 170594. The remaining seven use statewide footprints cross-checked against the 2024 orthophoto. The editable register preserves the source feature IDs, view links, roof planes and placements. Screened walls, opening sizes and thresholds include estimates. [Municipal address layer](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0) · [University chapter house map](https://blogs.uoregon.edu/uofsl/chapterhousesmap/) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Editable register](../data/metadata/fairmount-kincaid-exterior-review.json).

| Exterior | Modeled features |
| --- | --- |
| 1517 Walnut Street | Two street gables, circular vent, raised steps and pale rail. [West view](https://www.google.com/maps/@?api=1&map_action=pano&pano=5nzALZiZrnwFXKyCjTdouQ&heading=82.4) |
| 1680 Walnut Street | Intersecting roofs, shed dormer, glazed south bays and a timber-trimmed gable. [South view](https://www.google.com/maps/@?api=1&map_action=pano&pano=4BaNxK_r5viV9ntyRRAsYw&heading=351.98) · [East view](https://www.google.com/maps/@?api=1&map_action=pano&pano=7ivfWVhkWoKWBY4mMh8Sbw&heading=264.87) |
| 1671 Walnut Street | Paired west gables, porch posts and upper sash. [West view](https://www.google.com/maps/@?api=1&map_action=pano&pano=3TYMkcoWG8zv7ukcXJfQ8g&heading=83.19) |
| 1991 E 19th Avenue | Blue-gray roof, lower west garage and a separate south roof projection. [Southwest view](https://www.google.com/maps/@?api=1&map_action=pano&pano=xwuoznBj7tG5cnoSfelFqw&heading=25.36) |
| 1931 Moss Street | Tan siding, dark roof, cross gables, dormers and raised west porch. [West view](https://www.google.com/maps/@?api=1&map_action=pano&pano=wWvCQPjewS-vOWhImMJ2Rg&heading=84.65) |
| 1879 Moss Street | Wood cladding, brown roof and a lower east addition. The primary street elevation is partly screened. [Southwest view](https://www.google.com/maps/@?api=1&map_action=pano&pano=KN1tTWiwMviaFbvzz71hHw&heading=50.78) · [Property record](https://www.zillow.com/homedetails/1879-Moss-St-Eugene-OR-97403/48408390_zpid/) |
| Pi Beta Phi Chapter House | Brick east face, dark shutters, pale pediment and arched trim, attic glazing and the lower north wing. [2026 east view](https://www.google.com/maps/@?api=1&map_action=pano&pano=CIABIhAxXdZG8aKuAcc7M5F14Q54&heading=280.54) · [2024 north view](https://www.google.com/maps/@?api=1&map_action=pano&pano=KzvSSNmd7qSC3sWtFZHmiA&heading=184.18) |
| Alpha Chi Omega Chapter House | Pale brick, white colonnade, crossed gallery rail and the stepped north entry. [North view](https://www.google.com/maps/@?api=1&map_action=pano&pano=54nTX-Zb4js0aqmduX4MDg&heading=159.1) |

The six marked approaches are estimated scene locations. The entrance lists for 1991 E 19th and 1879 Moss are empty because the door locations are screened in available views.

## Verification

Nine matched WebGL views cover all eight exteriors and both chapter roofs. Campus context haze was disabled in both comparison passes to make the materials visible. The package removes 2,048 source triangles across four batches. The current and previous comparisons verify 140 other batch members and all surviving indices and vertex attributes.

All 5,396 historical roof samples intersect adopted geometry. On shared cells, 23 of the 24 building and grid medians fall. At 1931 Moss, the 2013–2015 median rises from 0.978 m to 1.023 m. Its 2017 median falls from 0.713 m to 0.342 m and the DOGAMI median falls from 0.803 m to 0.454 m. The historical grids contain vegetation near some roof edges. [NOAA elevation archive](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI elevation mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

The geometry audit checks 7,710 graph edges with 13.125 m minimum clearance. Desktop and phone production find all eight buildings and verify 14 collision probes and six walkable modeled approaches. The route from 968 Alder to the Pi Beta Phi approach uses 159 points. A corrupted source anchor restores the eight baseline candidates. The repeat export, staged assets, installed assets and production response match byte for byte.

The local inventory has 232 L2 buildings, 292 active L1 buildings, 27 historical mappings, seven L2 outdoor groups and eight L1 outdoor groups. The scene has 524 selectable buildings, 294 batch members and two separate roof refinements. The package is local and uncommitted.

Run `python scripts/build-fairmount-kincaid-exterior-review.py --stage OUTPUT --audit AUDIT.json` to reproduce the model. [Builder](../scripts/build-fairmount-kincaid-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/fairmount-kincaid-exterior-review/site.json).
