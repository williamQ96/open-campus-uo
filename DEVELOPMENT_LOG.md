# Project development log

**English** | [简体中文](DEVELOPMENT_LOG.zh-CN.md)

This log belongs only to **Open Campus: UO**. Update it alongside each project change with the intent, resulting behavior, verification and publication status. Keep entries newest first; append corrections instead of rewriting past results. Link existing evidence rather than reconstructing an unverified history. English is the default; keep the Chinese companion consistent.

Reusable methods, algorithms, contracts and validation practices belong in the upstream [methodology log](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/METHODOLOGY_LOG.md). Do not copy this campus development log or campus-specific release notes into upstream. The methodology log is maintained in the separate upstream repository.

## 2026-11-03 - Asset refinement inventory (local)

- Added a maintainable inventory covering 534 exterior identities, 534 planned building-specific interiors and 13 existing environment, prop, shared-interior and character/animal entries. The user-specified baseline assigns Knight exterior level 2 and other existing assets level 1; absent interiors remain ungraded. Levels 3–5 await user criteria.
- Validated unique IDs, both building ID sets against the manifest, status/level assignments and evidence paths. Inventory is local and uncommitted; no publication or model changes. See [inventory](docs/asset-refinement-inventory.md).

## 2026-11-03 - Knight Library north facade refinement (local)

- Refined the two entrance pavilions, window plaques, spandrel and cornice in the existing Architectural Toon palette; retained building identity and geographic massing. Source evidence and inferred dimensions are recorded in [the refinement note](docs/knight-refinement.md).
- Blender 4.5.15 rebuilt the pilot and expansion. The expansion audit passed: 534 unique identities and no embedded images. A standalone Blender render was visually inspected, and all 42 preview unit tests passed; a local browser review confirmed the campus placement, north-facing facade and toon materials with no console warnings or errors; hardware performance was not tested. Existing illustrative vegetation obscures portions of the building. Local work only; not committed or published.

## 2026-11-01 — Publication confirmed: 0.13.0 deployed and anonymously verified

- Implementation [ba2aeb8](https://github.com/williamQ96/open-campus-uo/commit/ba2aeb8a8649023973990274e3e5b51f835ba4a5) is pushed and [GitHub Pages deployment](https://github.com/williamQ96/open-campus-uo/actions/runs/41349051268) succeeded. [Live explorer](https://williamq96.github.io/open-campus-uo/) returns anonymous HTTP 200 with iteration 16 and 534 entrances.
- Live checks passed: Chapman Hall card and exact placeholder, selected-label suppression, model hover/click, hero-free Overview classroom with no hero/outdoor-GLB requests, exact outdoor pose/framing restoration, ordinary E-entry playable hero with Follow/First-person, and 390 px touch walk/full-drag run/cancel with no Run button or page overflow. Zero page errors. All three remote campus/ground/classroom GLB hashes match local files. See [production evidence](data/metadata/release-v013-verification.json); diagnostic screenshots remain local.
- The published lock pins clean upstream implementation 16e754a (pipeline 0.12.0 / template 0.4.0). [Upstream CI](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41348974431) succeeded completely. Downstream source/media/assets/geography/ground audit succeeded. At this record, [the downstream complete browser workflow](https://github.com/williamQ96/open-campus-uo/actions/runs/41349051286) is still in_progress; its format, JS and build steps succeeded, with complete browser regression running. This does not claim a finished remote browser suite. Local prior scenario results remain preserved separately.
- This documentation/evidence-only confirmation uses [skip ci] and changes no runtime, asset or deployment. Historical pending/local entries retain their original capture context. Development logs remain downstream, methodology updates upstream; attachments and local diagnostics stay excluded.

## 2026-11-01 — Publication batch: Open Campus: UO 0.13.0

User authorized pushing both accumulated local iterations and deploying Pages. This release combines iteration 15 analog phone walk/run, 534 inferred portals and exportable shared classrooms with independent world/GPU lifetime, and iteration 16 Overview cards, hero-free room inspection and subtle hover. Shared runtime is synced to clean upstream implementation 16e754a918e87d77cebc8e511e5932191f8d4924 (pipeline 0.12.0 / template 0.4.0), dirty=false; historical model generation, phase15/16 local evidence and reconstruction pins retain their original provenance. Local verification passed 34 upstream Python, 42 JS per repository and full upstream 17-case browser suite, with consumer search/room/card/phone/navigation/landmark scenarios. Source/model geometry is retained and the new original classroom GLB is registered. This entry prepares publication; successful Actions and anonymous live checks will be recorded after deployment. Development logs/art/evidence stay downstream, reusable methods upstream; attachments and local screenshots/traces are excluded.

## 2026-11-01 — Local pending iteration 16: Overview building card, observer rooms and hover

- **Overview selection:** clicking a label or building body, or choosing a search result, opens a single building-anchored card. Name at top, exact `to be fill` information placeholder, Enter at bottom, close button. Hide only the selected building's ordinary label; restore on close or character view. Keep other labels/decluttering, world anchoring, search framing, portrait/landscape limits and the existing character-mode selection panel.
- **Observer room:** Overview Enter now loads an explicit overview inspection document with open ceiling, orbit controls and no indoor hero object/model request. The outdoor hero stays at its saved campus position. Return restores that position and the prior Overview framing. Ordinary Follow/First-person door entry remains a playable three-view classroom. Inspection mode is carried in the URL and uses the existing isolated-world/GPU lifetime; no hidden live campus is added.
- **Mouse hover:** small emissive lift for individual buildings, stronger persistent selection, clearing hover without clearing selection. Batched context resolves one stable footprint ID with boundary tolerance and uses a per-building source-footprint edge cue, preserving material batches. One pending mouse pick at most every 80 ms; skip drags/modals, clear on pointer leave; no touch hover. No quality settings or geographic/model assets are reduced or regenerated.
- **Verification:** 34 upstream Python, 42 JS per repository, full upstream browser 17 cases, both format/build checks pass. Initial downstream focus run passed 7/9; two test-only assumptions used a live :visible locator and expected an off-camera label to appear. Stable-ID targeting and explicit facing corrected those tests; final card/hover/phone/observer scenarios passed 3/3, search/ordinary-room scenarios 6/6, and navigation/landmark/material checks 4/4. Native UO review confirms Chapman Hall card text, hidden label, heroPresent=false / player=null / original outsidePlayer retained, no character-model request, exact outdoor pose/framing recovery and zero page errors. See [structured evidence](data/metadata/phase16-verification.json) and [design guide](docs/interiors-mobile.md). Screenshots remain local under artifacts. The existing Vite large shared-code advisory remains; no phone-FPS claim.
- **Ownership / status:** generic implementation and card/observer/hover methods are maintained locally upstream with separate method records. UO profile iteration 16 and these project records remain downstream. All 43 managed runtime hashes match upstream; dirty=true honestly identifies uncommitted work. This iteration and the prior local batch are not committed, pushed or deployed; published 0.12.0 and all historical model/reference evidence are preserved. Local preview: http://127.0.0.1:5173/.

## 2026-11-01 — Local pending iteration 15: analog mobile movement and building interiors

- **Mobile behavior:** Follow and First person now map lower-half drag continuously from stationary through walking to 4.6 m/s running (6 px dead zone / 48 px full stick); upper-half looking remains independent. Removed the separate Run button. Actual displacement controls the gait threshold and distance-based footsteps; keyboard/Shift/jump and touch cancellation remain.
- **Entrances / shared classroom:** all 534 building records have lightweight original green/gold inferred doorways; all 534 approach points pass the existing footprint-collision audit. Mouse click or touch enters in every camera mode; E and an Enter button work nearby in character modes. All buildings share an original inferred 24 × 18 m classroom, 15 desk/chair sets, teaching desk, board, windows, ceiling, furniture collision and exit. Indoor three views, familiar movement and audio remain; Overview opens the ceiling. These are estimated doors and a generic room, not verified real entrances, accessibility or UO floor plans.
- **World lifetime / return:** dynamic campus/interior entry plus full-document navigation, explicit pagehide renderer/GPU disposal and BFCache reconstruction keep one active world. Indoor production requests contain no outdoor GLBs or campus code chunk. Restore outdoor position, hero facing, camera pose/framing/mode, density, motion and display/sound settings from same-tab session state; denied/invalid storage falls back to the regular map start. Navigation, selection, NPC trajectories, beta and developer state restart. The stable-ID doorway override contract allows later correction and independent indoor detail.
- **Open assets / methodology:** original classroom GLB is 162,700 bytes (10 meshes / no embedded images), SHA-256 397a9825a4efe1c2d9136f80c2b9ef056254148b9c023ccbcbb4485ed450489e, registered under CC BY 4.0. Parametric code and export script are Apache-2.0. No new reference photos or third-party assets; existing campus/ground geometry and provenance stay unchanged. Generic runtime/design/indoor-lifetime policy are implemented locally upstream with a separate methodology log; project art/evidence and this log stay here.
- **Actual verification:** 34 upstream Python; 40 JS per repository; both format/build checks passed. Full upstream browser 13 passed before the added storage-denial case, then final 4 interior cases passed. Downstream full run passed 27/28; the sole failure was a stale iteration-14 feedback assertion, corrected to use the current profile. Focused mobile/audio/feedback/interior rerun passed 10/10, followed by final 4/4 interior cases including denied storage. All 29 current browser cases are covered across those runs; this is not a claim of a fresh single 29-case full run. Assets 23, building IDs 534, semantic paths 70 / parking 20 and ground-height audit passed. Production-preview test confirms exact return position/view, saved Low density / No motion / muted sound, zero outdoor GLB/code requests and zero page errors. See [design](docs/interiors-mobile.md) and [structured evidence](data/metadata/phase15-verification.json). Existing Vite shared-code size advisory remains.
- **Final polish:** the hero faces the teaching board when entering, and Follow camera height stays below the ceiling. The final consumer E-entry/return smoke case passed after this adjustment; formatting/build remain passing.
- **Status:** local uncommitted changes only; no push or deployment. Published 0.12.0 remains unchanged. Viewer lock matches all 41 upstream managed files and reports dirty=true against the actual upstream base. Historical reconstruction locks/evidence and user attachments are preserved. Local viewer is available at http://127.0.0.1:5173/.

## 2026-10-31 — Publication confirmed: 0.12.0 deployed and anonymously verified

- Implementation [f26e5a5](https://github.com/williamQ96/open-campus-uo/commit/f26e5a511b471ad9095baeebb62be863a1011ca3) is pushed and [GitHub Pages deployment](https://github.com/williamQ96/open-campus-uo/actions/runs/41277741074) succeeded. [Live explorer](https://williamq96.github.io/open-campus-uo/) returns anonymous HTTP 200 with iteration 14, adaptive Overview near=32 m, rigged hero, 18 cloud clusters, Mid 29 instances and static haze cache off.
- Production search, three views, No density, beta start/exit and 390 px no-overflow layout passed; zero JavaScript errors. The 34,638,580-byte campus model and 9,630,380-byte ground layer match local SHA-256. See [production evidence](data/metadata/release-v012-verification.json).
- Clean upstream implementation 64ed0a2 is pinned; [upstream checks](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41277680207) succeeded. Downstream source/media/asset/geography/ground audits succeeded. At this record, [the complete downstream browser workflow](https://github.com/williamQ96/open-campus-uo/actions/runs/41277741143) is in_progress (awaiting final result); local complete 24-case browser integration already passed. This is not a claim of a finished remote browser run.
- This evidence-only follow-up uses [skip ci] after a successful Pages build and anonymous production verification; it changes no runtime, assets or deployment. Historical local preparation records are retained and superseded for publication status. Development records stay downstream, methods upstream; attachments and local traces are excluded.

## 2026-10-31 — Publication batch: Open Campus: UO 0.12.0

User authorized pushing all accumulated local changes and updating Pages. This release combines phases 12–14: roofs and seeded semantic activity, developer tools, Zombie School and restart, sky/clouds/ground coverage, adjustable motion, pedestrian detours, and depth/quality-preserving CPU fixes. Static haze caching remains off. The runtime is synced to clean upstream `64ed0a21898d8f156bc8657595a5407629491bb1` (pipeline 0.11.0 / template 0.3.0), with dirty=false; historical geometry and local measurement records retain their actual prior provenance. Tests already passed 34 upstream Python, 35 JS in each project, 9 upstream and 24 downstream full browser cases, both format/build checks and asset/media/geographic audits. This commit prepares publication; successful Actions and anonymous live checks will be recorded after deployment. Development logs/assets stay downstream; methods remain upstream. User attachments, traces, raw local data and Blender backups are excluded.

## 2026-10-31 — Pending local iteration 14: distant flicker and quality-preserving rendering assessment

- **Bug diagnosis/fix:** controlled same-pose tests reproduced pale roof stripes with a 0.08 m near plane and removed them by changing only near to 16 m. The default viewer now derives a conservative Overview near plane from the static map bounds with 8 m padding, a one-tenth empty-space distance and downward power-of-two quantization, capped at 64 m; the default campus view uses 32 m. Follow/First person and inside-bounds views retain 0.08 m. Roof/paving materials, source geometry, FOV and far coverage stay intact.
- **Default optimization:** render all 63 world-anchored labels through a separate small CSS scene; retain 184 static map transforms; cache identical minimap raster inputs and avoid replacing unchanged coordinate text. Dynamic actors, label projections/pinning/update frequency, route invalidation, three views, antialiasing, pixel ratio, lighting and population are retained. No asset regeneration or model simplification.
- **Assessment:** native headless Chrome/RTX5090 steady orbit label CPU time measured 0.334→0.191 ms (about 43% less); render submission 1.405→1.249 ms. Geometry is identical at 1,585,723 counted mesh vertices, 947,049 steady rendered triangles / 229 draw calls, same pixel ratio. A CPU-throttled/DPR2 stress run also reduces label work. Native Chrome was already near the 120Hz cap; these are subsystem gains, not a 40% overall FPS or embedded-browser/phone guarantee. The reported embedded-browser slowdown was not reproduced in that separate native setup.
- **Not adopted by default:** optional static spatial-haze field caching preserved the tested Toon/PBR image to one channel unit in one pixel, but repeated GPU trials gave small, unstable benefits while adding 5,166,728 attribute bytes with CPU/GPU copies and load work. Keep cache_static_haze=false in UO; default extra cached vertices/attribute bytes are zero. Preserve the experiment and exact comparative records rather than claiming a general win.
- **Verification:** 34 upstream Python, 35 upstream and 35 downstream JS cases passed; full browser suites passed 9 upstream / 24 downstream. Both formatting checks and production builds passed. Audits verified 22 asset files, 17 source images and all 534 building identities; GLB/Blender/image inputs and historical provenance remain unchanged. Runtime hashes match upstream with dirty=true. See [report](docs/overview-performance.md) and [structured verification](data/metadata/phase14-verification.json). Vite's existing chunk advisory remains.
- **Ownership/status:** generic depth, render caching and evidence-led optional-cache methods are local upstream with a separate methodology entry. Campus measurements, review outputs, profile iteration 14 and this development log remain downstream. Work remains uncommitted, not pushed or deployed; both base commits and the published site remain unchanged. No public profiling API or analytics events were added; harness references exist only in isolated test pages.

## 2026-10-31 — Pending local iteration 13: sky, comfort, detours, restart and ground coverage

- **Behavior:** blue gradient sky with 18 merged rounded-block cloud clusters; reduced-motion-aware drift. First-person motion is now No/Low/Mid/High, default Low, with 0/3/6/10.5 mm maximum vertical sway, proportional lateral motion, zero roll and no change to footstep/animation contacts. System reduced motion takes precedence.
- **Collision recovery:** walking students wait, attempt a bounded bypass inside inset authored pedestrian paving, then rejoin their fixed route at normal speed. Preserve holes/building/road exclusions, cache waypoint heights, use consistent contact margins and permit at most one planning request per frame. Narrow or blocked passages still yield; no habitat fallback.
- **Zombie recovery:** height-aware contact ends the round once and freezes play. A centered You are dead modal sits above a 30% black world shade below the UI. Escape does not dismiss it. Restart reloads the original T-junction spawn/facing and all fresh-page defaults, including Overview, Mid density, Low sway and beta/developer off.
- **Ground development:** archive a second public-domain USDA NAIP reference covering the full 2 × 2 km (two tiles acquired 2024-06-08). Use broad smoothed color cues plus inferred aprons/lawns/urban concrete/asphalt, with original matte grain. Preserve exact source dates, export extent, license and SHA in the image directory; Google screenshots remain context-only. New editable `assets/landcover/eugene-ground.blend` and texture-free `landcover.glb` add 9,630,380 bytes / 320,000 triangles. Retain the original terrain for physics/checks while drawing a single full base; fix duplicate-ground depth flicker. Existing roads and 534 building identities stay unchanged in this phase.
- **Verification:** 34 upstream Python, 31 upstream and 31 downstream JS cases passed; 8 upstream browser cases and the full 21-case downstream suite passed, followed by two new ground/material/mobile-modal cases. Both formatting checks and production builds passed. Audit verified 22 asset files, 17 source images, 70 semantic paths / 20 prop slots, all 534 building identities and the new foundation's original heightfield coordinates (maximum float export error 0.00000376 m). No embedded image textures. Review screenshots and structured checks are linked in the [phase guide](docs/phase13-environment-comfort.md) and [evidence](data/metadata/phase13-verification.json). Vite's existing chunk advisory remains; no physical-device FPS claim. The final shade/label stacking correction then passed four focused consumer browser cases and regenerated both builds.
- **Ownership / status:** generic rendering, comfort, bounded bypass and terminal-state contracts are maintained locally in upstream, with its separate methodology log. Images, classification, Blender/GLB assets, screenshots and this project log stay downstream. Current phase 12 + 13 work remains local, uncommitted, not pushed or deployed; base commits and the published site are unchanged. The managed-runtime lock honestly remains dirty.

## 2026-10-31 — Pending local phase 12: gait bug fixes, roofs, semantic templates and Zombie School beta

- **Bug fixes:** replace the independent animation/audio clocks with one actual-displacement gait phase. Explorer walk/run are 1.7/4.6 m/s and footfall spacing 0.95/1.5 m; ordinary walk cadence is about 1.8 contacts/s rather than the former >4/s. Sampled 65 poses of the delivered GLB and set its contact offset to 0.15625 cycles; retain source hash and markers in `data/metadata/gait-calibration.json`. First-person sway is limited to 3 mm vertical / 1 mm lateral with zero roll, optional and reduced-motion-aware. Mobile hold-to-run supports escaping chase mode and releases on contact end/reset.
- **Roof development:** explicitly treat all 534 identities using inferred gable/metal/tile/slate or flat/parapet/seam/skylight/service grammar, with a smaller background budget. Landmark source geometry is retained with roof color/detail treatment; no new photo evidence or photoreal claim. Save a new editable source at `assets/roof-refinement/eugene-campus.blend`, preserving previous campus/pilot files. Reopening it verified 534 independent identities and no assigned legacy gray `roof` material. GLB remains 93 semantic meshes, now 34,638,580 bytes versus 25,382,236 before; this is an explicit download/geometry cost increase. Successful temporary export replaces the served GLB atomically.
- **Activity development:** 70 precompiled routes (14 pedestrian, 8 driving, 40 grass, 8 tree) and 20 fixed parking slots, checked against authored surface masks. No cross-habitat graph fallback. The activity-v1 snapshot is archived; activity-v2 stores heights and original bends while navigation remains v1. Selected tree anchors are committed in config: regeneration produces identical bytes without ignored preparation artifacts.
- **Demand-generated templates:** shared base assets plus only active instances; Mid 29 / High target 74 / No zero, with actual destruction/disposal rather than a hidden High pool. Versioned per-ID seeds replay independent student m/f presentation, bounded normal height, continuous skin RGB, six hair styles, five bag styles, colors, speed/run state; vehicles/riders and squirrels vary too. Merge accessory parts by bone attachment. Ordinary animation performs no building/terrain classification each frame; no device FPS claim is made.
- **Developer entry:** About → Developer mode, default off; click an unobstructed NPC to inspect/copy template version, seed, properties, fixed path/slot and current state. Removing the object or disabling the entry clears the panel. Beta monsters are also inspectable; the entry is reserved for later tools.
- **Beta development:** first-level Beta functions tab beside Settings/About. ZOMBIE SCHOOL!!! is opt-in and saves/restores ordinary density; enabling it destroys civilians/props and spawns up to 28 uniform original chibi monsters on clear terrain within 160 m. They wander within 12 m at 0.45 m/s, attract at ≤30 m, chase at 2.2 m/s, release beyond 60 m and reset the wander center at their current location. Shared geometry/material, collision, throttled obstacle routing, pause-in-dialogs and full exit disposal are implemented. No combat/damage was added.
- **Verification:** 34 upstream Python cases, 26 upstream and 23 downstream JS tests passed. Full browser regression passed 6 upstream / 19 downstream cases; the calibrated rig/audio change then passed its focused browser case. Both formatting checks and production builds passed. Asset audit verified 20 files, media audit retained 16 source images, semantic masks/routes/slots passed, and all geographic source identities/records were preserved. Local visual checks covered roofs, six student accessories/hairstyles, the monster and developer panel. An initial touch-release test used the wrong CDP contact; correcting the fixture yielded passing native release checks. Vite's existing large-chunk advisory remains; no physical-device FPS benchmark is claimed.
- **Method flow / status:** reusable compiler, seeded templates, gait calibration hooks, developer and reversible beta lifecycle / Zombie School template are implemented and documented in the sibling upstream. These campus configurations/assets and this development record remain downstream. Work is local, uncommitted and not pushed/deployed; bases remain downstream `30b20091909811ffd003960bb5ddf4260b0b3c42` and upstream `c02f6cd3098dcff2635f4d9a347f9308639bc1f3`. The shared runtime lock accurately records `dirty: true`; published versions/site remain unchanged. See [phase guide](docs/phase12-npc-beta.md).

## 2026-10-31 — Publication confirmed: both repositories pushed and Pages updated

- **Live site:** [Open Campus: UO](https://williamq96.github.io/open-campus-uo/) is updated and accessible without login. The deployed implementation is [`b6a9cc54d8beac7a19574601faf4f94381d3afcb`](https://github.com/williamQ96/open-campus-uo/commit/b6a9cc54d8beac7a19574601faf4f94381d3afcb), application 0.11.0.
- **Upstream:** reusable implementation [`6b15ce8`](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/commit/6b15ce8878051dbbd0928d4332f507e6a5df4780) and methodology publication record [`c02f6cd`](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/commit/c02f6cd3098dcff2635f4d9a347f9308639bc1f3) are pushed. The clean viewer lock intentionally pins the implementation revision; the later record changes only methodology documentation.
- **GitHub checks:** [upstream implementation](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41264186786), [upstream record](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/actions/runs/41264324084), [downstream checks](https://github.com/williamQ96/open-campus-uo/actions/runs/41264257199) and [Pages deployment](https://github.com/williamQ96/open-campus-uo/actions/runs/41264257127) all succeeded. The committed-source integration includes all 16 downstream browser cases and asset/media/geographic audits.
- **Production verification:** anonymous HTTP 200 and a ready 3D scene; the deployed 25,382,236-byte campus GLB matches its source SHA-256. Mid has 29 ambient/prop collision bodies including eight squirrels; No clears them. Three views, building search and feedback dialog work. Music, footstep and squirrel file bytes match local originals/exports. A 390 px layout has no horizontal overflow, and the page reports no JavaScript errors. No real feedback issue was created. See [structured production evidence](data/metadata/release-v011-verification.json).
- **Record ownership / provenance:** project development and deployment records remain here; the upstream keeps methodology records only. Historical reconstruction/art source hashes and build-time states were preserved. Chat attachments and Blender backups were not uploaded.
- **Confirmation commit:** this final documentation-only record and current-status wording do not change the tested/deployed runtime. The commit uses `[skip ci]` to avoid repeating the complete test suite for publication evidence; all implementation checks and deployment results above refer to their exact tested commits.

## 2026-10-31 — Publication batch: Open Campus: UO 0.11.0

- **Scope:** publish the accumulated local batches together: fixed walking-route origins; photo-pattern landmark/campus refinement, 534 stylized building records and exterior haze; four-level campus density, open squirrels and collision; music, grounded footsteps, reduced-motion-aware first-person sway; downstream GitHub feedback drafts. Existing three views, search, minimap, navigation and mobile controls remain available.
- **Ownership:** this development log and campus assets stay downstream. Only generic methods, template code and the methodology log were published upstream. Chat attachment folders, generated test artifacts and Blender backup files are excluded.
- **Upstream pin:** runtime upgraded through the hash-checked sync tool to clean upstream commit `6b15ce8878051dbbd0928d4332f507e6a5df4780` (pipeline 0.10.0, template 0.2.0). The viewer lock now truthfully records `dirty: false`. Historical asset-generation locks, model hashes and the art layer's actual build-time dirty provenance are preserved; the model is not relabeled as regenerated.
- **Verification:** before publication, 32 upstream Python tests, 19 upstream/16 downstream JS tests, formatting/builds and asset/media/geographic-invariant audits passed. Full browser integration from the implementation batch passed 4 upstream and 16 downstream cases. GitHub Actions will validate committed source bytes and build/deploy the static site. Completion and live checks are recorded below after they finish.
- **Status:** user authorized push and website update for all local batches. Upstream implementation is pushed; this downstream commit prepares the Pages publication. The prior local-only entries remain historical records. See the subsequent deployment record for confirmed online status.

## 2026-10-31 — Pending local iteration 11: density, wildlife, sound and feedback

- **Purpose / behavior:** replace two switches with one No / Low / Mid / High slider, default Mid. No removes moving actors, props and collision bodies while keeping the hero and map. Add a decimated open squirrel model, authored estimated routes with pauses, class-sized capsule volumes, player substep collision and NPC yielding. Density changes actual populations; blocked spawns may reduce targets.
- **Assets:** archive the original Innerscene CC0 squirrel GLB and IntelligentGene / Another Page Studio CC0 Overworld (BGM) MP3. Preserve creator/license evidence and actual file hashes. Provide a 900-triangle, one-material, no-image squirrel GLB (93,480 bytes) and editable Blender source; clear unused imported materials/images before saving the adaptation. The footstep is original deterministic synthesis dedicated to CC0. Credits are visible in About and NOTICE; CC0 sources remain CC0.
- **Audio / motion:** master sound icon beside Directions, default on; retry after a user gesture when autoplay is blocked. Music loops quietly and hidden tabs pause audio. Actual grounded displacement drives footsteps in Follow/First person. Idle, blocking, airborne movement, Overview and dialogs suppress steps. Gentle first-person camera sway is independent of player/navigation coordinates and respects the motion setting and system reduced-motion preference.
- **Feedback:** user approved the native GitHub confirmation flow. Content is required; title and coordinates are optional. Blank titles use a UTC draft identifier plus iteration. Coordinates stay blank until explicitly included. Continue opens a prefilled downstream issue; reporters log in and confirm on GitHub. Preserve drafts, popup fallback and lossless long-body copy/paste. Do not claim creation from the campus page or send content/coordinates to analytics. No test issues were created.
- **Method flow:** generic density/collision, wildlife/audio/profile hooks, walking motion and feedback draft behavior live in the upstream template and were synced with a dirty lock. The early-playable, moderate-fidelity, source-plus-inference, community/developer refinement loop is documented upstream in English/Chinese. Local assets, routes and this development log remain downstream.
- **Verification:** downstream 16 JS unit tests and all 16 browser tests passed; formatting and production build passed. The upstream passed 32 Python unittest cases, 19 JS tests, 4 synthetic browser tests, formatting and build. Source/media audits passed: 19 archived asset files, 16 reference images, and retained geographic invariants for all 534 buildings. Reopening the adapted Blender file verified one 900-face mesh with no image/material texture dependencies; original/runtime MP3 bytes match. Browser tests cover counts at every density (0/7/29/74 bodies), clean-mode removal, audio mute/play, distance-based steps, reduced motion, optional-location feedback and a 320 px header/form. Existing mobile two-finger walking, searches, three views and fixed navigation origins remain tested. Browser rendering uses local Chrome/SwiftShader, not a physical-phone performance claim. Vite retains its existing large-chunk advisory.
- **Evidence:** [interaction guide](docs/ambience-feedback.md), [asset archive](data/asset-sources/campus-life/README.md), `tests/browser/ambience-feedback.spec.js`, `tests/ambience.test.js`. Preview remains available on the local development server. Campus model and geographic source binaries were not rebuilt by this iteration.
- **Publication status:** local and uncommitted; no push or deployment, as requested. Downstream base remains `7c6558d9272b315afad94d234db4778bc0f55d95`; upstream base remains `0361592966089072333ce3bf6eea22772c5d3079`. Viewer lock retains `dirty: true`; iteration 11 identifies the local feedback draft, not a newly published package release.

## 2026-10-31 — Pending local batch: layered campus and background refinement

- **Request:** extend Architectural Toon Realism using photo-derived patterns rather than photographic replication; upgrade peripheral whiteboxes cheaply without changing geographic placement or street/block planning.
- **Modeling:** retain the original pilot Blender source; refine Gerlinger Hall/Annex from two newly archived CC BY 4.0 photographs, and add restrained details to Knight Library, EMU and Johnson Hall. Provide stylized appearance for all 534 records: 135 in the art-priority area and 399 in the background. Generic types, colors and roofs are seeded by stable IDs; source coordinates, footprints and height records remain unchanged.
- **Landscape:** retain the 300-tree aerial-guided pilot and add 300 explicitly inferred trees and additional campus lawns. No new aerial extraction is claimed.
- **Delivery / maintenance:** the new Blender source keeps 534 independently editable building objects, 542 source meshes total. Export-only copies batch 470 anonymous IDs into 21 meshes; the GLB has 93 meshes and is approximately 25.4 MB. The model contains no embedded photographs. Original sources and the old model stay intact.
- **Viewer:** fixed-world exterior haze, desaturation and tint are on by default, with a Background haze switch; the priority area remains clear. Vertex evaluation and terrain-field offset metadata reduce recurring shader/raycast work. Existing interactions, NPC/prop switches and the preceding fixed-start navigation change remain in place.
- **Sources / audit:** [photo evidence](data/metadata/campus-expansion-photo-evidence.json), [per-ID model audit](data/metadata/campus-expansion-audit.json), [implementation/report](docs/campus-expansion.md). The image archive now has 16 approved records. Binary source/model hashes are exact; text provenance retains raw hashes plus an additional portable LF digest to handle Git line endings.
- **Verification so far:** upstream 32 Python tests, 15 JS tests and 4 browser tests passed; downstream 12 JS tests and all 13 browser tests, formatting and builds passed. Geographic identity, original source Blender, image rights/checksums and zero embedded images passed audit. Export-only source granularity is being checked again against the final saved file.
- **Final export checks:** reopening the saved Blender file confirmed 542 source meshes and 534 unique independently editable building identities. The final GLB/source hashes and all 534 runtime identities passed audit; all 13 downstream browser tests passed again against that final export. Shared runtime hashes match both the local upstream files and the deliberately dirty viewer lock. Baseline HEAD/tracking revisions are unchanged.
- **Scope / publication:** project-specific records stay here; only the reusable hierarchy, algorithms, renderer hooks and validation practices go to the upstream methodology log. Downstream HEAD remains `7c6558d9272b315afad94d234db4778bc0f55d95`; upstream base remains `0361592966089072333ce3bf6eea22772c5d3079`. All changes are local, uncommitted, not pushed and not deployed; the local viewer/art records disclose the dirty method revision.

## 2026-10-31 — Pending local batch: stable walking navigation origin

- **Request / reason:** the blue origin followed the avatar and made navigation visually uncomfortable. Freeze the origin at route start.
- **Change:** Follow and First person capture A when Start route is pressed. Walking no longer replans/trims the route or moves the blue circle. The moving player/minimap marker, animated white chevrons and arrival detection remain active.
- **Mode transitions:** First person ↔ Follow retain the same origin. Overview keeps its independent manual A; returning to a walking mode restores the saved walking origin. Explicit Start route captures the current position for a new route; Clear/new endpoint selection resets the saved origin.
- **UI / docs:** English A label now says “You · fixed starting point” for an active walking route; English and Chinese navigation notes describe the behavior.
- **Verification:** focused life/navigation browser tests: **3 passed**, including >6 m movement in both walking modes, unchanged complete route coordinates, mode switching, an explicit restart and Clear. Additional checks are recorded below when complete.
- **Completed checks:** downstream **10 JS tests and all 13 browser tests passed**, including mobile controls, search and jump regressions; formatting and production build passed. Shared upstream template **12 JS tests and 4 browser tests passed**, with formatting/build passing. Local runtime hashes match the viewer lock and upstream files. Both repositories' HEAD and tracking revisions remain at their stated baselines; no commit, push or deployment was performed.
- **Logging:** this is the first maintained project development-log entry. Earlier work remains documented in [the campus life/navigation report](docs/campus-life-navigation.md), [visual refinement](docs/visual-refinement-v0.7.md), and earlier linked reports.
- **Local baseline:** downstream `7c6558d9272b315afad94d234db4778bc0f55d95`; shared upstream base `0361592966089072333ce3bf6eea22772c5d3079`. Changes are **uncommitted and not pushed**. No web deployment is requested for this batch.
- **Viewer lock:** the local lock deliberately records `dirty: true` because it includes uncommitted upstream runtime changes. Before publishing the next batch, commit upstream, re-sync the viewer to a clean revision, verify, then publish only when authorized. Do not relabel the historical reconstruction or art-generation pins.

## 2026-11-03 — Bicycle prop refinement (local, unpublished)

Refined the generic bicycle with open rims, spokes, seat post, crank and pedals; retained existing placement and routes. Regenerated runtime GLB and an additional editable Blender candidate while preserving the prior Blender file. PROP-03 remains level 1; scooter, rider proportions and in-campus review remain open. Production build, finite-vertex checks and a standalone browser review passed; see [details and evidence](docs/bicycle-refinement.md). The shared viewer lock still points to its original props source and must be reconciled on upgrade.

## 2026-11-03 — Environment batch (local, unpublished)

Restored the existing inferred ground layer reference; added generic vehicle hubs, pickup bed and scooter details. Existing bicycle reviewed in campus context. Preserved the upstream viewer baseline and added a separately verifiable local override record. Production build, 42 unit tests, finite-geometry check, local browser review and override hashes passed. The builder may overwrite ground metadata on regeneration; individual surveys and other inventory work remain open. [Evidence](docs/environment-batch-2026-11-03.md).

## 2026-11-03 — Vegetation clearance screen (local, unpublished)

Added a reproducible conservative 2D tree/footprint screen: zero tree centers inside candidate footprints; seven pilot tree crowns flagged for further inspection and none in the expansion snapshot. This is not a 3D intersection test or current tree survey, and does not change geometry or levels. Two exploratory campus views were captured; see [methods and candidate records](docs/vegetation-clearance-audit.md). Existing landcover checker also passed against the restored layer (160,801 vertices, 320,000 triangles and preserved terrain coordinates).

## 2026-11-03 — Cloud shape refinement (local, unpublished)

Varied the scale, direction and lobe arrangement of the existing procedural clouds, preserving their merged mesh and reduced-motion behavior. ENV-07 stays level 1 and seasonal/campus-view review remains open. Production build, 42 unit tests and a direct drift/reduced-motion check passed; [before and after](docs/sky-refinement.md). The downstream sky hash is recorded separately from the upstream viewer baseline.

## 2026-11-03 — Environment triage and provenance (local, unpublished)

Recorded context views for planting, stairs, paving, furniture and the shared room, plus runtime checks of estimated entrances and life density. Knight steps show vegetation crossing the illustrative approach; full pilot regeneration risks overwriting landmark work, so this remains an isolated-mesh correction task. Updated only this pass’s prop source-manifest sizes, hashes and license. Full asset checker now stops on pre-existing campus-expanded GLB and roof Blender hash mismatches from separate landmark work; these were not overwritten. See the [13-entry triage](docs/environment-triage-2026-11-03.md). No levels changed.

## 2026-11-03 — Isolated Knight tree correction (local, unpublished)

Moved one inferred conifer off a decorative Knight stair using a source-pinned runtime vertex patch and editable vegetation-only Blender candidate. Original combined building GLB and roof Blender were not rewritten. The patch checks 68 source positions and 204 split vertices atomically; comparison found no other vegetation vertex-position changes. Browser context review, production build and 43 unit tests passed. Shrubs still intrude and the approach is not surveyed; see [evidence and rebuild limits](docs/knight-vegetation-correction.md).

## 2026-11-03 — Paired understory correction (local, unpublished)

Moved the inferred shrub paired with the previously relocated Knight tree using a second source-pinned patch. The isolated Blender comparison confirms only 68 tree and 63 shrub vertices translated with topology counts unchanged. Browser review, production build and 43 unit tests passed; other planting and actual access remain unverified. [Evidence](docs/knight-vegetation-correction.md).

Final verification after both Knight patches: full-campus browser loading/movement regression passed; nine campus/interior browser tests passed before the shrub follow-up. The full 32-test browser run was interrupted during later work and was not completed. Override and ground checks pass; the global asset checker still reports the pre-existing landmark asset mismatch.

## 2026-11-03 — Landmark provenance and environment rebuild guard (local, unpublished)

Reconciled two obsolete source manifest entries against the earlier Knight build records, matching config/audit hashes and sizes, a successful expansion audit, and a targeted zero-distance Knight Blender/GLB vertex comparison; previous hashes are retained. The 27-file open asset check passes. The campus art builder now stages its Blender and GLB outputs, validates current environment assets, carries verified ground and source-pinned vegetation references for an identical GLB, and stops before replacement if patches no longer match. Five preservation unit checks passed; an isolated real Blender rebuild preserved both patches and ground, while synthetic stale-pin and existing-asset mismatch checks stopped before replacing prior assets. Other rebuild paths and multi-file atomicity remain outside this guard. [Details](docs/landmark-provenance-2026-11-03.md), [rebuild notes](docs/campus-expansion.md#protecting-adopted-environment-layers).

## 2026-11-03 — Portable inventory status alignment (local, unpublished)

Normalized the UO CSV status codes to the upstream template’s `existing` and `planned`; the Chinese guide explains their meanings and the shared classroom fallback. All 1,081 rows were compared: IDs, levels and every other field remained unchanged. The upstream structural validator passed; it does not verify source evidence or assess quality.

Final regression after the environment patches: all 32 browser tests passed in the workspace copy using local Chrome/SwiftShader; this completes the earlier interrupted run. The 43 JavaScript unit tests, five rebuild-preservation tests, 27-file open asset check, ground and expansion audits, override hashes and upstream inventory structural validation also passed. No hardware performance claim.

## 2026-11-03 — 3D vegetation overlap triage (local, unpublished)

Added a reproducible read-only Blender BVH screen of seven earlier 2D tree candidates against their corresponding authored building meshes. Three show surface intersections (two Knight, one EMU); four did not in this limited test. The original stair tree intersects Knight while the edited candidate does not. No additional tree was moved: coarse clearance candidates are roughly 26–30 m away and need better reference/placement review. [Evidence and limits](docs/vegetation-clearance-audit.md#read-only-3d-follow-up). Levels remain unchanged.

## 2026-11-03 — Dated aerial review and rider contact (local, unpublished)

Reviewed the archived 2024 NAIP image and licensed Knight/EMU photos for three intersecting trees. Suppressed one inferred EMU tree whose center is on visible open lawn/paving in the dated image; no speculative 26–30 m relocation was made. Two Knight trees remain unresolved in dense or occluded imagery. The unchanged source GLB contains 600 generated trees and the presentation reports 599 visible. Added a source-pinned reversible patch, isolated editable candidate and rebuild preservation. Adjusted generic bicycle/scooter riders to maintain hand and foot contact across sampled heights. Before integration, production build, 45 JS unit tests, six affected browser tests, six rebuild-preservation tests, isolated Blender build and geometry comparison passed. [Evidence and limitations](docs/environment-refinement-2026-11-03.md). No levels changed.

Post-integration after environment reconnection: verified all candidate and destination hashes before applying once. Production build, 45 JS unit tests, six affected browser tests, six preservation tests, 28-file open-asset check, reference-media audit, expansion/ground audits, override and portable inventory checks passed. Project Blender mesh audit matched its recorded evidence. All remains local and unpublished.


## 2026-11-03 — sourced building cards and exterior plan

Added optional, ID-keyed official UO building information for 32 identities, with sources and checked dates; missing or unavailable information displays an explicit unknown state. This is information coverage, not an exterior level promotion. Added a proposed exterior-only batching plan; Knight remains the only level-2 building example, while other levels are unchanged. The existing individual interiors and campus geometry are unchanged. Staged validation: production build, 45 unit tests, five targeted browser tests including phone sizes and missing data. Viewer override hashes are recorded. Remaining: source and refine the rest of the campus in verified regional batches.


## 2026-11-03 — Johnson rear and planting detail

Added a source-pinned reusable geometry layer for Johnson Hall: simplified rear door, stone surround, canopy and steps, plus photo-inspired flanking shrub masses. The 2012 archived CC BY 4.0 reference, inferred details and before/after visual evidence are recorded in docs/johnson-rear-refinement.md. No base campus GLB or interiors were rebuilt; building and ENV-03 remain level 1. Staged verification: production build, 46 JavaScript tests, seven rebuild-preservation tests, six landmark/card browser tests and a fixed-camera context review. Layer and viewer override hashes are recorded; local only, not published.


## 2026-11-03 — Gerlinger Hall and additional cards

Added photo-informed Gerlinger Hall entrance, railings and illustrative flanking shrubs as a second independently pinned detail layer; the original campus GLB and interiors remain untouched. Source, limitations and controlled context screenshots are in docs/gerlinger-refinement.md. Multi-layer rebuild protection now preserves and validates each layer, including the existing Johnson layer. Six sourced official building cards bring coverage to 38. Flagged an unresolved mismatch between the Annex photo/model and UO 2025 building survey; no Annex geometry was changed. No levels promoted. Staged validation: build, 46 unit tests, eight rebuild tests, six landmark/card browser tests, visual captures and viewer hashes; local and unpublished.


## 2026-11-03 - Building information follow-up

Added ten official UO sourced building entries (48 total) and an automated check of known identities, dates and official HTTPS domains. A browser check verified the Straub card. Known occupants remain partial; no asset grades or interiors changed. Local, unpublished.


## 2026-11-03 - Gerlinger identity and facade correction

Compared official UO survey/site-plan evidence with the approximate existing coordinates: the Annex identity is spatially consistent but the old arched/dormered appearance was wrong. Added an isolated source-pinned modern flat-roof replacement and approximate planted frontage; original GLB remains intact. Deactivated the previous Hall detail layer because its east-elevation reference was placed on the north side, preserving the candidate for a later accurate rebuild. Annex card now cites the Department of Dance. Limitations and visual evidence: docs/gerlinger-annex-correction.md. No level promotion; local and unpublished. Staged validation: build, 48 JS tests, eight rebuild tests, six landmark/card browser tests, dedicated Annex selection, and visual context comparisons.


## 2026-11-03 - Gerlinger Hall east facade

UO plans and source mesh ray samples confirmed the east wall. Added an independently source-pinned, photo-informed east pediment, windows, awnings, entry, balcony rails and approximate planted shrubs; the incorrectly north-placed candidate remains disabled. Updated the card with UO Human Physiology office information. Detail primitives now batch by semantic kind using vertex colors, resolving a browser draw-call ceiling failure while retaining material modes. Source, uncertainty and diagnostic images: docs/gerlinger-east-refinement.md. No grade promotion, base GLB or interiors changed. Staged build, 49 JS tests, eight rebuild tests, landmark/Annex browser checks and visual review passed. Local, unpublished.


## 2026-11-03 - EMU tree 216

Suppressed one inferred tree whose center has no clear canopy on the archived 2024 NAIP aerial; tree 297 remains unchanged because its boundary is ambiguous. The source-pinned patch validates exact exported positions, was regenerated byte-for-byte from the pinned Blender source, and leaves the base GLB untouched. Source trees 600; visible trees 598 including earlier tree 273 suppression. Guard now checks multiple suppression hashes and counts. See docs/emu-tree-216.md for uncertainty and before/after. No grade promotion, interior or building edit. Staged build, 49 JS tests, nine guard tests, affected landmark/Annex browser checks and visual review passed. Local, unpublished.


## 2026-11-03 - Four additional sourced cards

Added official UO information for Computing Center, Jaqua Academic Center, Matthew Knight Arena and McArthur Court. Sourced card coverage is now 53 building identities. Data validation and a Jaqua browser check passed. No level or geometry changes; local and unpublished.


## 2026-11-03 - Johnson north frieze

Corrected the north entablature wording to the historically documented Administration Building using a reversible, source-pinned runtime text layer. Browser canvas renders original text without photo pixels; typography and current condition remain approximate. The original GLB, existing rear layer and interiors remain unchanged. Before/after, source and limitations: docs/johnson-frieze-refinement.md. Building stays level 1. Staged build, 50 JS tests, nine rebuild tests, visual comparison and landmark/material/draw-call browser checks passed. Local, unpublished.


## 2026-11-03 - Three further building cards

Added official UO information for Cascade Hall, Ford Alumni Center and Outdoor Program Barn. Sourced coverage is 56 building IDs; occupants remain partial. Dataset validation and a Cascade browser check passed. No geometry or level changes; local and unpublished.

### 2026-11-03: Friendly Hall west facade

Added a source-pinned, selectable west-facade procedural replacement with archived CC0 photo and official historic assessment evidence. Preserved the original GLB and building identity; the level remains 1. See docs/friendly-west-refinement.md for limitations and validation.

### 2026-11-03: Building card information

Added five official-source building information records for Bean, the Central Power Station, Collier House and the two Living Learning Center entries. Identities and current tenant lists remain subject to verification. See docs/building-information-east-campus.md.

### 2026-11-03: Friendly west details and planting

Added paired-window mullions, entrance column pairs, a belt course and six illustrative shrubs from the existing archived photo reference. Scene selection, render modes and pilot regression passed; no level promotion. See docs/friendly-west-refinement.md.

### 2026-11-03: Villard Hall east

Added a source-pinned, selectable simplified east facade and illustrative planting from a CC0 photo and UO elevation. Other elevations and dimensions remain unverified; level remains 1. See docs/villard-east-refinement.md.

### 2026-11-03: University Hall exterior

Added a source-pinned simplified two-tower exterior and illustrative planting, plus a reusable tapered roof primitive. Historical evidence and gaps are documented; level remains 1. See docs/university-hall-refinement.md.

### 2026-11-03: University and Villard arch details

Introduced reusable two-axis arch geometry; refined University Hall windows and tower dormers and Villard east ground-floor windows. Existing dated references, level 1, and uncertainty remain. See individual refinement documents.

### 2026-11-03: University entries and Villard roof

Added illustrative arched entry bays and stairs at University Hall and tapered Villard roof volumes. Both remain level 1; tree clearance, access and dimensions are unverified. See respective refinement notes.

### 2026-11-03: Anstett south frontage

Added a source-pinned south frontage, illustrative planters, shrubs and benches; enriched its card from UO. Added semantic prop support to the reusable detail layer. Level remains 1; see docs/anstett-south-refinement.md.

### 2026-11-03: Peterson south frontage

Reused the paired-building vocabulary in a source-pinned illustrative south frontage and three shrubs; enriched the card with the UO-listed Oregon MBA. Existing background junctions and dimensions remain unverified; level 1. See docs/peterson-south-refinement.md.

### 2026-11-03: Bench detail and Knight Campus cards

Refined two illustrative Anstett bench backs and armrests, and added two official-source Knight Campus information cards. Rejected two Peterson seam trials due to overlapping geometry; see the corresponding refinement notes. Levels unchanged.

### 2026-11-03: Anstett planter refinement

Added stone rims, soil and varied low vegetation to the two illustrative beds; expanded the reusable palette. Species and current site conditions remain unverified; level unchanged. See docs/anstett-south-refinement.md.

### 2026-11-04: Tykeson north frontage

Added source-pinned simplified glazed frontage, canopy and illustrative planting to the existing approximate envelope. Source, inferred orientation, occlusion and unresolved dimensions are recorded; level remains 1. See docs/tykeson-north-refinement.md.

### 2026-11-04: Susan Campbell Hall

Added a reversible, source-pinned simplified L-shaped exterior and gambrel roof, and a reusable gambrel primitive. Historic source and significant unknowns are documented; level remains 1. See docs/susan-campbell-refinement.md.

### 2026-11-04: Hendricks exterior source audit

Compared the UO survey, aerial context and staged roof candidate. Rejected the candidate because its building boundary is unresolved and it obscures existing details; level remains 1. See docs/hendricks-exterior-audit.md.

### 2026-11-04: Generic transport prop details

Added simple vehicle bumpers, mirrors and window separators and scooter hub, grip and reflector details. Regenerated the GLB and retained level 1; see docs/prop-detail-2026-11-04.md.

### 2026-11-04: Versioned editable prop snapshot

Created a non-overwriting Blender import of the current prop GLB, stored its source hash in the scene and verified all five mesh coordinates and transforms against a fresh import. Procedural source remains authoritative; older Blender files remain preserved.

### 2026-11-04: Straub west frontage

Added a reversible, UO-survey-informed west facade overlay. The footprint, windows and entrance remain approximate; the roof and other sides remain unresolved, and level stays 1. See docs/straub-west-refinement.md.

### 2026-11-04: Condon east entrance

Added a reversible source-informed entrance, approximate terrain-adjusted steps and illustrative planting. Building and environment categories remain level 1; see docs/condon-east-refinement.md.

### 2026-11-04: Fenton south entrance

Added a reversible survey-informed entrance overlay with illustrative steps and shrubs. The source footprint and heights remain approximate; building and environment categories remain level 1. See docs/fenton-south-refinement.md.

### 2026-11-04: Chapman west entrance and two building cards

Added a reversible west-entry overlay and illustrative planting informed by UO surveys; the approximate building and environment entries remain level 1. Refreshed Villard and Chiles cards with scoped UO-sourced occupants. See docs/chapman-west-refinement.md and docs/building-info-2026-11-04.md.

### 2026-11-04: Oregon Hall facade and two office cards

Added a source-informed reversible west-wing frontage overlay; the nearest-roof identity and placement remain approximate and level 1. Updated Lillis and Columbia cards using scoped UO office evidence; see docs/oregon-south-refinement.md and docs/building-info-offices-2026-11-04.md.

### 2026-11-04: Oregon Hall raised lawn

Added a source-informed schematic raised lawn and retaining edge as a reversible non-building layer; dimensions, present conditions and access remain unverified. ENV-05 and ENV-06 remain level 1. See docs/oregon-south-refinement.md.

### 2026-11-04: Collier House and two building cards

Added a reversible survey-informed runtime exterior replacement with approximate roof, porch and addition; prior GLB and interior remain intact and level stays 1. Refreshed Collier and Clinical Services cards with scoped official uses. See docs/collier-house-refinement.md and docs/building-info-collier-clinical-2026-11-04.md.

### 2026-11-04: Collier collision alignment

Added validated source-pinned conservative collision envelopes and routing checks for the reconstructed Collier exterior, retaining the original footprint. Porch and steps are deliberately blocked; graph and browser checks passed. See docs/collier-house-refinement.md.

### 2026-11-04: Venue cards and exterior boundary review

Updated McArthur and Hayward cards with scoped UO-sourced program uses; documented McArthur/Esslinger footprint overlap and rejected an unaligned Clinical Services roof candidate. No geometry was added in this review.

### 2026-11-04: Outdoor Barn solar illustration and arena card

Added a reversible, source-informed illustrative solar array and validated primitive rotation. Exact roof identity and array configuration remain unverified; level stays 1. Added a sourced basketball home-venue association to the Matthew Knight Arena card. See docs/outdoor-barn-solar-refinement.md and docs/building-info-arena-2026-11-04.md.

## 2026-11-04 — provisional Volcanology identity

Added a source-pinned optional identity annotation and scoped official-source faculty-office card for roof-399a0551. Map match is approximate, original manifest unchanged, level remains 1. Rejected facade candidate due to terrain and roof intersections. See docs/volcanology-identity-audit.md. Verified 62 unit tests, 6 targeted browser tests and production build.

## 2026-11-04 — illustrative Volcanology south elevation

Added a source-pinned, photo-informed south facade for the provisional map match after testing terrain and roof heights and checking front and oblique browser views. Identity and dimensions remain uncertain; level 1 and original entry/collision data remain unchanged. See docs/volcanology-identity-audit.md.

## 2026-11-04 — Anstett landscape furniture

Added two illustrative globe lamps and a seasonal basket to a separate source-pinned Anstett landscape layer, based on the archived 2019 reference. Positions, species and conditions remain uncertain; levels remain 1. See docs/anstett-south-refinement.md.

## 2026-11-04 — four generic road-vehicle models

Refined four procedural vehicle kinds and corrected the pickup windshield; added SUV to the export and a matching six-model Blender snapshot. Scene placement and collision are unchanged, PROP-02 stays level 1. See docs/vehicle-family-refinement-2026-11-04.md.

## 2026-11-04 — pilot bench family

Source-pinned selection and reusable environment geometry refine nine existing bench backs and armrests while retaining seats, lamps, locations and original GLB. Runtime merging retains the draw-call budget. Existing path/ground placement uncertainty remains; PROP-01 stays level 1. See docs/pilot-bench-batch-2026-11-04.md.

## 2026-11-04 — regional fern-like planting

Refined three existing inferred planting clusters with reusable fern-like foliage and source-pinned suppression, merged into the existing understory batch. Eight candidates remain unchanged due to partial paving/building conflicts; species and locations unverified, ENV-03 stays level 1. See docs/pilot-ferns-2026-11-04.md.

## 2026-11-04 — plaza planting conflicts

Suppressed three inferred plaza planting clusters after comparing existing paving and 2024 USDA NAIP; no locations were guessed. Added source-pinned reusable environment patch list and rebuild checks. Five other candidates remain uncertain; ENV-03 and ENV-05 remain level 1. See docs/plaza-plant-clearance-2026-11-04.md.

## 2026-11-04 — pilot globe lamp family

Refined eight existing illustrative lamps with reusable stepped bases and globe supports, merged into the existing metal batch. Three locations remain unaltered pending review; styles and positions are not surveyed, PROP-01 stays level 1. See docs/pilot-lamps-2026-11-04.md.

## 2026-11-04 — Anstett south elevation

Reworked the source-pinned south facade in one photo-informed pass: corrected wing window bays and added brick piers, entry surround, central motif and twin stair walls. Existing landscape components and original GLB remain; dimensions and other elevations unverified, level 1. See docs/anstett-south-refinement.md.

## 2026-11-04 — Collier multi-elevation exterior

Used labeled UO 2018 historical photos to add two schematic east porches, west chimney, roof/eave and porch details. Added conservative collision envelopes for the new visible geometry; original footprint, GLB, vegetation and interiors are preserved. Dimensions and present conditions remain unverified, level 1. See docs/collier-house-refinement.md.

## 2026-11-04 - Villard multi-elevation exterior

Added schematic north and south facades, corner roofs, north steps and conservative collisions using the UO 2017 historic assessment. Existing east elevation, footprint, GLB and interiors remain. Dimensions and accessibility remain unverified; level 1. See docs/villard-east-refinement.md.

## 2026-11-04 - Susan Campbell multi-elevation exterior

Added schematic multi-pane windows, six wing dormers and conservative collision volumes, using the UO historic survey. Removed overlap-buried details; original layout, source GLB and interiors remain. Entrances, exact details and accessibility are unverified; level 1. See docs/susan-campbell-refinement.md.

## 2026-11-04 - Condon original entry and addition

Added schematic entry cornice, addition facade frame and flat-roof edge guided by UO survey. Source mesh, landscape, navigation and interiors remain unchanged. Exact dimensions, unviewed sides and accessibility remain unverified; level 1. See docs/condon-east-refinement.md.

## 2026-11-04 - Friendly Hall multi-elevation exterior

Used UO historic elevation and roof plans to add schematic north, south and east facade details, a mansard-like roof and conservative collision boxes. Prior west details, vegetation, source GLB and interiors remain. Wing massing, grading and accessibility remain unverified; level 1. See docs/friendly-west-refinement.md.

## 2026-11-04 - Chapman multi-elevation exterior

Added schematic north and south cornices and sash detailing using UO historic assessment and existing glass geometry. Original flat roof, west entrance, GLB, vegetation, navigation and interiors remain. Entries, grading and accessibility are unverified; level 1. See docs/chapman-west-refinement.md.

## 2026-11-04 - Fenton orientation correction and stacks

Oregon archive identified the previously south-placed principal entrance photo as the east elevation. Relocated the schematic bay, removed steps pending grade verification, and added illustrative south/west stacks windows and roof rail. Original GLB, landscape and interiors remain. Real grade, details and accessibility remain unverified; level 1. See docs/fenton-south-refinement.md.

## 2026-11-04 - Gerlinger multi-elevation exterior

Used UO historic views to add schematic south windows, louvers and dormers, plus north wing windows. Prior east layer, source GLB, vegetation, navigation and interiors remain. Base-mesh north pediment provenance, grade, access and current details remain unverified; level 1. See docs/gerlinger-east-refinement.md.

## 2026-11-04 - Oregon Hall east-wing exterior

Added schematic four-level east-wing window bands and roof-edge trim informed by UO survey; the unphotographed east side is extrapolated. Preserved west facade, planter, source GLB, vegetation, navigation and interiors. Identity, boundaries and access remain unverified; level 1. See docs/oregon-south-refinement.md.

- 2026-11-04: Added source-pinned schematic McKenzie Hall west/east exterior overlays; see docs/mckenzie-exterior-refinement.md for sources, visual checks, collision caveats and remaining level-1 gaps.

- 2026-11-04: Added source-pinned schematic Allen Hall west exterior overlay and consolidated adjacent Anstett vegetation and prop draws; see docs/allen-west-exterior-refinement.md for sources, visual checks, collision caveats and remaining level-1 gaps.

- 2026-11-04: Added source-pinned Carson Hall schematic exterior, source-checked wall recolor and rebuild preservation; see docs/carson-exterior-refinement.md for evidence and level-1 limitations.

- 2026-11-04: Added source-pinned PLC tower facade and nearby planting batching; corrected Carson navigation test axes. See docs/plc-tower-refinement.md and docs/carson-exterior-refinement.md.

- 2026-11-04: Added source-pinned schematic museum west exterior and pointed-arch geometry, with nearby planting batching; see docs/museum-west-refinement.md for evidence and level-1 limitations.

- 2026-11-04: Added source-pinned Bean exterior study and wall recolor with nearby planting batching. See docs/bean-exterior-refinement.md for sources and level-1 limitations.

- 2026-11-04: Added source-pinned LLC North exterior study, wall recolor and guarded source-building mesh consolidation. See docs/llc-north-refinement.md for references and level-1 limits.

- 2026-11-04: Added source-pinned LLC South facade, wall color and guarded local roof reconstruction. See docs/llc-south-refinement.md for references and level-1 limits.

- 2026-11-04: Added source-pinned natural and cultural history museum exterior study and wall recolor. See docs/natural-museum-refinement.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned central power station exterior study and wall recolor. See docs/power-station-refinement.md for evidence and level-1 limits.

- 2026-11-04: Refined the reusable generic scooter and regenerated its prop export; see docs/scooter-detail-2026-11-04.md for evidence and level-1 limitations.

- 2026-11-04: Refined the generic bicycle and saved verified six-prop Blender snapshot; see docs/bicycle-drivetrain-2026-11-04.md.

- 2026-11-04: Refined nine illustrative pilot bench seats with source-pinned slats; see docs/pilot-bench-seats-2026-11-04.md.

- 2026-11-04: Refined reusable fern fronds at three existing sites; see docs/fern-arched-2026-11-04.md for evidence and limitations.

- 2026-11-04: Added reversible source-pinned color variation to the pilot canopy batches; see docs/pilot-canopy-tone-2026-11-04.md for scope and limitations.

- 2026-11-04: Added subtle cloud underside shading without changing cloud geometry; see docs/cloud-shading-2026-11-04.md.

- 2026-11-04: Added source-pinned Knight Law Center western exterior study and wall recolor. See docs/knight-law-refinement.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned Clinical Services roof slope study with rebuild protection; see docs/clinical-roof-refinement.md.

- 2026-11-04: Added source-pinned Cascade Hall wall color study. See docs/cascade-wall-study.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned Miller Theatre Complex western study and wall recolor. See docs/miller-west-study.md for evidence and level-1 limits.

- 2026-11-04: Added source-pinned thin overlay collision for the Miller west facade, with footprint-adjacency and route safeguards. See docs/miller-west-study.md.

- 2026-11-04: Added editable Blender snapshot and verified single-mesh GLB for the nine pilot bench detail overlays; see docs/pilot-bench-editable-overlay.md for source and exclusions.
