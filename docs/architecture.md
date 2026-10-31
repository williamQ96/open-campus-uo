**English** | [简体中文](zh-CN/architecture.md)

# Architecture and asset contracts

## Repository boundary

This is the UO instance of the generic reconstruction pipeline. It owns the area, source ledger, campus content and presentation. Generic algorithms, schemas, scaffolding and the explorer template live upstream.

`pipeline.lock.json` pins reconstruction without a Git submodule. Exported manifests retain actual pipeline revision, dirty state, configuration hash, source checksums and parameters. The viewer has a separate template lock so UI updates do not falsely change historical asset provenance.

```text
configs/                    AOI, source references, reconstruction and spawn configuration
data/metadata/              source evidence, catalogs, checksums and audits
assets/                     editable Blender source scenes
exports/                    ignored intermediate and generated outputs
apps/web-preview/src/       managed reusable viewer runtime
apps/web-preview/public/    UO profile, branding, scene, fonts and licenses
```

## Coordinates and identities

Work in metres. Blender uses local East/North/Up; glTF uses X east, Y up, Z south. The exporter performs the axis conversion once. Heightfield rows ascend north; the runtime samples with `north = -z` and the exact terrain triangle diagonal, not bilinear interpolation.

Record horizontal CRS, vertical datum, units and origin explicitly. Targets and measured accuracy are distinct. Candidate IDs are location-derived seeds, not independently verified institutional identities. Named anchors and explicit approximate envelopes retain their own provenance.

Keep raw, blockout, detailed and optimized assets related by stable identity. Materials target exchangeable PBR representations; future collision proxies should be separate from high-resolution display meshes.

## Viewer

The browser consumes `manifest.json`, GLB and heightfield; it does not reconstruct LiDAR or edit Blender source. Shared modules implement three views, walking/jump/collision, building search, camera framing, billboard labels, selection, minimap and settings. A profile supplies local branding and source text. Runtime preferences supply spawn heading.

The live site is publicly accessible through Sites. The hosting identity is in `apps/web-preview/.openai/hosting.json`; credentials are never committed. See [hosting](hosting.md) and [template adoption](viewer-template.md).

Godot, Unity and Unreal remain optional asset consumers. Cross-engine validation, streamed tiles, LOD and 3D Gaussian Splatting are future work. 3DGS would complement editable meshes, not replace their core geometry or collisions.
