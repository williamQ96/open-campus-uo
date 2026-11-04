# Anstett Hall south frontage

A source-pinned detail layer adds an interpreted brick south facade, central arched windows and entrance, two planters with shrubs and two benches. The original Lillis complex meshes and `roof-0a498bf7` identity remain. The [2019 Gary Halvorson / Oregon State Archives CC BY 4.0 photograph](https://commons.wikimedia.org/wiki/File:Anstett_Hall,_University_of_Oregon,_Eugene_-_DPLA_-_7f05aff2c79e236edd0bed0104b6f145.jpg) is archived with attribution and hash; the [UO survey and site plan](https://cpfm.uoregon.edu/anstetthall2025) identifies the 13th Avenue frontage and is linked only. No photograph is a runtime texture.

The facade, steps, planters, bench and shrub placement are simplified and not surveyed; current conditions, species, dimensions, collisions and accessibility are unverified. They do not establish a walkable route. Other elevations retain the existing model, and level remains 1. No interior is changed. The card now reports classrooms, offices and the Anstett Family Accounting Suite from the [UO business complex page](https://business.uoregon.edu/about/lillis-complex), not a complete tenant list. [Before](images/anstett-south-before.png) / [after](images/anstett-south-after.png).

## Bench follow-up

Both illustrative benches now have slatted backs and armrests inspired by the existing archived 2019 photograph. Their dimensions, exact positions, current condition, collision and clearance remain unverified. [Scene review](images/anstett-bench-slats.png).

## Planter follow-up

The two illustrative raised beds now have stone rims, soil and varied low foliage instead of solid pale tops. Forms are informed by the archived 2019 photograph; species, placement and present conditions remain unverified. No accessibility or clearance claim is made. [Scene review](images/anstett-planters-after.png).

## Globe lamps and hanging basket

A separate source-pinned landscape detail layer adds two illustrative globe lamps and a seasonal hanging basket, inspired by the existing attributed 2019 photograph and UO survey already linked above. The pole bases use scene-ground samples around 1.74 m and 2.06 m. The flower colors and form are stylized; species are unidentified. Position, dimensions, current conditions, clearances and collision are not surveyed; these are not accessibility or navigation guarantees. The existing building, planters, benches and underlying source geometry remain intact. This local improvement does not change the level of the shared vegetation or landscape furniture categories.

[Before](images/anstett-lamps-before.png), [after](images/anstett-lamps-after.png), [close view](images/anstett-lamps-close.png). 64 unit tests, the campus loading/selection browser test, visual browser review and the production build passed.

## South elevation follow-up, 2026-11-04

The existing source-pinned facade was revised as a coherent front elevation from the linked UO historic survey and attributed 2019 photograph. Each wing now has one two-storey window bay instead of two; brick piers, cornices and the central vertical brick motif frame the retained triple arches. The entrance now has a rectangular glazed double door within the existing arched stone surround, with simplified columns and lintel. Both existing stair flights receive stepped brick side walls and stone coping. This is an original stylized interpretation rather than a measured replica; details, dimensions, roof, other elevations and current conditions remain incomplete or uncertain. The visible entry and added stair walls do not update navigation or collision and are not evidence of accessibility. Level stays 1.

The 20 existing vegetation objects, 32 bench objects and 10 planter-wall/rim objects were checked unchanged; the independently authored lamps also remain. The former specification is retained at `assets/exterior-refinement/anstett-south-before-2026-11-04.json`. The source campus GLB and interiors remain unchanged. [Before](images/anstett-south-v2-before.png), [front](images/anstett-south-v2-after.png), [oblique](images/anstett-south-v2-side.png). Verified 75 JavaScript tests, 6 targeted browser tests including selection, mobile and draw-call budget, 12 rebuild-layer tests and production build.

## Entry orientation needs reconciliation, 2026-11-04

The linked [UO 2025 survey](https://cpfm.uoregon.edu/anstetthall2025), page 1, describes the notable stair entry as facing west into the courtyard; the current `anstett-south-detail.json` models the referenced entrance on a south-facing plane. The survey's site diagram does not by itself resolve the modeled footprint's nearest-roof identity and facade mapping. This is a potential discrepancy, not proof that either mapping is correct. The overlay and entry positions were not changed; reconcile the survey, current campus plan and source mesh before moving them. Level remains 1.
