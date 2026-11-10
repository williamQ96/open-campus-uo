# Same-building overlay batching, 2026-11-10

The new source-pinned Knight, Gerlinger and Johnson details increased the fixed campus draw count to 182, failing the existing strict `<180` budget. The threshold is unchanged.

`src/building-overlay-batches.js` combines exactly three compatible pairs of original additive meshes after installation: Knight balconies/window reveals; Gerlinger east/masonry; Johnson rear/capitals. No base GLB, JSON layer, standalone export, vegetation, collision or building identity is removed or rewritten. The surviving mesh preserves its building selection identity and material. The independent inputs/exports remain editable and verifiable; runtime batching is not a new clean upstream template pin.

Before any scene mutation, each complete pair checks fixed exact source-byte SHA-256, source asset and building identity, parent ownership, static identity transforms, exact material serialization/flags, non-shared geometry/material ownership and every position/normal/color value against newly generated pinned source geometry. All combined buffers are allocated before commit. A failed contract throws while retaining the original scene. A deliberately omitted diagnostic layer skips that pair rather than dropping its counterpart. Historical layer variants with different explicitly configured pins are likewise excluded from the current-recipe batch map, but remain installed and rendered; current configured pins with mismatched raw bytes still throw. Only the donor building mesh is removed; any vegetation siblings remain. Superseded owned buffers and donor materials are disposed once.

Unit acceptance preserves all attributes as exact concatenations and tests corruption, transform/material/ownership mismatch and transactional rejection. Browser comparison reports **182 before, 179 after**, with the same three selected building IDs, identical entrance records and no page errors. The unchanged canopy-tone test passes its strict budget through toon/PBR transitions. No geometry was simplified, hidden at distance or excluded to gain the three calls.

This narrowly pinned UO integration may be generalized upstream separately with appropriate contracts; it is not a broad automatic batcher and intentionally rejects source changes until reviewed. No push or deployment is performed by this step.

## Historical comparison acceptance

The older Gerlinger portico and Johnson rear-window tests initially failed solely because their entire view records required equal draw counts: current optimized Gerlinger views were 63/43/101 versus historical unbatched 64/44/102; Johnson was 56/71 versus 57/72. Camera, collision, entrance and identity checks were unchanged. The tests now retain exact equality for every non-draw view field and require `after draws <= before draws` for each view; the separate exact three-draw reduction and strict global `<180` test remain. No increase is permitted and no dummy draw was added to satisfy historical equality.

New rerun screenshots are isolated outside the repository; any fixed-path historical PNGs produced by the first run were preserved as new validation artifacts and the pre-existing originals restored byte-for-byte from their verified Git versions.

The full-run failure traces also confirmed the Johnson gable/hip and roof comparison failures at only the draw equality assertion: 81/57 historical versus 80/56 current. Their draw assertions receive the same non-increase treatment, retaining the existing blocked-state, entrance, selection and error checks. This is evidence-specific test maintenance, not a blanket change to draw budgets.

The measured benefit is three fewer draw calls at the fixed acceptance view, not a claim of frame-time or mobile-device speedup. Batching broadens each surviving mesh bounding volume; geometry remains intact and the global draw budget and per-view non-increase checks are the verified scope.
