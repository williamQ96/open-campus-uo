# Local iteration 13: environment, motion and recovery

> Published in Open Campus: UO 0.12.0. Local preparation/measurement notes below retain their original context; see the development log for deployment confirmation.


**English** | [简体中文](zh-CN/phase13-environment-comfort.md)

This local batch extends [iteration 12](phase12-npc-beta.md). It was first published with 0.12.0; the local verification records retain their original pre-publication state.

## Explorer behavior

- A blue gradient sky and 18 clusters of original rounded block clouds replace the pale background. Clouds use one merged mesh, no image downloads or cloud shadows; system reduced motion stops their drift.
- Settings has **First-person motion: No / Low / Mid / High**, default **Low**. Peak vertical/lateral offsets are 0/0, 3/1, 6/2 and 10.5/3.5 mm. There is no roll. This changes only first-person visual offsets; movement, footstep contacts and model gait keep the same actual-distance phase. System reduced motion overrides every level to zero sway.
- Walking students first yield on collision. After roughly 0.5–0.74 s they try a short side-step, parallel bypass and return to their original fixed path. Every segment must stay inside the inset authored pedestrian paving and clear buildings and current collision bodies. Only one actor may request a plan per frame; unsuccessful requests retry after 1.1 s. Narrow or blocked paving can still queue actors safely. There is no fallback through vehicle lanes or planted areas. Other actor classes retain their fixed habitat paths and collision yielding.
- Zombie contact now ends the round. Height-aware contact fires once and pauses the scene. A **30% black scene shade** sits below labels and interface controls; a centered **You are dead** window requires **Restart**. Restart reloads the page, restoring the original T-junction spawn facing EMU, Overview, Mid activity, Low motion, default sound, beta off and developer mode off. Escape cannot dismiss the death window. Exiting beta normally still restores the prior density.
- Three camera modes, search, directions, minimap, density controls, feedback, desktop controls and mobile move/look/run remain available.

## Ground coverage and reference evidence

The new reference is a **2024-06-08 USDA NAIP aerial orthophoto**, exported across the full 2 × 2 km scene. It is not a live satellite map. The two source tiles, exact EPSG:3740 extent, export parameters and unchanged PNG hash are in [the source record](../data/metadata/naip-2024-main-campus-reference.json). The image is in [the reference archive](../data/reference-images/aerial/naip-2024-main-campus-rgb.png), with its own public-domain status and credit in the [manifest](../data/reference-images/manifest.json) and [attribution](../data/reference-images/ATTRIBUTION.md). The user-provided Google screenshots only identify the requested area; they are not traced, imported or redistributed as open assets.

Smooth broad aerial color cues, then choose a small original palette of campus grass, context planting, warm campus concrete, cooler urban concrete, asphalt and a broad water cue. Infer building aprons and background paved parcels. These are illustrative materials, not an exact surface, ownership, vegetation, parking or access survey. The visible roads and authored detail paving retain their existing geography; the new layer fills the previous blank base beneath them. Existing trees retain their earlier placements. No photographic pixels or image textures are embedded in the GLB.

`assets/landcover/eugene-ground.blend` is the separate editable ground source. `public/scene/landcover.glb` adds **9,630,380 bytes**, one mesh, 160,801 vertices and 320,000 triangles. It follows the existing 401 × 401 heightfield with a 0.018 m presentation offset. The old terrain is retained for checks/physics but is not drawn twice; this avoids coplanar flicker. Roads and authored paving draw above the foundation. Original world-space procedural grain supplies a matte surface in both PBR and toon modes; exported assets retain vertex colors and roughness without a custom shader dependency.

The 534 building identities, source coordinates, historical heightfield and previous editable campus/roof assets remain intact. New surface inference is independent of the roof work and does not relabel the 2008 geographic source as current.

## Regenerate and verify

Using the sibling upstream environment and Blender 4.5 LTS:

```powershell
../open-geospatial-to-3d-reconstruction-pipeline/.venv/Scripts/python.exe scripts/prepare-landcover.py
../open-geospatial-to-3d-reconstruction-pipeline/.tools/blender-4.5.15-windows-x64/blender.exe -b --python scripts/build-landcover.py
../open-geospatial-to-3d-reconstruction-pipeline/.venv/Scripts/python.exe scripts/check-landcover.py
```

Regeneration also updates `presentation.json`; review and update the asset-source checksum register after changing asset bytes. Regenerate semantic activity with `scripts/prepare-semantic-activity.py` when authored paving changes. The optional `pedestrian_regions` polygon/multipolygon is an eroded, obstacle-excluded area for local bypasses, not a new navigation graph.

See [structured verification](../data/metadata/phase13-verification.json), the [development log](../DEVELOPMENT_LOG.md) and review outputs: [ground](images/phase13-ground.png), [sky](images/phase13-sky.png), [death](images/phase13-death.png). Generic runtime and transferable methods are maintained upstream; this scene, source archive and project log stay downstream. No device FPS benchmark is claimed.
