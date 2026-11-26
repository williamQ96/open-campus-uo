# SPDX-License-Identifier: Apache-2.0
"""Build the registered Many Nations Longhouse exterior and east approach."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-straub-earl-site-review.py")
loader = spec_from_file_location(source.stem, source)
site = module_from_spec(loader)
loader.loader.exec_module(site)
geometry, tools = site.geometry, site.tools
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/longhouse-site-review.json"
DIRECTORY = "longhouse-review"
GROUND = "longhouse-approach"
TIMBER = (97, 77, 61)
BOARDS = [(100, 81, 67), (110, 88, 71), (105, 85, 69), (94, 77, 65)]
DARK = (67, 58, 49)
SILL = (152, 142, 125)
GLASS = (81, 108, 113)
ROOF = (135, 137, 97)
FASCIA = (136, 128, 110)
HOOD = (159, 165, 156)
PAVING = (162, 156, 142)


def roof_layer(parts, area, roof_at, depth, offset, wall, roof):
    """Shear a shallow prism to give both faces the same roof pitch."""
    prisms = []
    site.flat(prisms, area, offset - depth, offset, wall, roof)
    for mesh in prisms:
        points = mesh.vertices.copy()
        points[:, 1] += roof_at(points[:, 0], -points[:, 2])
        mesh.vertices = points
        parts.append(mesh)


def roof_details(parts, spec, roof_at):
    outline = Polygon(spec["roof_outline_enu_m"])
    cover = outline.buffer(-0.22, join_style="mitre")
    roof_layer(parts, outline, roof_at, 0.29, 0, DARK, FASCIA)
    roof_layer(parts, cover, roof_at, 0.04, 0.05, FASCIA, ROOF)
    w, s, e, n = cover.bounds
    for left, low, right, high, color in [
        (w + 0.32, s + 0.7, w + 3.44, n - 2.2, (126, 132, 93)),
        (w + 3.68, s + 0.5, e - 2.63, s + 5.5, (143, 137, 100)),
        (e - 2.50, s + 2.6, e - 0.35, n - 1.2, (128, 133, 93)),
        (w + 4.08, n - 5.88, e - 2.65, n - 0.46, (137, 139, 96)),
    ]:
        roof_layer(
            parts, box(left, low, right, high), roof_at, 0.014, 0.059, ROOF, color
        )
    hood = spec["roof_hood"]
    body = box(*hood["bounds_enu_m"])
    hood_top = hood["rise_m"]
    roof_layer(parts, body, roof_at, hood_top, hood_top, DARK, HOOD)
    roof_layer(
        parts,
        body.buffer(0.12, join_style="mitre"),
        roof_at,
        0.08,
        hood_top + 0.08,
        HOOD,
        HOOD,
    )


def glazing(add, left, right, bottom, top):
    add(left, right, 0.009, 0.045, bottom, top, GLASS)
    for i, x in enumerate(np.linspace(left, right, 10)):
        post = 0.085 if i % 3 == 0 else 0.034
        low = bottom if i % 3 == 0 else top - 1.36
        add(x - post, x + post, 0.044, 0.107, low, top, SILL if i % 3 == 0 else DARK)
    for z in (bottom, bottom + 1.32, bottom + 2.62, top - 1.36, top):
        add(left - 0.07, right + 0.07, 0.042, 0.115, z - 0.051, z + 0.051, SILL)
    add(left - 0.09, right + 0.09, 0.018, 0.31, top + 0.08, top + 0.15, DARK)


def siding(parts, spec, plan, field, roof_at, entry, floor):
    n0 = plan.bounds[1]
    for a, b in zip(plan.exterior.coords, list(plan.exterior.coords)[1:]):
        length, add = tools.face(parts, a, b)
        step = (np.asarray(b) - a) / length
        p = (np.asarray(a) + b) / 2
        visible_grade = geometry.sample_ground(field, *p)
        bottom = max(floor, visible_grade - 0.22)
        openings = []
        if a[1] == b[1] == n0:
            window = spec["south_window"]
            left, right = (e - a[0] for e in window["east_range_m"])
            low = visible_grade + window["base_above_grade_m"]
            top = window["top_z_m"]
            glazing(add, left, right, low, top)
            openings.append((left - 0.07, right + 0.07, low, top))
        elif a[0] == b[0] == plan.bounds[2]:
            center = entry["position_enu_m"][1] - a[1]
            width = entry["width_m"]
            low = entry["threshold_z_m"]
            site.allen.doors(add, center, width, low)
            openings.append(
                (
                    center - width / 2 - 0.1,
                    center + width / 2 + 0.1,
                    low - 0.08,
                    low + 2.48,
                )
            )
            add(center - 1.17, center + 1.17, 0.015, 1.02, low + 2.66, low + 2.84, DARK)
        elif a[1] == b[1] == plan.bounds[3] or a[0] == b[0] == plan.bounds[0]:
            center = (
                a[0] - spec["north_door_east_m"]
                if a[1] == b[1]
                else a[1] - spec["west_door_north_m"]
            )
            width = 1.53
            low = geometry.sample_ground(field, *(np.asarray(a) + step * center)) + 0.14
            add(
                center - width / 2,
                center + width / 2,
                0.018,
                0.057,
                low,
                low + 2.22,
                DARK,
            )
            add(
                center - 0.018,
                center + 0.018,
                0.057,
                0.079,
                low + 0.08,
                low + 2.14,
                SILL,
            )
            openings.append(
                (center - width / 2, center + width / 2, low - 0.10, low + 2.22)
            )
        count = max(1, round(length / 0.185))
        for i in range(count):
            x, end = i * length / count, (i + 1) * length / count
            top = min(roof_at(*(np.asarray(a) + step * t)) for t in (x, end)) - 0.20
            slots = [(bottom, top)]
            for left, right, low, high in openings:
                if end > left and x < right:
                    slots = [(bottom, min(top, low)), (max(bottom, high), top)]
            for low, high in slots:
                if high - low > 0.015 and end - x > 0.016:
                    add(
                        x + 0.006,
                        end - 0.006,
                        0.005,
                        0.035,
                        low,
                        high,
                        BOARDS[(i * 7 + i // 4) % len(BOARDS)],
                    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    plan = orient(Polygon(spec["footprint_enu_m"]))
    old = next(row for row in manifest["buildings"] if row["id"] == spec["id"])
    prior = Polygon(old["footprint_enu_m"])
    assert plan.is_valid and Polygon(spec["roof_outline_enu_m"]).contains(plan)
    checked = []
    for record in manifest["buildings"]:
        if record["id"] != spec["id"]:
            assert (
                plan.intersection(Polygon(record["footprint_enu_m"]).buffer(0)).area
                < 0.02
            ), record["id"]
    for i, (a, b, *_) in enumerate(graph["edges"]):
        edge = LineString([graph["nodes_enu_m"][a], graph["nodes_enu_m"][b]])
        if edge.distance(plan) < 0.42 <= edge.distance(prior):
            checked.append(i)
    assert not checked, checked

    origin_e, origin_n, z, east_slope, north_slope = spec["roof_plane"]

    def roof_at(e, n):
        return z + (e - origin_e) * east_slope + (n - origin_n) * north_slope

    ring = plan.exterior
    base = (
        min(
            geometry.sample_ground(field, *ring.interpolate(distance).coords[0])
            for distance in np.arange(0, ring.length, 0.5)
        )
        - 0.38
    )
    parts, approaches = [], []
    gate = spec["entrances"][0]
    assert ring.distance(Point(gate["position_enu_m"])) < 0.0001
    entry, paving = site.approach(approaches, field, gate)
    approaches.append(
        tools.approaches(
            [{"outline": list(paving.exterior.coords), "rgb": PAVING}],
            field,
            plan,
        )
    )
    site.surface(parts, plan, base, lambda e, n: roof_at(e, n) - 0.17, TIMBER, DARK)
    siding(parts, spec, plan, field, roof_at, entry, base)
    roof_details(parts, spec, roof_at)
    mesh = trimesh.util.concatenate(parts)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
    ground = trimesh.util.concatenate(approaches)
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = tools.load_builder(
        "build-frohnmayer-exterior-review.py"
    ).source_removals(spec, config, appearances)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb, {spec["id"]: mesh}, ground, GROUND, "longhouse-paving"
    )
    descriptor = out / "site.json"
    record = {k: spec[k] for k in ("name", "id", "campus_id", "footprint_enu_m")}
    record.update(
        area_m2=round(plan.area, 2),
        base_z_m=round(base, 4),
        roof_z_m=round(float(mesh.bounds[1, 1]), 4),
        entrances=[entry],
    )
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        ground_node=GROUND,
        buildings=[record],
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    config["longhouse_site"] = {
        "url": f"{DIRECTORY}/site.json",
        "sha256": tools.digest(descriptor),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    audit = dict(
        footprint_m2=record["area_m2"],
        old_footprint_overlap_m2=round(plan.intersection(prior).area, 2),
        elevations_m=[record["base_z_m"], record["roof_z_m"]],
        east_entry=entry,
        triangle_count=len(mesh.faces),
        approach_triangles=len(ground.faces),
        route_edges=len(graph["edges"]),
        new_conflicts=checked,
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
