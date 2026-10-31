**English** | [简体中文](zh-CN/viewer-template.md)

# Shared explorer template

Open Campus: UO is the first downstream of the generic browser explorer maintained in [the upstream repository](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline). Its [downstream registry](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/downstream-projects.md) can grow to other maps.

The managed runtime includes the three camera modes, 45° building framing, movement/collision/jump, wheel zoom, search, billboard labels, minimap, selection and Settings / About. UO content remains in `public/viewer-profile.json`, `public/scene/`, branding assets, source catalogs and original Blender models.

`viewer-template.lock.json` records the upstream template revision and SHA-256 of managed files. `pipeline.lock.json` independently pins reconstruction. A UI update must not relabel historical geometry; when asset attribution or reconstruction changes are deliberately rebuilt, update that separate reconstruction evidence too.

## Upgrade

With upstream Python installed, run `python -m geospatial3d sync-viewer --output /path/to/open-campus-uo/apps/web-preview`. It checks existing managed hashes before replacement and preserves project profiles, scene data, hosting identity and package settings. `--adopt` is for the initial approved adoption; later upgrades should resolve local shared-code edits explicitly.

Run movement and real-campus browser tests, compare UI/source acknowledgements, and rebuild the static site before publication. The canonical template has its own synthetic browser regression, without copying UO buildings or coordinates upstream.

Code/template software is Apache-2.0. Original documentation and model/design contributions are CC BY 4.0; see [licensing](../LICENSING.md). Third-party source terms and notices remain independent.
