# Hilyard and West University exterior review

On 2026-11-24, the local default viewer adopted four editable exteriors under their existing scene IDs.

| Building | Scene ID | Exterior modeled |
| --- | --- | --- |
| Catherine Cornwall Townhouses, 978 Hilyard St | `roof-a3d5625f` | Shallow roof, salmon end wall, dark siding bays, west stair and a raised south gallery over parking. |
| Hilyard House, 725 E 14th Ave | `roof-ca59da4d` | Crossed roof wings around an open courtyard, brick wall and pale upper siding, and a four-column south portico. |
| Campus Studios, 735 E 14th Ave | `roof-dcc94271` | Flat roof, red end bays, gray center glazing and a covered parking opening below the upper stories. |
| Bushnell University, 722 E 11th Ave | `roof-ae986c58` | Three-story main shell, roof equipment, glazed bays and an entrance cover on E 11th. |

The 2024 aerial separates the 735 footprint from its 751 neighbor and resolves the step at the north end of Hilyard House’s open courtyard. The court uses the aerial boundary after comparison with the coarse state outline. The property-manager images support the front details and the covered spaces at 978 and 735. A university photograph and acquisition release support the 722 building identity, height and rooftop details. The 722 north windows, the deeper parking extents, a number of support positions and door and stair dimensions use approximate geometry. The skybridge at E 11th requires a paired review with the different 770 footprint. [Editable registration](../data/metadata/hilyard-west-exterior-review.json) · [2024 Oregon ortho](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Catherine Cornwall Townhouses](https://vonkleinrentals.com/all-rentals/catherine-cornwall-townhouses/) · [Hilyard House](https://vonkleinrentals.com/all-rentals/hilyard-house/) · [Campus Studios](https://vonkleinrentals.com/all-rentals/campus-twins/) · [Bushnell acquisition](https://bushnell.edu/news/bushnell-university-closes-on-university-district-hospital-properties/) · [Bushnell exterior aerial](https://bushnell.edu/news/the-register-guard-see-inside-bushnells-university-district-campus-renovation/).

## Roof and courtyard checks

The three historical grids cover all 3,397 interior roof sample cells. The source and replacement both intersect 3,179. Median absolute errors below use each building’s common cells.

| Building | Shared roof cells | 2013–15 archive, source → L2 | USACE 2017, source → L2 | DOGAMI Lane County, source → L2 |
| --- | ---: | ---: | ---: | ---: |
| 978 Hilyard | 271 | 1.082 → 0.431 m | 1.134 → 0.144 m | 1.305 → 0.109 m |
| 725 E 14th | 1,284 | 1.750 → 0.915 m | 1.779 → 0.308 m | 1.749 → 0.299 m |
| 735 E 14th | 655 | 0.898 → 0.110 m | 0.749 → 0.047 m | 0.880 → 0.098 m |
| 722 E 11th | 969 | 0.834 → 0.129 m | 0.745 → 0.088 m | 0.756 → 0.084 m |

The Hilyard House courtyard has 116 diagnostic cells. The highest ray intersection there is the court surface at −1.183 m ENU. At 978 Hilyard, tree-covered new edge samples have median USACE residual 7.035 m and median Lane County residual 5.973 m. The historical roof registration remains approximate on that edge. [Acquisition details and local 2017 alignment](campus-surface-2017-2026-11-24.md) · [Lane County project report](https://pubs.oregon.gov/dogami/ldq/reports/2013_2014_OLC_Lane_County_Delivery_2_4.pdf).

## Viewer verification

- Eleven before-and-after views cover street elevations, the courtyard, gallery, parking opening and roofs. Two source batches omit 1,803 triangles. Vertex arrays and surviving indices remain exact for the other 86 members in those batches.
- Static checks cover 7,710 route edges with a nearest clearance of 3.124 m. Desktop and mobile production each confirm four searchable exterior names, four walkable approaches, five collision-free spaces and 22 solid support samples. Anchor, terrain and GLB failures each restore the four source meshes. The first 46-case Playwright run passed 44 cases. Both affected files passed all four cases after the census import and stair offset assertions were fixed.
- Staged and adopted assets match byte for byte. The preceding six exteriors re-exported with matching GLB and descriptor hashes. The production census is 519 selectable buildings, 340 batch members and seven independent roof treatments. The [outdoor ledger](asset-refinement-inventory.md) records 181 L2 buildings, 338 active L1 buildings, 13 L1 outdoor groups and 21 historical mappings.

[Builder](../scripts/build-hilyard-west-exterior-review.py) · [Adopted descriptor](../apps/web-preview/public/scene/hilyard-west-exterior-review/site.json).

```powershell
python scripts/build-hilyard-west-exterior-review.py --audit D:/path/to/hilyard-west-audit.json
```

Use `--stage <directory>` for an isolated export. Renders and audits are in `exterior-l2/east-campus-20261124/hilyard-west-stage/` in the research worktree. This batch is local.
