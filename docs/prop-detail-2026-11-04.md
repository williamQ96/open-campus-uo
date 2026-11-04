# Generic transport prop details — 2026-11-04

The original procedural vehicle family now has simple front/rear bumpers, side mirrors and window separators; the scooter has wheel hubs, handle grips and a rear reflector. These unbranded forms are generic design interpretations, not a survey of models or placement on campus. [UO Transportation Services](https://transportation.uoregon.edu/bike) is contextual evidence for campus cycling, not a vehicle-design reference. No third-party geometry or imagery was copied. The original generated geometry is CC BY 4.0; procedural code is Apache-2.0.

[Before](images/props-detail-before-2026-11-04.png) / [after](images/props-detail-after-2026-11-04.png) show the procedural models in a neutral test scene. The source and exported GLB were updated together; the prior editable Blender import is retained and does **not** contain these latest details. Placements, routes, colliders, bicycle and rider pose are unchanged. Sizes, vehicle styles and placement remain illustrative; both PROP-02 and PROP-03 remain level 1.

Validation: finite position coordinates for five exported prop types; 57 JavaScript tests; production build; and campus browser navigation and rendering tests. Screenshots are visual checks, not a real-world measurement or an accessibility assessment.

## Editable snapshot follow-up

The new `assets/props/campus-props-2026-11-04.blend` imports the current GLB, while both earlier Blender files remain intact. The procedural `apps/web-preview/src/props.js` remains the source of truth: the Blender file is an editable snapshot, and editing it does not update the runtime automatically. Its scene custom property `campus_props_glb_sha256` records the exact source GLB hash. Reopening the snapshot and comparing all five meshes against a fresh GLB import matched vertex coordinates, polygon counts and object transforms.

For a new snapshot, use `blender -b --python scripts/import-campus-props-versioned.py -- --input <GLB> --output <new .blend path>`; the importer refuses to overwrite an existing output. The earlier import script targets the original path and should not be used to replace preserved assets.
