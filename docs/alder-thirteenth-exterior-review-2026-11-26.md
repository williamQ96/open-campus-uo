# Alder and East 13th exterior review

The former combined candidate is now four independently selectable buildings. Flock13 retains `roof-5ed4d412`. The corner shops, Gopuran Building and The Duck Store have their own IDs. Parcel outlines, the 2024 aerial and dated ground views constrain the placement. Screened walls, roof highs, trim and approach dimensions include estimates. [City taxlots](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/arcgis/rest/services/EugTaxlots/FeatureServer/0) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Editable model register](../data/metadata/alder-thirteenth-exterior-review.json).

| Exterior | Scene ID | Modeled details |
| --- | --- | --- |
| Alder & 13th Corner Shops, 1285 Alder | `alder-thirteenth-corner` | Brick street corner, red fascia, retail bays and the rear pitched roof |
| Gopuran Building, 839 E 13th | `alder-gopuran` | Narrow stone-fronted wing, upper balcony railing and glazed Webfoot entrance |
| Flock13, 871 E 13th | `roof-5ed4d412` | Seven levels, two light courts, metal walls with yellow accents and a timber-covered terrace above the storefronts |
| The Duck Store, 895 E 13th | `alder-duck-store` | Three clerestory gables, gray and yellow screen strips, recessed timber portal and five porch columns |

The 2024 streets show the retained corner and Gopuran front and rear. The design team's completion gallery documents the finished Flock13 street podium and The Duck Store's refreshed frontage. [Corner street view](https://www.google.com/maps/@?api=1&map_action=pano&pano=GeSUjl43td0KZn59HQbp5w&heading=51.14) · [Webfoot frontage](https://www.google.com/maps/@?api=1&map_action=pano&pano=mQFZ6tndG0dXGvNCh_vabQ&heading=21.77) · [Alley view](https://www.google.com/maps/@?api=1&map_action=pano&pano=AwzEEZmfxmCmKabnFcb8sw&heading=200.57) · [Design and completed exterior](https://rowellbrokaw.com/flock13).

Chapter Alder is represented by the construction state shown in the municipal September 2026 update. A 1,067.871 m² L-shaped slab, the columns, top-deck formwork and rails, fencing and crane fit inside the three registered permit lots totaling 1,258.32 m². The observed framing and fence details are approximate. The developer lists fall 2027 for delivery. The 1261 Alder house is retired from the default scene and preserved in the historical mapping. The corner property remains in use on taxlot 01400. [Municipal update](https://www.eugene-or.gov/m/newsflash/home/detail/7547) · [Municipal construction photo](https://www.eugene-or.gov/ImageRepository/Document?documentId=86041) · [Municipal zone verification](https://pdd.eugene-or.gov/LandUse/ApplicationReport?file=ZVR-25-0024&pdf=True) · [December 2025 demolition reporting](https://eugeneweekly.com/2025/12/24/choice-site-steep-price/) · [Project schedule](https://www.realcrg.com/project/chapter-alder).

## Verification

Five matched WebGL views cover the street corner, construction deck, shopfronts, Flock13 courts and alley. The package removes 2,031 source triangles across two batches. It preserves the attributes, surviving indices and 40 other batch members in the isolated audit. Roof probes hit both arms of the slab and leave the retained corner open in the construction mesh. The Flock13 terrace and tower hits differ by more than 19 m. The Duck Store probe distinguishes a ridge from its valley.

The local geometry audit checks 7,710 navigation edges and finds 2.5836 m minimum clearance. Desktop and phone production previews find all four buildings and verify four walkable estimated approaches and 11 collision probes. The route from 968 Alder to the Flock13 approach uses 108 points. Corrupting the former house's source anchor rolls back both original candidates, three split IDs and the construction closure. The staged, installed and served assets agree byte for byte.

The local inventory contains 224 L2 buildings, 300 active L1 buildings, 27 historical mappings, seven L2 outdoor groups and eight L1 outdoor groups. The default scene contains 524 selectable buildings, 302 batch members and two independent roof refinements. The package is local and uncommitted.

Run `python scripts/build-alder-thirteenth-exterior-review.py --stage OUTPUT --audit AUDIT.json` to reproduce the model. [Builder](../scripts/build-alder-thirteenth-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/alder-thirteenth-exterior-review/site.json).

The background tree review later registered removal of source tree 157 in this site descriptor. The assumed stem falls 8.447 m inside the Flock13 footprint. The 2024 aerial shows the roof at that point. The GLB reproduced byte for byte, and the tree returns when this site review is disabled. [Background tree review](context-trees-l2-2026-11-26.md).
