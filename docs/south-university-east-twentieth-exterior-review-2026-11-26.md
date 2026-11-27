# South University and East 20th–21st exterior review

The local package rebuilds eight legacy ranges as 13 addressable houses. The old IDs stay with the larger overlap or primary address. Five separately confirmed buildings get their own IDs. The source registration contains 14 municipal records and 13 distinct outlines. City records 129433 and 129658 at 2090 Hilyard duplicate the same polygon and tax lot. Both receipts stay with the one rebuilt house. [Editable specification](../data/metadata/south-university-east-twentieth-review.json) · [Reproducible exporter](../scripts/build-south-university-east-twentieth-review.py).

## Buildings and separation

The review uses 2017, 2021 and 2025 Lane County aerials, 36 street bearings from 26 panoramas, municipal outlines and address data, and the 2013–15 and DOGAMI surface grids. The 2017 surface raster misses the selected area. Roof transitions and visible materials were estimated from the recorded views. Behind foliage, selected window, door and fine trim dimensions remain approximate.

| Legacy range | Addressable exteriors | Physical detail |
| --- | --- | --- |
| 2090 Hilyard | 2090 Hilyard | Western low roof joined to the taller eastern hips. Street trees obscure the entrance. |
| 741 East 21st | 741 East 21st | South-facing porch, rear roof wing and low chimney. |
| 892 East 20th | 892 East 20th and 2028 Kincaid | 2.321 m between the roof outlines. 2028 keeps a recessed wall beneath its gabled porch and two separate posts. |
| 853 and 893 East 20th | 853 and 893 East 20th | 8.331 m between roof outlines, with separate south entries. |
| 720 and 740 East 20th | 720 and 740 East 20th | 2.116 m between roof outlines. The west house keeps its returning low wing. |
| 675 East 20th | 675 East 20th and 1998 Hilyard share one house | The two wings remain joined under the low roof. The Hilyard-side frontage has an estimated gate. |
| 2040 and 2060 Alder | 2040 and 2060 Alder | 1.206 m between roof outlines and independent east-facing gates. |
| 731 and 741 East 20th | 731 and 741 East 20th | 0.729 m between the roof outlines. 731 retains two light roof sections and 741 a separate front gable. |

## Verification

All 3,478 eligible roof rays hit, with 2,860 paired previous and rebuilt samples. Twenty-four of 26 building-by-grid median absolute errors decrease. The 2013–15 median at 892 East 20th rises from 0.8810 to 1.2750 m. The DOGAMI median at 2028 Kincaid rises from 0.4627 to 0.5564 m.

Eighteen paired cameras and index checks verify 3,082 removed source triangles and 47 untouched neighboring ranges. Rays between all five pairs miss both replacement roofs. On the 2028 porch, a vertical ray hits the canopy at 7.626 m, and an inward ray at eye level crosses approximately 1.238 m to the recessed wall. The old network check covers 7,710 edges with a minimum clearance of 5.7835 m.

Desktop and phone verify 13 named selections and four address lookups. Fifteen occupied samples cover thirteen interiors and two porch posts. Six clear samples cover all five building gaps and the middle of the 2028 Kincaid porch. Each device checks 48 clear gate approaches. All twelve gates route from Knight Library to their modeled approach points. Invalid GLB and shifted source anchor tests restore the eight earlier ranges, including the previous collision at four of the five split gaps.

The local inventory has 568 L2 building exteriors, 39 active L1 exteriors, 39 historical mappings and all 15 outdoor asset groups at L2. The publicly deployed checkpoint remains `c3dc42c`.
