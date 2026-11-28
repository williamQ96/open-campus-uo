# Building exclusions from the three November 28 screenshots

The numbered screenshots show the west and southwest edge (1), the south edge (2), and the east edge (3). The 105 additions below match visible labels to the active scene's stable building IDs. Each has at least one marked view with at least 98% of its projected roof inside the outline. The camera poses were fitted against the screenshots using identifiable label anchors.

Edit [the building scope registry](../apps/web-preview/data/building-scope.json) to add or restore IDs. The viewer excludes these IDs from labels, selections, building cards, search and entrance actions. The models and collision geometry continue to load as context. Exclude these IDs from future building refinement. The scope is a user choice about the campus directory and refinement queue. The recorded building identities and ownership sources are retained.

The third outline passes through the label for 1864 Moss Street (`roof-b8fa3497`). Its projected roof sits outside the outline, so it is pending review. Buildings without a clearly matched visible label in these screenshots require separate confirmation. The main UOPD East Station building and Annex B retain their existing scope. Earlier exclusions and their evidence are in the [November 27 release record](overview-release-2026-11-27.md).

## Camera readout

The lower-left camera readout appears with the first Overview frame and remains available in the detailed scene. Its coordinates are local east, north and height in meters. Heading runs clockwise from north. Pitch is positive above the horizon. Overview also reports the orbit target in the same coordinates and the camera-to-target range in meters. A screenshot with these values records the camera's pose when movement slows.

## Added building IDs

| Building ID | Building | Confirming screenshot |
| --- | --- | --- |
| `alder-1774-west` | 1774 Alder Street / West Building | 1 |
| `alder-1908-1912` | 1908 / 1912 Alder Street / 772 East 19th Avenue | 2 |
| `blackstone-west-north` | 1750 Alder Street / Blackstone Manor Northwest Building | 1 |
| `e16-alley-630-632` | 630–632 East 16th Alley | 1 |
| `east14-712` | 712 East 14th Avenue | 1 |
| `east16-736` | 736 East 16th Avenue | 1 |
| `east16-771-773` | 771 / 773 East 16th Avenue | 1 |
| `east17-762` | 762 East 17th Avenue | 1 |
| `east18-888` | Talisman / 888 East 18th Avenue | 2 |
| `east19-960` | 960 East 19th Avenue | 2 |
| `east20-740` | 740 East 20th Avenue | 2 |
| `east20-741` | 741 East 20th Avenue | 2 |
| `hilyard-1477` | 1477 Hilyard Street | 1 |
| `hilyard-1547-1549` | 1547–1549 Hilyard Duplex | 1 |
| `kincaid-1214` | 1214 Kincaid Street | 1 |
| `kincaid-1863` | 1863 Kincaid Street | 2 |
| `roof-04683fef` | Aldersgate Apartments | 1 |
| `roof-046adce7` | 1517 Walnut Street | 3 |
| `roof-0587b8ad` | Campbell Club | 1 |
| `roof-0945ffaf` | Gamma Phi Beta Sorority House / 1021 Hilyard Street | 1 |
| `roof-0b345e8f` | 2081 Fairmount Boulevard | 3 |
| `roof-0e2e42c5` | The Ellis / 780 East 13th Avenue | 1 |
| `roof-136be56b` | 2303 McMorran Avenue | 2 |
| `roof-18949f29` | 2040 Alder Street | 2 |
| `roof-19858777` | 633 E 12th Avenue Parking Garage | 1 |
| `roof-1a3a0846` | 750 East 18th Avenue | 2 |
| `roof-1dfcdc64` | 1678 Orchard Street | 2 |
| `roof-22175da6` | 2281 Rose Lane | 3 |
| `roof-2229f729` | 1725 Hilyard Alley | 1 |
| `roof-2243c394` | 892 East 20th Avenue | 2 |
| `roof-22f89f22` | 765 East 18th Avenue | 1 |
| `roof-24824438` | 1790 Alder Street | 1 |
| `roof-24910633` | 2086 Potter Street | 2 |
| `roof-28f18190` | 1861 Franklin Boulevard | 3 |
| `roof-2cb36f2e` | 1947 Villard Street | 3 |
| `roof-2dd9b16c` | 2290 Parkside Lane | 2, 3 |
| `roof-35a23996` | 1860 Potter Street | 2 |
| `roof-3a76e3ec` | 731 East 20th Avenue | 2 |
| `roof-3ce27cdc` | 1923 Garden Ave | 3 |
| `roof-3d7a4503` | 2091 Fairmount Boulevard | 3 |
| `roof-4058a38b` | Campus Court / 1544 Alder Street | 1 |
| `roof-4680399a` | Heron House / 1888 Harris Street | 2 |
| `roof-4855fc7e` | Coho Townhouses (North) | 1 |
| `roof-4c32075c` | 1945 Kincaid Street / 1946 Harris Alley | 2 |
| `roof-4fa203d9` | 1915 Alder St | 2 |
| `roof-513d7fee` | The Rive Eugene | 1 |
| `roof-57dfe898` | Spencer Apartments | 2 |
| `roof-58a0e6b1` | 1692 / 1698 Hilyard Street | 1 |
| `roof-5a0db2c6` | 951 East 19th Avenue | 2 |
| `roof-5be21a96` | 1926 Potter Street | 2 |
| `roof-5e7ce49c` | The 1840 | 2 |
| `roof-649a6455` | Delta Tau Delta Chapter House | 2 |
| `roof-6594bfe8` | 2039 Harris Street | 2 |
| `roof-6750545e` | 1710 Hilyard Street | 1 |
| `roof-71f4af04` | Lorax Manner | 1 |
| `roof-7c1c7fb1` | University Business Operations Center | 1 |
| `roof-7c4b468d` | 2288 Birch Lane | 3 |
| `roof-7c73e16e` | Marlatt Apartments · West Wing | 1 |
| `roof-7e72b4ca` | 1959 Harris Street | 2 |
| `roof-846446eb` | 1838 Orchard St | 3 |
| `roof-8705a1c2` | Camelot / 800 East 18th Avenue | 2 |
| `roof-8aa49f9b` | 1834 Fairmount Blvd | 3 |
| `roof-95785982` | 853 East 20th Avenue | 2 |
| `roof-99cda8af` | 2171 Hamble Avenue | 3 |
| `roof-9cf9957b` | 1956 Fairmount Blvd | 3 |
| `roof-9d174b26` | 640 East 15th Avenue | 1 |
| `roof-a0566b7b` | 1989 Villard St | 3 |
| `roof-a49cdd04` | 1884 Garden Avenue | 3 |
| `roof-a53a0c57` | 2012 Villard Street | 3 |
| `roof-a577913c` | 1762 Hilyard Street | 1 |
| `roof-a633294a` | 674 East 16th Avenue / 685–695 East 16th Alley | 1 |
| `roof-aba1513b` | 1442 East 20th Avenue | 2 |
| `roof-ada23895` | 810 / 830 East 13th Avenue | 1 |
| `roof-adc35a27` | 1820 Walnut Street | 2 |
| `roof-b0798c1b` | 1992–1994 Potter Street | 2 |
| `roof-b1145ae3` | 671 East 16th Avenue | 1 |
| `roof-b4507d3f` | 630 East 14th Avenue | 1 |
| `roof-b4c9a6ff` | 720 East 20th Avenue | 2 |
| `roof-b8f94f8e` | Rainier Building | 3 |
| `roof-bb028710` | 1637 Villard St | 3 |
| `roof-bb7cc41d` | 1760 Walnut Street | 3 |
| `roof-bb7e0053` | Eugene Springfield Fire Station 13 · University Station | 2 |
| `roof-bb9ee65a` | 1468–1476 Orchard Aly | 3 |
| `roof-bece0173` | 1136 East 20th Avenue | 2 |
| `roof-bef4cf29` | 1841 E 15th Ave | 3 |
| `roof-c60174af` | 1740 Fairmount Blvd | 3 |
| `roof-c7815e30` | 746 East 19th Avenue | 2 |
| `roof-ce1d33a1` | UOPD East Station Annex A | 3 |
| `roof-ceb2cf04` | 360 Sunset Drive | 3 |
| `roof-d4aef710` | 1875 Alder Street | 2 |
| `roof-d5a8b80c` | 2275 Fairmount Boulevard | 3 |
| `roof-d6ddd6ae` | Pi Beta Phi Chapter House | 1 |
| `roof-d709354e` | 2105 Fairmount Boulevard | 3 |
| `roof-dcd48157` | 625–627 East 17th Avenue | 1 |
| `roof-e086d515` | 1778 Villard St | 3 |
| `roof-e32e043f` | 2285 Parkside Lane | 3 |
| `roof-ef20fcce` | 1961 Hilyard Street | 2 |
| `roof-f1fd1004` | Alderwood Manor / 1860 Alder Street | 2 |
| `roof-f43dd76e` | 1637 Orchard Street | 3 |
| `roof-f447a8a6` | 1772 Hilyard St | 1 |
| `state-1841241` | Chi Omega House | 1 |
| `state-1841280` | 1878 Villard St | 3 |
| `university-1960` | 1960 University Street | 2 |
| `villard-1946` | 1946 Villard Street | 2 |
| `walnut-1588` | 1588 Walnut Street | 3 |
