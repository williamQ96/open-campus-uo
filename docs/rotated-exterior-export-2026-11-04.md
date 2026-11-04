# Runtime facade overlay exports — 2026-11-04

The reusable `apps/web-preview/scripts/export-exterior-detail.mjs` exports a source-pinned, box-only, non-replacing building overlay using the same `createExteriorDetail` geometry construction and XYZ rotation order as the runtime. Rotations are baked into vertex data. It checks the input JSON hash, current presentation pin and original `campus-expanded.glb` hash before export and checks that inputs remain unchanged before writing. It refuses to overwrite an existing output. No external image or geometry is added. Source code is Apache-2.0; original GLBs are CC BY 4.0.

From `apps/web-preview`, start the local Vite server with `npm run dev` and, in another terminal, run `node scripts/export-exterior-detail.mjs rec-east-detail.json ../../assets/exterior-refinement/<new-name>.glb`. The output must not already exist. The exporter is intentionally restricted to pinned building box overlays; it does not export plants, labels, whole buildings or collision metadata. It creates a single mesh in the original scene coordinate frame. Do not load it together with the runtime overlay or treat it as a complete standalone building. The single merged mesh is editable as mesh data, while the source JSON remains the separately editable per-box source. It is not a per-object Blender snapshot.

| Overlay | Standalone GLB | Source vertices checked |
| --- | --- | ---: |
| Student Recreation Center east | [GLB](../assets/exterior-refinement/rec-east-detail-2026-11-04.glb) | 936 |
| Jaqua | [GLB](../assets/exterior-refinement/jaqua-exterior-detail-2026-11-04.glb) | 3,672 |
| Knight Campus 2 east | [GLB](../assets/exterior-refinement/knight-campus2-east-detail-2026-11-04.glb) | 1,764 |
| Lillis south | [GLB](../assets/exterior-refinement/lillis-south-detail-2026-11-04.glb) | 1,404 |

Each export was reopened from disk independently and compared with the corresponding runtime-generated positions, normals, colors, source hash, building identity and world transform. All maximum vertex-attribute differences were zero; the transforms were identity. A synthetic combined X/Y/Z rotation test matched an independently computed corner within 1e-5 m. The Student Recreation runtime and reopened GLB had zero differing pixels under the identical local renderer and camera; [side-by-side image](images/rec-export-comparison-2026-11-04.png). This is an isolated overlay comparison, not an in-campus survey or a full-building render. The exporter itself verifies the binary in memory before writing, checks for changed inputs and uses exclusive file creation; an existing-output rejection was verified.

Blender was not found and no software was installed. Consequently none of these four GLBs has a new per-object `.blend` snapshot, and the older unrotated Blender exporter has not been changed or validated for rotation. Previous GLBs and snapshots remain untouched. The runtime geometry and asset levels are unchanged. All artifacts are local and unpublished.

**Additional exterior:** The [Knight Campus 1 partial south GLB](../assets/exterior-refinement/knight-campus1-south-detail-2026-11-04.glb) was exported with the same process and its 2,808 vertices, normals, colors, identity transform and source hash were independently verified from disk. It is an overlay only; see [the site record](knight-campus1-south-2026-11-04.md).
