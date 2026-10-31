**English** | [简体中文](zh-CN/visual-refinement-v0.7.md)

# v0.7 — modular landmarks and aerial-guided landscape

2026-10-31 · Architectural Toon Realism

This pass refines Knight Library, Johnson Hall and EMU using the seven archived, openly reusable photographs. A fixed **2024-06-08 USDA NAIP orthophoto subset** adds vegetation distribution and broad roof context. Follow, First person, Overview, search framing, labels, minimap, jump and zoom retain their existing behavior.

![v0.7 overview](images/refinement-v07-overview.png)

## Production position

**Build a coherent, recognizable first pass; improve precision and realism through long-term correction.** Reasonable inference is welcome when recorded and kept editable. This is exterior art with historical geographic evidence, not a current measured twin. No new field measurements, phone capture, photogrammetric solve, splats or AI geometry model were used.

The supplied technical discussion informed the hybrid approach: geographic skeleton + appearance references + repeated architectural modules + portable materials. Its filename/hash and adopted/pending methods are recorded in [method provenance](../data/metadata/refinement-methods-v07.json). Embedded third-party illustrations and private conversation contents were not imported as image assets.

## Features and correction ledger

| Asset | Observed vocabulary used | Inference and next useful correction |
| --- | --- | --- |
| Knight Library · `roof-6684e091` | Tall many-pane north windows, brick reveals, pale frieze/cornice, three balconies, exterior lantern character | Bay dimensions/subdivisions, ornament, side/rear windows and roof equipment are approximate. Next: check entrance widths and roof-wing layout. |
| Johnson Hall · `roof-906c030e` | Six columns, light capitals/entablature, parapet medallion motif, broad front stair, green rear awnings | Fluting/profile, reliefs, proportions, glazing and stair rise are approximate. Next: measured control lengths and connected corner views. |
| EMU · `roof-266f13fd` | 2017 brick/glass vocabulary, continuous clerestory, historic curved Fishbowl glass, canopy and terrace | Roof blocks, glazing rhythm and terrace layout are inferred; historical and later motifs form a staged hybrid, not one exact dated facade. Next: reconcile the modern footprint/entrances with permitted current captures. |
| Landscape | Aerial dark/textured-green canopy cues and open-lawn character | 300 generated trees are illustrative, not surveyed stems. Species, heights, crowns, understory and some paths are inferred. Next: compare seasonal imagery and an open tree inventory if available. |

![Johnson Hall](images/refinement-v07-johnson.png)

There are 20 editable semantic meshes across 14 authored building IDs and landscape. Repeated window/column patterns are in [the art configuration](../configs/visual-pilot.json). The original 2008 terrain, building catalog, stable IDs and Census centerlines retain their provenance. Decorative stairs, planting and terraces do not establish collision meshes, legal access or survey accuracy.

## Aerial source and placement

This is **aerial orthophotography, not a satellite image or Google basemap**. Raster `m_4412364_sw_10_060_20240608` is selected explicitly from the USDA service. The archived PNG covers 540 × 450 m at 0.6 m/px in EPSG:3740, matching the scene's horizontal frame. See the [image](../data/reference-images/aerial/naip-2024-pilot-rgb.png), [export request, extent and source metadata](../data/metadata/naip-2024-reference.json) and [credit](../data/reference-images/ATTRIBUTION.md#naip-2024-pilot-rgb).

The [official USDA catalog](https://catalog.data.gov/dataset/national-agriculture-imagery-program-naip-imagery) records public-domain distribution. We retain the agency credit and `LicenseRef-PD-USGov` designation, rather than relabeling the image CC BY or CC0. No Google imagery, traced Google geometry or hosted 3D asset is incorporated.

Preparation favors dark/textured green RGB patches, smooths the cue and samples in the known north-up frame. Seeded placement applies building/path setbacks, open-quad areas, minimum spacing and the spawn-to-EMU sightline. This heuristic can confuse shadows and shrubs; it does not provide tree heights or species. New diagonal connections and planting remain illustrative terrain-draped surfaces.

## Delivery and validation

- [Editable Blender](../assets/visual-pilot/knight-emu-johnson.blend) and [standard PBR GLB](../apps/web-preview/public/scene/visual-pilot.glb), approximately 11.65 MB, with the existing optional toon adapter.
- [Presentation/source hashes and independent art-method revision](../apps/web-preview/public/scene/presentation.json). Geographic reconstruction and viewer-runtime pins remain separate.
- [Upstream progressive modeling policy and reusable code](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/progressive-modeling.md): facade-module poses and RGB canopy cues. UO geometry, parameters and photos stay downstream.
- [Diagnostic evidence](../data/metadata/visual-refinement-v07-diagnostics.json): no page errors; 48–139 draw calls and approximately 588k–640k visible triangles. Chrome/ANGLE SwiftShader software rendering measured roughly 158 ms median frame intervals at 1440 × 960. This is not a hardware GPU or 60 FPS claim. Full-terrain chunking/LOD remains future work.

Local checks passed: 6 movement/terrain unit tests, 8 browser tests, production build, formatting and media audit. Browser tests cover camera modes, terrain/collision/jump, zoom, search/labels, narrow viewports, all three landmark selections and material fallback. Upstream has 25 Python tests including the new methods. Source images remain outside runtime downloads.

The [asset audit](../data/metadata/visual-refinement-v07-audit.json) verifies exported building IDs, GLB structure, zero embedded photo textures, source/module/asset hashes and the unchanged historical manifest.

Rebuild with a clean upstream checkout at `presentation.json` → `art_pipeline.commit`, its Python environment and Blender 4.5:

```powershell
& '../open-geospatial-to-3d-reconstruction-pipeline/.venv/Scripts/python.exe' scripts/prepare-visual-pilot.py
& '../open-geospatial-to-3d-reconstruction-pipeline/.tools/blender-4.5.15-windows-x64/blender.exe' --background --factory-startup --python scripts/build-visual-pilot.py
```

Preserve manual Blender edits before regenerating the procedural layer. Original model contributions remain CC BY 4.0; software is Apache-2.0 and images retain their individual terms. The [v0.6 report](visual-pilot.md) and original screenshots remain historical evidence.
