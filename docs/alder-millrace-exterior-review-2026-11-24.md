# Alder Street and Millrace apartment exteriors

Reviewed on 2026-11-24 for Open Campus: UO. All three buildings retain their existing selection IDs and use original exterior meshes in the local default scene.

| Building | Stable ID | State footprint | Exterior review |
| --- | --- | --- | --- |
| 1915 Alder St | `roof-4fa203d9` | `20-1073616` | Compact hipped roof over two brick levels, a pale post-supported entry hood, paired street-facing windows and low basement windows. |
| Hess Apartments, 1390 Alder St | `roof-7dcf2f03` | `20-1073339` | Long gable, vertical siding, three balcony levels, stair near the north end of the Alder elevation and an open covered parking bay. |
| Millrace Apartments, 1805 Garden Ave | `roof-77a7eb6c` | `20-1073439` | Flat deck with a parapet, pale lap siding, green balcony rails and posts, narrow upper windows and enclosed ground patios. |

The outline registration pairs Oregon building footprints with Eugene municipal addresses. Roof orientation and material follow the 2024 orthophoto and the historical slope and height fits. The rebuild carries the three established roof types into the registered outlines and refits their centers and spans. It preserves the fitted eave and ridge heights to within 1 mm. Thresholds, gallery projections, window dimensions and obscured openings remain approximate. The Millrace entrance is a representative approach on the parking side. [State inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Lane County lidar](https://www.fisheries.noaa.gov/inport/item/57407) · [Prior roof fits](context-roof-refinements-2026-11-23.md).

- The June 2024 image of 1915 Alder shows the brick courses, grouped windows, shutters and centered cream canopy. [Alder Street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=pis7zBMAGlEsaDs4rcqYBg&heading=90).
- The July 2024 view at 1390 Alder shows the parking opening, three rows of windows and north-side stairs. The leasing listing corroborates the address, balcony and covered parking. [Hess street image](https://www.google.com/maps/@?api=1&map_action=pano&pano=jctcJj_gV1p17eiiTgLCMA&heading=276) · [Hess leasing listing](https://www.zillow.com/apartments/eugene-or/hess-apartments/5XtRxW/).
- The July 2024 Millrace view shows three visible levels along the south elevation. The east return is largely blank. The city inspection packet identifies the property and provides dated photographs. [South elevation](https://www.google.com/maps/@?api=1&map_action=pano&pano=-ZKjZ6ehs-1Tpeo9k6qEug&heading=336) · [East return](https://www.google.com/maps/@?api=1&map_action=pano&pano=uHea1IbrMdF6CGTNhA474Q&heading=269) · [Eugene City Council packet, 2023-11-15](https://ompnetwork.s3-us-west-2.amazonaws.com/sites/134/documents/cc_agenda_packet_11-15-23_ws_post.pdf?V3F_Ie_wlwiSehdcSvQSTtaVQAvpmNCp=).

The street photographs were used as visual references. The GLB contains original geometry and vertex colors, with no photographs or image textures. [Model parameters](../data/metadata/alder-millrace-exterior-review.json) · [Builder](../scripts/build-alder-millrace-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/alder-millrace-exterior-review/site.json).

## Placement and validation

- Compared six before-and-after views covering the front, side and roof. The batch check confirmed that 484 source triangles were removed and the attributes, indices and selection IDs of 113 neighboring members were retained.
- Checked all 7,710 active route edges. The smallest route clearance was 10.618 m. The three street approaches are walkable. The Hess parking bay now passes ground collision while its recessed core remains solid.
- Local production has 519 selectable buildings, 404 source-batch members, 14 separate roof treatments and 139 road segments. The terrain, planting counts and other entrances retain their prior registrations.
- Production desktop and mobile checks verified name-based selection and the three fallbacks for a bad source anchor, changed terrain hash and damaged mesh. All 22 targeted browser cases passed across two runs using the viewer's supported name search.
- The [outdoor ledger](asset-refinement-inventory.md) records 117 L2 exteriors, 402 independent L1 buildings, 13 L1 environment groups and 21 historical mappings.

Rebuild the local scene package and retain the resulting audit.

```powershell
python scripts/build-alder-millrace-exterior-review.py --audit D:/path/to/alder-millrace-audit.json
```

Use `--stage <directory>` to produce an isolated package before adoption. The repeat build matched both GLB and descriptor hashes. Paired renderings, test outputs and point checks are retained in the research worktree under `exterior-l2/east-campus-20261124/alder-millrace-stage/`. The changes are local, with publication pending.
