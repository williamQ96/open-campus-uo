**English** | [简体中文](MAINTENANCE.zh-CN.md)

# Long-term downstream maintenance

Both projects are maintained independently over the long term.

| Project | Focus |
| --- | --- |
| Upstream Pipeline | Reconstruction methods, algorithms, automation, validation, reproducibility, interchange contracts and reusable viewer behavior |
| Open Campus: UO | Campus data, stable building identities, specific geometry, roofs, facades, materials, paths and the exploration experience |

Reconstruction and viewer versions are pinned separately. `pipeline.lock.json` records the asset-generation revision; `apps/web-preview/viewer-template.lock.json` records the shared renderer and file hashes. Use a separate upstream worktree for the older reconstruction pin rather than relabeling existing assets as newly generated.

Before advancing the reconstruction pin, rebuild a small area and compare provenance, coordinate frame, terrain quality, candidate IDs and browser behavior. Location-quantized candidate IDs can split or merge when methods change; a stable building registry remains a refinement task.

Reusable fixes belong upstream. UO-specific geometry, identities and content stay downstream. Shared viewer upgrades check file hashes before replacing managed code and preserve the scene, project profile, branding and hosting identity. Resolve local code changes explicitly rather than overwriting them.

Maintain adopted image/photo originals in [`data/reference-images/`](data/reference-images/README.md), updating their manifest, attribution, dates, use and hashes with asset changes. Use sources that permit open redistribution, modification and export; preserve historical exclusions and seek approved replacements. The reusable policy/checker lives upstream; CI pins it independently from the reconstruction and viewer runtime.

Automatically generated blockouts must not replace manually refined authoritative assets. Current priorities are candidate cleanup, verified identities and heights, roof/facade refinement, paths and collision, followed by LOD and tiling as needed.

Both repositories and the UO live site are public. Code is Apache-2.0 and original content is CC BY 4.0; third-party terms remain separate.
