# Carson grouped-window transom candidate, 2026-11-10

Status: reference and generated-geometry checked candidate; not implemented. This bounded pass inspected Carson and read Allen's existing source limitations. It did not expand to uncertain Allen wing/entry reconstruction.

## Reference and rights

[UO 2006 Carson Cultural Resource Survey](https://scholarsbank.uoregon.edu/bitstreams/87a6f7fd-12a7-43af-a9b7-f30907a2d778/download), page 4, was downloaded outside the repository, rendered with the installed PDF renderer and visually inspected. Reviewed PDF SHA-256: `7980ddf56bde177cecdb79ed3b319c598551069d812621f650e80842346f1f3c`. It shows the brick building's east-frontage grouped metal windows, with horizontal as well as vertical pane divisions; its site plan and established Carson documentation support the east elevation. No CC/open photo license was established: **link-only reference**, no archived PDF/image, no texture, no assumed permission from public accessibility. The historic photo does not establish current window replacements or measured profiles.

## Actual missing geometry

Current `apps/web-preview/public/scene/carson-exterior-detail.json` has 387 explicit objects. Every grouped window includes three vertical metal dividers; the entire specification contains zero metal components with y thickness below 0.2 m. For the existing east span, backing object 102 is centered at (-49.88,9.5,42.5), size (0.8,18.3,21). Object 105 is the first east glazing at (-49.37,2.5,34.625), size (0.05,1.5,2.08); objects 106-108 are its vertical bars at x=-49.33, y size 1.5 and z thickness 0.045. The repeated columns are z=34.625,39.875,45.125,50.375. Existing window-row centers are y=2.5,5.8,9.15,12.5,15.85.

This was checked beyond object labels: the current `createExteriorDetail` generated one merged mesh. Rays from x=-45 toward -x at z=34.9 and y=15.2,15.5,15.8 all intersected the plain east glass at x=-49.345001220703125. No implicit helper horizontal bar occupies those points. This confirms an actual omission in the current overlay, not a claim based on an outdated source or a fresh measurement of the original campus GLB.

## Limited proposed change

Add a restrained horizontal metal subdivision to the existing four east column groups, initially the upper four rows only (y=5.8,9.15,12.5,15.85), leaving the lowest/entry-adjacent row unchanged. Use the current window coordinates and width; do not infer a new full facade count, recreate stair towers or move the model to fit the historical photo. A centered divider is an explicit schematic interpretation of visible casement subdivision, not a claim of exact pane ratio or operating mechanism. No extra upper/lower bars are justified without inspecting a clearer source. Preserve all 387 objects and all glass apertures apart from the deliberate thin divider crossing; the added strips must meet, not float in front of, existing vertical bars and remain within each framed opening.

The same merged mesh makes zero added draw calls feasible, not yet measured. Required acceptance: exact source snapshot; old object equality; strip/window and vertical-bar contact; actual rays showing the new divider while the remaining glass stays exposed; source-pin and identity preservation; front/oblique camera-asserted images with vegetation untouched; entrance/collision equivalence; unique standalone export and real stdout/roundtrip evidence. At street distance the gain may be modest; reject excessive dark grille density rather than claiming stronger detail. No runtime, tests, global metadata or source registration was changed by this candidate pass.
