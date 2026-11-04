# Carson Hall exterior study, 2026-11-04

The [UO 2006 cultural resource survey](https://scholarsbank.uoregon.edu/bitstreams/87a6f7fd-12a7-43af-a9b7-f30907a2d778/download) describes five stories, brick walls, flat roof, concrete cornice, four-wing massing and grouped metal casement windows; its photograph identifies the east elevation. This historical reference is linked, not redistributed or used as a texture. New procedural geometry and color parameters are CC BY 4.0.

The existing `roof-2cd1068b` uses an approximate curated anchor inside a LiDAR-derived footprint; it can include canopy or omit parts of the building. A source-pinned color patch changes only 124 matched vertical wall vertices to brick, leaving roof, generic windows and the original GLB intact. A reversible layer adds illustrative five-level grouped windows and cornices on selected east, west, north and south wall segments. [East before](images/carson-east-before.png) / [after](images/carson-east-after.png); [west before](images/carson-west-before.png) / [after](images/carson-west-after.png). The existing flat roof remains; source imagery does not establish individual roof fixtures.

Facade spacing, sizes, complete wing boundaries and the current appearance are not surveyed; unmodified segments retain generic windows. Entry, glass stair towers, dining wing, planting and actual accessible routes remain unverified and are not reconstructed. Site terrain and trees were left as found. The overlay projects outside the base mesh and has no additional collision. A 0.5 m navigation-graph screening of conservative rectangles enclosing modeled spans found no crossing graph edges; it is not a pedestrian clearance or accessibility survey. Interior and original campus asset are unchanged. The building remains level 1.

The wall patch validates the exact source hash, unique building identity, color, normal and expected vertex count before applying a cloned-geometry color change. The rebuild preservation path verifies its file hash and source hash and refuses mismatched rebuilds.

## Navigation check correction, 2026-11-04

The initial automated rectangle check used render-space south coordinates as ENU north coordinates. The corrected sign and the same 0.5 m margin were rerun against the actual six facade envelopes and found zero graph-edge intersections. The automated test now uses ENU coordinates. This is still not a pedestrian-clearance or accessibility survey.
