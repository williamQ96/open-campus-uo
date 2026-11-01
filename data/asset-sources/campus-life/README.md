# Campus ambience source archive

**English** | [简体中文](README.zh-CN.md)

Reviewed 2026-10-31. Original downloads remain here; adapted portable assets and editable source stay in the project. Exact bytes and SHA-256 are recorded in [the asset manifest](../manifest.json). [Structured provenance](sources.json) records creator pages, license review, download URLs and modifications.

| Asset | Creator / license | Original and use |
| --- | --- | --- |
| [Tree squirrel](https://www.innerscene.com/tools/library/3d-parts/tree-squirrel-6499352e) | Innerscene, CC0-1.0 | `tree-squirrel.glb` is unchanged. Original static model simplified to about 900 faces, one brown flat material and 0.55 m silhouette; no source texture is used. |
| [Overworld (BGM)](https://opengameart.org/content/overworld-bgm) | IntelligentGene; optional credit **Another Page Studio**, CC0-1.0 | `overworld.mp3` is unchanged; identical runtime copy loops quietly. Creator describes a calm, minimal looping track. |
| Soft footstep | Open Campus contributors, CC0-1.0 | Original deterministic noise/tone synthesis from `scripts/generate-footstep.py`; no third-party recording. Output is `apps/web-preview/public/audio/footstep.wav`. |

The [CC0 legal text](CC0-1.0.txt) accompanies the source records. CC0 sources remain CC0. Original squirrel adaptation contributions are CC BY 4.0, credited to Zhongyi “William” Qiu and Open Campus contributors; scripts are Apache-2.0. The squirrel is a generic illustrative animal, not a measured campus species record. It is a static mesh with procedural route motion, brief pauses and bobbing, not a newly rigged animal.

Rebuild from the repository root:

```powershell
blender --background --python scripts/build-campus-squirrel.py
python scripts/generate-footstep.py
python scripts/check-open-assets.py
```

`assets/animals/campus-squirrel.blend` and `apps/web-preview/public/animals/campus-squirrel.glb` retain the adapted model. Rebuilding a binary may change its bytes; inspect the result and update its manifest deliberately. No proprietary map model, Google imagery, branded vehicle or restrictive marketplace asset is included.
