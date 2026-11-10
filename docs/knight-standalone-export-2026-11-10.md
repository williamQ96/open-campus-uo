# Knight Library additive standalone export, 2026-11-10

The [balcony GLB](../assets/exterior-refinement/knight-library-balconies-2026-11-10.glb) contains only the 21 additive parapet, return, coping and support components described in [the facade refinement record](knight-refinement.md). It is not the complete library: original building, landscape, collision, navigation and Blender scene are excluded. Original source GLB and earlier assets remain untouched. The layer retains campus coordinates and `roof-6684e091`; do not load it on top of a runtime scene that already applies the same layer.

Original simplified geometry remains CC BY 4.0, exporter code Apache-2.0. Existing photo references informed the interpreted forms but are not embedded. Dimensions and current conditions are not survey-verified; no maturity level change is implied.

Output: 30,284 bytes, SHA-256 `79f0eef62f0dab23248eb09f7b3e1bff802dbb9a1de7ae116bee0ddc33acebba`. Its [machine-readable evidence](../assets/exterior-refinement/knight-library-balconies-2026-11-10.glb.evidence.json) records source/generator/base hashes and actual generation time. The sole mesh has 792 vertices (264 triangles); position, normal and color reimport errors are zero. Vertex colors, material color/roughness/metalness/side/opacity, provenance and identity transforms are verified.

## Reproduce without overwriting

From `apps/web-preview`, with the matching local Vite server running:

```sh
node scripts/export-knight-detail.mjs knight-library-balcony-detail.json ../../assets/exterior-refinement/NEW-NAME.glb --base-url http://127.0.0.1:5195/
```

`KNIGHT_EXPORT_BASE_URL` is also supported. Only explicit localhost HTTP ports are accepted. The exporter accepts only the balcony and window-reveal JSON filenames, fixed Knight building identity and additive box/hip geometry. It validates the presentation pin, unchanged base bytes, matching server-served source and base, local-generator versus served-generator attributes, export/import attributes and material, and stable inputs before writing. Existing output or evidence paths are refused; each file uses exclusive creation. If interrupted after the GLB write, preserve and reconcile it instead of retrying the same filename blindly. No publication or runtime wiring occurs.

`tests/knight-export.test.js` independently reimports the archived balcony file and compares its attributes and material with the local generator; it checks receipt hashes and rejects remote destinations, other input names and existing outputs. Both tests passed. This is asset-reuse verification, not an additional campus screenshot, browser performance test or architectural survey. Existing visual evidence remains in the facade refinement record. Window-reveal support does not itself claim that a window asset was exported.

## Final exporter and window-reveal verification

After the exporter was finalized and formatted, its exact UTF-8 SHA-256 is `f28c7479fa6198dfde3356c5e1c1e9f316005ab20b9f33644e0b96365d44d827`. A second export to a new temporary destination reproduced the archived balcony GLB byte-for-byte; its separate [final-exporter verification receipt](../assets/exterior-refinement/knight-library-balconies-2026-11-10.final-exporter-verification.json) preserves the true later time and final exporter hash; the private temporary output path is replaced with the canonical archived path and explicitly labeled as a same-hash verification artifact without rewriting the initial receipt.

The frozen window-reveal layer (source SHA-256 `aa58ed85991c5db92b921ede21bec4d9c1959b782e5acc815cf57a2302417dbf`) now also has a [standalone GLB](../assets/exterior-refinement/knight-library-window-reveals-2026-11-10.glb) and [evidence receipt](../assets/exterior-refinement/knight-library-window-reveals-2026-11-10.glb.evidence.json). Output SHA-256 is `4e33f4a00c348f22d8f2b4b6d3d3907b09552b97ca7684266fe05aa2c8afe23c`, 56,216 bytes, one mesh, 1,512 vertices (504 triangles). Position, normal and color roundtrip errors are zero; material and source identity checks passed. It contains only the additive reveal pieces, not original windows or the complete building. Source visual acceptance is recorded separately by the window-refinement work.

The final dedicated Node suite has three passing tests: two independent asset/local-generator equality tests plus CLI rejection cases. No shared presentation, manifest or development log was edited by this export task.
