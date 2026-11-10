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

- 2026-11-04: Added an illustrative source-pinned Ford Alumni Center north/east exterior study and route-screened collision; see docs/ford-alumni-study.md. Local only.

### 2026-11-04 — Science complex footprint screen (local only)

Added a reproducible 2D manifest-footprint screen and source-based Huestis and Global Scholars notes. Huestis overlaps the existing Willamette candidate by 746.09 m²; 13 of 63 named candidates have at least one screened overlap. These are candidates, not confirmed mesh collisions. Global Scholars is a rectangular placeholder while UO describes two enclosed courtyards. No building, interior, collision, maturity grade or deployed version changed. Reproduced the screen against the SHA-256-pinned manifest; see `docs/science-and-global-footprint-audit-2026-11-04.md`.

### 2026-11-04 — Bounded low-frame navigation candidate (local only)

The published browser regression trace and local approximately 1 FPS reproduction identified movement time discarded by the per-frame clamp. A local candidate bounds visible horizontal movement time to 0.25 seconds per frame, retains collision substeps, and calculates walking/running state from the movement timestep. The original 6 m / 15 s test is unchanged. The navigation, simulated slow-frame and mobile browser batch passed 8/8 after correcting an initial mobile state regression; 117 unit tests, build, formatting and viewer hashes passed. The underlying low renderer throughput remains unresolved; GitHub has not run the candidate. Details and limitations: `docs/github-browser-regression-2026-11-04.md`. Not pushed or deployed.

### 2026-11-04 — Generic road vehicle profiles (local only)

Refined the shared car, SUV and pickup bodies with sloped hood and rear profiles while retaining their established bounding boxes, placements and collision shapes. Van, bicycle and scooter geometry is unchanged. Regenerated and hash-pinned the standalone GLB; its six position arrays match the procedural source. All 117 pre-existing unit tests and a new focused profile test passed, as did five browser tests including the original draw-call limit, production build, formatting and the 106-record open-asset check. The prior GLB is retained. Blender was unavailable, so the previous editable snapshot predates this change and a new one remains outstanding. See `docs/vehicle-profile-2026-11-04.md`. PROP-02 remains level 1; no deployment.

### 2026-11-04 — Jaqua exterior (local only)

Added a source-pinned, selectable four-face glass-and-metal schematic overlay to the approximate Jaqua envelope, using one merged mesh and eight perimeter collision strips. Existing terrain, building source and interiors are unchanged. Two context views and the architect reference were reviewed; 119 unit tests, 14 preservation tests, build, 107 open-asset records and viewer hashes passed. The browser batch covers selection, render modes, navigation and the existing draw-call budget. Geometry, roof, pool and actual boundary are unverified; level remains 1. Blender was not found, so no new editable Blender snapshot is claimed. See `docs/jaqua-exterior-2026-11-04.md`. Not published.

### 2026-11-04 — Knight Campus 2 east face (local only)

Added a source-pinned east-side glass and fin overlay on the existing approximate Knight Campus 2 envelope, with one merged mesh and four narrow collision strips; selection and terrain remain. The existing 85 m envelope is shorter than the approximately 107.6 m length published by UO, and actual offset mass, other facades, roof, bridge and surroundings remain unresolved. Level stays 1. Source pins, route screening, 120 unit tests, 14 preservation tests, build, 108 open-asset records, browser selection/navigation and existing draw-call budget passed. Editable runtime JSON is preserved; no new Blender snapshot was produced. See `docs/knight-campus2-east-2026-11-04.md`. No deployment.

### 2026-11-04 — Lillis south entrance (local only)

Added a source-pinned, selectable schematic glass and light portal overlay to a sampled south wall of the approximate-nearest-roof Lillis candidate, with illustrative photovoltaic panels and one perimeter collision strip. Source photo is reference-only; no logo or third-party geometry is embedded. The campus source, surroundings and interiors remain unchanged. Seven modeled wall ray samples and matched before/after views were checked; 121 unit tests, 14 preservation tests, build, formatting, 109 open-asset records, source hashes and five browser selection/navigation/budget checks passed. Level remains 1; real boundaries, geometry and other elevations remain unverified. The editable runtime JSON has no new Blender snapshot. See `docs/lillis-south-2026-11-04.md`. Not published.

### 2026-11-04 — Student Recreation Center east face (local only)

Added a source-pinned, selectable schematic east glass facade on a sampled sloped wall of the approximate recreation-center candidate. Original geometry, terrain, plantings and interiors remain. A separate-mesh candidate reached 180 draw calls and failed the unchanged <180 limit; the final layer uses the existing checked source-mesh merge. Six browser tests including original positions/colors/normals, selection, navigation and draw budget, 122 unit tests, 14 preservation tests, build, formatting, 110 open-asset records and viewer hashes passed; the current 40-layer preservation was additionally checked as a metadata simulation. Actual footprint, glazing, entry and other elevations remain unverified; level stays 1. The rotated runtime JSON has no independent Blender/GLB snapshot, and the existing unrotated exporter cannot faithfully generate one. See `docs/rec-east-2026-11-04.md`. No deployment.

### 2026-11-04 — Rotation-aware facade exports (local only)

Added a reusable, source-pinned runtime-box overlay GLB exporter with baked XYZ rotations, input stability checks and exclusive output creation. Exported recreation-center, Jaqua, Knight Campus 2 and Lillis overlays to new standalone GLBs, retaining prior assets. All four on-disk files match runtime positions, normals, colors and identity transforms; a synthetic three-axis rotation and a side-by-side recreation image comparison passed. The originals and collision data are separate, and no per-object Blender snapshot was created. Asset levels and runtime are unchanged. See `docs/rotated-exterior-export-2026-11-04.md`. Not published.

### 2026-11-04 — Knight Campus 1 partial south facade (local only)

Added a source-pinned schematic folded-glass pattern to 61 m of the existing south envelope, stopping at least 4 m in model coordinates from the unresolved unnamed neighbor. The source mesh is preserved through the existing verified merge; no building, terrain, tree or interior moved. A standalone rotated-overlay GLB was independently checked against all 2,808 runtime vertices, normals, colors and transform. Nine browser checks, 123 unit tests, 14 preservation tests, build, formatting, 116 open-asset records and viewer hashes passed; 41 layers passed a metadata-only preservation simulation. Two-volume massing, bridge, actual boundaries and the remaining facade are unresolved, level stays 1, and no per-object Blender snapshot was produced. See `docs/knight-campus1-south-2026-11-04.md`. Not deployed.

### 2026-11-04 - HEDCO exterior (local only)

Added a source-pinned schematic brick and vertical-window treatment to two sides of the approximate HEDCO envelope, with merged detail and six route-screened collision strips. The rectangle, flat roof and window layout are not a faithful reconstruction of the actual courtyard complex; level remains 1. An overlay-only GLB matches all 6,984 runtime vertices, normals and colors; no new Blender snapshot was made. Original building, layout and interiors are preserved. See `docs/hedco-exterior-2026-11-04.md`. No deployment.

### 2026-11-04 - Bounded fern variation (local only)

Introduced deterministic, bounded variations in the existing reusable fern fronds across three existing clusters; placements, topology, source GLB and batch remain. An independent normalized fern GLB matches all 2,040 runtime positions and normals and records the source hash. Level remains 1; actual species and locations are unverified, and no new Blender snapshot was produced. Computing Center was deferred because its approximate footprint overlaps the Chiles candidate. See `docs/fern-variation-2026-11-04.md`. Not deployed.

### 2026-11-04 - Shared estimated entrance portal (local only)

Added a center stile and paired handles to the existing shared two-mesh entrance marker, affecting 534 inferred entries without changing locations, inference, interaction, collision or interiors. The extra 60 triangles per instance preserve the prior bounds; a local first-person view measured 190 draw calls, while the existing defined-camera budget test remains the acceptance check. The new two-mesh standalone GLB is source-pinned and omits placement; no Blender snapshot was created. PROP-04 remains level 1 and entries are not surveyed. Pacific Hall facade work was deferred pending reliable candidate registration. See `docs/shared-entrance-portal-2026-11-04.md`. Not deployed.

### 2026-11-04 - Entrance performance and cloud export (local only)

Same-camera testing found 190 draw calls both before and after portal refinement; the initial added 32,040 triangles were reduced to 6,408 by planar trim while retaining visual detail and two instanced meshes. The fixed-camera budget test remains unchanged. The optimized portal GLB was re-exported and the earlier version retained. A separate reusable cloud-mesh GLB now matches the existing runtime cloud geometry and controlled render; it omits dome, drift and camera following, and its fog/tone mapping defaults require consumer setup. No new Blender snapshots or maturity promotions. See `docs/entrance-performance-2026-11-04.md` and `docs/cloud-standalone-2026-11-04.md`. Not deployed.

### 2026-11-04 - Reference footprint screening and lamp overlay export (local only)

Screened 63 named project candidates against 664 public Oregon reference polygons, retaining only overlap metrics and identifiers. Pacific Hall official plan and state geometry suggest a possible merged or misassigned Lawrence/Pacific mesh; state records have duplicate building IDs and unavailable source dates, and no identity or geometry was changed. Added a bounded reusable box/column environment exporter and an independently checked GLB for 40 existing details on eight inferred lamps; it omits original lamps and does not change scene visuals. No Blender snapshot or maturity promotion. See `docs/oregon-footprint-screen-2026-11-04.md` and `docs/pilot-lamp-overlay-export-2026-11-04.md`. Not deployed.

### 2026-11-04 - Pilot paving treatment (local only)

Added a source-pinned, subtle world-space joint material to the existing authored pilot paving in both toon and PBR, without changing its geometry, paths, terrain, buildings or interiors. NAIP establishes broad dated hardscape context only; the grid is illustrative and ENV-05 remains level 1. The standalone GLB and existing Blender files do not include the runtime shader. Matched toon views showed 71 draw calls before and after; shader fragment cost is not a device benchmark. 127 Node tests, 17 Python tests, five browser checks, build, formatting and hashes passed; a metadata-only simulation preserved 42 detail layers and this patch. See `docs/pilot-paving-joints-2026-11-04.md`. Not deployed.

### 2026-11-04 - Unplaced bike-rack candidate (local only)

Added an original parameterized low-poly hoop rack and source-pinned standalone three-hoop GLB using published UO dimensions as context. UO map A27 indicates a covered facility near the approximate Tykeson envelope, but a nearby trial falls on the modeled lawn with existing shrub and building alignment uncertainties; no site geometry or rack placement was added. Source, scope and coordinate checks are recorded in `docs/bike-rack-candidate-2026-11-04.md`. 128 Node tests, 17 Python tests, four browser checks, build, formatting and asset/viewer hashes passed. PROP-01 remains level 1; no new Blender snapshot or deployment.


## 2026-11-04 — pilot lawn and bike rack screening

Local: added source-pinned illustrative pilot lawn tone in toon and PBR, with no geometry or navigation changes; ENV-05 remains level 1. Screened UO F50, F20 and A12 bike-parking points against the scene and left the rack unplaced due to modeled lawn/building conflicts. See docs/pilot-lawn-tone-2026-11-04.md for evidence, limitations and standalone-export gap.


## 2026-11-04 — campus lawn extension

Local: extended the source-pinned lawn tone to the existing vertex-colored campus lawn extension, preserving geometry and vertex colors. ENV-04 and ENV-05 remain level 1. Matched screenshots show 39 draw calls before and after; see docs/campus-lawn-extension-2026-11-04.md for source, validation and runtime-only export limitations. Not published.


## 2026-11-04 — context tree trunks

Local: source-pinned octagonal trunk geometry replaces the 300 inferred context-tree square trunks, preserving their positions, canopy and navigation. ENV-02 remains level 1. Same-view draw calls remain 39 and triangles rise by 1,200. See docs/context-tree-trunks-2026-11-04.md for checks, sources and runtime-only export limitation. Esslinger and Chiles remain unmodified pending boundary evidence. Not published.


## 2026-11-04 — Unthank west facade

Local: added a source-pinned, schematic Unthank west facade and standalone overlay, preserving the existing building envelope and interiors; level remains 1. Three west-wall collision strips were checked against route edges. Approximate footprint, Bean overlap, other faces and export limitations remain unresolved. See docs/unthank-west-2026-11-04.md for sources and validation. Not published.


## 2026-11-04 — arena north facade

Local: added an illustrative source-pinned north curtain wall and standalone overlay for the Matthew Knight Arena placeholder. Existing estimated entrance and modeled navigation remain intact; level remains 1. Actual curved form and other elevations remain unverified. Yasui south facade deferred due to overlapping model geometry and collision. See docs/arena-north-2026-11-04.md for sources and export limits. Not published.

Verification: revised entrance comparison passed after correcting the initial 2 cm shift; 132 JavaScript and 19 Python tests, 13 browser tests, build, format and 136 asset hashes passed. Metadata-only preservation carried 44 detail layers; no full Blender rebuild. Local only.

Final v3: separated coincident entrance-facing surfaces after visual review; strict entrance comparison and 13 browser tests passed. Rechecked 132 JavaScript tests, build, formatting, viewer hashes and 137 assets; metadata-only preservation retained 44 layers. Local only.


## 2026-11-04 — context tree export and Hayward screening

Local: exported the existing 300 refined context trees to a single source-pinned standalone GLB and verified geometry plus an independent rendered view. ENV-02 remains level 1; per-tree Blender source remains unavailable. A Hayward roof candidate was isolated after the existing solid west-stand placeholder produced a misleading warehouse-like result; no Hayward scene change. See docs/context-trees-standalone-2026-11-04.md and docs/hayward-west-screen-2026-11-04.md. Not published.

Validation: 132 JavaScript tests, 19 Python tests, five browser checks, build, formatting, viewer hashes and 139 asset records passed. A metadata-only preservation simulation retained 44 layers and excluded the isolated Hayward study. No full Blender rebuild; local only.


## 2026-11-04 — shared planting material

Local: fixed 40 inferred pilot shrubs rendering black because canopy tone changed a material shared with a mesh lacking vertex colors. Canopy materials are cloned before enabling their vertex colors; shrub geometry and canopy values remain unchanged. ENV-03 remains level 1. See docs/planting-shared-material-fix-2026-11-04.md for evidence and export implications. Not published.

Verification: 133 JavaScript tests including shared-material isolation, 19 Python tests, six browser tests, build, formatting, viewer hashes and 139 archived assets passed. Metadata-only preservation carried 44 layers; no full Blender rebuild. Local only.


## 2026-11-04 — bounded pilot shrubs

Local: added source-pinned bounded variation to 40 existing inferred pilot shrubs across two groups, with no expanded bounds, relocated plants or canopy changes. Exported a verified one-mesh standalone PBR GLB; ENV-03 remains level 1. See docs/pilot-shrub-variation-2026-11-04.md for sources, two view comparisons and Blender/export limitations. Not published.

Validation: 133 JavaScript tests, 20 Python tests, seven browser tests, build, formatting, viewer hashes and 141 asset records passed. Metadata-only preservation carried the shrub layer and 44 exterior layers; no full Blender rebuild or hardware benchmark. Local only.

## 2026-11-04 - isolated understory candidate

Investigated 71 existing low shrub groups; an earlier fern-named patch suppresses three additional shrubs. A bounded 64-group variation was prototyped but its foreground silhouette exposed sharp underlying foliage, so it was isolated and not integrated. See local-only research notes and before/after screenshots. Inventory remains level 1; no standalone export. Local only.
Validation after isolation: build, two existing browser tests, 20 Python tests, viewer override hashes and 141 archived assets passed. The Vite build reports its existing large-chunk warning.

## 2026-11-04 - complete pilot bench export

Local: combined existing original supports and refined wooden details for nine inferred pilot benches in a standalone GLB; runtime and campus positions remain unchanged and PROP-01 stays level 1. The export is a two-mesh campus-coordinate collection, not nine separately editable benches. Cedar/Yasui overlap remains unresolved; no facade change. Sources, comparison, provenance and limitations: docs/pilot-benches-complete-2026-11-04.md. Not published.

Validation: 133 JavaScript and 20 Python tests, five targeted browser checks, build, formatting, viewer hashes, 142 asset records and 1,081-row inventory passed. No full rebuild, Blender snapshot or hardware benchmark; existing build chunk warning remains.

## 2026-11-04 - provisional Alder north facade

Local: added a source-pinned illustrative 42-box north facade and porch to the unnamed roof-ee63827c candidate near Alder Building; its identity remains provisional and level 1. An unmerged version exceeded the existing fixed-view draw budget; a validated static batch merge retains 179 calls and source/selection semantics at the tested points. No interior change or publication. Sources, visual comparisons, collision/entrance tests and standalone overlay limitations: docs/alder-north-provisional-2026-11-04.md.

Validation: 134 JavaScript tests, 20 Python tests, three browser tests, build and metadata-only preservation of 45 layers passed; no full Blender rebuild or hardware benchmark.
Additional checks: formatting, viewer hashes, 144 archived asset records and the 1,081-row inventory passed.

## 2026-11-04 - University–Villard shrub batching

Local: merged two compatible, source-pinned non-selectable shrub layers without changing building meshes, layout or materials. At 1440 × 1000 the same fixed initial overview fell from 179 to 178 draw calls, with identical triangles; seven comparison images matched pixel-for-pixel. At two closer views coarser culling drew 640/320 extra triangles, with unchanged pixels. All 534 entrance records and both building search selections were retained; levels unchanged. Evidence and limitations: docs/shrub-batching-performance-2026-11-04.md. Not published.

Validation: 135 JavaScript tests, 20 Python tests, three browser checks and build passed; no hardware frame-time test or full rebuild.

## 2026-11-04 - isolated Agate facade study

After shrub batching passed, screened a potential Agate Hall west facade against UO's survey, dated photograph and archived NAIP. The unnamed roof-b068940e identity remains provisional. A candidate retained numerical entrance state but concealed its green entrance marker in the matched campus view, so it remains isolated and is not loaded; no level, collision or campus geometry changed. The first version exceeded the existing batch-bound guard; that guard was not changed. Details and before/after evidence: docs/agate-west-candidate-2026-11-04.md. Local only.
Additional checks after the isolated Agate screen: format, viewer hashes, 145 archived asset records, 1,081 inventory rows and all seven comparison-image hashes passed.
Follow-up: a visible University PBR comparison also matched exactly (eight A/B pairs total), and actual pointer clicks selected University and Villard in both batched and unbatched scenes.

## 2026-11-04 - Agate west provisional refinement

Correction: the earlier claim that the Agate v1 candidate hid the entrance marker was a visual-review error; the original entrance crops match and rays found the marker in front. The v1 study remains isolated. Adopted a second source-pinned 77-box west overlay that fills its tan entry seam, preserving the original estimated marker and provisional unnamed identity; level remains 1. Integrated into the existing three-building static batch, with original geometry and export verified. Source, image/ray evidence, navigation and limitations: docs/agate-west-provisional-2026-11-04.md. Local only; no interiors changed or publication.

Validation: 136 JavaScript, 20 Python, four browser tests, build and metadata-only preservation of 46 layers passed; fixed overview remained 178 calls under the unchanged limit. No hardware benchmark or full Blender rebuild.
Additional verification: formatting, viewer hashes, 147 archived asset records, 1,081 inventory rows, six image hashes and five recorded entrance rays passed.

## 2026-11-04 — provisional Longhouse-area exterior

- Added a source-pinned 23-box south frontage and bounded palette to the unidentified `roof-f736712f` candidate near Many Nations Longhouse. The UO references, approximate location, visual before/after and unresolved identity/roof/entry limitations are documented in `docs/longhouse-south-provisional-2026-11-04.md`. The asset remains unidentified, level 1; interiors and placement are unchanged.
- Palette checks match 92 of 20,148 source vertices before modifying colors; source GLB remains untouched and 22 batch identities stay intact. The editable JSON and original-source pins are recorded; standalone 828-vertex overlay GLB round-trips positions, normals and colors with zero error and excludes the base and palette. No Blender snapshot was generated.
- Validated 138 JavaScript and 21 Python tests, production build, formatting, 150 archived asset hashes, viewer override hashes, 1,081 inventory rows, real-GLB geometry/merge check, entry picking/navigation, Agate and vegetation selection regressions. Matched three-view calls were 44/167/17 before and after; original overview budget test passed at 178 (<180). 534 entrance records were unchanged. An earlier temporary test failed to initialize after injecting the already-integrated overlay twice; it was corrected to test the actual scene without changing the limit. No device benchmark or full Blender rebuild was run. Local only; not published.

## 2026-11-04 — Lokey Education candidate wall color

- Applied an illustrative source-pinned brick tone to 120 vertical wall vertices of approximate `roof-74ecc113` only, using the existing wall-patch pipeline. UO education-complex material context, a 2013 reference photograph, matched views, approximate identity and incomplete roof/entrance/source-export limitations are recorded in `docs/lokey-wall-color-2026-11-04.md`. The candidate remains level 1. Original GLB, campus layout and interiors remain unchanged; no Blender snapshot or baked standalone export was created.
- Real-GLB browser validation confirmed all other positions, normals, indices, material and object identity unchanged; a wrong expected count was rejected. Building selection, estimated entry and all 534 entrance records matched before/after. Four matched views remained 28/89/23/67 draw calls; the existing overview test passed at 178 (<180). 138 JS and 21 Python tests, three browser tests, production build, formatting, viewer hashes and 151 source/model hashes passed. No hardware benchmark or full Blender rebuild. Local only, not published.

## 2026-11-04 — van profile and Onyx Bridge candidate screen

- Added a generic sloped hood to the existing procedural van; placement, collision, routing and visible envelope are unchanged. Regenerated the six-kind prop GLB and retained the preceding version; `docs/van-profile-2026-11-04.md` records the neutral comparison, UO context and the missing current Blender snapshot. PROP-02 remains level 1.
- The UO historic survey describes Onyx Bridge as four stories with exterior trusses, while its approximate nearest-roof candidate is 166 m² and 4.14 m high. Recorded the identity/scale uncertainty and nearby candidate distances in `docs/onyx-candidate-screen-2026-11-04.md`; no truss, geometry, identity or collision was changed.
- 139 JS tests, 21 Python tests, seven targeted browser tests, production build, formatting, viewer override hashes and 152 archived asset hashes passed. All six exported prop positions match the procedural generator; five unchanged prop types retain their former positions, normals, colors and transforms. The van has 2,196 vertices versus 2,184 before. The fixed overview stayed 178 draw calls (<180); no hardware frame-time or campus-context van visual assessment was performed. No new Blender snapshot or deployment; all work remains local.

## 2026-11-04 — context tree trunk variation

- Added a source-pinned second pass for 300 existing inferred context-tree trunks: upper radius 78% of the existing base and stable bark-color factors within ±6%. It leaves canopy attributes and indices, tree centers/heights, terrain, layout and interiors unchanged. Reference context, limitations and before/after/PBR views are in `docs/context-trunk-variation-2026-11-04.md`; ENV-02 remains level 1.
- Added a non-overwriting standalone 300-tree GLB with position/normal/color round-trip error zero and exact indices. The previous standalone GLB remains unchanged and its original browser test still passes. Neither export is a per-tree Blender scene; no new Blender snapshot was created. Metadata-only preservation verifies the new layer and its dependency on the original trunks.
- 139 JS, 22 Python and six targeted browser tests passed, including unchanged canopy preservation, both old and new exports, selection and the original <180 fixed overview (178). Matched close views stayed 39 draws and 749,989 triangles; PBR was reviewed. Build, formatting, 154 asset hashes, viewer hashes and 1,081 inventory rows passed. No full rebuild or hardware performance/peak-memory benchmark. Changes remain local and unpublished.

## 2026-11-04 — EMU circular paving

- Added an optional, bounded circular staggered-joint treatment to the existing pilot paving shader at the EMU forecourt. The archived 2017 CC0 photo and 2024 public-domain NAIP cue inform its broad character and approximate location; individual stone layout, dimensions, stairs and current conditions remain unverified. `docs/emu-radial-paving-2026-11-04.md` records the evidence and matched toon/PBR views. ENV-05 remains level 1; no geometry, campus layout or interior was changed.
- 141 JS, 22 Python and six browser tests passed, including all 534 entrance records, modeled collision, unrelated-pixel and navigation checks. The matched close view stayed 71 draws / 819,257 triangles; the fixed overview stayed 178 (<180). Build, formatting, 155 archived asset hashes, viewer hashes, 1,081 inventory rows and metadata-only preservation passed. The runtime shader is absent from standalone GLB and Blender files; no new baked export, Blender snapshot, full rebuild or device benchmark. Local only, not published.
- Screened a separate far-north landcover correction against the archived aerial; the isolated 792-vertex candidate had minimal in-scene visibility under existing spatial haze, so it was not integrated or exported.

## 2026-11-04 — rounded cloud volumes

- Replaced 90 existing cloud lobes in the runtime with low-poly rounded volumes while preserving each lobe's horizontal center/base and existing 18-cluster motion, palette and material. The NWS context, matched campus and PBR views, limitations and reproducible export are documented in `docs/rounded-cloud-volumes-2026-11-04.md`; ENV-07 remains level 1. The original sky generator and old standalone cloud export remain unchanged.
- Added a separate 27,000-vertex cloud GLB; reimported positions, normals and colors have zero error. It excludes the sky dome and animation, and no new Blender snapshot was made. Two matched campus views held draws at 71 and 70 and each reduced triangles by 18,000. The fixed overview remained 178 draws (<180); no device frame-time or peak-memory benchmark was run.
- 143 JS, 22 Python and seven browser tests passed, including old/new export, reduced motion, navigation and existing budget; build, formatting, viewer hashes, 156 archived asset checks and 1,081 inventory rows passed. Existing build chunk warning remains. Local only; not published.
- Screened Frohnmayer against the UO guide and 2024 aerial: the named 505 m² roof candidate appears to cover only part of a multi-wing complex. `docs/frohnmayer-candidate-screen-2026-11-04.md` records the limitation; no building geometry, identity, collision or interior was changed.

## 2026-11-04 - individual pilot bench export

- Added `assets/exterior-refinement/pilot-benches-individual-2026-11-04.glb`: nine separately pivoted groups with original metal supports and wood. Source-pinned export and 18-mesh world-space roundtrip checks preserve the prior combined export, which remains available. `docs/pilot-benches-individual-2026-11-04.md` records the source, matched comparison, limits and reproduction. PROP-01 stays level 1; no runtime visual or campus layout change. No new Blender snapshot; individual wood components remain merged.
- Screened UO map bike-parking area A20: 25 sample points on the approximate scene area hit modeled lawn, so the generic rack was not placed; map coordinates, uncertainty and remaining evidence needs are documented. No field inventory claimed.
- 143 JavaScript tests, production build and two focused browser tests passed; geometry comparison was exact, while the screenshot comparison permits small raster differences (max channel 44). Existing build chunk warning remains. Local only, not published.

## 2026-11-04 - landscape reference screen

- Recorded primary UO references for Gerlinger Field Green and Science Walk in `docs/landscape-reference-screen-2026-11-04.md`. Their broad historic descriptions support future investigation, but do not establish individual modeled tree positions or a registered, licensed artwork layout. Existing science-building overlap issues remain open. No asset, runtime, inventory level or publication changed, and no new runtime test was required for this documentation-only screen.

## 2026-11-04 - grass-detail candidate screen and inventory reconciliation

- Tested a world-space near-camera grass-fleck shader on the two existing lawn meshes. Two targeted browser checks passed, including the unchanged fixed-view draw budget and toon/PBR shader load, but the visual result resembled repetitive ground marks rather than convincing grass. The candidate was rejected, the previous `src/lawn-tone.js` restored, and the temporary candidate code and screenshot retained in the task workspace outside the project. No runtime appearance, geometry or performance threshold was changed by this screen.
- Reconciled PROP-01 in `docs/asset-refinement-inventory.csv` with the previously completed nine individual bench groups and remaining component/Blender limitations; it remains level 1. CSV parsed as 1,081 rows and 143 JavaScript tests passed after restoring the runtime. Local only, not published.

## 2026-11-04 - squirrel eye details

- Added two small eye accents to the existing generic squirrel, merged into its shared mesh without changing the source body, actor counts, paths, collision, buildings or interiors. No species claim; LIFE-01 remains level 1. OSU regional context, CC0 source and licensing, three-angle views, guarded generator and limitations are in `docs/squirrel-eyes-2026-11-04.md`.
- Exported a separate source-pinned GLB with exact position/normal/color reimport checks; original source GLB and Blender snapshot are retained, and no new Blender snapshot was made. Adds 160 triangles per visible squirrel; one mesh per actor remains. No hardware frame-time benchmark was run.
- 143 JS tests, build, formatter and two targeted browser checks passed, including unchanged fixed-view draw budget and eight default squirrels; the squirrel test and build were repeated after the final source guard. Inventory parsed at 1,081 rows. Existing chunk warning remains. Local only, not published.

## 2026-11-04 - University Hall dormers and eaves

- Refined University Hall's existing full exterior with linked-photo-informed dormer pediments and side frames, continuous main and tower eaves and stylized brackets on all four sides. Preserved the prior source specification, layout, original 210 objects, interior and existing vegetation. Source, four campus views, isolated before/after and unverified details are in `docs/university-hall-refinement.md`. University Hall remains level 1 pending stronger whole-building evidence and review against Knight; no invented level standard.
- Added an independent full replacement GLB with four prior illustrative shrubs; exact exported position/normal/color checks passed. Original campus GLB and Blender snapshots are unchanged; no new Blender snapshot or editable individual component hierarchy. At isolated view two draw calls stayed unchanged and triangles rose 10,004 to 12,420. Two campus before/after draw counts matched; no hardware frame-time measurement.
- 143 JS, 22 Python and three affected browser tests passed; the campus comparison was repeated after adjusting cameras. Original fixed-view <180 budget, selection, render modes, 534 entrance records and two sampled collision checks passed; production build and formatter passed. Initial test discovery path and initial formatting check failed, then corrected and passed. Existing chunk warning remains. Inventory remains 1,081 rows. Local only, not published.

## 2026-11-04 - Villard exterior eaves and tower crest

- Refined Villard's existing east oculus surrounds, east/north/south cornice brackets, entry balcony side returns and four tower-cap crests, using the archived CC0 photograph and UO survey as references. The original 206 specification objects, campus layout, shrubs, collision and interior are unchanged. The central-roof railing candidate was rejected as visually misaligned; the west/theater junction and other historic details remain uncertain. See `docs/villard-east-refinement.md` for source, matching views and limits. Villard remains level 1.
- Added a source-pinned standalone full-exterior GLB with the eight prior illustrative shrubs; position, normal and color reimport errors were zero. Original campus GLB and Blender sources are unchanged; no new Blender snapshot, collision or individually editable component hierarchy. Isolated draw calls stayed 2 and triangles rose from 6,948 to 9,780; two campus comparisons held draw counts. No hardware frame-time benchmark.
- 143 JS, 22 Python and three browser tests passed, including selection, both render modes, existing fixed-view <180 budget, 534 entrance records and two sampled collision checks. Build and formatter passed; existing large-chunk warning remains. Inventory remains 1,081 rows. Local only, unpublished.

## 2026-11-04 - Johnson Hall shallow roof and cornices

- Added a source-informed shallow light hipped roof above Johnson's existing flat roof and continuous rear/side cornice brackets. Three original roof markers are covered and represented by simplified copies at the same horizontal coordinates on the new roof; their identities are unverified. Prior rear layer, front portico/frieze, building ID, vegetation, interior and layout are retained. UO survey, 2024 public-domain aerial, 2012 CC BY 4.0 photograph, matched views and outstanding gable-on-hip accuracy are documented in `docs/johnson-rear-refinement.md`. Johnson remains level 1.
- Exported a source-pinned roof/rear overlay GLB including prior illustrative shrubs, but not the source building, front lettering, navigation or collision; position/normal/color reimport errors zero. No new Blender snapshot. Isolated combined source and overlay kept 13 draws while triangles rose from 8,480 to 9,660; two campus views had matching before/after draw counts. No hardware benchmark.
- 143 JS, 22 Python and two browser tests passed; the original fixed-view <180 budget, selection, 534 entrance records and two sampled collision checks passed. Build and format passed; existing chunk warning remains. Inventory remains 1,081 rows. A Friendly gable candidate was retained outside the project because it visibly conflicted with existing dormers; Friendly runtime unchanged. Local only, not published.

## 2026-11-04 - Johnson Hall gable-on-hip correction

- Replaced the prior truncated hipped roof with a shallow central-ridge roof and hipped ends, following the UO historic survey's gable-on-hip description and 2024 aerial context. The outer two illustrative existing roof markers were tilted and lowered to contact the new roof; horizontal centers, the rest of the prior exterior, vegetation, collision and interior remain. `docs/johnson-rear-refinement.md` records reference, matched views and unverified details. Johnson remains level 1.
- Added reusable `gable-hip` construction with dimensional guard and a surface-ray test of the ridge, slopes and marker contact. The former specification and generator are preserved; a new source-pinned overlay GLB passed exact position/normal/color roundtrip. Original base GLB, prior overlay and Blender snapshots remain; no new Blender snapshot or full building/collision in the overlay. Isolated draws stayed 13, triangles 9,660 to 9,652; two campus views retained draw counts. No hardware frame-time benchmark.
- 144 JS, 22 Python and two browser tests passed; selection, entrance records, sampled collision and existing <180 fixed-view budget passed, as did build and format. The initial marker test expected a 0.10 m gap instead of the existing 0.12 m support thickness; corrected and passed. Existing chunk warning remains, inventory 1,081 rows. Local only, unpublished.

### 2026-11-04 — Collier north upper bay study (local)

Used a linked UO photograph to add paired tapered upper bays and a schematic balcony railing to Collier House; preserved its anchor, collision specification and interiors. The prior spec and generator are retained, the standalone GLB round-trips positions/normals/colors, and the building remains level 1 because the lower bays, porch roof relationship and current dimensions require verification. Matched campus north/east views retained 60/93 draw calls; selection, entrance, collision probes and existing toon/PBR budget browser tests passed, as did 145 JS tests and the production build. See `docs/collier-house-refinement.md` for sources, images and limitations. Friendly roof/dormer candidate remains isolated after visual review. Local only; not published.

### 2026-11-04 — Collier lower bays and central porch (local)

Added the photographed lower bay forms aligned with the existing upper bays, narrowed the illustrative porch to the central span and removed conflicting outer porch pieces; original anchor, interiors and conservative collision rectangles remain. Level 1 remains because proportions, porch structure and current conditions are unverified. Three matched views retained 60/60/93 draw calls; selection, entrance, collision probes, existing toon/PBR budget, 146 JS tests and production build passed. The standalone GLB round-trip retained positions, normals and colors; no new Blender snapshot. See `docs/collier-house-refinement.md` for references, comparison and limitations. Local only; not published.

### 2026-11-04 — University Hall tower study (local)

Used cited UO records and a licensed historical photo to replace each end tower's single schematic arch with three narrower arches and add simplified roof cresting. Existing building anchor, entrances, surroundings, collision and interiors remain; the prior specification is retained. The building remains level 1: mansard form, chimneys, proportions, access and present condition require further evidence. Three campus views retained 80/36/26 draw calls; selection, entrance records, collision probes, existing toon/PBR budget, 147 JS tests and production build passed. The generated GLB reimport matched positions, normals and colors, but is not an updated Blender snapshot. See `docs/university-hall-refinement.md`. Local only; not published.

### 2026-11-04 — University Hall mansard study (local)

Replaced three constant-slope roof approximations with reusable two-slope mansard forms and adjusted the four tower dormer pairs to remain attached and visible. An early candidate accidentally touched entrance objects; these were restored and a per-object regression verifies the final scope. Building anchor, entry, surrounding scene, interiors and collision are preserved. The unmeasured slopes, dormers, chimneys and current conditions remain uncertain; the building remains level 1. Four matched views retained 80/36/26/121 draws; roof/dormer geometric tests, selection, entrance records, collision probes, existing toon/PBR budget, 149 JS tests and production build passed. GLB positions/normals/colors round-tripped; no updated Blender snapshot. See `docs/university-hall-refinement.md`. Local only, unpublished.

### 2026-11-04 — Friendly flared-roof study deferred (local)

Compared a flared-gable and 17 extended dormer caps with the current Friendly replacement. The UO 2025 survey and preliminary assessment describe the roof using different terminology, and the extended candidate presents chunky far-side silhouettes in elevated views. Preserved the candidate, generator and images for review; restored the original runtime generator and left the pinned Friendly layer and level 1 unchanged. West/south screening views matched 77/34 draws, while the east view was obstructed and the north camera fell back, so those are not a complete campus verification. See `docs/friendly-west-refinement.md` for sources and exact limitations. No export or publication.

### 2026-11-04 — Villard roof profile study (local)

Used the cited UO survey and elevation context to replace five constant-slope roof profiles with the existing reusable two-slope approximation. Their bounds, all other components, collision, entrance, vegetation and interiors remain unchanged; the prior specification is retained. The west/theater junction, roof curvature, exact dimensions and current condition are unverified, so the building remains level 1. Matched east/north/south views retained 27/133/21 draws; the attempted west camera fell back and is not a valid visual check. Five-roof geometry, selection, entrances, collision probes, existing toon/PBR budget, 150 JS tests and production build passed. The generated GLB reimport matched positions/normals/colors, but is not an updated Blender snapshot. See `docs/villard-east-refinement.md`; local only, unpublished.

### 2026-11-04 — Villard west camera and junction screen (local)

Identified the old west camera coordinate as blocked by the theater collision, causing the existing return fallback. Established four reproducible first-person views from collision-free positions and added a browser regression for blocked/valid coordinates. The model shows a gap where UO's 2025 survey identifies an attachment; the 2017 proposed connection is not sufficient as-built evidence after renovation. Preserved geometry, collision and level 1 pending current imagery or measured plans. See `docs/villard-east-refinement.md`; local only, unpublished.

Chapman north entry was also screened using the 2016 assessment and a collision-free local view; foreground geometry obstructs that view and a measured entry-to-model mapping remains unresolved. No Chapman geometry changed. See `docs/chapman-west-refinement.md`.

### 2026-11-04 — Susan Campbell brick parapet study (local)

Used UO's survey and a licensed 2011 photograph to add two illustrative brick parapet volumes to the long roof elevation and reposition the associated existing window frames. Roof intersection and glass visibility are tested; unrelated objects, anchor, collision and interiors remain unchanged. The prior specification is retained. Position, proportions, orientation, courtyard entry and current conditions remain unverified, so level stays 1. Three software-rendered views retained 87/58/45 draws with partial occlusion; selection, entrances, collision probes, existing toon/PBR budget, 151 JS tests and production build passed. The building-only standalone GLB reimport matched positions/normals/colors, not a Blender snapshot. See `docs/susan-campbell-refinement.md`; local only, unpublished.

### 2026-11-04 — Exterior provenance pin reconciliation (local)

Reconciled stale downstream hashes for five locally refined building specifications and the exterior generator after matching each old building hash to its preserved prior snapshot and checking the current presentation/base pins. Retained prior source records and registered the checked snapshots and latest GLBs; no scene geometry changed. All 101 tracked viewer outputs and 169 archived asset files now match their recorded hashes; 22 Python tests passed, and the preservation function validated 47 current exterior layers with source tree count 600. The first direct probe omitted rebuilt statistics and correctly failed input validation; the corrected probe passed. See `docs/exterior-source-pin-reconciliation-2026-11-04.md`. Local only, unpublished.

### 2026-11-04 — Susan courtyard entry study (local)

Using the UO survey's courtyard photograph and an approximate scene mapping, added a stylized door/porch at the inner elevation and two small conservative post collision boxes; removed the conflicting schematic window. The exact position, orientation and accessibility are not verified. The existing separately estimated south-side interaction marker remains unchanged and the new door is not an interactive entrance; level remains 1. No existing navigation edges intersect the two new boxes at 0.5 m margin. Three software-rendered views retained 47/47/88 draws; geometry, post collision, selection, entrance records, existing toon/PBR budget, 152 JS tests and build passed. The building-only GLB reimport matched positions/normals/colors; no new Blender snapshot. See `docs/susan-campbell-refinement.md`. Local only, unpublished.

### 2026-11-04 — Fenton entrance and balustrade connection (local)

Used the UO survey and state masonry assessment to distinguish the decorative arch from Fenton's rectangular east door and connect the previously floating balustrade to the entry cornice. Existing footprint, vegetation, collision and interiors are unchanged. The source's steps were not modeled because the current terrain/threshold relationship requires verification; massing, exact dimensions, access and current condition remain uncertain, so level stays 1. Matched east/oblique/south software-rendered views retained 54/77/36 draws; geometry, selection, entrance records, collision samples, original toon/PBR budget, 153 JS tests and production build passed. The overlay-only GLB reimport matched positions/normals/colors and is not a new Blender snapshot. Source/output pins and prior records were updated; see `docs/fenton-south-refinement.md`. Local only, unpublished.

## 2026-11-04 — Straub west roof and attic study

Added an estimated west-wing gable and light attic band to the existing source-pinned Straub overlay based on the linked UO survey, preserving the original building, existing overlay geometry and collision data. Three ground views and an aerial view were inspected; west/northwest browser comparisons retained selection, entrance data, sampled collision and draw counts. The existing lawn performance-budget test passed. A standalone additive GLB was exported and its position, normal and color attributes matched on reimport. Source and export are registered with hashes and the earlier specification is retained. Exact roof geometry and rear junctions remain unverified; level stays 1. See `docs/straub-west-refinement.md`. No publication.

## 2026-11-04 — Fenton east elevation candidate deferred

Compared the two-storey east elevation described by the linked UO survey with the current three-row estimated massing. A source-isolated two-storey facade candidate leaves original windows and eave discontinuities exposed, so it was not integrated. Two browser views retained 54 and 77 draw calls; this is a visual screen rather than a full navigation or performance validation. See `docs/fenton-south-refinement.md`; runtime assets and level remain unchanged. Local only, unpublished.

## 2026-11-04 — Fenton source filter and Anstett orientation review

Screened an isolated Fenton mesh filter: 144 indexed triangles were removed in memory and two campus views retained 54/77 draws; the candidate still has incomplete end faces and lacks the guards and interaction checks needed for integration, so the runtime is unchanged. Also recorded a discrepancy between the UO survey's west-facing Anstett entry description and the current south-plane overlay; neither placement was changed. See the respective refinement records. No new GLB or Blender snapshot; local only, unpublished.

## 2026-11-04 — Guarded Fenton east-window correction

Integrated the source-pinned Fenton east-window correction after validating all 144 removed window triangles and their 288 source vertex signatures. A cloned runtime mesh preserves all remaining indices, original GLB and identity; mismatched source hash, geometry or target rejects without mutation. The original eave, entrance and collision remain; angled corner windows and actual proportions still need verification, so Fenton remains level 1. Before/after browser checks preserved selection, entrance data, sampled collision and draw counts; the existing draw budget and walking navigation regression passed. Build, 156 JS tests, 23 Python tests and formatting checks passed. The additive overlay export roundtripped attributes but does not include the base mesh or source filter; no new Blender snapshot. See `docs/fenton-south-refinement.md`. Local only, unpublished.

## 2026-11-04 — Fenton corner lower windows and load check

Replaced the oversized lowest generic windows on two existing angled corner faces with smaller, source-informed windows, extending the source-verified filter from 144 to 168 triangles. Prior source specification, upper windows, roof, building identity, original GLB and collision remain. Three camera-verified before/after views, source tamper, draw budget and walking-navigation regressions passed, along with 157 JS tests, 23 Python tests, build and formatting. The current roof boundary remains too uncertain to alter safely. Six in-browser SHA-256 samples for the 34.8 MB GLB were 22.0–23.4 ms; limited scene-ready comparisons do not isolate total load overhead. The roundtripped additive GLB excludes the base and triangle filter, and no Blender snapshot was created. Fenton remains level 1; see `docs/fenton-south-refinement.md`. Local only, unpublished.

## 2026-11-04 — University Hall entry stairs

Using the linked UO historic assessment, connected the existing east and west entry steps to stylized solid concrete wing walls and central handrails. A first floating-wall candidate was corrected after oblique visual review; a reusable wedge primitive produces the adopted walls. Earlier model components, roof, building anchor, collision, navigation and interior remain. Three camera-verified before/after views retained selection, entrances, sampled collision and draw calls; the existing performance budget and walking navigation regression passed. 158 JS tests, 23 Python tests, build and formatter passed. The roundtripped standalone replacement excludes terrain, navigation and collision, and no new Blender snapshot was made. Dimensions and access remain unverified, so level remains 1. See `docs/university-hall-refinement.md`. Local only, unpublished.

## 2026-11-04 — University Hall stair collision

Added six restricted full-height 2D collision boxes for the two modeled stair wings and center rails, with the previous specification retained. Both side lanes remained traversable in 0.42 m-radius simulation; no existing navigation edge intersects the boxes with a 0.5 m margin. Before/after browser checks preserved all entrance records and the 38-point Johnson-to-University route; the existing walking regression passed. Actual stair access, vertical movement and accessibility remain unverified. The standalone GLB does not include collision. Level remains 1. See `docs/university-hall-refinement.md`. Local only, unpublished.

## 2026-11-04 — Tykeson upper frontage

Reworked the existing source-pinned Tykeson front overlay to a two-row upper cladding and adjusted glazing, referencing the attributed historical image and design architect project. The existing entrance canopy, planting, base blockout, roof, collision, campus placement and interior remain. Three camera-verified views retained 68/69/98 draws and an aerial candidate retained 82; selection, entrance, sampled collision, toon/PBR and original performance-budget checks passed. The roundtripped additive overlay excludes base, terrain, navigation and collision; no new Blender snapshot. The three actual building volumes and other elevations are still absent or unverified; level remains 1. 160 JS tests, 23 Python tests and build passed. See `docs/tykeson-north-refinement.md`. Local only, unpublished.

## 2026-11-04 — Gerlinger east portico

Added a stylized columned entry surround to Gerlinger Hall's previously mapped east facade, informed by the linked UO assessment and attributed historical photo. The original layer, door, upper windows, planting, roof, base GLB and interiors remain; the curved entry arch and actual grade require more work. Three verified camera views retained selection, entrance data, sampled collision and 62/43/101 draws; the south view is obstructed. Geometry tests keep the door visible and the lintel below the upper window. The existing toon/PBR draw budget passed. The additive GLB roundtripped attributes but excludes the source building, terrain and collision; no Blender snapshot. Entry columns are visual only, with no access guarantee. Level remains 1; see `docs/gerlinger-east-refinement.md`. Local pending publication review.

## 2026-11-04 - Lamp overlay generator pin refresh

Re-exported the existing additive lamp overlay after the shared generator changed, retained the old file, and verified 3,840 positions, normals and colors plus scene merge and material consistency. No runtime geometry changed; PROP-01 remains level 1. See `docs/pilot-lamp-overlay-export-2026-11-04.md`.

## 2026-11-04 - Johnson rear upper window and band

Added a source-informed approximate upper window, awning and horizontal band to the existing rear layer. Two views retained 56/71 draws, selection, entrances and sampled collision; the new additive GLB roundtripped positions, normals and colors. Prior source is retained; no interior or collision changed. Dimensions and present condition remain unverified, so level remains 1. See `docs/johnson-rear-refinement.md`. Local only; publication paused.

## 2026-11-04 - Fixed person prototype (local)

Added a source-attributed, stylized named-person prototype near Deschutes with a bounded, collision-screened walk, endpoint pauses, minimap marker, lightweight interactive label, proximity text and linked accessible profile card. Reuses the rigged base with procedural plaid and accessories; the user-provided line is fictional game text and appearance dimensions are not verified. See `docs/fixed-person-dan-carrere.md` and review image. Local only; publication paused pending user review.

## 2026-11-04 - Fixed person building occlusion (local)

Added throttled two-point building occlusion for person labels and bubbles without changing the reviewed character. Real-scene desktop/touch blocked and clear views, card interaction, path, 178-draw budget and low-frame-rate regression passed; partial occlusion is approximated and trees are not checked. See `docs/fixed-person-dan-carrere.md`. Local only; bubble reference and publication remain pending.

## 2026-11-04 - Fixed person speech bubble reference

Adjusted the dialogue bubble to the user-provided rounded white reference, with an inset shadow and a lower-left tail pointing toward the character; positioned it above-right without overlapping the name. The reference was visually checked in the parent thread and is not redistributed. The reviewed person appearance is unchanged. See `docs/fixed-person-dan-carrere.md`; publication validation pending.

## 2026-11-04 - Six-view test fixture efficiency

CI-mode full browser regression produced 168 passes and three 90-second timeouts in Gerlinger, Tykeson and University Hall six-view comparisons; the original isolated retest reproduced two timeouts. Reused one browser context per comparison with a new page per version and explicit local storage and cookie cleanup, retaining every original camera, screenshot, assertion and 90-second limit. All three passed in an isolated CI-mode retest. Failure artifacts remain in the local task workspace; full regression is being rerun before publication.

## 2026-11-05 - Fixed person floating card (local)

Changed the named-person profile to a non-modal card projected beside the person, with left/right or below-person placement and viewport bounds. The path remains paused while its card is open; moving the camera or player updates the anchor and the card closes when the person leaves view or is occluded. Escape, close, focus restoration, model/label activation and touch remain supported. Preserved the speech and profile data. Local validation: 164 unit tests, production build, formatting, four fixed-person desktop/touch and occlusion browser tests, and five existing building-card browser tests passed. The full browser suite was not rerun; the previously reported Linux CI timeouts remain unresolved. Prepared for user-authorized publication.

## 2026-11-05 - Overview zoom and character speeds (local)

Forwarded Overview wheel events from building and fixed-person labels to the existing orbit controls so a label moving beneath the pointer during a pan does not swallow zoom. Keyboard walking now uses the former run speed (4.6 m/s), Shift uses 9.2 m/s; touch remains analog up to 9.2 m/s and walk/run feedback follows the new threshold. The shared movement function applies indoors as well. Validation: 165 unit tests, production build, formatting, desktop wheel bounds before and after pan (including over a building label), touch pinch after pan, four mobile movement tests, five building-card tests and a one-render-per-second sprint test passed. Two fixed-person card tests failed twice; the same tests failed at the same assertions against the HEAD versions of the changed runtime modules. The underlying person-card failures remain unresolved. Full browser suite and Linux CI were not rerun. The pre-existing wildlife.js template-lock mismatch was present at HEAD and is unchanged. Local isolated branch only; not published.


## 2026-11-05 - Touch zoom bounds and person-card investigation (local)

Extended the browser regression to exercise real two-finger gestures to the existing 12 and 6000 orbit-distance limits, both before and after a two-finger pan; both desktop and touch tests passed. The two existing fixed-person failures reproduce with the HEAD versions of the changed runtime modules: the moving label keeps Playwright waiting for a stable target before hover can pause the person, and the mobile dialog is initially at (0, 0) before its next render update positions it beside the person (observed at 50 ms). These failures remain unresolved; no person behavior or test assertions were changed. Of 43 locked viewer files, the three modified files match their override hashes and upstream pins; wildlife.js is the sole mismatch and its actual hash equals HEAD, with no registered override. No push or deployment.

## 2026-11-10 - Squirrel close-up accents and immediate person-card anchoring (local)

Refined the existing generic CC0-derived squirrel with an original charcoal nose and restrained chest/fur vertex colors. Source geometry, silhouette, placement, routes and original GLB remain unchanged; the refined animal retains one draw object and 1,060 triangles. Temporary merge geometries are now released. A new independently reimported standalone GLB preserves all 3,180 position, normal and color values exactly; previous exports remain. See `docs/squirrel-eyes-2026-11-04.md` for limitations and review images. LIFE-01 stays level 1.

Fixed the named-person card's initial top-left flash by computing its anchor synchronously after opening, reusing that calculation during subsequent updates. New same-task desktop/mobile assertions fail 0/2 against the original implementation and pass 2/2 against the fix; all six related person-card/occlusion browser regressions pass. The existing moving-target test focuses the label before a real click rather than waiting indefinitely for animation stability; no interaction assertion was removed.

Validation so far: 169 JS unit tests, 23 Python unit tests, production build, semantic activity, campus expansion and landcover checks pass; the squirrel campus/batching browser regression passes. All 189 archived model/source files verify after restoring the existing sky archive's LF checkout bytes (no Git content change). The downstream override now explicitly records the previously unregistered wildlife customization; the upstream template pin is unchanged. Entire-tree formatting passes with line endings set to auto; the ordinary check reports pre-existing Windows CRLF checkout differences, and no unrelated reformat was applied. Existing sound-bundle size warning remains. No full browser suite/Linux CI rerun and no push/deployment; remaining usage is not visible.

## 2026-11-10 - Knight Library solid balcony silhouettes (local)

Added three source-informed solid stone balcony parapets, side returns, coping and tapered undersides on the north elevation using the archived CC-BY-4.0 photograph. The source-pinned layer has 21 pieces merged into one mesh. Original building GLB, footprint, windows, entrances and collision remain. Dedicated before/after browser test passes: 42 to 43 draw calls, unchanged sampled collision/entrances and no page errors. See `docs/knight-refinement.md` for images and limitations: dimensions, carvings and current conditions are not verified; single-view acceptance only. Knight remains level 2. No push/deployment.

## 2026-11-10 - Integration follow-up and archive byte protection (local)

Completed all 14 selected browser integration tests: five building-card cases, two overview pan/zoom cases, one low-render-rate sprint case and six fixed-person opening/interaction/occlusion cases. A direct-node Vite server on a unique strict port prevented accidentally testing another checkout; no browser/runtime tests were weakened. The missing-information warning is deliberately induced by its passing fault-tolerance test. These results supersede the earlier interrupted partial navigation run, not the unrun full browser/Linux CI suites. Protected the already-checksummed historical sky JS archive with a precise `-text` Git attribute so future Windows checkouts preserve its expected bytes; the archive content and digest did not change. No push/deployment.

## 2026-11-10 - Knight tall-window depth and reusable layer exports (local)

Added seven photo-informed masonry window reveals as a separate source-pinned, one-mesh layer (42 components), preserving the pane apertures, blank plaques and completed balconies. This is interpreted outward wall thickness around the existing glazing, not surveyed recess geometry; Knight stays level 2. Front and oblique before/after browser checks now assert actual player coordinates and viewing direction, preventing a rejected viewpoint's default-spawn fallback from passing as visual evidence. Both corrected views passed with unchanged sampled collision/entrances and no page errors; draw calls changed 44 to 45 and 41 to 42. Existing tree occlusion remains. See `docs/knight-refinement.md`.

Exported the balcony and reveal layers as separate reusable GLBs with source/generator hashes and true generation-time evidence. Positions, normals and colors survive reimport with zero error, and local/browser construction agrees; material and identity also verify. The exporter accepts only the two pinned Knight layers, an explicit localhost port and new output files. It does not export the original building, collision or Blender scene. Original evidence is retained; the shareable verification record omits workstation paths. See `docs/knight-standalone-export-2026-11-10.md`.

Final local checks: 173/173 JS unit tests, production build, format with automatic line endings and all 191 archived source/model checksums pass. This complements the 14/14 integrated browser regressions above and the dedicated Knight views; full browser suite/Linux CI remain unrun. Earlier geometry and source evidence remain intact. No commit, push or deployment.

## 2026-11-10 - Gerlinger masonry, Johnson capitals and evidence corrections (local)

Added a shallow Gerlinger east masonry overlay: 36 central alternating brick accents and 15 compact window-crown pieces, preserving existing apertures and awnings. Rejected floating outer-corner candidates after visual review and fitted the retained accents against the actual source mesh. Front/oblique checks retain entrances and sampled collision, with 64 to 65 / 44 to 45 draw calls. Added six Johnson north column capitals with twelve original simplified volutes, preserving the inscription and original column geometry; the 2,832-triangle layer passed front/oblique checks at 81 to 82 / 86 to 87 draws. Both buildings stay level 1. Standalone GLBs and zero-error attribute roundtrip evidence are retained; see their dated refinement documents. Aggregate scene draw-budget validation is separate: the full diagnostic suite subsequently detected 182 draws against the existing <180 budget; a guarded overlay batching fix is in progress, not a reason to increase the threshold.

The Johnson rail audit corrected an earlier candidate premise: the source stair generator and actual GLB already contain two rail assemblies. Adding two more would be unsupported; no rail geometry was changed. Inventory evidence links were updated without changing any status/level, and its count was reconciled to 1,082 rows including the later fixed-person entry. A locally registered Knight balcony output digest was corrected to exact raw JSON bytes rather than an LF-normalized digest; the source JSON, presentation pin and exported artifact were already consistent and unchanged.

Windows autocrlf also altered the unchanged bike-rack, sky and random-template generator working bytes, causing exact-export provenance checks to fail. Their GLB embedded hashes match both Git HEAD and LF source bytes. Restored only those canonical LF bytes and added exact file attributes to preserve them; no geometry, export checksum or assertion was changed. Stable browser reruns are pending. No push/deployment.

## 2026-11-10 - Tykeson canopy, keyboard access and draw-budget recovery (local)

Refined Tykeson's two existing canopy plates into a framed/ribbed, glass-colored infill treatment and added fine upper-cladding seams clipped around the retained window openings. The complete prior 52-object JSON is preserved; all other 50 original objects remain exact. Both verified viewpoints retained 71 draws, entrances and collision. The new standalone GLB roundtrips exactly; opaque glass-colored shading, inferred spacing and unresolved hidden massing remain documented. Level stays 1.

Building cards now anchor synchronously when opened or switched, with desktop/mobile same-task regressions failing on the original implementation and passing after the fix. Keyboard Enter/Space activates labels and card buttons without global movement shortcuts swallowing the native action; keyboard-opened cards receive focus and restore it safely on closing, while pointer opening does not steal focus and Tab remains non-modal. Ten focused browser cases passed, with a strengthened keyboard-enter test pass afterward.

Recovered the original scene budget without removing geometry or raising its threshold: three fixed-source, same-building overlay pairs are merged only after exact JSON digests, generated geometry, static transforms, material and unique ownership checks all succeed. Positions/normals/colors and raycast identity are preserved, along with vegetation and independent source exports. Actual comparison is 182 draws before versus 179 after; the existing toon/PBR <180 regression passes. A configured historical source pin is not eligible for the new recipe and remains separate, whereas corruption under a supported current pin is rejected atomically. Historical before/after tests retain all non-draw exact assertions and permit only fewer/equal draws, rather than requiring redundant work.

Canonical source line endings are now pinned in Git attributes so strict viewer hash checks and the ordinary formatter pass on Windows. Three historically literal-CRLF exporters remain exact-byte exceptions. Past raw-byte generation receipts are unchanged; see `docs/source-byte-normalization-2026-11-10.md`. Full-suite work remains diagnostic until its changed-source/HMR failures are reconciled under the stable version. No commit, push or deployment.

## 2026-11-10 - Frozen current-browser acceptance completed (local)

The current 186 browser tests across 144 files all passed on a frozen source/scene/test state: 182/182 in the main stable batch, plus four complementary fixed-person tests, with zero skipped or flaky results. Raw SHA-256 snapshots confirmed no changes across either stable batch. This is complete current-suite coverage in two batches, not a single 186-test invocation. The earlier non-frozen diagnostic (163 passes, 14 failures) remains preserved; all fourteen failures subsequently passed after the documented fixes and stable reruns. See `docs/browser-validation-2026-11-10.json` for actual times and report hashes.

Final supporting checks passed: 183 JavaScript unit tests, 23 Python tests, production build, default formatting, all 43 viewer baseline/override raw hashes, registered viewer outputs and 195 source/model file checksums. Existing large sound-chunk warning remains. Windows Chrome/SwiftShader acceptance is not Linux CI, real mobile-GPU benchmarking or live deployment verification. Isolated exporter tests retain their artificial removed-DOM console warnings in raw logs. No commit, push or deployment. The next source-supported Susan Campbell candidates remain a plan, not completed geometry.

## 2026-11-10: Next local refinement batch (in progress)

Continued the authorized UO refinement after the frozen 186-case browser acceptance. Susan Campbell's two photo-supported small arched parapet details are being added to the existing merged layer; the complete pre-change specification is preserved. The source pin is updated locally, but visual/export/regression acceptance is still pending. Earlier acceptance applies to the preceding checkpoint, not automatically to this new geometry. No commit, push or deployment.

### Local Susan/NPC results before integration retest

- Susan: retained all 463 existing components and added eight parts for two shallow arched motifs supported by the archived 2011 photo. Exact old source snapshot retained; level remains 1. Front/oblique actual-camera comparisons pass with 81→81 / 79→79 draw calls; entrances and collision contracts unchanged. Standalone GLB 642704 bytes, SHA-256 `40b507d808bab0d438e7481b572a0f03631a409fa68bb7e882c08b27efaffb25`; all 17808 position/normal/color attributes round-trip exactly. The initially tree-obscured front proof was replaced by a verified unobstructed local facade close-up, not claimed as a full-building view. Uncertain projecting window groups remain deferred.
- NPC controls: Space on the person label or close button incorrectly triggered campus jumping. Two new browser cases failed before the fix; all eight related cases pass after narrowly preserving native button Space activation without propagating to movement. Enter/Escape remain tested.
- Local production build and standard formatter pass. Frozen targeted integration retest is running; preceding full-suite receipt is retained separately. No commit, push or deployment.

### Susan/NPC batch acceptance

Frozen focused browser regression: **27/27 passed**, zero failures/skips/flaky, 4.7 minutes; source/browser-test/scene pre/post hashes identical. Existing global draw budget remains **179 (<180)**. The expected invalid-source negative test remains enforced. Full current JS suite **186/186** and Python suite **23/23** pass; build, format, viewer hashes and **197** archived asset records verified. See `docs/browser-validation-2026-11-10-round2.json`. This focused retest supplements, not replaces, the earlier 186-case full-browser receipt. Uncommitted/local only.

## 2026-11-10: Friendly Hall round-shaft batch (in progress)

Following the verified Susan/NPC checkpoint, four photo-supported freestanding porch shafts change only their primitive from box to existing octagonal column. All positions, dimensions, materials and the other 486 objects are preserved. The old source is archived with nested provenance. Local source pin updated; final visual/export/regression evidence is still pending. No commit, push or deployment.

### Friendly batch acceptance and evidence-based stopping point

Only four shaft shape fields changed semantically; all other 486 objects, dimensions/materials/placement, collision and navigation remain exact. New serialized source uses LF and preserves the complete prior raw-byte snapshot, so raw Git text diff is larger than the semantic edit. The building adds 80 triangles but no draw calls. Three actual-camera comparisons pass; standalone building-only GLB (796100 bytes; `cc96fee2b2bf1564a3deb81335557cb1a3e9e9d87bc955fc5f862e1ea2f4311a`) round-trips 22068 position/normal/color attributes exactly. Export stdout receipt was recorded later with actual record time; no unavailable export timestamp invented.

Final frozen focused browser regression **7/7 passes**, zero failed/skipped/flaky, source/test/scene hashes unchanged; fixed scene budget remains **179**. See `docs/browser-validation-2026-11-10-round3.json`. All **187 JS tests**, build and normal formatter pass; all **43** template/override raw hashes and **199** archived asset records verified. The unchanged Python scope passed 23/23 in the preceding batch.

A bounded review of University Hall, Villard Hall and Gerlinger Annex found no reliable new small addition: existing details already cover the visible candidates, unresolved roof mappings need better evidence, and the Annex reference has an existing identity warning. See `docs/refinement-candidate-audit-2026-11-10-c-stop.md`. End this batch rather than invent geometry or consume quota without benefit. Usage balance is not exposed. Every change remains local/uncommitted; no push/deploy or upstream-pin claim.

## 2026-11-10: Continued evidence and interaction quality pass (in progress)

Following the final geometry checkpoint, the continued request now checks new public sources rather than repeating exhausted photo candidates, and tests real interaction defects. Archived reference README counts were stale: verified all 23 manifest records against raw bytes and corrected both languages to 15 photo files, 2 aerial subsets, 5 design images and 1 texture. Retained files are not all valid current building references; the existing Gerlinger Annex identity warning remains explicit. No source image added or relicensed. A newly reproduced person-label pointer/focus conflict is under bounded repair and verification. No publication.

### New-source Annex and NPC focus results (integration pending)

- Reopened official UO survey evidence and independently inspected the photographed building sign and site plan: the modern Annex north frontage can be distinguished from the misidentified archived Commons image. The survey image has no verified open image license and stays link-only; no source pixels are added or reused as textures. Five shallow 0.03 m recesses are an explicitly stylized use of the existing module, not measured count/spacing. Only the upper panel is repartitioned; the other 83 objects, facade envelope, collision and entrance records remain unchanged. Real raycasts verify 0.03 m depth. Context/oblique/close comparisons keep 39/38/36 draws unchanged; trees are not moved or hidden.
- Annex export: 179300 bytes, SHA `9572877db1ce9a010e09f87eddb953926bd38faaf4bcb782ba7bd30776ed7bf8`; 2700 building and 2208 vegetation vertices round-trip position/normal/color exactly. Raw stdout retained, unknown export time stays null.
- Reproduced NPC pointerleave incorrectly clearing ongoing keyboard focus (red 0/1). Separated model-hover, label-hover and focus; 10/10 related browser checks now pass, including reverse blur, hidden/disposed cleanup and not stealing another input focus.
- All 189 JS tests, build and normal formatter pass. Frozen 16-case integration retest is running; no publication.

### Annex/NPC batch acceptance

Frozen integration **16/16 passed**, 144.9 s, no failed/skipped/flaky cases and no runtime/scene/browser-test hash drift. Global draw count remains **179**; Annex context/oblique/close counts remain **39/38/36**. Current 189 JS tests, build/format, 43 raw viewer/template records, 201 asset registry records and 23 reference-image archive records verified. See `docs/browser-validation-2026-11-10-round4.json`. Local uncommitted only; continuing independent source research after this checkpoint.

## 2026-11-10: Chapman west relief batch (in progress)

Independent review confirms the west entry projection lacks the photo-visible shallow arcade pattern; existing other-face motifs are outside this scope. Proceeding with original, limited 10 m relief using the existing generator and retained 144 objects. Source remains link-only UO survey: a new attribution-only low-resolution photo does not satisfy the pinned archival license whitelist, and focused CC/PD replacements were different universities. No false license, CI relaxation or public photo intake. Source pin updated locally; visual/export/regression checks pending. The reviewed pinned reference checker passes all 23 existing records; semantic activity, campus identity and landcover checks also passed.

### Chapman and native-button results (integration pending)

Chapman now retains all 144 prior objects and adds 121 pieces for a continuous shallow stone band with twelve 4 cm arch-relief motifs. The first isolated-arch version looked like hanging horseshoes and was rejected, not accepted because tests passed. Equivalent rotations were normalized into the existing validator range without relaxing it; corrected close/oblique cameras now show the actual frieze. Final three-view local comparisons maintain 109/44/41 draws. The original 144-object fixture now checks the exact preserved prefix and explicit added count, not a weakened inequality.

Independent overlay GLB is 419904 bytes, SHA `90ebcc700a8809c30242066f3f8877344f53c6e7cf8d56e726e7c5c704d5573d`, with 10872 building and 720 shrub vertices; position/normal/color round-trip error is zero. Raw stdout is retained and unknown generation time remains null.

A further real keyboard defect was reproduced: Follow and Settings buttons consumed Space as a world jump (red 0/2). The shared key handler now returns only for Space targeted at a native button. Native activation works without jumping; viewport Space still jumps and mouse-click Follow then W still moves. Eight local related cases pass. Existing upstream baseline remains unchanged; the downstream override is explicitly hashed. Frozen 15-case integration retest is running. No commit/push/deploy.

### Chapman/native-button batch acceptance

Frozen integration **15/15 passed**, 132.5 s, zero failed/skipped/flaky; source/scene/browser-test hashes unchanged. Chapman view budgets **109/44/41** remain unchanged; global count **179**. Native button activation, viewport jumping, W movement, NPC/building keyboard controls and overview wheel/pinch/slow-frame regressions pass. Current **191 JS tests**, build/format, 43 viewer raw hashes, 203 open-asset records and all 23 reference-image records pass. See `docs/browser-validation-2026-11-10-round5.json`. This supplements previous full/focused receipts, not a fresh full-browser run. No commit, push or deployment.

## Release closeout, 2026-11-10T22:09:23.045485+00:00

The user instructed: finish the current batch, record it, push/deploy, then stop. No further implementation started. The latest Carson candidate remains explicitly unimplemented; the additional search/touch audit passed 6/6 without code changes. Read-only proposed extra overlay batching was rejected: incompatible semantic buckets or already-batched content, no safe new benefit.

Publishing the complete locally verified November 10 batch from existing `main` baseline `8cbb19b71268090c086a8ec2eb25ed8476137fb3`. A fresh fetch showed no ahead/behind divergence with origin/main. Existing GitHub Pages workflow is the deployment route; no credentials, permissions or hosting settings are being changed. Release commit and actual workflow/deployment outcomes are recorded by GitHub after this entry, not assumed here. All earlier local/pending statements are historical. No additional refinement will run after publication verification.
