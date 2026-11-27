# Patterson, Hilyard and East 11th exterior review

This local package rebuilds seven exteriors from seven old source ranges. Six unchanged sites keep their IDs. The Sigma Phi Epsilon house at 967 Patterson uses a new ID and the range from its two demolished roofs remains in the inventory as historical evidence. [Editable specification](../data/metadata/patterson-hilyard-review.json) · [Reproducible exporter](../scripts/build-patterson-hilyard-review.py).

| Site | Reconstructed details |
| --- | --- |
| Patterson House, 979 Patterson | Brick west entrance, pale gable, raised platform, four canopy columns and tall arched window bays. The west portico crosses the terrain limit. [City housing inventory](https://www.eugene-or.gov/Archive/ViewFile/Item/4782). |
| Sigma Phi Epsilon, 967 Patterson | Three-story west elevation with two shallow-sloped stone-faced bays, a recessed red door and an open roof terrace. The archived municipal outlines show the old buildings, and the 2025 aerial shows the cleared redevelopment parcel. The dimensions, materials and the rear envelope follow the preliminary GMA concept and parcel evidence. The final built geometry remains to be surveyed. [City demolition record, property 61](https://coeapps.eugene-or.gov/cmoweblink/0/edoc/4198616/Ord.%2020700.pdf) · [City-filed construction sheet](https://pddfiles.eugene-or.gov/documents/ebuild/4594119) · [Chapter exterior concept](https://www.epageflip.net/i/1527312-pre-campaign-feasibility-study/6) · [Housing address](https://sigepnationalhousingllc.residentportal.com/auth/signup-property). |
| Beta Theta Pi, 1009 Patterson | Intersecting roof sections, low south porch and a south approach. Street trees obscure window and door details. [University chapter house map](https://blogs.uoregon.edu/uofsl/chapterhousesmap/). |
| Alpha Phi, 1050 and 1052 Hilyard | One continuous L-shaped roof with intersecting gables, lap siding, sash windows, half-timber details and a street-facing gate. The two municipal addresses select the same building. [National Register inventory](https://npgallery.nps.gov/GetAsset/fa408773-7be6-4286-b457-a73f5b1d2d9a). |
| Gamma Phi Beta, 1021 Hilyard | A separate octagonal tower and conical cap, brick ground level, upper timber framing and the rear wing. The 1959 addition remains joined to the original mass. [National Register nomination](https://npgallery.nps.gov/GetAsset/1faab1b0-6fa1-4a82-bd98-9ae3af25ecfe). |
| 763 East 11th | Brick street front with columns, arched windows and three distinct roof dormers. The dormer dimensions and deeper street façade detail are estimated from the July 2024 street view and aerial. |
| 751 and 755 East 11th | One office roof registered to 2025, with a raised central equipment roof. The open south parking court stays available. The trees and long setback obscure fine façade details. |

The terrain apron keeps the west buildings visually grounded. The west entrances of 979 and 967 Patterson sit outside the walkable boundary. Five other entries have dedicated approach geometry inside it.

## Verification

The two surface grids furnish 5,300 eligible rays on six existing buildings, and all hit. There are 3,264 paired previous and rebuilt samples. Six of 12 absolute error medians fall and six rise. The 967 replacement uses the dated project concept because surfaces predating construction describe the demolished buildings.

| Increased median absolute error | Surface | Previous (m) | Rebuilt (m) |
| --- | --- | ---: | ---: |
| Gamma Phi Beta | 2013–15 | 1.1237 | 1.5925 |
| Gamma Phi Beta | DOGAMI | 1.1854 | 1.4614 |
| 763 East 11th | 2013–15 | 0.6127 | 0.6605 |
| 763 East 11th | DOGAMI | 0.7569 | 1.1402 |
| 751 and 755 East 11th | 2013–15 | 1.0547 | 1.4034 |
| 751 and 755 East 11th | DOGAMI | 0.9941 | 1.2446 |

Fifteen matched cameras and index checks preserve 31 unrelated building ranges. The rebuild removes 2,084 source triangles, with a minimum clearance of 4.2662 m across 7,710 checked network edges. The 967 terrace ray hits at 7.450 m, below the two street wings at 9.416 and 9.277 m. Three separate dormer rays on 763 East 11th hit at 10.460, 10.500 and 10.470 m, and the Gamma Phi Beta tower reaches 12.040 m.

Desktop and phone verify seven named selections, five address variants, ten collision probes and twenty clear approach probes per device. Four gates route from Knight Library. The gate at 1009 Patterson has a clear approach to the nearby Hilyard Alley segment, whose graph component is disconnected from the wider campus network. Bad mesh data or a changed source-range anchor restores the seven older ranges and their entrances.

The local ledger has 555 L2 building exteriors, 47 active L1 exteriors, 39 historical mappings and 15 L2 outdoor groups. The public deployment remains at `c3dc42c`.
