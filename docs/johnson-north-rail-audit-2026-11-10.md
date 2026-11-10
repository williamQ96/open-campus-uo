# Johnson Hall north stair rail audit, 2026-11-10

Read-only geometry/source audit. No geometry, placement, collision, navigation, asset level or source GLB changed.

## Corrected premise

The north stair approach already has two rail assemblies. `scripts/build-visual-pilot.py` calls `approach_steps` for Johnson; that helper generates three upright posts and a sloping top rail on **each** side. Reading only the Johnson call site incorrectly suggests the model has stairs and lamps but no rails. Do not add another two assemblies on that premise.

The actual `campus-expanded.glb` Johnson group (`roof-906c030e`) confirms both existing assemblies in its `metal` mesh. World-space post centerlines are x = -415 and -387 m, at z = 16, 20 and 23.2 m. Their bases are y approximately 4.030, 4.256 and 4.437 m respectively, and each post rises 1 m. The top rail climbs approximately 0.407 m over 7.2 m. Each side contributes 96 indexed position entries / 32 unique corner positions to this local bound. These are source-model coordinates, not measurements of the real site.

## Photo comparison and decision

The archived `data/reference-images/photos/johnson-hall/front-pd.jpg` (`johnson-front-pd`, Adam850, PD-self, provenance retained in the reference manifest) clearly shows two narrow interior stair rails with sloping handrails and intermediate uprights. Their spacing relative to the entrance/columns and the photographed stair profile differ from the simplified source approach. The image is a historical perspective view, not a surveyed plan/elevation; it does not establish exact centerlines, slope, stair dimensions or present-day conditions.

An additive pair would leave the existing outer pair in place, creating four assemblies and suggesting a layout not supported by the photograph. Moving or suppressing the existing merged metal triangles would need exact source signatures and a jointly reviewed stair/landing interpretation. The current task should not turn a small rail embellishment into an unverified step reconstruction. Therefore **no rail layer is added** in this pass.

## Safe next step

Obtain or reconcile a usable north stair/landing plan or additional openly reusable, adequately scaled views. Then review the complete stair/landing proportions, two rail centerlines, endpoints and pillar clearances together. If a source-safe triangle filter is used, isolate the existing rail faces only and preserve lights and unrelated metal work. Any modeled rails remain visual interpretation unless navigation/collision and accessibility are independently assessed. No claim of walkability, code compliance or accessibility follows from this audit.

Verification used the preserved local GLB decoded with the installed Three.js GLTFLoader and transformed into world coordinates, plus direct inspection of the archived photograph and generator. No dependencies were installed and no browser screenshot is presented as new visual acceptance.
