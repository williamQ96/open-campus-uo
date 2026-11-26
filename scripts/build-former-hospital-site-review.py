# SPDX-License-Identifier: Apache-2.0
"""Build the observed early construction phase on the former hospital site."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import LineString, Point, Polygon, box
import trimesh

source = Path(__file__).with_name("build-university-district-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
district = module_from_spec(loader)
loader.loader.exec_module(district)
ROOT, SCENE = district.houses.ROOT, district.houses.SCENE
base, geometry, design = district.base, district.geometry, district.design

PACKAGE = "former-hospital-site-review"
GROUND = "former-hospital-construction"
KEY = "former_hospital_site"
SOIL = (147, 123, 98)
GRAVEL = (164, 150, 128)
CONCRETE = (176, 170, 151)
TIMBER = (174, 117, 76)
TIMBER_EDGE = (137, 90, 58)
STEEL = (128, 133, 125)
WIRE = (112, 115, 109)
CRANE = (164, 151, 105)
BARRIER = (180, 103, 48)


def grade(field, point):
    return geometry.sample_ground(field, *point)


def draped(field, area, color):
    return design.tools.approaches(
        [
            {"outline": list(piece.exterior.coords), "rgb": color}
            for piece in geometry.sections(area)
        ],
        field,
        Polygon(),
    )


def varied_yard(field, area):
    mesh = draped(field, area, SOIL)
    e, _, south = mesh.vertices.T
    variation = 4.5 * np.sin(e * 0.83 + south * 0.40) + 3.0 * np.cos(
        e * 1.47 - south * 1.13
    )
    mesh.visual.vertex_colors[:, :3] = np.round(
        np.asarray(SOIL)[None, :] + variation[:, None]
    )
    return mesh


def rod(parts, a, b, width, color):
    design.tools.beam(parts, np.asarray(a), np.asarray(b), width, color)


def fence(parts, field, line):
    stations = np.linspace(0, line.length, round(line.length / 2.8) + 1)
    posts = [line.interpolate(x).coords[0] for x in stations]
    for east, north in posts:
        y = grade(field, (east, north))
        base.flat(
            parts,
            box(east - 0.028, north - 0.028, east + 0.028, north + 0.028),
            y - 0.04,
            y + 1.97,
            STEEL,
        )
        base.flat(
            parts,
            box(east - 0.115, north - 0.094, east + 0.115, north + 0.094),
            y - 0.025,
            y + 0.082,
            CONCRETE,
        )
    for first, last in zip(posts[:-1], posts[1:]):
        za, zb = grade(field, first), grade(field, last)
        for z in (0.12, 0.97, 1.87):
            rod(parts, (*first, za + z), (*last, zb + z), 0.026, STEEL)
        for i in range(1, 6):
            t = i / 7
            a = tuple((1 - t) * np.asarray(first) + t * np.asarray(last))
            b = tuple((1 - t - 0.1) * np.asarray(first) + (t + 0.1) * np.asarray(last))
            z0, z1 = (1 - t) * za + t * zb, (1 - t - 0.1) * za + (t + 0.1) * zb
            rod(parts, (*a, z0 + 0.17), (*b, z1 + 1.83), 0.011, WIRE)


def timber_wall(parts, start, stop, datum, windows=True):
    width, add, _, plan, _, _ = district.chapter.setup_face(parts, start, stop)
    height = 3.28
    for z in (0.00, 3.18, 3.24):
        add(0, width, -0.079, 0.075, datum + z, datum + z + 0.052, TIMBER_EDGE)
    divisions = max(1, round(width / 3.7))
    for i in range(divisions):
        a, b = i * width / divisions, (i + 1) * width / divisions
        window = (a + (b - a) * 0.27, a + (b - a) * 0.74)
        for x in np.linspace(a + 0.032, b - 0.032, max(3, round((b - a) / 0.39))):
            if windows and window[0] < x < window[1]:
                for lower, upper in ((0.05, 0.86), (2.39, height)):
                    add(
                        x - 0.025,
                        x + 0.025,
                        -0.066,
                        0.066,
                        datum + lower,
                        datum + upper,
                        TIMBER,
                    )
            else:
                add(
                    x - 0.025,
                    x + 0.025,
                    -0.066,
                    0.066,
                    datum + 0.05,
                    datum + height,
                    TIMBER,
                )
        if windows:
            if i % 4 == 1:
                first = plan(a + 0.15, 0.11)
                last = plan(b - 0.15, 0.11)
                rod(
                    parts,
                    (*first, datum + 0.2),
                    (*last, datum + 2.94),
                    0.075,
                    TIMBER_EDGE,
                )
                rod(
                    parts,
                    (*last, datum + 0.2),
                    (*first, datum + 2.94),
                    0.075,
                    TIMBER_EDGE,
                )
            left, right = window
            for x in (left, right):
                add(
                    x - 0.04,
                    x + 0.04,
                    -0.074,
                    0.074,
                    datum + 0.05,
                    datum + height,
                    TIMBER_EDGE,
                )
            for z in (0.84, 2.38):
                add(
                    left,
                    right,
                    -0.075,
                    0.075,
                    datum + z,
                    datum + z + 0.073,
                    TIMBER_EDGE,
                )


def framing(parts, field, spec, parcel):
    depth = spec["framing_return_depth_m"]
    for i, (first, last) in enumerate(spec["south_framing_runs_enu_m"]):
        west, south = first
        east, _ = last
        platform = box(west - 0.09, south - 0.10, east + 0.09, south + depth)
        assert parcel.covers(platform)
        level = grade(field, platform.centroid.coords[0]) + 0.43
        base.flat(parts, platform, level - 0.42, level, (124, 126, 127), CONCRETE)
        timber_wall(parts, first, last, level)
        for start, direction in [(first, 1), (last, -1)]:
            e, n = start
            stop = (e, n + min(depth - 0.4, 5.6 if i % 2 else 8.2))
            timber_wall(
                parts,
                start if direction > 0 else stop,
                stop if direction > 0 else start,
                level,
                windows=False,
            )


def tower_crane(parts, field, position):
    e, n = position
    floor = grade(field, position)
    size, height = 0.77, 31.25
    posts = [
        (e - size, n - size),
        (e + size, n - size),
        (e + size, n + size),
        (e - size, n + size),
    ]
    base.flat(
        parts,
        box(e - 1.25, n - 1.25, e + 1.25, n + 1.25),
        floor - 0.10,
        floor + 0.20,
        CONCRETE,
    )
    for p in posts:
        rod(parts, (*p, floor), (*p, floor + height), 0.08, CRANE)
    for y in np.linspace(floor + 0.24, floor + height, 18)[:-1]:
        for i, a in enumerate(posts):
            b = posts[(i + 1) % 4]
            rod(parts, (*a, y), (*b, y), 0.046, CRANE)
            rod(parts, (*a, y), (*b, y + 1.82), 0.043, CRANE)
    z = floor + height - 0.16
    for y in (n - 0.65, n + 0.65):
        rod(parts, (e - 9, y, z), (e + 28, y, z), 0.095, CRANE)
        rod(parts, (e - 9, y, z + 1.00), (e + 28, y, z + 1.00), 0.074, CRANE)
        for x in np.arange(e - 9, e + 25, 2.8):
            rod(parts, (x, y, z), (x + 2.8, y, z + 1.00), 0.044, CRANE)
    base.flat(parts, box(e - 9, n - 0.65, e - 6.9, n + 0.65), z - 0.72, z + 0.49, STEEL)
    rod(parts, (e, n, z + 1.02), (e, n, z + 3.9), 0.082, CRANE)
    for x in (e - 8.7, e + 24):
        rod(parts, (e, n, z + 3.9), (x, n, z + 0.98), 0.037, STEEL)


def make_site(spec, field):
    lots = {key: Polygon(ring) for key, ring in spec["taxlots_enu_m"].items()}
    south, north = lots["1703323104701"], lots["1703323104702"]
    fenced = Polygon(spec["construction_fence_enu_m"])
    walk = Polygon(spec["protected_sidewalk_enu_m"])
    assert south.covers(fenced) and walk.distance(fenced) > 1.0
    yard = fenced.buffer(-0.10)
    assert fenced.covers(Point(spec["tower_crane_enu_m"]))
    old_roofs = union_all(
        [Polygon(ring) for ring in spec["former_roofs_enu_m"].values()]
    )
    cleared = old_roofs.buffer(0.38).intersection(north.buffer(-0.35))
    parts = [
        varied_yard(field, yard),
        draped(field, cleared, GRAVEL),
        draped(field, walk, CONCRETE),
    ]
    for a, b in zip(fenced.exterior.coords[:-1], fenced.exterior.coords[1:]):
        fence(parts, field, LineString([a, b]))
    fence(parts, field, LineString(spec["closed_sidewalk_enu_m"]))
    for e, n in [(-900.67, 16.45), (-900.68, 183.98), (-887.8, 12.48), (-771.5, 12.52)]:
        z = grade(field, (e, n))
        base.flat(
            parts, box(e - 0.44, n - 0.13, e + 0.44, n + 0.13), z, z + 0.29, CONCRETE
        )
        base.flat(
            parts,
            box(e - 0.035, n - 0.033, e + 0.035, n + 0.033),
            z + 0.28,
            z + 1.09,
            BARRIER,
        )
    framing(parts, field, spec, yard)
    tower_crane(parts, field, spec["tower_crane_enu_m"])
    return design.science.ordered_mesh(trimesh.util.concatenate(parts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(
        (ROOT / "data/metadata/former-hospital-site-review.json").read_bytes()
    )
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [
        json.loads(path.read_bytes()) for path in (manifest_path, config_path)
    ]
    field_path = SCENE / manifest["heightfield_url"]
    digest = design.tools.digest
    assert digest(manifest_path) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    mesh = make_site(spec, json.loads(field_path.read_bytes()))
    appearances = json.loads(
        (ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    targets = {
        id: target
        for target, ids in appearances["context_batches"].items()
        for id in ids
    }
    retired = spec["retired_ids"]
    assert len(retired) == len(set(retired)) == 5
    patches = district.houses.shared.frohnmayer.source_removals(
        {"absorbed_batches": [{"id": id, "target": targets[id]} for id in retired]},
        config,
        appearances,
    )
    output = args.stage or SCENE / PACKAGE
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    design.site.memorial.gerlinger.export(
        model, {}, mesh, GROUND, "former-hospital-surface"
    )
    bundle = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": [],
        "absorbed_ids": retired,
        "batch_removals": patches,
        "closed_site_boxes_enu_m": spec["closed_site_boxes_enu_m"],
        "context_trees": spec["context_trees"],
    }
    descriptor.write_text(
        json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if args.stage is None:
        config[KEY] = {"url": f"{PACKAGE}/site.json", "sha256": digest(descriptor)}
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf8",
            newline="\n",
        )
    facts = {
        "triangles": len(mesh.faces),
        "removed_triangles": sum(b - a for a, b in (p["triangles"] for p in patches)),
        "absorbed_ids": retired,
        "closed_site_boxes_enu_m": spec["closed_site_boxes_enu_m"],
        "glb_sha256": bundle["sha256"],
        "descriptor_sha256": digest(descriptor),
    }
    args.audit.write_text(
        json.dumps(facts, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(facts)


if __name__ == "__main__":
    main()
