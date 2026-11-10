# Next exterior refinement batch: Susan Campbell Hall

Date: 2026-11-10. **Planning only: neither candidate is implemented or accepted.** Hold active source/geometry changes until the current full-suite diagnosis and stable retest are complete and the coordinating thread authorizes continuation. Keep the asset at level 1.

## Source and scope

- Archived photo: `data/reference-images/photos/susan-campbell-hall/exterior-2011.jpg`, reference ID `susan-campbell-2011`; Gary Halvorson / Oregon State Archives; CC BY 4.0, https://creativecommons.org/licenses/by/4.0/.
- Source page: https://commons.wikimedia.org/wiki/File:Susan_Campbell_Hall,_University_Of_Oregon,_Eugene_-_DPLA_-_4e7906177b35545a22a8ec321bd92da7.jpg
- Existing historical context: https://cpfm.uoregon.edu/susancampbellhall2025 and `docs/susan-campbell-refinement.md`.
- Active editable replacement: `apps/web-preview/public/scene/susan-roof-detail.json`, building `roof-fd061857`. Its 463 objects currently include the L-shaped body, roof, two parapets and courtyard porch. Preserve all unrelated work.
- Image supports historical visible appearance, not current conditions, surveyed dimensions, exact facade mapping or physical function. No photo textures or new third-party assets are proposed.

## Candidate 1: two small arched parapet details

Priority: first. Status: source-backed, geometrically feasible in a limited read-only screen; **not built**.

The photograph shows a small light-framed arched opening above each tall window in the two brick projections. Existing geometry has no arch/disk form at those positions. Active objects 450 and 451 are the brick parapets, centered at x=-455 and -435, y=16.68, z=167.9 with size [2.2,3.8,1.5]. Objects 178-180 and 198-200 contain their windows; objects 181 and 201 are the stone caps.

Read-only clearance:

- Window frame top: 16.25 + 2.05/2 = **17.275 m**.
- Stone cap bottom: 18.67 - 0.18/2 = **18.58 m**.
- Available vertical band: **1.305 m**. A future approximately 0.65-0.75 m tall motif could fit without shortening the existing window or moving the cap; proposed dimensions are not authorized geometry or measured dimensions.
- Brick face southmost z: 167.9 + 1.5/2 = **168.65 m**.
- Independent actual-GLB triangle intersection confirmed z=168.64999389648438 at both x centers and y=17.5,17.9,18.3. Tested artifact: `assets/exterior-refinement/susan-campbell-courtyard-exterior-2026-11-04.glb`, SHA-256 `8cddd1eb2efeff87feccfbe5c2d1ac3a83b8024cf69cd2afd9a009032060320e`; its mesh nodes have no nonidentity node transforms. This validates model placement only, not real-world registration.

Implementation conditions: preserve source bytes in a new immutable snapshot; add a restrained arch surround, dark inner field and at most a few horizontal marks on the exposed brick face, without inventing operational ventilation or exact relief. Check finite bounds and face direction, existing window/cap clearance, untouched unrelated objects, and actual front/oblique camera positions. Target **zero additional draw calls**, modifying the existing merged building layer rather than adding another runtime layer. Preserve campus base GLB, all collision/navigation, entrance records and the courtyard work. Refresh precise presentation digest and current export-equivalence fixtures as needed; retain historical exports.

## Candidate 2: localized projecting window group and pale spandrel

Priority: second, conditional. Status: photograph-supported architectural feature, **mapping still needs work; not ready to implement**.

The photograph shows localized projecting pale window groups and a shallow spandrel between storeys, unlike uniformly flat glazing. Current long-elevation ordinary glass is uniformly at z=168.3 with size [1.35,2,0.08]; relevant upper-row glass indices are 39,47,55,63,71,79,87,95. The complete specification has no bay-prism forms; the two column forms belong to the separate courtyard porch and are not this feature.

Before editing: establish the least ambiguous window group's position relative to the two existing brick projections in the photograph and the replacement model. Do not infer a full set of bays from repeated spacing, change all windows, or move ground/entry geometry to force a match. If the correspondence cannot be supported, defer. Verify actual glazing/frame depth, existing parapet/cornice contact and a feasible shallow projection while preserving the retained aperture and known body envelope. Use the existing merged layer with a **zero additional draw-call target**. Dimensions, count and placement remain interpretations; hidden faces and current condition are unverified.

## Required acceptance for any later implementation

- Read archived image/license and active spec again before work; compare actual generated geometry, not only helper names.
- Keep exact original bytes, source hashes, stable building identity and all unrelated objects.
- Tests for aperture/clearance, finite geometry, original source pin, unchanged entrances/collisions and draw count.
- Actual-coordinate-asserted front/oblique before/after images with visual inspection; do not accept a fallback default camera as the requested view.
- External Playwright output and an isolated no-HMR preview while concurrent work continues.
- Unique standalone artifact with export/reimport evidence; never overwrite historical snapshots/exports or double-load it over runtime.
- No promotion of asset level, deployment or claim of surveyed/current accuracy from these local improvements.

## Implementation follow-up, 2026-11-10

Candidate 1 now has a local implementation and focused geometry/browser/export checks documented in [Susan refinement](susan-campbell-refinement.md#small-parapet-arch-study-2026-11-10). The earlier candidate description is retained as planning history, not a claim that no implementation exists. Candidate 2 remains deferred; no uncertain projecting-window changes were made. Integration acceptance and publication are separate.
