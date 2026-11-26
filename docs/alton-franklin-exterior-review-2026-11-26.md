# Alton Baker shelters and the Best Western Franklin wing

Three exteriors pass local L2 review. The Alton Baker models use the City's labelled shelter map, City footprints, the 2025 Lane County aerial and the capital plan's shelter photograph. Both have open bays, green roofs, post-and-beam framing, utility fixtures and stationary picnic tables. Shelter 2 retains `roof-abe13121`. Shelter 1 uses the new `alton-baker-shelter-one` scene ID. The brochure provides the table counts and lengths. Support spacing, table placement and service details are approximate. [City shelter map](https://www.eugene-or.gov/DocumentCenter/View/81968/Alton-Baker-Rental-Maps) · [City park brochure](https://www.eugene-or.gov/DocumentCenter/View/39622/Alton-Baker-Park-Flyer) · [Capital plan photo, printed page 138](https://www.eugene-or.gov/ArchiveCenter/ViewFile/Item/6000#page=146).

The Best Western New Oregon Franklin wing retains `roof-4b32d15b`. The City footprint and 2025 aerial establish the higher rear box, west shed and east sloping roof. July 2024 panoramas show the yellow west siding, tall east roof fin, street-facing glazing and low terrace wall. The registered roof outline leaves the open terrace and part of the east apron at ground level. Openings on the screened elevations are approximate. [Hotel's address and property record](https://www.bestwestern.com/en-us/book/hotel/eugene/best-western-new-oregon/38013) · [Editable model dimensions and photo references](../data/metadata/alton-franklin-exterior-review.json) · [Exporter](../scripts/build-alton-franklin-exterior-review.py).

## Historical source geometry

Lane County's 2017 aerial shows a building south of the Millrace at `roof-885f60ba` and a separate building east of Villard Alley at `roof-6dc8ed19`. Their footprints are open in the 2021, 2023, 2024 and 2025 captures. The river site is now used for parking. The Villard site is grass and the neighboring western building remains present. The default scene retires the two source meshes and their collision and generic entries. Both IDs and original mesh ranges remain available for historical comparison and fallback. [Lane County aerial layers](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [2024 Oregon aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

## Verification

The new meshes intercepted 2,253 of 2,466 height rays. The 213 misses are at the hotel's open terrace or apron. The previous Shelter 1 site had no building mesh. The remaining two models provide 1,623 paired height cells.

| Model | 2013–15 median error | 2017 median error | DOGAMI median error |
| --- | ---: | ---: | ---: |
| Shelter 2, previous → new | 1.1504 → 1.1958 m | 0.8082 → 0.3180 m | 0.6233 → 0.1122 m |
| Shelter 1, new model | 1.3597 m | 0.3879 m | 0.1323 m |
| Franklin wing, previous → new | 1.2675 → 0.4914 m | 1.1238 → 0.3446 m | 1.0846 → 0.2447 m |

Ten matched views cover the shelters, the hotel and the retired footprints. The installed meshes remove 848 source triangles while preserving all vertex attributes and remaining index sequences for 47 peers in four batches. The exporter checks 7,710 route edges. Staged, repeated, installed, built and served package bytes match. The previous west boundary package also reproduces its installed bytes.

Local production on desktop and phone selects all three new exteriors. Thirteen collision probes cover open shelter aisles, solid columns and tables, the hotel terrace and both former building footprints. The scene has 525 selectable buildings, 263 batch members and 593 approaches. The shelters are beyond the current route network and have no authored approaches. Invalid GLB bytes and an invalid source anchor independently restore the four previous source meshes and their generic approaches.

This revision is local and uncommitted.
