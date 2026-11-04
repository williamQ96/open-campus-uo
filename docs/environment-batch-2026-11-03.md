# Environment batch · 2026-11-03

Local, unpublished; the existing level 1 classifications remain unchanged.

- **PROP-02:** Added wheel hubs and a readable pickup bed to the generic original vehicles. The forms and placement remain illustrative, not a vehicle survey.
- **PROP-03:** Added scooter deck grip, fenders and a lamp after the earlier bicycle work. A [campus-context review](images/bicycle-campus-review.png) confirms the bicycle renders on a path; the rider connection and proportions need further work. The [five-prop neutral review](images/prop-batch-review.png) includes the entire export collection. Updated GLB and an editable Blender candidate were regenerated; the original Blender file remains preserved.
- **ENV-04:** Restored the existing `landcover.glb` reference and its SHA-256 in `presentation.json` after the scene configuration had omitted it. The browser reported `landcover: true`, 534 building records and 600 tree instances with no page errors. [Overview](images/ground-campus-review.png). This restores an existing inferred 2024-NAIP-guided layer, not a current survey. The expansion builder can overwrite presentation metadata again; check the reference after future rebuilds.

The unmodified `viewer-template.lock.json` remains the upstream baseline. `viewer-overrides.json` records the downstream props source and exported output hashes separately; `python scripts/check-viewer-overrides.py` from the web-preview directory verifies both against that baseline. Reconcile the local override when upgrading the shared viewer.

Validation: web production build, 42 unit tests, finite geometry coordinates, local Chrome/SwiftShader visual review, and override hash check passed. Visual checks are not device performance claims. Other inventory work remains open.

Context only, no images or geometry copied: [UO bike parking](https://transportation.uoregon.edu/bike); [UO campus tree tour](https://cpfm.uoregon.edu/sites/default/files/tree_tour_oct_2021.pdf); [OSU native plants west of the Cascades](https://extension.oregonstate.edu/catalog/pub/ec-1577-gardening-oregon-native-plants-west-cascades). Their contents remain subject to the owners' terms. UO's tree tour establishes some species on campus, not the species or position of every procedural tree. Original geometry remains CC BY 4.0.

**Rebuild follow-up:** The campus art builder now preserves validated ground/patch references and stops before replacement when a patch is incompatible. See [rebuild protection](campus-expansion.md#protecting-adopted-environment-layers).
