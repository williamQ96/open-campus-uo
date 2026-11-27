# SPDX-License-Identifier: Apache-2.0
"""Register the cemetery's western tree belt and the verge beside Frohnmayer."""

import argparse
from copy import deepcopy
from importlib import import_module
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Point, box
from shapely.ops import unary_union

drive = import_module("build-frohnmayer-east-drive")
inner = import_module("build-pioneer-cemetery-inner-grid")
site, cemetery = drive.site, drive.east18.cemetery
PACKAGE = "pioneer-cemetery-west-trees-review"
GROUND = "pioneer-west-verge"
CANOPY = "pioneer-west-trees"
UNDERSTORY = "pioneer-west-understory"

# The local crown profiles use the recorded inventory dimensions and distinguish
# broad fir tiers, slender incense cedars and the lower red-cedar skirts.
CONIFERS = {
    "fir": (0.34, (0.86, 1.0, 0.87, 0.70, 0.51, 0.33, 0.18), (71, 96, 68)),
    "incense-cedar": (0.30, (0.54, 0.83, 1.0, 0.93, 0.74, 0.53, 0.26), (89, 109, 65)),
    "red-cedar": (0.24, (0.84, 1.0, 0.93, 0.77, 0.57, 0.42, 0.24), (77, 105, 71)),
}


def conifer(parts, center, height, radius, form, phase):
    e, n, z = center
    bottom, profile, shade = CONIFERS[form]
    vertices, faces, colors = [], [], []
    for level, spread in enumerate(profile):
        fraction = bottom + (0.98 - bottom) * level / len(profile)
        tip = min(1.0, fraction + 0.19)
        ring = []
        for sector in range(14):
            angle = phase + level * 0.22 + sector * np.pi / 7
            reach = spread * radius * (0.91 + 0.09 * np.sin(angle * 5 + phase))
            h = height * (fraction + 0.012 * np.cos(angle * 3))
            ring.append((e + reach * np.cos(angle), z + h, -n - reach * np.sin(angle)))
        for sector, a in enumerate(ring):
            b = ring[(sector + 1) % len(ring)]
            i = len(vertices)
            vertices.extend([a, b, (e, z + height * tip, -n), (e, z + height * (fraction - 0.023), -n)])
            faces.extend([(i, i + 2, i + 1), (i, i + 1, i + 3)])
            tone = 2 * ((sector + level) % 5 - 2)
            colors.extend([tuple(c + tone for c in shade) + (255,)] * 4)
    crown = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    crown.visual.vertex_colors = np.asarray(colors, dtype=np.uint8)
    parts.append(crown)


def branched_crown(parts, center, height, spread, trunk, form, phase):
    e, n, z = center
    pine = form == "pine"
    palette = [(97, 120, 73), (106, 129, 82), (118, 138, 90)]
    if pine:
        palette = [(101, 120, 67), (109, 127, 74), (91, 111, 68)]
    for branch in range(7):
        angle = phase + branch * np.pi * 2 / 7
        reach = spread * (0.39 + (branch % 3) * 0.09)
        branch_height = height * ((0.72 if pine else 0.66) + 0.033 * (branch % 3))
        crown = (e + reach * np.cos(angle), n + reach * np.sin(angle), z + branch_height)
        site.cylinder_between(
            parts, (e, n, z + height * (0.48 if pine else 0.39)), crown,
            max(0.016, trunk * 0.28), (106, 88, 66), sides=6,
        )
        site.orb(
            parts, crown,
            (spread * 0.48, spread * 0.44, height * (0.116 if pine else 0.155)),
            palette[branch % 3],
        )
    site.orb(parts, (e, n, z + height * 0.89), (spread * 0.39, spread * 0.39, height * 0.11), palette[1])


def make_tree(parts, field, tree, index):
    e, n = tree["position_enu_m"]
    z = site.ground_height(field, e, n)
    height, spread, trunk = (tree[k] for k in ("height_m", "crown_radius_m", "trunk_radius_m"))
    form = tree["form"]
    phase = index * 2.399963
    bark = (104, 84, 64) if form.endswith("cedar") else (92, 80, 65)
    site.cylinder_between(
        parts, (e, n, z - 0.14), (e, n, z + height * 0.57), trunk, bark, sides=9
    )
    site.cylinder_between(
        parts, (e, n, z + height * 0.53), (e, n, z + height * 0.91),
        max(0.014, trunk * 0.56), bark, sides=7,
    )
    if form in CONIFERS:
        conifer(parts, (e, n, z), height, spread, form, phase)
    else:
        branched_crown(parts, (e, n, z), height, spread, trunk, form, phase)


def build(spec, metadata, stage, audit):
    road_spec = site.read(metadata / "frohnmayer-east-drive.json")
    manifest, field, _ = drive.green.east.pinned_site(site.scene, road_spec)
    for pin, package in (
        ("frohnmayer", drive.PACKAGE),
        ("cemetery", cemetery.PACKAGE),
        ("southwest_green", drive.green.PACKAGE),
    ):
        assert site.pin(site.scene / package / "site.json") == spec["pins"][pin]
    road, paths, _, city, blocked, previous_verge, lot = drive.footprints(
        road_spec, manifest, metadata
    )
    wider = deepcopy(road_spec)
    wider["legacy_road"]["verge_blend_m"] = spec["additional_verge_blend_m"]
    *_, full_verge, _ = drive.footprints(wider, manifest, metadata)
    verge = full_verge.difference(previous_verge)
    base = site.read(metadata / "pioneer-cemetery-landscape-review.json")
    conger, approach = cemetery.named_path_footprints(base)
    assert verge.area > 80 and verge.distance(conger) > 2.0
    access = unary_union([road, paths, city, blocked, lot, conger, approach])
    terrain, trees, shrubs, solids = [], [], [], []
    site.drape(terrain, field, verge, tuple(road_spec["legacy_road"]["turf_color_srgb"]), 0.087, 0.65)
    minimum = float("inf")
    for i, row in enumerate(spec["trees"]):
        e, n = row["position_enu_m"]
        r = row["trunk_radius_m"]
        trunk = box(e - r, n - r, e + r, n + r)
        clearance = trunk.distance(access)
        assert clearance > 0.60, (row["inventory_id"], clearance)
        minimum = min(minimum, clearance)
        make_tree(shrubs if row["form"] == "understory" else trees, field, row, i)
        if row["solid_trunk"]:
            solids.append(trunk.bounds)
    assert len(solids) == 16
    for row in spec["low_plant_groups"]:
        x, y = row["position_enu_m"]
        assert Point(x, y).distance(access) > max(row["spread_m"]) * 0.65
        inner.low_shrub(shrubs, field, row)

    stage.mkdir(parents=True, exist_ok=True)
    model, desc = stage / "site.glb", stage / "site.json"
    faces = site.export(
        model,
        (GROUND, terrain, "landscape-surface"),
        (CANOPY, trees, "landscape-vegetation"),
        (UNDERSTORY, shrubs, "landscape-vegetation"),
        surface_layer=GROUND,
    )
    p = road_spec["pins"]
    site.fairmount.write_json(
        desc,
        {
            "source_presentation_sha256": p["presentation"],
            "source_base_model_sha256": p["model"],
            "source_heightfield_sha256": p["heightfield"],
            "prerequisite_site_sha256": spec["pins"]["frohnmayer"],
            "ground_node": GROUND,
            "url": f"{PACKAGE}/site.glb",
            "sha256": site.pin(model),
            "buildings": [],
            "closed_site_boxes_enu_m": solids,
        },
        compact=True,
    )
    report = {
        "mature_tree_count": sum(row["form"] != "understory" for row in spec["trees"]),
        "inventory_understory_count": sum(row["form"] == "understory" for row in spec["trees"]),
        "low_plant_groups": len(spec["low_plant_groups"]),
        "solid_stems": len(solids),
        "minimum_trunk_clearance_m": round(minimum, 3),
        "verge_extension_m2": round(verge.area, 2),
        "faces": faces,
        "asset_sha256": site.pin(model),
        "descriptor_sha256": site.pin(desc),
    }
    site.fairmount.write_json(audit, report)
    print(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    metadata = site.root / "data/metadata"
    build(site.read(metadata / "pioneer-cemetery-west-trees.json"), metadata, args.stage, args.audit)


if __name__ == "__main__":
    main()
