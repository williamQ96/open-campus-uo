# SPDX-License-Identifier: Apache-2.0
"""Build the registered East Campus Graduate Village exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-vivian-olum-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/graduate-village-site-review.json"
DIRECTORY = "graduate-village-review"
GROUND = "graduate-village-approaches"
SIDING = (132, 157, 140)
SIDING_SHADE = (119, 145, 131)
BASE = (116, 115, 103)
ROOF = (147, 155, 150)
FASCIA = (194, 200, 184)
TRIM = (215, 218, 197)
GLASS = (80, 109, 111)
PAVING = (167, 162, 151)


def lower_half(bounds, difference):
    """Return the part of the bounding area where a fitted plane is lower."""
    normal, constant = difference[:2], difference[2]
    length = np.linalg.norm(normal)
    if length < 1e-10:
        return box(*bounds) if constant <= 0 else Polygon()
    x0, y0, x1, y1 = bounds
    center = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
    side = (normal @ center + constant) / length
    span = np.hypot(x1 - x0, y1 - y0) + 1.0
    if side > span:
        return Polygon()
    if side < -span:
        return box(*bounds)
    outward = normal / length
    tangent = np.array([-outward[1], outward[0]])
    origin = center - side * outward
    return Polygon(
        [
            origin - tangent * span * 2,
            origin + tangent * span * 2,
            origin + tangent * span * 2 - outward * span * 2,
            origin - tangent * span * 2 - outward * span * 2,
        ]
    )


def roof_cells(region, planes):
    bounds = region.bounds
    for i, plane in enumerate(planes):
        difference = plane - np.delete(planes, i, axis=0)
        facet = region
        for constraint in difference:
            facet = facet.intersection(lower_half(bounds, constraint))
            if facet.area < 0.001:
                break
        if facet.area > 0.001:
            surface = shapely.set_precision(facet, 0.0005)

            def heights(e, n, coeff=plane):
                return e * coeff[0] + n * coeff[1] + coeff[2]

            yield surface, heights


def volume(parts, wall, other, planes, floor, paint):
    planes = np.asarray(planes)
    for area, height in roof_cells(wall, planes):
        site.surface(parts, area, floor, lambda e, n: height(e, n) - 0.10, paint, ROOF)
    eaves = wall.buffer(0.54, join_style="mitre").difference(other)
    for area, height in roof_cells(eaves, planes):
        shared.shared.roof_layer(parts, area, height, 0.155, 0, FASCIA, ROOF)

    def top(e, n):
        return float(np.min(planes @ (e, n, 1)))

    return top


def windows(add, center, width, z, high, bays):
    left, right = center - width / 2, center + width / 2
    add(left - 0.054, right + 0.054, 0.008, 0.115, z - 0.058, high + 0.075, TRIM)
    stops = np.linspace(left, right, bays + 1)
    for i, (a, b) in enumerate(zip(stops, stops[1:])):
        add(
            a + 0.023,
            b - 0.023,
            0.116,
            0.137,
            z + 0.037,
            high - 0.029,
            GLASS if i % 2 else (91, 119, 120),
        )
    for x in stops:
        add(x - 0.022, x + 0.022, 0.135, 0.16, z, high, TRIM)
    add(
        left,
        right,
        0.139,
        0.168,
        z + (high - z) * 0.73,
        z + (high - z) * 0.73 + 0.052,
        TRIM,
    )
    add(left - 0.064, right + 0.064, 0.160, 0.234, z - 0.065, z - 0.002, TRIM)


def facet_details(parts, a, b, roof, levels, gate):
    length, add = tools.face(parts, a, b)
    if length < 1.1:
        return
    way = (np.asarray(b) - a) / length
    minimum = min(roof(*a), roof(*b))
    base = levels[0] - 0.76
    add(0.008, length - 0.008, 0.011, 0.07, base - 0.24, base + 0.24, BASE)
    if length > 2.0:
        add(0.01, 0.11, 0.01, 0.078, base + 0.23, minimum - 0.12, TRIM)
        add(
            length - 0.11, length - 0.01, 0.01, 0.078, base + 0.23, minimum - 0.12, TRIM
        )
    for seam in np.arange(base + 0.31, minimum - 0.29, 0.212):
        if all(abs(seam - (z - 1.06)) > 0.17 for z in levels):
            add(0.009, length - 0.009, 0.007, 0.026, seam, seam + 0.018, SIDING_SHADE)
    for level in levels[1:]:
        band = level - 1.08
        if band < minimum - 0.34:
            add(0.005, length - 0.005, 0.013, 0.111, band, band + 0.17, TRIM)
    if gate is not None:
        center, data = gate
        start = data["threshold_z_m"]
        site.allen.doors(add, center, data["width_m"], start)
        if min(center, length - center) > 1.05:
            add(
                center - 0.99,
                center + 0.99,
                0.031,
                1.09,
                start + 2.41,
                start + 2.55,
                FASCIA,
            )
            add(
                center - 0.095,
                center + 0.095,
                0.045,
                0.22,
                start + 2.59,
                start + 3.19,
                TRIM,
            )
    count = max(1, round(length / 2.62))
    step = length / count
    if step < 1.37:
        return
    for j in range(count):
        center = step * (j + 0.5)
        xy = np.asarray(a) + way * center
        top = roof(*xy)
        for z in levels:
            if z + 1.52 > top - 0.44:
                continue
            if gate is not None and z < levels[0] + 1 and abs(center - gate[0]) < 1.65:
                continue
            width = min(step * 0.70, 1.78 if j % 3 else 1.91)
            windows(add, center, width, z, z + 1.49, 2 if j % 3 else 3)


def elevations(parts, plan, regions, field, gate):
    border = plan.exterior
    ground = float(
        np.median(
            [
                geometry.sample_ground(field, *border.interpolate(d).coords[0])
                for d in np.arange(0, border.length, 1.35)
            ]
        )
    )
    for a, b in zip(border.coords, list(border.coords)[1:]):
        for x, y, roof, floors in site.science.face_spans(a, b, regions):
            edge = shapely.geometry.LineString((x, y))
            point = Point(gate["position_enu_m"])
            match = (
                (edge.project(point), gate) if edge.distance(point) < 0.003 else None
            )
            levels = [ground + 0.83 + 3.00 * i for i in range(floors)]
            facet_details(parts, x, y, roof, levels, match)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    cfg = SCENE / "presentation.json"
    config = json.loads(cfg.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, plans, approaches, ground, gates = {}, [], [], [], [], []
    for model in spec["models"]:
        id = model["id"]
        plan = orient(Polygon(model["footprint_enu_m"]))
        assert plan.is_valid
        floor = (
            min(
                geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
                for d in np.arange(0, plan.exterior.length, 0.52)
            )
            - 0.41
        )
        high = plan.intersection(box(*model["tall_wing_bounds_enu_m"]))
        low = plan.difference(high)
        for region in (low, high):
            assert region.area > 300
        parts = []
        h3 = volume(parts, high, low, model["high_planes"], floor, SIDING_SHADE)
        h2 = volume(parts, low, high, model["low_planes"], floor, SIDING)
        gate, path = site.approach(ground, field, model["entrance"])
        position = Point(gate["position_enu_m"])
        assert plan.boundary.distance(position) < 0.002
        elevations(parts, plan, [(high, h3, 3), (low, h2, 2)], field, gate)
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        meshes[id] = shared.shared.shared.index_mesh(mesh)
        records.append(
            {k: model[k] for k in ("id", "name", "campus_id", "footprint_enu_m")}
            | {
                "area_m2": round(plan.area, 2),
                "base_z_m": round(floor, 4),
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "entrances": [gate],
            }
        )
        approaches.append(dict(outline=list(path.exterior.coords), rgb=PAVING))
        plans.append(plan)
        gates.append(gate)
    assert plans[0].distance(plans[1]) > 10
    collision = shapely.union_all(plans)
    old = shapely.union_all(
        [
            Polygon(x["footprint_enu_m"]).buffer(0)
            for x in manifest["buildings"]
            if x["id"] in meshes
        ]
    )
    route_count, clearance = shared.check_routes(
        plans, [], gates, old, manifest, graph, config, set(meshes)
    )
    neighbors = shapely.union_all(
        [
            Polygon(item["footprint_enu_m"]).buffer(0)
            for item in manifest["buildings"]
            if item["id"] not in meshes
        ]
    )
    for gate in gates:
        anchor = np.asarray(gate["position_enu_m"])
        angle = np.deg2rad(gate["outward_degrees"])
        forward = np.array([np.sin(angle), np.cos(angle)])
        walk = LineString([anchor, anchor + forward * gate["approach_distance_m"]])
        assert neighbors.distance(walk) > 0.5, gate["gate"]
    ground.append(tools.approaches(approaches, field, collision))
    land = trimesh.util.concatenate(ground)
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = tools.load_builder(
        "build-frohnmayer-exterior-review.py"
    ).source_removals({"absorbed_batches": spec["batches"]}, config, appearances)
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(glb, meshes, land, GROUND, "graduate-village-paving")
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=records,
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["graduate_village_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    cfg.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        footprint_m2={r["id"]: r["area_m2"] for r in records},
        triangles={k: len(v.faces) for k, v in meshes.items()},
        route_edges=route_count,
        closest_route_m=round(clearance, 3),
        model_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
    )
    args.audit.write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
