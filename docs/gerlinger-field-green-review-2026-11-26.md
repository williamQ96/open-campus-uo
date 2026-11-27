# Gerlinger Field Green landscape review

The current registration covers the open lawn between Gerlinger Hall, Gerlinger Annex, Pioneer Cemetery and University Street. The 2007 campus survey records the field's three perimeter walks, south bicycle connection and planted edges. Lane County's 2017, 2021 and 2025 orthophotos establish the present outlines. November 2020 and June 2026 street views confirm the diagonal street approach, the east retaining wall, the blue parking sign, and the southern path entry. [UO landscape survey](https://cpfm.uoregon.edu/sites/default/files/gerlinger_field_green_05_10_07.pdf) · [Lane County orthophotos](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Street approach](https://www.google.com/maps/@?api=1&map_action=pano&pano=QxdujQm-DQnJ2_bfq3wjsA&heading=266.37) · [Street edge](https://www.google.com/maps/@?api=1&map_action=pano&pano=CIABIhAwe59LBf0I4-G9Z0Vn_JAd&heading=276.52).

| Feature | Registration |
| --- | --- |
| Lawn and perimeter walks | About 4,149 m² of open lawn, six modeled walks, and about 1,111 m² of pavement including the Annex apron. Asphalt, concrete, the Hall walk joints and the curb ramp use separate surfaces. |
| East edge and south path | About 39.4 m of low wall and 909 m² of planted ground, with a simplified blue parking sign at the sidewalk. The east wall segments leave both path openings clear. |
| Annex stair and apron | The June 2026 view shows a diagonal concrete stair profile, an open space below it and marked surface parking. The model estimates 15 treads, two landings, a concrete outer fascia and guardrails. The stair count, dimensions, parking stripes and upper landing are estimates. |
| Vegetation | The UO registry anchors ten edge trees. Crown dimensions and the arrangement of low ivy are approximate. The site hides 42 conflicting procedural pilot trees and 12 shrubs using checked source mesh ranges. |

The apron covers the visible east end of the Annex parking row. The original Gerlinger Hall south flights and the breezeway are retained from the adjacent exterior reconstruction. The field route adds nine navigation edges from University Street to the Hall south walk. The registered line is 60.59 m and the preview router returns 57.93 m between the test endpoints. The south path and the Annex stair have modeled standing surfaces. The west parking continuation and precise Annex landing connection need more evidence. [Annex and parking view](https://www.google.com/maps/@?api=1&map_action=pano&pano=CIABIhDHIJVQd5u8oP0oQWPv-Vmm&heading=7.22) · [South path entry](https://www.google.com/maps/@?api=1&map_action=pano&pano=CIABIhBBB11-IDr7uclODSQRkYa6&heading=272.19) · [UO tree inventory](https://cpfm.uoregon.edu/trees) · [Gerlinger exterior review](gerlinger-site-review-2026-11-24.md).

Both exports matched byte for byte. Source imagery and the paired views are retained in the research worktree under `exterior-l2/gerlinger-field-green-20261126/`. The geometry is part of the default outdoor scene in the November 27 release. [Release history](../DEVELOPMENT_LOG.md#2026-11-27---release-expanded-outdoor-l2-landscapes).

- [Editable registration](../data/metadata/gerlinger-field-green-review.json)
- [Exporter](../scripts/build-gerlinger-field-green-review.py)
- [Runtime descriptor](../apps/web-preview/public/scene/gerlinger-field-green-review/site.json)
