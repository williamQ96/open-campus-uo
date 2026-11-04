# Environmental asset triage · 2026-11-03

Local and unpublished. These are partial improvements and checks, not a new level definition. All 13 existing entries remain at the user-assigned level 1.

| ID | Work and next action |
| --- | --- |
| ENV-01 | [Screened](vegetation-clearance-audit.md): seven candidate tree/footprint proximity cases. Knight steps show vegetation overlapping the illustrative approach. Isolate and review tree/understory geometry against the authored landmark before adjusting it. |
| ENV-02 | Screened 300 generated input trees; no candidate overlap using the conservative test. Regional species and actual locations remain unverified. |
| ENV-03 | [Knight close view](images/knight-landscape-review.png) shows shrubs and tree forms across the steps; [EMU view](images/emu-landscape-review.png) shows generic planting beside paving. These are inferred forms, not surveyed plantings. |
| ENV-04 | Existing ground layer reference restored and ground checker passed; see [batch evidence](environment-batch-2026-11-03.md). Land-cover classification and elevation remain historical/inferred. |
| ENV-05 | Ground layer and two landscape views checked. Widths, path connections, real surface boundaries and accessibility remain unverified. |
| ENV-06 | Knight close view exposes an apparent obstruction at the decorative stair. Dimensions, collision and actual construction remain unverified. |
| ENV-07 | Cloud clusters refined with [before/after evidence](sky-refinement.md); no current-weather claim. Campus/seasonal review remains. |
| PROP-01 | [Bench view](images/bench-context-review.png) shows a nearby tree trunk obscuring part of the bench; verify their clearance from another angle and correct position or placement where warranted. Locations and styles are illustrative. |
| PROP-02 | Vehicle hubs and pickup bed refined; style, dimensions and positions remain generic. |
| PROP-03 | Bicycle and scooter refined and bicycle reviewed on a campus path; rider pose still needs work. |
| PROP-04 | Browser reports 534 inferred and zero authored entries. The algorithm marks all 534 candidate approach checks clear against its historical collision model, **not** verified entrances, actual clear paths or accessibility. |
| INT-SHARED | [Overview](images/shared-interior-review.png) shows the common generic classroom kit. It is not a real Knight or other building interior; 534 individual interior placeholders remain uncreated. |
| LIFE-01 | Default mid-density browser state reported 8 walking students and 8 squirrels. Models, movement and species remain generic and are not a population survey. |

The pilot's trees, planting, furniture and landmark geometry are exported together. A full procedural rebuild could overwrite existing hand-refined landmark work; isolate and validate changes to those semantic meshes before replacing the combined export. The reference photographs and their usage terms remain separate; no new third-party visual asset was copied.

The prop GLB and its new editable candidate now have updated size, SHA-256 and license entries in `data/asset-sources/manifest.json`. The full asset checker still reports pre-existing mismatches for `campus-expanded.glb` and `assets/roof-refinement/eugene-campus.blend`, both already modified by the separate landmark work before this environment pass. Those building records were not rewritten. Resolve their provenance with that work before release.

**Follow-up:** The obstructing inferred tree and its paired shrub were subsequently moved using isolated source-pinned runtime patches; the original building files remain unchanged. See [correction and remaining gaps](knight-vegetation-correction.md). Other findings in this triage remain open.

**Provenance follow-up:** The two prior landmark source-record mismatches were reconciled against documented build metadata and a targeted mesh comparison; the complete asset-source check now passes. See [evidence](landmark-provenance-2026-11-03.md).

**Final verification:** The full 32-test browser suite subsequently passed in the workspace copy with local Chrome/SwiftShader; the 43 JS unit tests, five rebuild-preservation tests, open-asset, ground, expansion, override and portable inventory checks passed. These tests do not establish real-world survey accuracy.

**3D follow-up:** Of seven screened pilot trees, three have surface intersections with the authored Knight or EMU building meshes; four showed none in this limited test. The edited tree 60 candidate no longer intersects the Knight mesh. The three unresolved positions require source and placement review; see [mesh audit](vegetation-clearance-audit.md#read-only-3d-follow-up).

**Latest batch:** Source review and the local 273 tree suppression, plus generic rider-contact adjustment, are recorded in [environment refinement](environment-refinement-2026-11-03.md). Two Knight tree intersections remain unresolved and levels are unchanged.
