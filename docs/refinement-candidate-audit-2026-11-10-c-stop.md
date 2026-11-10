# Bounded exterior candidate audit, 2026-11-10 C

Status: **no implementation recommended from this bounded pass**. Read-only review of three existing archived-photo candidates; no runtime, geometry, test, source pin or global log changed. This is not an exhaustive campus audit. Susan, Friendly, Johnson rails and Anstett orientation were excluded.

## University Hall: already-covered recognizable detail

Viewed `data/reference-images/photos/university-hall/exterior-2005.jpg`: Gary Halvorson / Oregon State Archives, CC BY 4.0. Provenance: https://commons.wikimedia.org/wiki/File:Deady_Hall,_University_of_Oregon,_Eugene_-_DPLA_-_1ab3ead15b82b80bb858c0fb7db25bec.jpg . Read the complete refinement follow-ups and inspected actual `university-hall-detail.json` objects rather than relying on role names (this older specification has no role field).

The clearest small silhouette candidate, tower cresting, already exists. Current specification has 490 objects; tower caps are indices 4 and 7, and dark horizontal rails/posts start at 418, e.g. rail 418 at (-468,24.56,-127.16), size (3.1,0.07,0.07). Dormer pediments, eave brackets and entry walls/rails also have completed documented treatments. Photograph-visible chimneys remain uncertain in the documentation; the single oblique image does not establish a reliable roof-plan mapping/count. Do not infer them from repetition or model symmetry. Stop rather than add redundant cresting or speculative chimneys.

## Villard Hall: recognizable features covered; unresolved work not a small safe addition

Inspected archived `data/reference-images/photos/villard-hall/east-2017.jpg` via a local inspection preview, refinement history and the actual 382-object `villard-east-detail.json`. Source is Daderot, CC0: https://commons.wikimedia.org/wiki/File:Villard_Hall_-_University_of_Oregon_-_Eugene,_Oregon_-_DSC09617.jpg . The east view supports arched window ornaments, cornice brackets and the entrance balcony, but these already have layered surrounds, moldings and balcony side returns. Four tower crests are real spec components (indices 302-381 above y=23), not absent features inferred from the original massing. The documented central roof-railing candidate was previously rejected for poor alignment. West/theater connection and entry/ground details remain uncertain; this photo does not resolve those existing limitations. No new high-value, clearly mapped small addition was established.

## Gerlinger Annex: archived photo cannot authorize an Annex detail

Viewed `data/reference-images/photos/gerlinger-annex/exterior-2013.jpg` and read `docs/gerlinger-annex-correction.md`. That archival label is not reliable building-identity evidence: the existing correction expressly prohibits using the pictured arched/dormered facade to justify the modern Annex. Current `gerlinger-annex-correction.json` has 84 objects (76 boxes and 8 shrubs), a flat-roof modern replacement. Do not import the historical facade's rings, dormers or pediments into it. Reliable identification/current imagery is needed, not extra geometric effort. No new attribution or license claim is made beyond the preserved archive record.

## Draw-call feasibility is necessary, not sufficient

The existing exterior generator consumes explicit spec primitives and merges building geometry. A future supported addition could target the same merged mesh with zero additional draw calls, but that architecture does not establish missing-detail evidence or positional correspondence. This pass identified no addition meeting all three requirements: demonstrably absent, clearly photo-mapped, and worth the extra geometry. No implementation, export, rendering test or performance result is claimed. Leave this batch stopped rather than filling the work queue with speculative detail.
