**English** | [简体中文](zh-CN/verification.md)

# Verification records

Later milestones: [v0.2 main campus](v0.2-main-campus.md), [v0.3 roads](v0.3-roads-controls.md), [v0.4 search](v0.4-building-search.md), and [reusable template](viewer-template.md).

## Original v0.1 loop

The 2026-10-30 Memorial Quad baseline used one verified NOAA/DOGAMI tile with 11,436,019 source points. Cropping yielded 1,016,116 points, including 216,517 ground points. A 2021 DEM catalog hit was rejected after all 129,600 AOI samples proved NoData. The [source audit](../data/metadata/source-audit.json) records actual CRS, coverage and hashes.

A real Blender 4.5.15 LTS background process generated the editable scene and GLB. The terrain had 181 × 181 vertices at 2 m spacing, 73.38% occupied ground cells and 732 nearest-filled edge vertices. A 2,161-cell internal holdout had 0.107 m RMSE and 0.165 m P95 absolute error. These are interpolation consistency measures, not independent absolute survey accuracy. The scene contained 27 heuristic building candidates with unresolved canopy, identity and courtyard limitations.

The initial checks comprised five upstream geometry/source tests, four movement/coordinate tests, two browser integration tests and a production build. GLB header/length, required nodes and schema-v1 manifest validation passed.

## Runtime checks

Browser tests use real GLB assets and software WebGL; their timings are not hardware performance claims. They check actual mesh-vs-heightfield ray heights, movement, collision, jump, views, search, settings and narrow layouts. External HTTP requests are blocked. Fonts are pinned through Fontsource and their OFL notices are bundled.

CI uses Ubuntu 24.04 for Playwright compatibility. Local previews produce diagnostic screenshots; CI saves screenshots/traces on failure. Tests do not deploy the website. Anonymous production access is checked separately during publication.

Independent control points, precise current building identities, cross-engine import, full facade reconstruction, touch movement, streaming and independent performance benchmarks remain unverified.
