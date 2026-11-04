# Gerlinger Hall: entrance, balconies and planting

2026-11-03; local, unpublished. Building `roof-9ac93ab7`, vegetation `ENV-03`.

A source-pinned layer adds simplified double entry doors and trim, two shallow metal balcony railings and photo-inspired shrubs flanking the entry. The reference is Rick Obst's [2013-10-19 photograph](../data/reference-images/photos/gerlinger-hall/exterior-2013.jpg), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see [archive metadata and attribution](../data/reference-images/manifest.json). No photograph is embedded. The new geometry is original CC BY 4.0; code Apache-2.0. Exact dimensions, plant species, access and present-day conditions are unverified. Entrance and balconies are decorative, not collision, access or structural data. Existing geometry and terrain are preserved.

[Before](images/gerlinger-before-clear.png) and [after](images/gerlinger-after-clear.png) are fixed-camera diagnostic views of the campus GLB with the existing procedural vegetation deliberately hidden for legibility; the added shrubs are visible in the after image. [Actual tree context](images/gerlinger-after-context.png) shows significant obstruction. No trees were moved or removed; further source-backed tree review is required. The existing simplified pediment, oversized entry surround, window rhythm and dimensions remain imperfect; this local pass does not establish Knight-equivalent fidelity. Building and ENV-03 remain level 1.

The [detail data](../apps/web-preview/public/scene/gerlinger-hall-detail.json) uses the same generator and base-GLB pin as Johnson's detail. Presentation now accepts multiple distinct source-pinned layers; the rebuild guard checks each file and rejects duplicates, changed layer hashes or a changed base. It retains the existing Johnson layer. Production build, 46 JS unit tests, eight rebuild protection tests and six landmark/card browser tests passed, as did the controlled visual capture. Chrome/SwiftShader is not a device performance measure.

## Unresolved identity discrepancy: Gerlinger Annex

The project's [archived 2013 image labelled Gerlinger Annex](../data/reference-images/photos/gerlinger-annex/exterior-2013.jpg) and the corresponding current model show arched historic detailing and dormers. UO's [2025 Gerlinger Annex historic resource survey](https://cpfm.uoregon.edu/gerlingerannex2025) identifies a 1969 modern, flat-roofed building at 1484 University Street. This discrepancy may involve the photograph caption, project identity matching or modeled building geometry. Do not assume which is wrong or refine the Annex from that photo until its location and model ID are reconciled against independent authorized evidence. This finding does not change the Annex geometry or grade.

Six further building cards now cite UO official information for Gerlinger Hall, Condon, Friendly, Hendricks, McKenzie and Susan Campbell. Known occupants are partial. This brings sourced entries to 38 of 534 building identities; the rest retain the unknown fallback. Information coverage does not promote exterior level.

**Later information batch:** Ten additional official-source building entries bring the total to 48; the card data test checks identity membership and official HTTPS domains.


**Correction:** The UO historic assessment identifies the reference entrance as the east facade, while this candidate was placed on the north facade. The candidate has been deactivated and retained for review. Its screenshots above show the former candidate, not the current scene. See [Annex and Hall orientation correction](gerlinger-annex-correction.md).


**Follow-up:** A new independently constructed detail layer is now placed on the documented east facade. The old north-facing candidate remains disabled. See [east facade refinement](gerlinger-east-refinement.md).
