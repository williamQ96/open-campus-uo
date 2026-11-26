# 1800 and 1850 Millrace Drive exterior review

The two municipal address points fall inside the same City of Eugene building polygon, object 169881. The 2024 Oregon aerial shows a continuous roof. The University of Oregon records construction at 1800 Millrace Drive in 1998, and the 2021 brochure markets the same building under both addresses. The local scene retains the selectable ID `roof-8bd064b7` and accepts either address in building search. [UO landscape survey](https://cpfm.uoregon.edu/sites/default/files/03_north_campus_riverfront_research_park-rfs.pdf) · [Campbell Commercial listing](https://www.loopnet.com/Listing/1800-1850-Millrace-Dr-Eugene-OR/24360431/) · [City building layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

The original 3D mesh uses the 3,476.18 m² municipal outline. It restores the two main shallow roof ridges, the low northern and southern wings and representative rooftop equipment grouped as seen in the aerial. July 2024 street views support the stone-toned plinth, gray wall panels, dark mullioned window bands and the covered north entrance. Vegetation screens parts of the east and west elevations. Glazing intervals on screened walls, rooftop equipment dimensions and the 3.3 m approach to the northern doorway are estimates. [North facade](https://www.google.com/maps/@?api=1&map_action=pano&pano=9SLIhM1hvATTlXjynt7ZPA&heading=161.47) · [North entrance from the east](https://www.google.com/maps/@?api=1&map_action=pano&pano=vu3LK5GotxKU7r7X9fHH4Q&heading=220.67) · [West facade](https://www.google.com/maps/@?api=1&map_action=pano&pano=IjST6u0VwgIPCN0wluplFQ&heading=141.38).

The [editable dimensions and references](../data/metadata/millrace-research-exterior-review.json) drive the [exporter](../scripts/build-millrace-research-exterior-review.py). The output is vertex-colored and contains original geometry. Photographs were used as visual references.

## Verification

The displayed mesh intercepted all 9,936 sampled height rays. The comparison uses 3,222 mutually covered cells per source. Three independent historical surfaces preserve the same height relationship between the low wings and the two main roofs. The 2017 surface informed the plane dimensions.

| Historical surface | Previous median absolute error | New median absolute error |
| --- | ---: | ---: |
| 2013–15 | 1.2022 m | 0.0543 m |
| 2017 USACE | 1.3128 m | 0.0248 m |
| DOGAMI Lane County | 1.2716 m | 0.0433 m |

Four browser camera pairs cover the north entrance, west facade, roof and east facade. The source batch loses exactly 702 triangles of the old candidate. The complete indices and vertex attributes for its eight peers match. The exporter verifies clearance against 7,710 route edges. Staged, independent repeat and installed bytes match.

The local production build has 524 selectable buildings, 283 batched buildings and 605 approaches. Desktop and phone each navigated 26 route points from 1600 Millrace Drive to the new north approach. Two probes within the footprint collide and the arrival point is clear. A browser with a deliberately damaged GLB restores the original selectable batch entry and retains the same census of buildings and approaches.

The model meets the local L2 exterior review. The change is local and uncommitted.
