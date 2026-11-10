# Follow-up exterior candidate audit B: Friendly Hall

2026-11-10. Read-only planning; **not implemented or accepted**. This independent document does not replace the Susan batch plan or Johnson rail audit. No runtime, source specification, global log, inventory or asset level changed.

## Recommended single bounded candidate: four outer porch column shafts

Source inspected: `data/reference-images/photos/friendly-hall/west-2017.jpg`, reference `friendly-west-2017`, Daderot, captured 2017-11-03, CC0 1.0, approved in the existing reference manifest. The photograph clearly shows rounded freestanding shafts under the two west entry porches. It does not justify claiming exact fluting, orders, measured radii or current conditions. The photo was viewed through an ephemeral reduced-size inspection copy; the original image bytes remain untouched.

The active `friendly-west-detail.json` (building `roof-556799cc`, `replace_building:true`) already has both entry porches and their inner/outer supports. It currently contains **no column primitive**: all eight support shafts are boxes. The four outer supports are objects **10, 11, 23, 24**, all `stone` boxes with size `[0.35,3.3,0.35]`, y center **4.752 m**, x center **-365.6 m**, and z centers **-31.65, -28.35, -55.65, -52.35 m**. Inner objects 206, 207, 210, 211 are closer to the wall and should remain unchanged rather than assuming they are also round.

Read-only actual geometry verification used the installed `createExteriorDetail` with the current source, not just names. Full output is one building mesh with 21,828 nonindexed position vertices plus one vegetation mesh with 3,600. Each isolated outer support emits 36 position vertices, with x bounds approximately -365.775 to -365.425 and y bounds 3.102 to 6.402; their z bounds are the corresponding center +/-0.175. Current source bytes SHA-256: `d8b439add6401343e891aa641fd4d12ae4aebe9a53bbc9cc99667f1bdcebdaba`.

### Minimal future implementation

Preserve a new immutable copy of the exact current specification, then change only those four outer shafts from `box` to the existing octagonal `column` primitive, retaining center, size, material and porch contacts. The existing primitive is a scaled eight-sided cylinder with the same axis-aligned bounds, so no new placement or footprint is required. It would add approximately 80 triangles total, but **zero draw calls**, as the existing building mesh remains merged. Do not add a separate overlay, new material, capitals, speculative fluting or landscaping for this small pass.

The change is modest but truthful: round-column readability in near/oblique views, not a new building reconstruction. If visual comparison shows the eight-sided approximation is not appreciably better at normal viewing distance, keep the baseline rather than padding the batch. Preserve all other 486 objects, entrances, collision boxes, roof study exclusions and vegetation. The current unresolved Friendly roof study must not be reactivated by this work.

### Required acceptance

- Source-snapshot hash and object-level equality proving only four shape fields changed.
- Same building/vegetation mesh counts and exact unchanged vegetation; finite new geometry, unchanged support bounds and porch contacts.
- Actual-coordinate-asserted front/oblique browser comparisons on a frozen preview with no new draw calls, unchanged selection, entrances and collision. Do not accept a fallback default spawn.
- Current exporter/reimport verification if a reusable standalone is produced; retain old snapshots.
- Remain level 1; no claim of structural support, surveyed dimensions, accessibility or contemporary conditions.

## Screened out rather than adding a weak second candidate

Friendly's paired dormer panes, sash bars, paired gable-window mullions, oculi and belt course already exist in the active source; adding them again would duplicate previous work. Its roof-profile candidate was explicitly rejected and is not a small reliable improvement. Anstett has useful facade imagery but the existing record explicitly leaves its west-entry versus south-plane registration unresolved; do not embellish that uncertain mapping further before reconciliation. Susan and Johnson rails were excluded as instructed.
