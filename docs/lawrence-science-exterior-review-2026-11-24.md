# Lawrence, Pacific and Columbia Hall exterior review

The local default has three selectable exteriors on the university's footprints. Lawrence retains `roof-57a37f8e` and absorbs the separate eastern roof `roof-21450e38`. Pacific `uo-035` and Columbia `uo-036` receive their names and building information from `roof-4041562c` and `roof-64589bec`. Those two earlier name holders retain their original geometry and IDs as unidentified candidates. [Identity crosswalk](lawrence-science-exterior-crosswalk-2026-11-24.md) · [UO Campus Map](https://map.uoregon.edu/).

| Building | Rebuilt exterior | Ground footprint |
| --- | --- | ---: |
| Lawrence | Ten modeled roof regions, original brick wings, 1924 east wing, taller additions, open courtyard with planter, and west, east and south approaches. | 4,927.60 m² |
| Pacific | Stepped volumes, pale geometric façade with modeled mullions and sills, and a low west entry court with three steps. | 2,500.49 m² |
| Columbia | Raised east wing, lower auditorium and service roofs, columned south loggia and elevated link to Pacific. | 1,226.07 m² |

Columbia's footprint describes enclosed space at ground level. The bridge and loggia have separate overhead geometry, and the loggia's modeled piers contribute ground collision. The bridge has 2.854 m of clearance at the lowest-clearance sampled terrain corner in the model. The Lawrence layout represents the complex visible in 2024 imagery and the campus survey. [Lawrence survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/lawrencehall_2025.pdf) · [Pacific survey](https://cpfm.uoregon.edu/sites/default/files/pacific05_30_07.pdf) · [Columbia survey](https://cpfm.uoregon.edu/sites/default/files/columbia05_30_07.pdf) · [OSIP 2024 imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

Historical lidar first returns were sampled on a 1 m grid. Each median uses the same locations in the old composite mesh and the new building mesh. The returns include roof equipment and vegetation where present. [NOAA collection 8866](https://www.fisheries.noaa.gov/inport/item/57407).

| Roof area | Sampled cells | Cells with hits in both models | Prior median absolute difference | New median absolute difference |
| --- | ---: | ---: | ---: | ---: |
| Lawrence | 4,924 | 4,098 | 3.416 m | 0.254 m |
| Pacific | 2,454 | 2,161 | 2.624 m | 0.357 m |
| Columbia | 1,357 | 1,159 | 6.996 m | 0.108 m |

The three exteriors reach L2 after individual review against Knight Library using the registered footprints, roof profiles, material separation, modeled entrances and paired views. The open courtyard, low Pacific entry wing and covered Columbia frontage distinguish the buildings at campus scale. Window spacing, threshold dimensions, planting and parts of the rear elevations remain approximate. Entrance interactions use the shared interior preview. [Knight Library example](knight-library-registration-2026-11-23.md) · [Upstream grading guidance](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/zh-CN/asset-refinement-inventory.md#等级及适用范围).

The builder checks all 7,705 navigation edges against the replacement outlines, courtyard planter and loggia supports at a 0.42 m radius. The check found zero new conflicts. Runtime probes cover the courtyard, planter, perimeter wall, bridge underpass and walls on either side. Position, normal, color and index buffers match the previous revision for both retained unnamed meshes. A failed site pin restores the prior geometry, identity bindings and approaches together.

The editable inputs are [the layout](../data/metadata/lawrence-science-site-review.json) and [the builder](../scripts/build-lawrence-science-site-review.py). Run `python scripts/build-lawrence-science-site-review.py --audit <audit.json>` from the checkout root. The research worktree holds source snapshots, paired renders and measurements under `exterior-l2/lawrence-science-20261124/`. The delivered GLB contains original modeled geometry. Work remains local.
