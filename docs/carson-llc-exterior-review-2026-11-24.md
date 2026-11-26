# Carson Hall and Living-Learning Center exterior review

The three models replace the earlier forms under their original scene IDs. University walls and floor references were registered to the 2024 aerial. The 2017 surface, university photographs and architectural reports guided roof forms and visible façade details. Carson (076) and both Living-Learning Center buildings (065 and 064) meet the project's [Knight Library L2 comparison](knight-library-registration-2026-11-23.md). [University map](https://map.uoregon.edu/) · [2024 OSIP imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface](campus-surface-2017-2026-11-24.md).

| Model | Registered wall area | Local translation east, north | Main exterior elements |
| --- | ---: | --- | --- |
| Carson Hall | 2,130.436 m² | −2.48 m, +1.45 m | Five-story pinwheel, lower northern dining and kitchen roof, raised rooftop equipment, brick walls, four-light casements, east portico and west canopy |
| Living-Learning Center North | 1,622.968 m² | −2.73 m, +0.48 m | Open U-shaped court, shallow roof pitches and raised ridge, two solar panel rows, stair towers, clerestory and glazed quad frontage |
| Living-Learning Center South | 1,127.715 m² | −2.63 m, +2.08 m | Shallow roof pitches and raised ridge, recessed wings, curved low terrace frontage, glass stair bays and projecting window shades |

The Carson survey records the low northern kitchen and east travertine portico. The first-floor map and dated photos guide the two entry locations. The Living-Learning Center housing study identifies the pale upper story, darker brick, stair glazing, louvres and North solar panels. The public floor maps and a university dissertation guided where each upper wing ends and how the South low terrace meets the four-story building. Façade spacing, façade setbacks, rooftop equipment, paving and thresholds remain approximate. [Carson 2025 resource survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/carsonhall_2025.pdf#page=4) · [Living-Learning Center housing study](https://cpfm.uoregon.edu/sites/default/files/uo_rhfmdstudy_101211_0.pdf#page=171) · [Roof and courtyard diagrams](https://scholarsbank.uoregon.edu/server/api/core/bitstreams/3cf8362c-b20b-4bad-b854-67f30a7185fd/content#page=54).

The common grade includes the elliptical quad lawn and walks, the open North court and the South terrace approaches. All 7,710 active route edges clear the replacement ground footprints, with 14.326 m minimum separation in the route-edge screen. Ten approach anchors were walkable in desktop and mobile production. Eight point checks covered walls beside the court and approaches. A damaged GLB or mismatched source terrain hash restored all three prior models and their approaches together.

| Roof surface | Eligible points | Paired scene hits | Previous median absolute difference | L2 median absolute difference |
| --- | ---: | ---: | ---: | ---: |
| Carson | 1,909 | 1,898 | 1.879 m | 0.082 m |
| Living-Learning Center North | 1,362 | 1,255 | 0.910 m | 0.083 m |
| Living-Learning Center South | 988 | 972 | 0.732 m | 0.110 m |

The roof comparison uses the same 2017 raster that informed the geometry and excludes samples near the building boundaries. The replacement covers all 4,259 eligible points. Sixteen paired views cover roof profiles, the Carson portico, LLC façade tiers, the quad and the South terrace. The inspected neighboring batch has matching position, normal, color and index archives. The scene census is 525 selectable buildings, including 452 source-batch members.

The [editable specification](../data/metadata/carson-llc-site-review.json) and [generator](../scripts/build-carson-llc-site-review.py) export the standalone package. Run `python scripts/build-carson-llc-site-review.py --audit <audit.json>` from the project root. The research worktree directory `exterior-l2/east-campus-20261124/` holds the source overlays, paired views, fit samples and production checks.
