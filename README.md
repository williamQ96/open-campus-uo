**English** | [简体中文](README.zh-CN.md)

# Open Campus: UO

A Blender-first, georeferenced University of Oregon campus asset project with an interactive Three.js explorer.

**[Open the live explorer](https://williamq96.github.io/open-campus-uo/)** — public, no sign-in required. Both the UO and upstream repositories are public.

[Development log](DEVELOPMENT_LOG.md) records project-specific changes and verification. Reusable methodology is recorded separately upstream.

## Phone layout and controls

The phone layout uses a compact header/search, a smaller top-right minimap and bottom view buttons. Follow and First-person lower-half touches create a floating analog joystick; upper-half touches look around. Roles stay fixed when crossing the screen midpoint. Cancel, blur, opening Settings/search and changing views stop movement. See [mobile verification](docs/mobile-controls.md).

## Campus life and directions

The green/gold rigged hero, walking/bicycle/scooter NPCs, road traffic and parked vehicles are available with one No / Low / Mid / High density slider (default Mid). Directions supports A/B building searches or map pins in Overview, and your position when starting the route → destination in Follow/First person, with a blue route and animated white chevrons. [Controls, open asset credits and limitations](docs/campus-life-navigation.md). Iteration 11 adds open squirrels, collision, music/footsteps, gentle first-person motion and GitHub feedback; see [ambience and feedback](docs/ambience-feedback.md).

## Layered campus expansion

The [layered campus refinement](docs/campus-expansion.md) gives all 534 records a stylized appearance, with 135 in the campus priority area and 399 as low-poly background. Gerlinger Hall/Annex join the photo-informed landmarks, and fixed-world haze softens the outer blocks. Geography and roads remain unchanged; Blender retains all building objects independently, with runtime-only batching. See the [development log](DEVELOPMENT_LOG.md) for confirmed publication and deployment status.

## Current scene

The 2 × 2 km scene covers the main Eugene campus and surrounding context, with **534 structure records, 63 named buildings and 140 road/path segments**. It is a square study extent, not an official campus property boundary, and excludes the Autzen complex north of the river.

Terrain and most geometry come from nine NOAA-hosted DOGAMI LiDAR tiles acquired in 2008. Seventeen explicit approximate envelopes supplement later or unextracted buildings. Roads use Census Bureau 2025 TIGER/Line® centerlines with estimated widths. The historical base remains approximate. A photo-informed Architectural Toon Realism pilot now refines the Knight Library–EMU–Johnson Hall area; it is not a precise current campus survey.

The character starts at the University Street / East 13th Avenue T-junction facing Erb Memorial Union. Settings / About contains source acknowledgements, quality notes and project links.

## Design direction

[Architectural Toon Realism](design/architectural-toon-realism/README.md) is the recommended visual style: original concept mockup, exact palette, source guide and a staged UO refinement plan. The [design archive](design/README.md) also preserves the existing Open Courtyard identity. The [first v0.6 visual pilot](docs/visual-pilot.md) established: three photo-informed landmarks, ten stylized buildings, one context envelope, 220 trees, lawns, paths and furnishings. That release left the surrounding campus as a whitebox; the campus expansion now provides its stylized context.

The reusable specification is the [upstream style library's default recommendation](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/tree/main/style), with other styles encouraged.

**v0.7** refines the three landmarks with modular windows, columns, cornices, entrances and terraces, plus **300 aerial-guided illustrative trees** and understory. See the [refinement report and correction ledger](docs/visual-refinement-v0.7.md). First passes favor coherent, recognizable models with explicit plausible inference; long-term maintenance improves precision and realism.

The [image and photo archive](data/reference-images/README.md) preserves adopted source images, mockups and branding with per-file authors, licenses, dates, use and checksums. Seven openly reusable photographs now support the refinement, with a dated USDA NAIP aerial subset; legacy reference exclusions remain documented. The archive is outside runtime downloads.

## Run locally

```powershell
cd apps/web-preview
npm ci
npm run dev
```

Open `http://127.0.0.1:5173/`. The repository includes the GLB, heightfield, metadata, branding and fonts; a first preview needs neither Blender nor raw LiDAR downloads. Desktop keyboard/mouse and phone touch are supported. In Follow and First person, drag in the lower half to walk and release to stop; drag in the upper half to look. Two fingers work independently. Overview supports orbit/pinch.

| Action | Control |
| --- | --- |
| Move / run | WASD or arrow keys / Shift |
| Jump | Space; land before jumping again |
| Follow / First person / Overview | 1 / 2 / 3, or the view buttons |
| Cycle views | V |
| Look / zoom | Mouse drag / wheel in Follow and Overview |
| Search | Search field or `/`; names and abbreviations such as EMU and PLC |
| Choose a result | Arrow keys and Enter, or click |
| Close search / clear selection | Escape, or the clear button |
| Reset | Return to start |
| Labels / wireframe / shadows | Settings / About |

Overview search frames a building at about 45° with a short transition. Walking views keep the character in place and turn toward the target. Selection persists across view changes; the label and minimap mark the target. Manual movement or dragging resumes normal camera control.

## Long-term upstream and downstream roles

[Open Geospatial-to-3D Reconstruction Pipeline](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline) maintains reusable reconstruction methods, automation, validation and the browser explorer template. This repository maintains UO data, names, specific models, branding and campus refinement.

`pipeline.lock.json` pins the reconstruction that generated the current assets. `apps/web-preview/viewer-template.lock.json` separately pins the shared viewer runtime. Local content is in `public/viewer-profile.json` and `public/scene/`; template upgrades preserve these files. See [maintenance](MAINTENANCE.md), [architecture](docs/architecture.md) and [template adoption](docs/viewer-template.md).

## Rebuild the geospatial assets

Use a clean upstream checkout at the commit in `pipeline.lock.json`. A separate worktree lets the upstream main branch advance while this reconstruction stays reproducible:

```powershell
# In an upstream clone; use the actual commit from pipeline.lock.json.
git worktree add ../pipeline-uo-build b1d0cdea9cb37896437bcf531e7ce76947fe6503
```

Prepare its Python environment and Blender as documented upstream, then run here:

```powershell
./scripts/rebuild.ps1 -PipelineRoot '../pipeline-uo-build' -Blender 'C:/path/to/blender.exe'
```

The script verifies the upstream pin and source checksums, generates Blender/GLB assets, and writes viewer spawn preferences. The default is `configs/eugene-main-campus.json`; the original Memorial Quad configuration and Blender scene remain as first-loop evidence. `-AllowUnpinned` is for deliberate development builds and records the actual revision and dirty state.

## Verification and records

[Access statistics](docs/analytics.md): repository traffic is archived privately each day; production website visits and basic interactions use [GoatCounter](https://opencampus-uo-williamq96.goatcounter.com/).

In `apps/web-preview`, run `npm test`, `npm run build`, and `npm run test:browser`. Local browser tests use Chrome; CI uses Playwright Chromium. Fonts and scene assets are self-hosted; integration tests block external requests. Routine preview screenshots are generated locally, with failure traces retained in CI.

- [First closed-loop verification](docs/verification.md)
- [Main-campus expansion](docs/v0.2-main-campus.md)
- [Roads and camera zoom](docs/v0.3-roads-controls.md)
- [Spawn and building search](docs/v0.4-building-search.md)
- [Public hosting](docs/hosting.md)
- [Roadmap](docs/roadmap.md) · [Source decisions](docs/source-discussion.md) · [Data records](data/README.md)

## Data and licensing

UO internal GIS is excluded. OSM, Microsoft/Oregon building-footprint compilations, Eugene GIS and Google Maps/Earth 3D are not core geometry inputs for this version. The rejected USGS 2021 DEM had only NoData in the trial area. NAIP 2024 now guides illustrative landscaping; self-captured photos have not been integrated.

Raw large datasets are ignored locally; source records and hashes are committed. Code uses **Apache-2.0**; original documentation and model/design contributions use **CC BY 4.0**. See [licensing and attribution](LICENSING.md) and [NOTICE](NOTICE). Third-party source data and fonts retain their own terms.
