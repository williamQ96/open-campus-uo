# Twenty-nine South Alder, Harris and Kincaid exteriors

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `east19-946` | 170711 | 946 East 19th. Independent shallow roof beside the Kincaid building. |
| `roof-4c32075c` | 170712 | 1945 Kincaid / 1946 Harris Alley. Paired low roof sections and west porch. |
| `roof-4680399a` | 216658 | Heron House at 1888 Harris. Hipped roof, stone base, balcony bands and east porch approach. |
| `roof-d9295859` | 170718 | 1948 Harris. Low hip and green arched facade panels. |
| `roof-24824438` | 170384 | 1790 Alder. Flat west volume, intersecting east roof slopes and a shaded east porch. |
| `east19-661` | 178178 | 661 East 19th. Separate low commercial roof and blue perforated front panel. |
| `roof-fd23ff0d` | 224340 | Shared 675 / 689 East 19th. Horizontal storefront glazing and vertical side trim. |
| `roof-f1fd1004` | 170665 | Alderwood Manor at 1860 Alder. Open light court, recessed east facade and masonry screen. |
| `alder-1884` | 170666 | Alderwood Manor at 1884 Alder. Stepped twin roof volumes, open parking, outdoor stair and two linked gallery levels. |
| `roof-ef20fcce` | 170687 | 1961 Hilyard. Broken-slope front gable and lower rear roofs. |
| `roof-d4aef710` | 182508, 182509 | 1875 Alder. Connected wings around the east parking court and projecting gabled street bays. |
| `roof-1531a79c` | 170716 | Shared 955 East 20th / 1977 Harris Alley. Multi-section roof and south entrance cover. |
| `roof-ff23cc0f` | 170704 | 1940 Kincaid. Cross gables and estimated east porch approach. |
| `roof-37a28e00` | 170651 | 945 East 19th. High street volume, lower rear roof and alley galleries. |
| `kincaid-1863` | 170656 | 1863 Kincaid. Small separate gable under tree cover. |
| `kincaid-1869` | 170657 | 1869 Kincaid. Independent flat roof, pale wall and green vertical facade bands. |
| `roof-5a0db2c6` | 170646 | 951 East 19th. Low roof, blue and pale panel bands and raised stone base. |
| `harris-alley-1871` | 170649 | 1871 Harris Alley. Independent low roof and exterior stair. |
| `roof-a01b7011` | 171065 | 1825 Harris. Long gable, east galleries and green doors. |
| `east19-1037` | 171068 | 1037 East 19th / 1890–1894 Potter Alley. Open roofed parking bay and separate low volume. |
| `east19-unnumbered-171069` | 171069 | Low unnumbered roof at East 19th. Two dated street bearings show its own outline. |
| `roof-ef402a58` | 170705 | 1960 Kincaid. Intersecting roof wings and east porch. |
| `alder-1944` | 170692 | 1944 Alder. Independent gabled residence and east porch. |
| `roof-a2ee58ee` | 170693 | 1926 Alder. Separate hipped roof and low south section. |
| `alder-1908-1912` | 170694 | Shared 1908 / 1912 Alder / 772 East 19th. Stepped roof and recessed lower opening. |
| `east19-992` | 170715 | 992 East 19th. North porch, dormer and chimney. |
| `roof-57d787f9` | 170717 | 1930 Harris. Separate hip, small porch and estimated east entrance. |
| `east19-960` | 182465 | 960 East 19th. Independent roof with dark projecting window bands. |
| `roof-779042c1` | 182466 | 980 East 19th. Sister building with its own roof and walkway clearance. |

Seventeen source ranges now represent 29 independently selectable exteriors. The County orthoimages show 1875 Alder's two intersecting roof sheets as one connected mass. The adopted model keeps their contours and the open parking court as one selection. The City separately records 1860 and 1884 Alderwood Manor. The 1860 light court is open to the sky. At 1884, the roof and ground collision follow two wings, while two elevated links and an exterior stair cross the open slot. The shared plan boundary is used for selection. Roof levels, facade spacing, columns and stair heights remain approximate where measurements are unavailable. [City roof layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [County aerials](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [City multifamily inventory](https://www.eugene-or.gov/AgendaCenter/ViewFile/Item/3?fileID=10) · [Alderwood Manor operator](https://vonkleinrentals.com/all-units/).

The 2013–15 and DOGAMI grids supply 17,436 rays within the adopted roof outlines, and all hit. Fifty-seven of 58 paired median errors fall across 14,670 paired cells. The 2013–15 median at 1944 Alder rises from 1.2750 to 1.5512 m. Both 1863 Kincaid comparisons have only three paired cells under tree cover. The 2017 raster supplies two anomalous points at 1860 Alder and is excluded. At 1884 Alder, sixty cells per survey in the exposed slot fall outside the actual roof outlines.

Thirty-seven matched views and exact index and vertex comparisons preserve 38 other members of the affected batch. Rays reach the floor through the 1860 court, verify the two different 1884 soffit elevations and the exposed link, clear the open slot and the 1875 court, and hit the Potter Alley parking canopy. The exporter checks 7,710 route edges with 1.7542 m minimum clearance.

Desktop and phone select all 29 exteriors and find five alternate addresses. Each passes 38 collision probes, twelve approach probes and directions to three estimated entrances. Both invalid asset cases restore all seventeen preceding meshes and entrances, including collision in the former Alderwood Manor slot. Staged, repeated, installed, built and served assets match. The package is local and uncommitted. [Editable dimensions and source receipts](../data/metadata/southwest-exterior-review.json) · [Exporter](../scripts/build-southwest-exterior-review.py).
