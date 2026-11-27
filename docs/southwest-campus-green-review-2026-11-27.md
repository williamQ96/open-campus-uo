# Southwest Campus Green and Spangler South Garden

The open lawn extends south from Knight Library between the Lokey Education complex and Pioneer Cemetery. Three county aerial dates establish the persistent lawn and terrace boundaries. The 2017 image includes temporary seating and tents. The 2021 and 2025 images show the open ground. The campus landscape survey and library survey identify the public approaches and planting layout. [2007 landscape survey](https://cpfm.uoregon.edu/sites/default/files/sw_campus_green_04_12_07.pdf) · [2025 Knight Library survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/knightlibrary_2025.pdf) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer).

| Feature | L2 registration |
| --- | --- |
| Green and walks | 5,490.41 m² of open lawn. The 1,293.48 m² of terrace and walks link the cemetery easement, the Education side and the Lot 20 pedestrian edges. |
| Spangler South Garden | Three long central planting beds, smaller beds by the library and west approach, three benches and four representative lamp positions across the site. |
| Lot 20 | 999.40 m² of pavement, 19.83 m of selected curb, 34 modeled divider strokes, four accessible symbols and two striped aisles. The west tree island and east returns keep the registered trees off the paved bays. A small Lot 20 board represents the observed sign. |
| Planting | Eleven beds and islands cover 425.60 m². The university tree inventory places 29 trees, including the Ponderosa pine and the row of honey locusts beside the lot. Six inferred trees are removed where they conflict with the open lawn, the walks or a registered position. |

The depiction follows the fall 2020 west lot street view for the blue symbols, low curb and planting edge. The university's parking directions identify Lot 20 south of the library. Bench and lamp profiles, planted species composition, sign wording and curb elevation use estimates. [University parking directions](https://testing.uoregon.edu/directions-and-parking) · [University tree inventory](https://cpfm.uoregon.edu/trees) · [Editable registration](../data/metadata/southwest-campus-green.json).

The university art catalogue lists Wayne Chabre's 1994 *Arboretum Illuminatum*, also called *Trees of Knowledge*. The campus map places the group near the center of Spangler South Garden. The three components are registered as a group in the editable inventory. The individual supports and geometry suitable for redistribution need separate evidence. [University catalogue](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/arboretum-illuminatum) · [Artist's photographs](https://www.waynechabre.com/public-art).

Four branches add 40 navigation edges. The first uses the approach node supplied by the pinned cemetery descriptor. The loader validates the combined graph and appends the branch after the cemetery during scene assembly. The original terrain, campus and navigation source pins are retained. The update is part of the November 27 outdoor L2 release. [Exporter](../scripts/build-southwest-campus-green.py) · [Runtime descriptor](../apps/web-preview/public/scene/southwest-campus-green-review/site.json).

Both production profiles load all 39 added waypoints, 610 exterior meshes and 368 resources. Eight surface probes and three fixture collision probes pass. The 144.98 m library-to-Education sample, the 116.91 m cemetery-to-lot sample and the 89.20 m Education-to-north-lot sample contain endpoint connections outside the measured surfaces. Those stretches measure 15.39 m, 48.33 m and 28.88 m respectively. All four authored branches stay on the registered paving within the 0.13 m audit tolerance. Two deterministic exports, six matched views, formatting, 197 unit tests and 12 focused browser tests pass.

## Paved route access

The viewer uses the modeled terrace, walks and cemetery paving to check how pins on these surfaces join the path graph. The coverage uses the same outlines as the site exporters and is enabled when the matching ground and routes load. Pins placed on grass still use approximate connections. Lot 20 asphalt remains a separate vehicle surface. [Coverage exporter](../scripts/build-campus-route-surfaces.py).

Desktop and phone return 148.71 m, 250.87 m and 146.23 m for the three Southwest Campus Green samples. All three stay within 0.13 m of the modeled paving. The first follows the tolerance at the pavement edge for 1.025 m. Five offset pin pairs were also tested in both directions across the two sites. [Cemetery route comparison](pioneer-cemetery-landscape-review-2026-11-26.md#paved-route-access).

## Reading garden artwork survey

The university's artwork tour describes three approximately 1.22 m tall sculptural lights, and the artist documents the group as reading-garden lighting. The survey maps the group to Knight Library's south side. The published references identify the work and its scale. Individual base locations still need dated site evidence. [University artwork tour, stop 9](https://cpfm.uoregon.edu/sites/default/files/art_tour_august_2020_0.pdf) · [Artist's catalogue](https://www.waynechabre.com/public-art).

## Kendall Plaza connection

The registered east terrace places three tiers across the former southwest connector. The revised branch follows the lower brick court and rounds the south end of the terrace. The branch adds two edges, bringing the Southwest site total to 42. The modeled walk footprint grows from 1,293.48 m² to 1,301.45 m². [Kendall Plaza review](kendall-plaza-landscape-review-2026-11-27.md).
