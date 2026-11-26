# Bushnell East Quad exterior review

The local viewer rebuilds two connected-building records along the eastern and southern sides of the Bushnell quadrangle. Both retain their original scene IDs. City outlines 171530 and 171529 overlap the corresponding original model footprints by 1,403.508 m² and 1,574.282 m², respectively. The 2026 campus map names the building functions and places the entries on the quadrangle side. [Campus map](https://bushnell.edu/campus-map) · [City building footprints](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Source hashes and editable roof zones](../data/metadata/bushnell-east-exterior-review.json).

- **Kellenberger Library, Lottie Price Music Building and Ross Evans Chapel** use the existing connected scene ID. The main labels have separate directory addresses at 1188 Kincaid and 894 E 11th. A campus photograph shows the west entry shared by all three. The original geometry reconstructs the music building's painted upper walls and hipped roof, the library's brick glazing bays and intersecting shallow roofs, and the clock, glass blocks and canopy at the connector. The paved approach follows the visible orthophoto alignment. Portions of the screened walls, the ramp and threshold use estimates. [Campus directory](https://bushnell.edu/student-life/campus-safety/) · [West entry photograph](https://bushnell.edu/wp-content/uploads/2026/07/family-visit-campus-tour-library.jpg) · [Approach photograph](https://bushnell.edu/wp-content/uploads/2026/04/065dc41e66b0599ef1c66518e227b202263889f5-1024x683.png).
- **Burke-Griffeth Hall, 875 E 12th Ave**, remains one connected exterior. The west-end Bistro, lower west block, higher dormitory wings, north entry and eaves follow the city outline, aerial photographs and height transitions. The quadrangle elevation includes brick bands, sash windows and the taller ground-floor glazing. The positions of screened windows, the entry threshold and rooftop exhaust details are approximate. [Residence Life](https://bushnell.edu/student-life/residence-life/) · [Burke-Griffeth exterior photograph](https://bushnell.edu/wp-content/uploads/2026/07/bushnell-burke-griffeth-hall-dorm-exterior.jpg) · [Campus Dining](https://bushnell.edu/student-life/residence-life/campus-dining/).

## Roof and scene verification

All 8,514 historical roof cells intersect the new meshes. The median absolute differences below are in meters and use only cells that hit both meshes. Each surface has 1,313 common cells for the connected academic exterior and 1,467 for Burke-Griffeth. [NOAA LiDAR archive](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI elevation mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

| Historical surface | Kellenberger, Price and Evans | Burke-Griffeth |
| --- | ---: | ---: |
| NOAA 2013–2015 | 0.709 → 0.245 | 1.383 → 0.197 |
| NOAA 2017 | 0.633 → 0.088 | 1.356 → 0.090 |
| DOGAMI Lane County | 0.624 → 0.134 | 1.373 → 0.112 |

Five visual pairs cover the clock and glass blocks, the north facade, residence quadrangle, Bistro and roof transitions. Two source ranges remove 1,206 triangles. A source-batch audit verifies all surviving triangle indices and attributes and the 40 other IDs across the two original batches. The 7,710-edge route scan finds no added conflicts. The nearest checked route edge is 12.2665 m from the revised collision polygons.

Desktop and phone production previews verify all four venue searches, two modeled walkable approaches and ten collision points. The two canopy posts block their small footprints, and the checked space between them stays open. The library and residence have a clear exterior gap at the tested location. An invalid second source anchor restores both source meshes. Staged, installed and served asset bytes match.

Formatting, 197 unit tests, four focused browser tests, the production build, 347 open archive hashes and 280 viewer pins passed. The scene uses original geometry and keeps source images external. This batch is local and uncommitted. [Builder](../scripts/build-bushnell-east-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/bushnell-east-exterior-review/site.json).
