# East 18th Avenue at the Rankin frontage

The registration continues along Pioneer Cemetery from the previous west site to University Street. Twelve tiles from the 2017, 2021, 2023 and 2025 Lane County orthophotos document both sidewalks, roadside parking, bicycle lane edges, the turn lane and the western crossing at University Street. The earlier cemetery survey defines the continuous north sidewalk. Dated imagery shows graves and planting between the street sidewalk and the separate Rankin Lane inside the cemetery. The modeled through-route follows the street sidewalks and the crossing at University Street. [Lane County orthophotos](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Cemetery review](pioneer-cemetery-landscape-review-2026-11-26.md#university-street-and-rankin-lane-perimeter).

| Feature | Modeled coverage |
| --- | --- |
| Street pavement | 2,829.76 m² of asphalt with centerline, bicycle lane edges, turn-lane line, parking ticks and curb markings. The roadway ends against the registered Southgate pavement. |
| South sidewalk | 268.47 m² of new sidewalk and aprons along the south frontage, including the observed driveway and side-street mouths. |
| North sidewalk | 322.94 m² of existing Rankin frontage registered for standing height using the original pavement tessellation and heightfield. |
| Navigation | 50 edges across the two sidewalks and the University Street west-leg crossing, attached to the earlier East 18th and University Street route nodes. |

The first frontage package fitted the asphalt around Southgate's paired crossing lines. The subsequent junction revision uses the dated aerial line positions, adds the two south sidewalk returns and connects the eastern crossing. The model estimates obscured curb transitions, parking stripe lengths and the sidewalk profiles at driveway mouths. [Editable registration](../data/metadata/rankin-frontage.json) · [Exporter](../scripts/build-rankin-frontage.py) · [West approach](east-18th-west-approach-2026-11-27.md) · [Southgate junction revision](southgate-junction-2026-11-27.md).

Desktop and phone each match all 611 local exterior IDs and 388 resources. All five sampled routes stay within 0.13 m of the modeled paved surfaces. The west-to-University route measures 216.489 m, and both crossing probes stay between Southgate's painted lines. The prior 0.106 m standing-height discrepancy is gone. Standing and visible paving match at the ten north sidewalk probes, and their difference stays below 1 mm at eight south sidewalk and crossing probes. Sixty-five served files match the build. The site, descriptor and route coverage reproduce byte for byte. This revision was first verified in the research worktree.

The final frontage package reserves the junction returns for the Southgate revision and publishes 2,829.01 m² of Rankin asphalt and 260.99 m² of Rankin sidewalk.
