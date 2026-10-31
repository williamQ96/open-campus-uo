**English** | [简体中文](README.zh-CN.md) · [Design archive](../README.md)

# Open Campus: UO — Architectural Toon Realism

Art-direction archive v1.0 · 2026-10-31 · **Recommended future style**

The [shared design conversation](https://chatgpt.com/share/6ae5adf2-4a74-83e8-b001-f9de17509c56) considered realism, Stylized PBR, low-poly, pixel/voxel and comic rendering. After a restrained Architectural Toon concept was generated, the user approved its appearance and requested a rule set. The resulting direction is **Architectural Toon Realism**: recognizable campus structure, clean natural materials, soft 2–3 tone shading, selective outlines and a miniature architectural-diorama reading at a distance.

The reusable guide is maintained [upstream](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/tree/main/style/architectural-toon-realism), where it is the **default recommended style** for future maps. It is a recommendation, not a requirement; other authors are encouraged to explore different visual languages.

## Original mockup

![Original AI-generated architectural-toon campus concept](mockups/uo-campus-concept.png)

**Concept artwork, not an accurate UO reconstruction or a screenshot of the running app.** The original 1672 × 941 PNG is archived unchanged. Its road details, buildings, river, sports grounds and vegetation cannot be used as geographic evidence. See [source provenance and checksum](provenance.json).

## Palette and design files

The final guide's exact sRGB material-color suggestions are preserved below and in [palette.json](palette.json). They are not UO official colors, measured material reflectance or tested UI contrast pairs. Keep natural variation within each material family.

| Material | sRGB HEX |
| --- | --- |
| Brick Red | `#B96F55` |
| Warm Stone | `#E4D6BB` |
| Roof Gray | `#A8ADB0` |
| Glass Blue | `#8FAEAE` |
| Grass Green | `#91B66F` |
| Foliage Green | `#658B54` |
| Deep Evergreen | `#385A45` |
| Path Sand | `#CDBB9F` |

- [Original final guide in Chinese, normalized from the shared conversation](source-guide.zh-CN.md).
- [Reusable style prompt](style-prompt.txt), preserved from the final answer.
- [Reusable English visual rules](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/tree/main/style/architectural-toon-realism/README.md), with a Chinese option.
- [Implementation and cost/runtime evaluation](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/tree/main/style/architectural-toon-realism/implementation.md).
- [Machine-readable provenance](provenance.json), including AI-generation disclosure and file hashes.

## UO application plan

This is a planned refinement of the existing scene, not a new campus dataset. Preserve the current historical/approximate provenance, object IDs, source dates and model confidence. The concept must not upgrade 2008 LiDAR placeholders into current measured buildings.

| Pass | UO work | Review before wider rollout |
| --- | --- | --- |
| Environment | Source ground categories, lawns, pedestrian paths and local vegetation independently; build a reusable tree library. | Confirm placement and source rights. Current road centerlines and estimated widths remain approximate. |
| Materials | Introduce brick, stone, roof, glass and paving families with the source palette as a starting point. | Avoid one-color buildings; retain standard PBR interchange materials and current identity assets. |
| Landmark pilot | Refine a small Knight Library–EMU–Johnson Hall area before treating all 534 placeholders equally. Verify roof, entrance and facade references first. | Check near, medium and aerial views against real references. Nearby source coverage and accuracy must be checked. |
| Navigation | Preserve Follow, First person, Overview, search, selected labels and minimap. | Vegetation/lines must not obscure the avatar, target or navigation; selected labels stay prominent. |
| Render and scale | Evaluate soft toon shading and optional selective outlines, then detail/instancing/compression where measurements justify them. | Compare the same geometry to PBR on target browsers; record frame time, memory, draw calls and download cost. |

The landmark pilot, three-view application and measurable release gates are editorial engineering extensions to the archived conversation, not claims of completed work. The final guide selected warm daylight; the earlier soft-overcast proposal remains an optional future lighting variant.

## Ownership and maintenance

UO owns local references, building identity, model refinements, region-specific palette/vegetation decisions and branding. Upstream owns reusable style methodology and future data-neutral rendering adapters. Keep geography → editable Blender assets → standard GLB/materials → renderer styling as separate layers; future style changes should not require rebuilding geographic evidence or duplicating the world for each camera mode.

**Current status:** docs and original mockup archived; the live explorer still uses grey terrain and white placeholder buildings. Foliage, detailed facades, toon shading, LOD and theme switching are not implemented by this change. These design assets are outside `apps/web-preview/public/`, so they do not add runtime downloads or change viewer/template pins.

## Credit and source scope

Credit **OpenCampus Architectural Toon Realism — Zhongyi “William” Qiu and contributors**, [Open Campus: UO](https://github.com/williamQ96/open-campus-uo) and the [upstream archive](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/tree/main/style/architectural-toon-realism); retain [CC BY 4.0](../../LICENSES/CC-BY-4.0.txt) and indicate modifications. Original rights-held docs/design contributions and copyrightable project rights in the AI-generated concept are offered under that policy. No exclusive right in a style is claimed. Third-party web/reference images from the conversation are not bundled or relicensed; the two initial screenshot attachments are recorded as source context, not copied here because the public share did not expose downloadable originals. Existing [Open Courtyard identity](../open-campus-philosophy.md) is preserved. See [licensing](../../LICENSING.md).
