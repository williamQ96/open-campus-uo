# Oregon Hall and Jaqua exterior review

Oregon Hall (UO 042) and the Jaqua Academic Center (UO 067) are L2 against the [Knight Library comparison](knight-library-registration-2026-11-23.md). Their existing scene IDs keep search and selection stable. The wall, roof and landscape traces reconcile campus maps and photographs with the 2024 aerial and 2017 surface. [University map](https://map.uoregon.edu/) · [2024 OSIP aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 campus surface](campus-surface-2017-2026-11-24.md).

| Model | Registered envelope | Main exterior elements |
| --- | ---: | --- |
| Oregon Hall, `roof-11d15952` | 2,297.707 m² | Three-story west wing, four-story east wing, connector tower, recessed entrance and balcony, six-pane window bands, north terrace, raised planter |
| Jaqua, `context-b0067` | 1,477.631 m² | Three-level glazed cube, dense metal mullions, braced upper frame, roof equipment and long skylight, south and west approaches, reflecting pool |

Oregon Hall's south survey image and plan show the brick arcade, balcony and planter. The recessed entrance is 2.43 m behind the outer façade plane. Its footprint leaves the porch open between the modeled supports. The north deck and higher west and east decks follow the visible 2024 roof divisions and historical surface. The first-floor map supplies three modeled south-facing door anchors. Façade spacing, support depths, parapets, door thresholds and planter edges remain approximate. [Oregon Hall 2025 survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/oregonhall_2025_0.pdf#page=4) · [2018 renovation by Fortis and Pivot](https://fortisconstruction.com/project/university-of-oregon-oregon-hall-renovation/).

Jaqua's outer frame was registered from the aerial perimeter and edge returns in the historical raster. The photos show the pale mullions, braced roof perimeter and basin. The model represents the inner and outer façade planes, roof deck and upper steel with simplified glazing and screen geometry. The water uses a stylized surface. Two walks reach the first-floor doors while the basin and building block movement. A source-checked procedural tree rooted inside the building was omitted with the replacement. Glass appearance, rooftop fittings, basin levels and entry details remain approximate. [ZGF project and photographs](https://www.zgf.com/work/1156-university-of-oregon-john-e-jaqua-academic-center-for-student-athletes) · [Reflecting pool approach details](https://www.targetti.com/en/Projects/Jaqua-Stairs-Tivoli).

| Sample subset | Eligible points | Paired hits | Previous median absolute difference | L2 median absolute difference |
| --- | ---: | ---: | ---: | ---: |
| Oregon Hall flat roof decks | 1,487 | 1,416 | 0.101 m | 0.028 m |
| Jaqua roof inside the upper frame | 1,088 | 627 | 1.422 m | 0.218 m |

These checks use the same 2017 source raster that informed the model. The Oregon subset uses inboard returns close to the identified deck levels. The Jaqua subset excludes the narrow roof frame and uses returns between 11.90 and 15.55 m. The replacement covers all 2,575 eligible points. Nineteen paired views include render modes and context. The retained neighboring batch's positions, normals, colors and indices match. The context tree index count fell by 240 with all 240 removed indices belonging to the anchored tree.

Verified 7,710 active route edges, eleven collision probes, five walkable entrance anchors and both building selections in desktop and mobile production. Corrupt model bytes, a wrong terrain hash or a shifted tree anchor each restored both old models and the earlier entrances. The visible scene has 525 selectable buildings, including 452 source-batch members.

The [editable specification](../data/metadata/oregon-jaqua-site-review.json) and [generator](../scripts/build-oregon-jaqua-site-review.py) export the standalone GLB and descriptor. From the project root run `python scripts/build-oregon-jaqua-site-review.py --audit <audit.json>`. Source overlays, paired images and production readings are retained in the research worktree under `exterior-l2/east-campus-20261124/`.
