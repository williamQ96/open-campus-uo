**English** | [简体中文](README.zh-CN.md)

# Data management

Verified NOAA/DOGAMI historical LiDAR is recorded in `metadata/source-audit.json` and `metadata/main-campus-audit.json`. Roads and semantic annotations have their own catalogs and audits. The 2021 DEM with no valid AOI samples was excluded.

- `raw/`: ignored large source point clouds, imagery, rasters and reference downloads.
- `processed/`: ignored intermediate results.
- `metadata/`: committed source evidence, dates, CRS/units, checksums, license references and validation status.
- [`reference-images/`](reference-images/README.md): committed, rights-reviewed image/photo inputs and project artwork, with a per-file manifest, attribution and source evidence. This is separate from ignored research downloads; unverified historical photos remain excluded and cited.

Each adopted input needs provider/product IDs, URL, acquisition/access dates when known, coverage, horizontal/vertical frame, units, hash, use terms and verification status. Unknown facts remain explicitly unknown.

Editable Blender source and browser-ready GLB/heightfields are versioned in their respective asset/application locations. Large raw LAZ files and rejected rasters are not committed. The public website serves application exports; raw-source storage and original-asset attribution are recorded separately.
