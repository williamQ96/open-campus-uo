# Friendly Hall: four round outer porch shafts (2026-11-10)

Local refinement only; level remains 1. Not committed, pushed or deployed by this task.

## Source and bounded interpretation

Archived `data/reference-images/photos/friendly-hall/west-2017.jpg` (reference `friendly-west-2017`, Daderot, 2017-11-03, CC0-1.0) shows plain round outer shafts on the two west porches. This is an original eight-sided stylization, not a measured reconstruction or copied mesh. No ornamental order, fluting, extra capitals, entrance claim or accessibility claim is added.

Only object indices **10, 11, 23, 24** in `friendly-west-detail.json` change `shape: box` to `shape: column`. Position, size and stone material remain unchanged. The four inner supports (206, 207, 210, 211) remain boxes. All other 486 objects and all metadata, collision boxes and source records are identical.

## Geometry and checks

- Each changed shaft: 36 to 96 nonindexed vertices; same exact bounds. Radius 0.175 m, height 3.3 m, original centers retained.
- Building: 21,828 to 22,068 vertices (+80 triangles); vegetation: 3,600 unchanged. Same two material-bucket meshes, zero extra draws.
- Dedicated object comparison verifies every unchanged object's position, normal and color arrays exactly; four changed shafts have circular cross sections and equal bounds. Existing Friendly collision/navigation test passes.
- Browser comparison routes the immutable before source and its correct pin, versus current source. Two porch front views and a corrected oblique view use actual first-person world positions. Camera, draw count, collision observations, entrances and building selection are exact before/after. No page errors.
- Screenshots: `docs/images/friendly-round-shafts-{west-porch,south-porch,oblique-porch}-{before,after}-2026-11-10.png`.

## Immutable artifacts

- Before JSON: `assets/exterior-refinement/friendly-before-round-shafts-2026-11-10.json`
  SHA256 `d8b439add6401343e891aa641fd4d12ae4aebe9a53bbc9cc99667f1bdcebdaba`
- Current JSON SHA256 `967cb118e6ae7fe3df80ed3b250f91e84798224a531c4f0a5ea360586dee3931`
- New independent **building-only** GLB: `assets/exterior-refinement/friendly-round-shafts-2026-11-10.glb`, 796,100 bytes.
  SHA256 `cc96fee2b2bf1564a3deb81335557cb1a3e9e9d87bc955fc5f862e1ea2f4311a`
- Base GLB SHA256 `29f22c38eb5737fba2c8b3ab9618e049443c052e169e175f19428e66174ae896`
- Runtime generator SHA256 `c0181be4a2256830571390bfb8497335d368e9d4e3aed9b9da625b5044fa1e40`

`export-friendly-round-shafts.mjs` requires source/config/base pins, refuses overwrite and checks source stability. It removes only vegetation from the standalone export, not from the campus scene. Reimport returns exactly one building mesh with original identity, transform, material color, and all 22,068 position/normal/color values with **zero numerical error**. Old artifacts remain untouched.

## Scope limits

This does not resolve preexisting terrain/porch-floor intersection, overall facade proportion or concealed support ambiguity. No speculative additional geometry was added to compensate for these limitations. Global presentation pin and logs are integrated separately by the coordinating worker.
