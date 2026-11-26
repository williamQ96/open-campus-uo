# Six exteriors from three merged South University models

| Source candidate | Exteriors in the default local scene | City gap |
| --- | --- | ---: |
| `roof-b0cb5ef5` | **1866 Onyx Street** retains the source ID, with the east hip and side landing. **1870 Onyx Street** gains `onyx-1870-west`, with its separate gable and west exterior stair. | 1.574 m |
| `roof-48d494fc` | **1208 East 19th House** retains the source ID, with the overlapping gables, sheltered porch, steps and picket fence. Its **rear garage** gains `e19-1208-rear-garage`, with two west doors and a lower roof section. | 0.894 m |
| `roof-27720a8d` | **1825 University Street** retains the source ID across the three municipal addresses on City 171041. It has a shallow stepped roof, west porch and east balcony. **1840 Onyx Alley** occupies the separate parcel and gains `onyx-alley-1840`, with the two registered gables. | 1.479 m |

The three gaps agree with the 2025 aerial and separate City building outlines. The dated frontage views show the Onyx stair, the 1208 garage doors and the two ends of the 1825 footprint. Foreground buildings, trees and fencing screen parts of 1840. The visible forms guide the model. Opening placement on screened faces, balcony depth, stair dimensions and porch levels use estimates. Four modeled approaches lead to the living buildings with documented outdoor approaches. [City building footprints](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Lane County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Source records and editable dimensions](../data/metadata/onyx-university-split-exterior-review.json).

| Model | 2013–15 paired median error | DOGAMI paired median error |
| --- | ---: | ---: |
| 1866 Onyx | 0.9986 → 0.5577 m | 0.9276 → 0.1204 m |
| 1870 Onyx | 1.4436 → 0.6271 m | 1.3997 → 0.0503 m |
| 1208 East 19th house | 1.3582 → 0.6872 m | 1.1032 → 0.1968 m |
| 1208 rear garage | 1.7768 → 0.3524 m | 1.5074 → 0.0512 m |
| 1825 University | 0.3782 → 0.2320 m | 0.4242 → 0.0442 m |
| 1840 Onyx Alley | 2.5382 → 0.7374 m | 2.2530 → 0.1256 m |

The roofs hit all 1,416 available rays, including 1,296 cells paired with the source meshes. Both elevation grids show improvement for all six roofs. The 2017 USACE surface has no coverage at these sites. Ten matched views include each split gap, the west frontage at 1825 and the separate 1840 gable.

Removing 1,016 source triangles preserves the index order and vertex attributes of 54 peer buildings. The exporter checked 7,710 route edges with a minimum clearance of 5.3516 m. Desktop and phone select all six IDs, pass 14 collision probes and reach the 1825 porch, 1208 gate, 1866 drive and 1870 stair foot from Knight Library in 151, 168, 178 and 170 route points. The rear garage and 1840 have no authored approaches. Invalid GLB bytes and an invalid source anchor each restore all three original merged candidates and generic approaches.

Stage, repeated, installed, built and served asset bytes match. Formatting, 197 unit tests, seven related browser cases, production build, inventory structure, 399 archived files and 342 viewer hashes passed. This revision is local and uncommitted. [Exporter](../scripts/build-onyx-university-split-exterior-review.py).
