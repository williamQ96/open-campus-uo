Published release 0.13.0. See DEVELOPMENT_LOG.md for actual deployment verification.

**English** | [简体中文](zh-CN/interiors-mobile.md)

# Iteration 15: analog movement and shared classroom

Published in 0.13.0. The published 0.12.0 model provenance is unchanged. Generic runtime and methods are maintained in [upstream](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/interiors-mobile.md).

- **Phone Follow / First person:** lower-half drag magnitude controls 0–4.6 m/s with a 6 px dead zone and 48 px full stick; slight drag walks, full drag runs. No separate Run button. Upper-half look, independent two-finger input, release/cancel safety and desktop Shift run remain.
- **Coverage:** all 534 building records receive an original green/gold doorway; all 534 estimated approach points clear the current footprint collision audit. This does not establish actual entrance locations, accessibility or path connectivity. Stable building-ID ENU overrides can be authored in `public/scene/viewer-settings.json` → `entrances`.
- **Enter / exit:** click or tap a visible door in any camera mode. In Follow / First person, approach and press E or use the Enter button. Inside, E near the exit, touching/clicking the exit door or Return to campus loads outdoors again.
- **Shared room:** an original 24 × 18 m classroom with 15 desk/chair sets, green board, teaching desk, windows, ceiling and exit; furniture/wall collision, all three views, walk/run/jump, existing hero/audio/comfort. Overview hides the ceiling. Every building currently uses the same inferred room; it is not a real UO floor plan or usage claim.
- **Resource boundary:** full-document navigation and dynamic entry imports keep one active world. Indoor requests exclude campus/base/landcover GLBs, outdoor graph/activity, scenery and campus NPCs. Explicit pagehide disposal also handles GPU resources retained by browser page caching; BFCache returns rebuild. Shared hero/fonts/code/audio can reuse HTTP cache. Future indoor detail can replace this template per stable ID, without keeping all rooms resident.
- **Return state:** same-tab session storage restores outdoor position, hero facing, camera view/heading/pitch/Follow distance, Overview framing, density, motion, display and sound settings. Invalid/unavailable state returns to the normal map start. Navigation/selection, NPC trajectories, developer and beta rounds restart. Storage-disabled behavior does not block entering or leaving.
- **Export / rights:** editable Apache-2.0 [`classroom.js`](../apps/web-preview/src/classroom.js); original CC BY 4.0 [`classroom-v1.glb`](../apps/web-preview/public/interiors/classroom-v1.glb), 162,700 bytes. [Asset note](../assets/interiors/README.md) documents export/credit; checksums are registered in `data/asset-sources/manifest.json`. No new photos or third-party models/textures were used.

Verification and actual publication status are recorded in [DEVELOPMENT_LOG.md](../DEVELOPMENT_LOG.md) and [phase15-verification.json](../data/metadata/phase15-verification.json). Historical model/image provenance is retained. The published viewer lock pins clean upstream implementation 16e754a918e87d77cebc8e511e5932191f8d4924; historical phase15/16 local evidence retains dirty=true as captured.


## Iteration 16: Overview card / observer visits / hover (included in 0.13.0)

Click a building model, its label, or a search result in Overview to open one map-anchored card: building name at top, exact `to be fill` information placeholder, Enter at the bottom and a close button. Hide only the selected building's label while the card is active; restore it when closed or when returning to character views. Cards follow camera projection and stay within phone portrait/landscape bounds. Other labels keep their existing decluttering behavior.

Overview Enter opens the classroom in `interior_mode=overview`. The room has **no hero object and makes no hero-model request**. The actual hero stays at the saved outdoor campus position; the indoor observer can orbit/pan/zoom and return to the same outdoor view/framing. Character modes are intentionally omitted during this observer visit. Follow/First-person doorway entry remains the regular playable room with its hero and three views. Both flows keep the separate-world lifecycle from iteration 15. The URL carries observer mode so it works even if storage is denied; return-location recovery still requires the documented session storage.

Mouse hover adds a small emissive tint to individual buildings without selecting them; selected tint takes priority. Batched background buildings get only their own source-footprint edge cue, preserving batches and avoiding a whole block glowing. Picks resolve stable building IDs with boundary tolerance. Mouse picking is limited to one pending sample per 80 ms, skipped during drag/modal activity and cleared on leave; touch does not create hover. No quality reduction or model regeneration. Shared code/design/validation are maintained in the published upstream; this campus log and evidence remain downstream.
