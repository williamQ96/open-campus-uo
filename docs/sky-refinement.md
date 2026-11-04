# Procedural sky refinement · 2026-11-03

Local and unpublished. ENV-07 remains level 1. The existing 18 stylized merged cloud clusters now vary in scale and orientation, with offset lobes and modest height variation. Their deterministic seed, one merged mesh, blue gradient, drift and reduced-motion behavior are retained. This is generic illustrative atmosphere, not observed or real-time Eugene weather. No external image or model was used.

[Before](images/sky-shape-before.png) · [After](images/sky-shape-after.png): standalone browser views at the same camera pose. Review alongside the campus and regional seasonal references remains open. Web production build and 42 unit tests passed; a direct check verified reduced-motion still prevents cloud drift and normal motion moves the cloud mesh. The local sky source hash is recorded separately in `apps/web-preview/viewer-overrides.json`, while the upstream viewer lock remains the original template baseline.
