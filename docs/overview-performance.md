# Overview depth stability and rendering assessment

**English** | [简体中文](zh-CN/overview-performance.md)

Local iteration 14 fixes a reproducible depth problem and removes repeated CPU work. It preserves the existing assets, perspective, pixel ratio, antialiasing, lighting, NPC density and all three camera modes. This batch is not pushed or deployed.

## Roof and paving flicker

The 24-bit depth buffer was covering 0.08–9000 m in every view. At Overview distances, nearby roof/trim layers could compete for the same depth values. With the camera, models, materials and lighting held fixed, changing only the near plane to 16 m removed the pale roof stripes. This is depth fighting; the weathered brown material itself does not need replacing. [Near-plane A/B images](images/phase14-depth-before.png), [improved precision](images/phase14-depth-after.png).

The actual fix is adaptive, rather than a globally larger near plane. Compute the static map bounds once, pad them by 8 m for nearby actors/jumps, and increase near only in empty space outside those bounds. Use at most one tenth of that distance, quantized downward to powers of two and capped at 64 m. The initial UO Overview selects 32 m. Inside the bounds, Follow and First person retain 0.08 m. FOV, far plane, perspective and source geometry are unchanged.

## Default optimizations

- Render the 63 world-anchored building labels through their own small CSS scene. Labels, pinning and decluttering keep their original projection and update behavior; their renderer no longer traverses every campus object and animated bone again.
- Compute and retain transforms for the 184 static map nodes. Dynamic hero, students, vehicles, wildlife and beta actors remain outside that frozen root.
- Redraw the minimap only when the exact displayed position, heading, target or route changes. Overview camera dragging does not change the minimap contents. Movement, new routes and clearing still invalidate it.
- Replace coordinate text only when its displayed value changes.

There is no mesh decimation, render-resolution reduction, label-frequency reduction, NPC removal or shadow-quality change. The scene still draws **947,049 triangles / 229 calls** in the measured steady default view, at the same pixel ratio.

## Measurements and limits

The reproducible harness uses headless Chrome on native ANGLE/D3D11 with an RTX 5090, a 1440 × 1000 CSS viewport and pixel ratio 1. It records steady idle, actual mouse orbit and actual right-button pan after initial compilation/upload/shadows. CPU profiles and optional GPU queries are instrumented measurements, not a claim about the Codex embedded browser or a phone.

| Mean CPU work during orbit | Before | Current default |
| --- | ---: | ---: |
| Label update | 0.334 ms | 0.191 ms |
| WebGL render submission | 1.405 ms | 1.249 ms |

Pan label work fell from 0.319 to 0.189 ms. A separate 4× CPU-throttled, pixel-ratio-2 probe also reduced orbit label work from 2.534 to 1.490 ms. That stress setup is synthetic; its frame intervals and GPU queue timing are **not** a mobile benchmark. Native rendering was already close to the 120 Hz cap, so this assessment does **not** claim a 40% overall FPS improvement or establish the embedded browser's bottleneck. The verified benefit is less repeated CPU work and stable distant surfaces.

Raw summaries: [native baseline](../data/metadata/performance/phase14-baseline-gpu.json), [native final](../data/metadata/performance/phase14-final-gpu.json), [stress baseline](../data/metadata/performance/phase14-baseline-4x-dpr2.json), [stress final](../data/metadata/performance/phase14-final-4x-dpr2.json). Source hashes, sample counts, GPU identity and setup are retained. Large local CPU traces remain ignored under `artifacts/`.

## Evaluated, off by default: static haze fields

An optional `scene/viewer-settings.json` setting, `cache_static_haze`, can precompute the existing spatial haze weights per static vertex after final placement. It preserves the shader's interpolation and works in Toon/PBR. A controlled image comparison changed only one pixel by one 8-bit channel value in each mode; no difference exceeded 1/255.

However, four-way dynamic/cached/cached/dynamic GPU trials showed small, unstable gains across repeat runs, on the order of hundredths of a millisecond. The cache adds **5,166,728 bytes of vertex attributes**, with CPU and GPU copies, plus load-time work. Therefore UO explicitly sets it to **false**: default cached vertices and extra attribute bytes are zero. Keep the option for target-device experiments, not as an assumed optimization. [First-trial measurements](../data/metadata/performance/phase14-haze-ab-initial.json), [repeat A/B results](../data/metadata/performance/phase14-haze-ab.json).

## Repeat and next candidates

With the local Vite server running, from `apps/web-preview`:

```powershell
node scripts/profile-overview.mjs my-overview-probe
node scripts/compare-render-cache.mjs
```

Both harnesses inject inspection references only into their isolated Playwright pages. They do not add a public debugging API or send analytics. The cache trial enables its configuration only in those test pages. Keep all other browsers/tests quiet during comparative measurements. GPU timer support is required for the cache microbenchmark.

If another browser still drags slowly, identify its actual GPU/backend, pixel ratio and CPU/GPU/compositor frame costs before choosing another change. Candidates that can preserve geometry include material-compatible batching with picking identities retained, spatial indexes for interaction queries, and spatially tiled ground with identical vertices/normals/colors and frustum culling. Each has CPU/memory/draw-call tradeoffs; none is claimed as implemented here. Dynamic resolution, fewer NPCs or reduced model detail would change the requested quality budget and are not the basis of these results.

See [verification](../data/metadata/phase14-verification.json), the project-only [development log](../DEVELOPMENT_LOG.md), and the [reusable upstream method](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/render-performance.md). Original GLB/Blender/image bytes and their previous provenance remain unchanged.
