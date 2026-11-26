# Six South University exteriors

| Scene ID | Address | Exterior detail |
| --- | --- | --- |
| `roof-213417ee` | Theta Chi Chapter House, 1125 East 19th Avenue | Both wings, the brick entrance gable and lettering, dark vertical siding, individual dormers and brick steps. |
| `roof-649a6455` | Delta Tau Delta Chapter House, 1886 University Street | Brick elevations, the east arch and gable, the ridge and dormers, and the lower northwest addition. |
| `roof-35a23996` | 1860 Potter Street | Stepped hips, dark horizontal siding, chimney and two yellow-green recessed doors. |
| `roof-7b1d50e1` | 1930 Onyx Street | The long low hip, vertical siding and two visible west alley doors. |
| `roof-16023474` | 1941 University Street | Intersecting high roofs, the lower rear wing, the alley garage door at scene grade and three upper sash windows. |
| `roof-b3d39b2f` | 1976 Onyx Street | Split roof planes and two sets of steps between the sidewalk and the covered east doorway. |

All six retain their scene IDs. Theta Chi uses the complete 581.74 m² City outline. The previous candidate intersected only 172.50 m² of that outline. At 1860 Potter, the National Register nomination used the Potter address for the preparer and lists the nominated farmhouse on Aspen Drive. The model uses the municipal Potter address and dated exterior evidence. The 1996 Holly Court advertisement is historical context for 1930 Onyx. Foliage screens parts of the three smaller Onyx and University frontages. Roof transitions, screened opening placements, door recess depth and approach grades include estimates. [Theta Chi IFC address](https://uoifc.com/theta-chi/) · [Delta Tau Delta IFC address](https://uoifc.com/delta-tau-delta/) · [Campbell nomination](https://heritagedata.prd.state.or.us/historic/index.cfm?do=main.loadFile&load=NR_Noms/79002088.pdf) · [Photographic links, coordinates and editable dimensions](../data/metadata/south-campus-frontages-review.json).

| Building | 2013–15 median absolute roof error | DOGAMI median absolute roof error |
| --- | ---: | ---: |
| Theta Chi | 1.0513 → 0.8400 m | 0.8295 → 0.4604 m |
| Delta Tau Delta | 1.6460 → 0.2789 m | 1.5946 → 0.3425 m |
| 1860 Potter | 1.4492 → 0.4943 m | 1.0327 → 0.2367 m |
| 1930 Onyx | 0.9958 → 0.2566 m | 0.9495 → 0.2641 m |
| 1941 University | 1.9952 → 0.8818 m | 2.1801 → 0.6190 m |
| 1976 Onyx | 1.0784 → 0.4690 m | 1.0670 → 0.3455 m |

The six roofs intercept all 3,472 rays from the two useful surface grids, including 2,488 cells also covered by the old roofs. Each paired median improves. The 2017 USACE grid yields one outlying cell at 1860 Potter with an error over 80 m. The table uses the two grids with full site coverage. Twelve matched views cover the visible elevations and roof transitions. Export removes exactly 1,425 source triangles and runtime comparison preserves the vertex attributes and index order of 51 untouched source batch members. The route checker covers 7,710 network edges with minimum clearance 5.2444 m.

Desktop and phone search select all six buildings. Fifteen collision probes include the restored west wing of Theta Chi. Six estimated routes lead from Knight Library to the modeled exterior approaches. The two viewports agree on route lengths of 147, 165, 136, 188, 175 and 200 points in table order. Damaged model bytes and an invalid final source anchor each restore all six old source meshes and their estimated entrances. Stage, repeat, installed, built and served package bytes match.

The package is local and uncommitted. Formatting, 197 unit tests, seven related browser tests and the production build passed. [Exporter](../scripts/build-south-campus-frontages-review.py).
