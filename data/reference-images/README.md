**English** | [简体中文](README.zh-CN.md)

# Image and photo archive

This is the versioned source-material directory for Open Campus: UO. It contains **7 licensed ground photographs, one dated USDA NAIP aerial subset and 5 project-design images** (the concept mockup, identity board, logo, mark and favicon), with downloaded bytes retained; the aerial record describes its service-side crop/reprojection. Original design locations and runtime brand files are preserved; their byte-identical archive copies are linked in the manifest.

- [Manifest](manifest.json): local files, authors, source/download links, capture/access dates, license evidence, building/use links, modifications and SHA-256/byte size.
- [Attribution](ATTRIBUTION.md): credits and license links for each image.
- [Source evidence](evidence.json): selected dated source declarations and manual review notes.
- [Historical modeling references](../metadata/visual-pilot-references.json): preserved v0.6 citations, including sources excluded from redistribution.
- [Reusable upstream policy and checker](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/reference-media.md).

## Photographs

| Building | Archived views | Date / limits |
| --- | --- | --- |
| [Knight Library](photos/knight-library/) · `roof-6684e091` | Two oblique views of the historic north facade; exterior light detail | Facades: 2018-07-11; light: 2017-06-26. The second facade image is not a separate side-elevation survey. |
| [Johnson Hall](photos/johnson-hall/) · `roof-906c030e` | Front portico and rear entrance | Rear: 2012-07-25. Front capture date unknown; uploaded 2006-06-06, which is not a capture date. |
| [Erb Memorial Union](photos/erb-memorial-union/) · `roof-266f13fd` | Historical University Street/Fishbowl entrance and post-renovation exterior | 2013-10-19 entrance predates the 2016 renovation; 2017-11-03 exterior is not evidence of 2026 conditions. |

These photos now inform the [v0.7 modular landmark refinement](../../docs/visual-refinement-v0.7.md). The initial archive update did not regenerate v0.6; its history remains in the [pilot report](../../docs/visual-pilot.md). The subsequent v0.7 pass rebuilds the art layer from these references and a [2024-06-08 NAIP aerial subset](aerial/naip-2024-pilot-rgb.png), with approximate dimensions and no photo textures. The aerial [export request/georeference](../metadata/naip-2024-reference.json) is retained separately from the PNG.

## Project artwork and outputs

[Project artwork](project/) contains the unchanged original AI-generated campus concept and Open Courtyard branding. The concept illustrates style only; it is not an actual campus photograph, model screenshot or geographic dataset. AI origin and the scope of project-held rights are recorded in the manifest and [original design provenance](../../design/architectural-toon-realism/provenance.json). Original identity generation source remains in [design-logo.py](../../scripts/design-logo.py).

The v0.6 and v0.7 rendered review screenshots remain in [docs/images](../../docs/images/) and are indexed under `related_outputs` in the manifest. They are outputs, not photo inputs. The [design archive](../../design/README.md), original identity PDF and source palette remain at their existing paths. This research archive is outside the web application's `public/` directory, so the app does not download it.

## Rights and intake

Third-party photographs retain their per-file **CC BY 4.0, CC0 or PD-self** status; the USDA aerial subset retains its explicitly declared public-domain status as `LicenseRef-PD-USGov`. Do not relicense them under the generic project license. Credit Gary Halvorson / Oregon State Archives and Rick Obst as specified; Daderot and Adam850 are also credited for provenance even where attribution is not required by their public-domain terms. The project artwork follows [project licensing](../../LICENSING.md), limited to rights held; no trademark rights or institutional endorsement are granted.

The three UO official photographs previously consulted were not approved for redistribution and remain **historical link-only records**, with their exclusion status and replacement reference IDs preserved. Their bytes are not in this public archive or in GLB textures. The supplied Google Maps satellite screenshot is area-of-interest context only: no screenshot pixels, traced footprints, tiles or Google 3D assets are imported into this archive or the model pipeline.

For new work, archive the original image only after confirming a source that permits the intended open redistribution, modification and asset export. Avoid unknown rights, NC, ND and provider-restricted sources; use an approved replacement. Record the source and license decision before modeling, keep original and edited files linked, and update both manifest and credits when an image changes. Check new uses and derived assets as well as image rights. A photo's date, orientation and limitations remain part of the modeling evidence.

## Audit

With a checkout of the upstream repository:

```powershell
python ../open-geospatial-to-3d-reconstruction-pipeline/scripts/check-reference-media.py --root .
```

Run from this project root. The `reference-media` CI job uses an explicitly pinned upstream checker revision. It verifies image registration, recorded metadata and hashes, not the underlying legal claims or architectural accuracy. The archive/checker update leaves the independent reconstruction and viewer-runtime locks unchanged.
