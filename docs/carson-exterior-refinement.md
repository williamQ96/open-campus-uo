# Carson Hall exterior study, 2026-11-04

The [UO 2006 cultural resource survey](https://scholarsbank.uoregon.edu/bitstreams/87a6f7fd-12a7-43af-a9b7-f30907a2d778/download) describes five stories, brick walls, flat roof, concrete cornice, four-wing massing and grouped metal casement windows; its photograph identifies the east elevation. This historical reference is linked, not redistributed or used as a texture. New procedural geometry and color parameters are CC BY 4.0.

The existing `roof-2cd1068b` uses an approximate curated anchor inside a LiDAR-derived footprint; it can include canopy or omit parts of the building. A source-pinned color patch changes only 124 matched vertical wall vertices to brick, leaving roof, generic windows and the original GLB intact. A reversible layer adds illustrative five-level grouped windows and cornices on selected east, west, north and south wall segments. [East before](images/carson-east-before.png) / [after](images/carson-east-after.png); [west before](images/carson-west-before.png) / [after](images/carson-west-after.png). The existing flat roof remains; source imagery does not establish individual roof fixtures.

Facade spacing, sizes, complete wing boundaries and the current appearance are not surveyed; unmodified segments retain generic windows. Entry, glass stair towers, dining wing, planting and actual accessible routes remain unverified and are not reconstructed. Site terrain and trees were left as found. The overlay projects outside the base mesh and has no additional collision. A 0.5 m navigation-graph screening of conservative rectangles enclosing modeled spans found no crossing graph edges; it is not a pedestrian clearance or accessibility survey. Interior and original campus asset are unchanged. The building remains level 1.

The wall patch validates the exact source hash, unique building identity, color, normal and expected vertex count before applying a cloned-geometry color change. The rebuild preservation path verifies its file hash and source hash and refuses mismatched rebuilds.

## Navigation check correction, 2026-11-04

The initial automated rectangle check used render-space south coordinates as ENU north coordinates. The corrected sign and the same 0.5 m margin were rerun against the actual six facade envelopes and found zero graph-edge intersections. The automated test now uses ENU coordinates. This is still not a pedestrian-clearance or accessibility survey.

## East upper-window transoms, 2026-11-23

Page 4 of the 2006 and [2025 UO surveys](https://cpfm.uoregon.edu/sites/default/files/2025-01/carsonhall_2025.pdf#page=4) shows the same east facade photograph. The updated opening description supports grouped steel casements with an offset horizontal division. The east overlay now has 16 thin metal transoms across four window groups on each of the four upper rows. The 0.20 m offset below each modeled center is an interpretation of the visible proportions. The existing glazing, mullions, ground-floor group, and all 387 prior components remain in place. The survey is a linked reference and no photo pixels are included in the geometry.

The new boxes add 192 model triangles to the existing single merged mesh. Geometry rays checked all 20 east groups, including exposed glass above and below the transoms and the undivided ground-floor row. First-person comparisons used the same verified cameras at front and oblique positions. Draw counts held at 312 and 272 respectively, selection still resolved to `roof-2cd1068b`, and all 534 runtime entrance records and both sampled collision states matched. The Carson selection test also passed in both render modes. The standalone overlay reimported as one mesh with 14,508 vertices and exact position, normal and color values. The source pin, viewer overrides and asset checksums passed.

The [earlier public-map footprint screen](interior-preflight-carson-hall-2026-11-16.md#base-presentation-geometry-screen) found that the projected base mesh intersects 90.67% of the UO 076 map polygon. The remaining envelope, stair-tower glazing, east entry and other elevations still need evidence and scene review. The window work advances the exterior toward the L2 target. Its full-building level remains 1 pending review.

Before/after source and views, reference PDFs and GLB round-trip evidence are retained in `D:/github/opencampus-interior-research-20261116/exterior-l2/carson-20261123/` with hashes in `manifest.json`. Local only.
