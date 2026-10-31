**English** | [简体中文](zh-CN/source-discussion.md)

# Source discussion and effective decisions

The initial [shared campus-modeling discussion](https://chatgpt.com/share/6ae54fb0-e6cc-83e8-8958-51a084c6b7cb?ogimg=plain) was read on 2026-10-30. This record keeps project decisions, not personal material or draft emails.

The scope evolved from GIS/LiDAR/photogrammetry/3DGS research and a possible Unreal campus toward a Blender-first, engine-independent asset library. The user requested a reproducible small-area loop, followed by campus and per-building refinement, and a Three.js browser consumer.

UO internal GIS is excluded; no request email is required or sent. OSM, Microsoft/Oregon footprint compilations, Eugene GIS and Google 3D are not core geometry inputs for this version. Verified NOAA-hosted DOGAMI point clouds were adopted; the AOI-all-NoData DEM was rejected. Source evidence is in [source-audit.json](../data/metadata/source-audit.json).

The two repositories were initially private. The user subsequently made Open Campus: UO public and requested anonymous website access, English-first documentation with Chinese alternatives, and a reusable upstream viewer template. The user then explicitly authorized making the upstream repository public as well; both repositories are now public.

The generic pipeline and UO project remain long-lived with distinct responsibilities. Blender is the editable source, GLB/glTF plus metadata are the interchange, and 3DGS is an optional future enhancement. Tool prices, performance targets and licensing suggestions from the old discussion are not treated as measured results or current guarantees.
