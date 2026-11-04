# Environmental refinement: tree 273 and rider contact

2026-11-03 · Local and unpublished. ENV-01 and PROP-03 remain at the user-assigned level 1; no new level standard is implied.

## Tree review and restrained correction

The project’s approved archived [2024-06-08 USDA NAIP pilot orthophoto](../data/reference-images/aerial/naip-2024-pilot-rgb.png), its [extent and source metadata](../data/metadata/naip-2024-reference.json), and the licensed [2018 Knight photographs](../data/reference-images/photos/knight-library/) and [2017 EMU view](../data/reference-images/photos/erb-memorial-union/exterior-2017.jpg) were reviewed. [Aerial comparison](images/tree-aerial-review.png) plots the generated centers of trees 129, 296 and 273 using the archived georeference. NAIP is a dated 0.6 m/px public-domain aerial reference, not a current tree census. The photographs are Gary Halvorson/Oregon State Archives, CC BY 4.0, and Daderot, CC0, respectively; credits and exact archive hashes are in the [reference manifest](../data/reference-images/manifest.json). No photographic texture is embedded in the scene.

The 2024 reference at tree 273 shows an open grass/paving boundary with no evident canopy at the generated center. The model tree also intersected the inferred EMU mesh. Accordingly, one procedural tree is suppressed in the runtime presentation instead of being moved to a speculative location. This is an inference for the dated visual reference, not proof of present-day conditions or a surveyed stem. [Before](images/tree-screen-emu.png) · [after](images/emu-tree-273-after.png). The original campus GLB and landmark Blender remain unchanged; a source-pinned patch and isolated editable candidate preserve reversibility. The underlying generator still contains 600 trees; one suppressed tree yields 599 visible. The local BVH audit retains original intersections and separately confirms the edited candidate’s target vertices collapse to a point.

Trees 129 and 296 remain unchanged: their projected centers lie in or near dense canopy and/or building edges in the aerial, and the two Knight photographs do not establish those stems or their positions. Better permitted references and mesh/placement review are needed before changing them. UO’s [Trees page](https://cpfm.uoregon.edu/trees) identifies a campus tree app, but availability does not establish rights to copy or redistribute its GIS. No such GIS data were used.

The campus art rebuild guard verifies and retains the suppression patch and visible/source counts for the same source GLB; changed source bytes fail before replacement. Other reconstruction paths and sequential replacement limits remain as described in [campus expansion](campus-expansion.md#protecting-adopted-environment-layers).

## Rider contact

Generic bicycle and scooter riders now keep their feet on the pedal or deck and their hands at the handlebars across sampled rider heights and widths. Proportions remain stylized and poses static. [Bicycle](images/bicycle-rider-contact.png) · [scooter](images/scooter-rider-contact.png). Vehicle types and placements remain generic. Original procedural geometry is CC BY 4.0, code Apache-2.0; no third-party vehicle geometry was imported.

Validation before integration: production build; 45 JS unit tests including suppression and rider contacts; six affected Chrome/SwiftShader browser tests; six rebuild-preservation tests; and an isolated Blender rebuild passed. Blender comparison found only the earlier moved tree/understory and tree 273 vertices changed in the isolated candidate; building geometry was not rewritten. These are not performance, accessibility or field-survey certifications.

**Post-integration verification:** Following reconnection, candidate and project hashes were checked before the one-time integration. The production build, all 45 JavaScript tests, six affected browser tests, six rebuild-preservation tests, 28 open-asset records, reference-media audit, campus expansion, ground, viewer overrides and portable inventory checks passed. A read-only Blender mesh audit matched the recorded report. Browser runs used the workspace copy after 14 relevant runtime/asset/test hashes were matched to the project.


**Later tree-count update:** A second individually source-pinned suppression applies to tree 216 after dated aerial review. Source count remains 600; visible count is now 598. See [tree 216 evidence](emu-tree-216.md).
