# Phase 12: gait fixes, inferred roofs, semantic activity and beta experiments

> Published in Open Campus: UO 0.12.0. Local preparation/measurement notes below retain their original context; see the development log for deployment confirmation.


[Later local iteration 13 adds adjustable motion, bounded pedestrian detours, environment coverage and death/restart; this page preserves the phase 12 scope.](phase13-environment-comfort.md)

**English** | [简体中文](zh-CN/phase12-npc-beta.md)

Local development batch, not yet pushed or deployed. Existing three views, search, labels, minimap, jump, fixed-origin directions and touch controls are retained. Feedback drafts now identify iteration 12; package release versions remain unchanged until publication.

## Bug fixes

Footsteps previously used a 0.72 m spacing while the rig ran on an unrelated clock. The hero's actual displacement now advances one shared gait phase for animation and sound. Walking/running speeds are 1.7/4.6 m/s with 0.95/1.5 m footfall spacing: ordinary walking is approximately 1.8 contacts per second. Blocking, idling, jumping and Overview remain silent. First-person camera motion is reduced to at most **3 mm vertically and 1 mm laterally, with no roll**. Settings and system reduced-motion preferences still suppress sway.

On phones, hold **Run** with another finger while moving the lower-half joystick. Releasing it returns to walking; losing focus, opening a dialog or changing view clears the held state. This also makes escaping beta zombies possible on touch devices.

## Roof development

All 534 source identities have an explicit roof treatment. Small/compact masses may receive inferred gables and weathered-metal, tile or slate colors. Larger buildings use flat parapets, surface seams and restrained skylight/service blocks. Protected landmark geometry retains its authored silhouette while its roof material and simple rooftop grammar are treated. Background roofs have a smaller detail budget than campus buildings.

These choices are **architectural inference**, not new reference photographs or a roof survey. Historical footprint/height records stay unchanged. New editable source: `assets/roof-refinement/eugene-campus.blend`; the prior campus and pilot Blender files are preserved. Runtime: `public/scene/campus-expanded.glb`, about 34.6 MB, 93 semantic meshes with export-only batching. The previous runtime was about 25.4 MB: richer roofs increase download/geometry cost. Source identities, no-photo-texture status and exact binary hashes remain audited. Export writes a temporary GLB and replaces the served file after success.

## Fixed positions and semantic paths

`prepare-semantic-activity.py` compiles **70 fixed routes**: 14 pedestrian, 8 driving, 40 grass and 8 tree-climb routes, plus **20 reserved curbside prop slots**. Ordinary actors never use a different surface class as a fallback. Pedestrian routes follow actual authored paving; cars use selected Kincaid/Agate/E 18th source-road segments; squirrels use the grass polygons and existing authored trees. Planting, driving classification, curb slots and access remain illustrative, not current observations or parking permissions.

Activity format 2 stores sampled world heights and fixed bends. `activity-zones.geojson` and `check-semantic-activity.py` validate the committed masks/routes/slots. Navigation stays a separate version-1 graph. `prepare-explorer-life.py` rebuilds navigation then calls the semantic compiler, preserving the separation.

Density constructs only the needed instances. Mid normally allocates 29; High targets 74; No destroys every ordinary actor/prop and collision body. No hidden High pool remains. Base source assets are shared once. Retained IDs keep their appearance; recreated IDs replay the same properties from the map seed. This removes per-frame ordinary-NPC building/terrain scans; frame performance still depends on the larger model and device.

## Template variation and developer mode

Students sample m/f avatar presentation, truncated normal height 1.4–2 m, continuous skin color, six procedural hairstyles, hair/clothing/bag colors, five bag styles, speed and walk/run state. Vehicle templates sample car/SUV/van/pickup, color, scale and speed; riders also vary. Squirrels sample size, fur, speed and pauses. Traits describe fictional avatars, not real students. Original procedural additions use the existing project license; the Kenney base and squirrel source keep their own CC0 terms.

Enable **Settings → About → Developer mode**, close the dialog, then click an unobstructed NPC. The panel shows template/version, seed, all sampled properties, path/slot, state and position, and can copy the record. Disabling developer mode or removing the inspected entity closes it. The entry is reserved for later tools. Beta monsters can be inspected too.

## ZOMBIE SCHOOL!!! beta

Open **Settings → Beta functions**, a first-level tab beside Settings and About. The experiment is off by default. Turning it on remembers ordinary density and switches to No. It spawns up to 28 uniform original chibi stitched monsters on clear terrain within 160 m, never on roofs, sharing one geometry/material.

They wander at **0.45 m/s** within **12 m** of their center. A hero within **30 m** attracts pursuit at **2.2 m/s**; beyond **60 m** the zombie stops chasing and uses its current position as a new wander center. The chase speed is above walking and below running. Buildings and actor collisions remain; obstructed pursuit can use the outdoor graph with throttled replanning. No combat, damage or score is implemented. Dialogs pause simulation. Disabling the beta disposes its actors and restores the prior density.

The [upstream semantic activity method](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/semantic-activity.md), [beta lifecycle](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/beta-functions.md) and [Zombie School template](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/beta/zombie-school.md) are maintained separately. Their current local revisions become public only in a later publication batch. Project progress and test results belong in this repository's development log.

The delivered rig was sampled at 65 animation phases: minimum foot heights occurred at cycles 0.171875/0.640625. Its configured contact offset is 0.15625 cycles, a first-pass pose calibration retained in `data/metadata/gait-calibration.json`. This aligns the shared contact phase with the rig rather than only slowing the sound.
