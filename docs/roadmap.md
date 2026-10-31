**English** | [简体中文](zh-CN/roadmap.md)

# Roadmap and acceptance

## Completed foundations

- Verified public-source coverage, CRS and checksums for the original 360 × 360 m Memorial Quad loop.
- Rejected a catalog-matched 2021 DEM after all AOI samples proved NoData.
- Built ground terrain, independent building placeholders, Blender source scenes, GLB, metadata and schema-v1 manifests.
- Expanded to a 2 × 2 km main-campus context, with named anchors and explicit approximate envelopes.
- Added basic terrain-draped roads, jumping, three views, wheel zoom, search, billboard labels, minimap and settings.
- Published a public, no-login browser site and separated reusable viewer behavior into an upstream template.

## Model refinement

- Verify building identities, footprints and heights; remove canopy false positives.
- Refine one representative building using appropriate photos or additional measurements.
- Improve roofs, facades, materials, pedestrian paths, curbs, steps and collision proxies.
- Validate absolute positioning with independent survey control points.
- Validate axes, scale, materials and normals in another engine.

## Scaling

- Add LOD, compression, tiles and on-demand loading when measurements justify them.
- Evaluate more recent and geographically independent source datasets.
- Keep Apache-2.0 software, CC BY 4.0 original content and third-party notices clearly separated as the project grows.
- Maintain deployment and template pins with reproducible upgrade checks.

Acceptance means the same verified configuration can generate usable assets, with provenance and estimation status visible. No unmeasured accuracy or frame-rate guarantees are implied.
