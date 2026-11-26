# Jordan Schnitzer Museum of Art west exterior, 2026-11-04

The [UO historic survey](https://cpfm.uoregon.edu/sites/default/files/schnitzermuseumofart05_30_07.pdf) depicts the historic building and site; the [museum history](https://jsma.uoregon.edu/about/history) describes patterned brick, cast stone and later expansion. The [UO Memorial Quadrangle history](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/memorial-quadrangle) locates the main facade facing the quad to the west. These sources were consulted only; photos were not redistributed or used as textures. Original geometry is CC BY 4.0.

A reversible source-pinned layer masks generic windows on the inferred west wall and adds a simplified patterned brick field, horizontal brick courses and pointed portal. Adjacent short north and south end-wall sections receive brick and trim. A reusable pointed-arch geometry type supports the portal. [West before](images/museum-west-before.png) / [after](images/museum-west-after.png); [close view](images/museum-entry-close.png). Its existing roof is retained. `roof-16751515` is an approximate locator in a LiDAR-derived footprint, which can include canopy and omits courtyards.

The portal and ornament are illustrative, not a measured reconstruction; exact entry position, brick pattern, inscriptions, sculpture, door and present details remain unverified. The tree in the existing scene obscures the entrance, and this decorative portal is not an interactive opening or verified accessible approach. The 2004 east expansion, most north and south elevations, courtyard, roof fixtures, planting and access are not reconstructed. The overlay adds no collision. Conservative west and end-wall rectangles screened against the ENU route graph with 0.5 m margin yielded zero intersections; this is not a pedestrian-clearance or accessibility survey. Terrain, trees, base GLB and interior were not changed. Keep level 1.

## Registered exterior and courtyard review, 2026-11-24

The local default preview replaces the museum exterior and its earlier west detail together. It keeps `roof-16751515` and restores the west and east roof heights, side pavilions, two side garden courts, and the 131.95 m² open Campbell Memorial Courtyard. The west arrival has patterned brickwork, a pointed portal, a layered surround, steps and the front apron. The rear addition has the low windows, small canopy and rail seen in the UO survey. The courtyard has brick arcades, a reflecting basin and simplified planting beds. Clicking the west approach enters the shared interior preview.

| Source | What informed the model |
| --- | --- |
| [UO building map](https://map.uoregon.edu/), building 024 | Main footprint, two open side notches, and the location and orientation of the enclosed court |
| [OSIP 2024 RGB orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer), EPSG:3740 | Roof breaks, openings and the paved west forecourt. The visible roof edges shift slightly from the mapped walls. |
| [USGS 3DEP lidar](https://apps.nationalmap.gov/downloader/), 2013–2015 campus grid | Relative roof heights and lower sloping galleries around the central court |
| [UO historic survey](https://cpfm.uoregon.edu/sites/default/files/schnitzermuseumofart05_30_07.pdf), PDF pages 4 and 6 | West portal, masonry bands, the outlined gardens and the 2004 rear addition |
| [Museum visitor map](https://jsma.uoregon.edu/sites/default/files/2024-08/2022FALLMAP.pdf) and [HBRA project photographs](https://hbra-arch.com/projects/academic/academic_schnitzermuseumofart_universityoforegon.html) | Court identification and the visible pool, brick arcades and upper windows |

Compared against the Knight Library example, the revised museum meets the project's L2 scope for exterior form, principal visible details, material differentiation and integration. The exact ornament, side garden treatments, roof fixtures, and entry heights remain approximate. The rear canopy and doors are façade details. The west approach is a game interaction point. Photographs and plans were used for reference. The package contains only original CC BY 4.0 geometry and metadata.

The registered footprint covers 2,267.61 m². Sampling 525 historical lidar cells at least 1.15 m inside adopted roof regions gave a median absolute height difference of 0.200 m, compared with 0.441 m for the prior manifest's single roof height. These cells come from the same historical grid used for registration. The small south gallery zone remained locally less accurate than the overall model. The route screen checked 7,705 edges for new conflicts at 0.42 m clearance and found zero. All 827 footing samples have at least 0.39 m of terrain cover. Matched west, east and elevated views cut four draw calls per view, and a separate courtyard view verified the new opening and the basin. Browser checks cover selection in both rendering modes, the three courts and enclosing walls, the west entrance round trip, and the previous-site fallback.

[Editable registration and source hashes](../data/metadata/museum-exterior-review.json) · [Builder](../scripts/build-museum-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/museum-exterior-review/site.json)

Reproduce from the repository root with `python scripts/build-museum-exterior-review.py --audit <path-to-audit.json>`. Source captures, paired views and numerical audits are retained in the research workspace under `exterior-l2/museum-20261124/`. The package remains local.

## Nearby planting batching

The nearby Tykeson and Fenton vegetation meshes are merged at load time only when both independently source-pinned layers are present and their identities and static material/transform contracts match. Building meshes and selection identities remain separate. Unit tests compare their geometry and colors; a local fixed view and the existing draw-call budget were checked. This reduces one draw call at the cost of coarser frustum culling across the nearby planting groups.
