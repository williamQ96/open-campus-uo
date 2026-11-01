# Shared classroom v1

Original inferred teaching-room kit, not an actual UO floor plan. The same template is used for all building IDs. It contains 15 desks/chairs, teaching desk, green board, windows, ceiling and exit. No photography, Google assets, school logos or third-party textures.

- Runtime editable source: [`classroom.js`](../../apps/web-preview/src/classroom.js), Apache-2.0.
- Portable model: [`classroom-v1.glb`](../../apps/web-preview/public/interiors/classroom-v1.glb), CC BY 4.0, Open Campus contributors. Credit Open Campus: UO / Zhongyi William Qiu and contributors; retain the project/license link and identify changes.
- Export with the local viewer running: from `apps/web-preview`, `node scripts/export-classroom.mjs public/interiors/classroom-v1.glb http://127.0.0.1:5173/`.
- Model copyright and template/accuracy metadata are embedded in GLB. File bytes/SHA-256 are in `data/asset-sources/manifest.json`.

The browser builds this small kit on demand from code; it does not preload this exported GLB into the campus world. Enter/exit reload documents and dispose the previous GPU world, including back-forward cache recovery. See [interaction design](../../docs/interiors-mobile.md).
