# SPDX-License-Identifier: Apache-2.0
"""Build the registered Hayward Field outdoor arena and its open canopy."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-northsite-millrace-site-review.py")
loader = spec_from_file_location(source.stem, source)
reference = module_from_spec(loader)
loader.loader.exec_module(reference)
site, tools, geometry, science, shared = (
    reference.site, reference.tools, reference.geometry, reference.science, reference.shared
)
flat, ring, union = reference.flat, reference.ring, reference.union
SCENE = reference.SCENE
SPEC = geometry.ROOT / "data/metadata/hayward-exterior-review.json"
DIRECTORY = "hayward-exterior-review"
GROUND = "hayward-exterior-ground"
CONCRETE = (178, 178, 166)
CONCRETE_DARK = (146, 146, 137)
PAVEMENT = (166, 159, 142)
TIMBER = (164, 105, 65)
METAL = (170, 184, 185)
SHADOW = (118, 138, 140)
SKIN = (207, 218, 215)
GLASS = (99, 135, 147)
FIELD = (126, 153, 91)
TRACK = (160, 88, 72)
STRIPE = (220, 206, 180)
SEATS = ((57, 95, 65), (63, 107, 72), (74, 113, 72))


def interpolate_stations(anchors, distances, samples):
    anchors = np.asarray(anchors)
    length = np.diff(distances)
    slope = np.diff(anchors, axis=0) / length[:, None]
    tangent = np.vstack([slope[0], (slope[:-1] + slope[1:]) * 0.5, slope[-1]])
    result = []
    segments = np.clip(np.searchsorted(distances, samples, side="right") - 1, 0, len(length) - 1)
    for segment, sample in zip(segments, samples):
        t = (sample - distances[segment]) / length[segment]
        a, b = anchors[segment : segment + 2]
        p, q = tangent[segment : segment + 2] * length[segment]
        result.append((2*t**3 - 3*t*t + 1)*a + (t**3 - 2*t*t + t)*p
                      + (3*t*t - 2*t**3)*b + (t**3 - t*t)*q)
    return np.asarray(result)


def canopy_stations(spec):
    outer = np.asarray(spec["outer_canopy_enu_m"])
    inner = np.asarray(spec["inner_canopy_enu_m"])
    middle = (outer + inner) * 0.5
    distances = np.r_[0, np.cumsum(np.linalg.norm(np.diff(middle, axis=0), axis=1))]
    stations = np.linspace(0, distances[-1], spec["bent_count"])
    return (
        interpolate_stations(outer, distances, stations),
        interpolate_stations(inner, distances, stations),
        np.interp(stations, distances, spec["roof_rim_height_local_m"]),
    )


def colored_quads(parts, quads, colors, *, two_sided=False):
    if not quads:
        return
    e_n_z = np.asarray(quads)
    positions = e_n_z[..., [0, 2, 1]].copy()
    positions[..., 2] *= -1
    if two_sided:
        positions = np.concatenate([positions, positions[:, ::-1]], axis=0)
        colors = [*colors, *colors]
    start = np.arange(len(positions), dtype=int)[:, None, None] * 4
    faces = (start + np.asarray([[0, 1, 2], [0, 2, 3]])).reshape(-1, 3)
    mesh = trimesh.Trimesh(vertices=positions.reshape(-1, 3), faces=faces, process=False)
    mesh.visual.vertex_colors = np.repeat(np.column_stack([colors, np.full(len(colors), 255)]), 4, axis=0)
    parts.append(mesh)


def ribbon_quads(rows):
    return [
        [rows[i, j], rows[i + 1, j], rows[i + 1, j + 1], rows[i, j + 1]]
        for i in range(len(rows) - 1)
        for j in range(rows.shape[1] - 1)
    ]


def beam_line(parts, points, width, color):
    for a, b in zip(points, points[1:]):
        tools.beam(parts, a, b, width, color)


def canopy(parts, field, outer, inner, heights):
    crown = np.asarray([[-0.015, -4.02], [0.14, -1.66], [0.32, -0.48], [0.52, 0.04],
                        [0.72, 0.11], [0.89, -0.05], [1.0, -0.16]])
    extent = inner - outer
    xy = outer[:, None, :] + extent[:, None, :] * crown[None, :, 0, None]
    z = heights[:, None] + crown[None, :, 1]
    profile = np.concatenate([xy, z[..., None]], axis=2)
    roof = ribbon_quads(profile)
    colored_quads(parts, roof, [SKIN if (i // 6) % 3 else (198, 212, 210)
                                for i in range(len(roof))], two_sided=True)
    for edge, shade in ((profile[:, 0], METAL), (profile[:, -1], SKIN)):
        beam_line(parts, edge, 0.21, shade)
    for column in (2, 4):
        beam_line(parts, profile[:, column] - [0, 0, 0.16], 0.13, METAL)

    foot = outer + extent * 0.28
    support_footprints = []
    for i, (points, start, span) in enumerate(zip(profile, foot, extent)):
        ground = geometry.sample_ground(field, *start)
        elbow = outer[i] + span * 0.032
        bent = np.vstack([[*start, ground - 0.12],
                          [*(outer[i] + span * 0.12), ground + 3.7],
                          [*elbow, heights[i] * 0.63],
                          points - [0, 0, 0.32]])
        beam_line(parts, bent, 0.48 if heights[i] > 21 else 0.38, TIMBER)
        beam_line(parts, points + [0, 0, 0.08], 0.095, SKIN)
        if i % 3 == 0:
            support_footprints.append(Point(start).buffer(0.28, quad_segs=2))
    skin_z = np.array([geometry.sample_ground(field, *p) for p in outer])
    exterior = np.stack([
        np.column_stack([outer + span * (inner - outer), height])
        for span, height in ((0.17, skin_z + 3.25), (0.015, heights - 5.33))
    ], axis=1)
    screens = ribbon_quads(exterior)
    colored_quads(parts, screens, [SHADOW if i % 4 == 0 else METAL for i in range(len(screens))],
                  two_sided=True)
    for low, high in zip(exterior[:, 0], exterior[:, 1]):
        tools.beam(parts, low, high, 0.14, METAL)
    return support_footprints, profile


def seat_bowl(parts, outer, inner, heights, track_outer, field):
    centers, riser_z = [], []
    rear = outer + (inner - outer) * 0.37
    for high, towards in zip(rear, inner):
        along = track_outer.exterior.project(Point(towards))
        edge = np.asarray(track_outer.exterior.interpolate(along).coords[0])
        direction = high - edge
        centers.append(edge + direction / np.linalg.norm(direction) * 0.92)
        riser_z.append(geometry.sample_ground(field, *edge) + 0.19)
    front = np.asarray(centers)
    z0 = np.asarray(riser_z)
    rise = np.clip((heights - z0) * 0.68, 7, 15.4)
    rows = 21
    blocks, colors = [], []
    for i in range(len(front) - 1):
        corners = slice(i, i + 2)
        aisle = i % 8 == 0
        for row in range(rows):
            a, b = row / rows, (row + 1) / rows
            step_a = front[corners] * (1 - a) + rear[corners] * a
            step_b = front[corners] * (1 - b) + rear[corners] * b
            top = z0[corners] + rise[corners] * b ** 1.24
            low = z0[corners] + rise[corners] * a ** 1.24
            lower = np.column_stack([step_a, low])
            up = np.column_stack([step_a, top])
            back = np.column_stack([step_b, top])
            blocks.extend([[lower[0], lower[1], up[1], up[0]], [up[0], up[1], back[1], back[0]]])
            seat = SEATS[(row + i // 8) % len(SEATS)]
            cross_aisle = aisle or row == 12
            face_color = CONCRETE_DARK if cross_aisle else tuple(max(0, value - 11) for value in seat)
            colors.extend([face_color, CONCRETE if cross_aisle else seat])
    colored_quads(parts, blocks, colors, two_sided=True)
    front_plan = front + (rear - front) * 0.26
    support_plans = []
    for start, end in ((5, 23), (24, 44), (45, len(front) - 3)):
        end = min(end, len(front))
        polygon = Polygon([*rear[start:end], *front_plan[start:end][::-1]])
        for part in geometry.sections(polygon.buffer(0)):
            if part.area > 1:
                support_plans.append(part)
    return support_plans


def north_open_stand(parts, track, floor):
    points = track["axis_e_m"] + np.array([-33.5, -25.7, -16.9, -7.4, 2.8, 13.4, 23.8, 33.3, 41.4])
    radius = track["outer_radius_m"]
    offsets = points - track["axis_e_m"]
    end = track["north_enu_m"]
    arc = np.sqrt(radius * radius - offsets * offsets)
    rows = []
    for step in range(9):
        rows.append(np.column_stack([
            points + offsets * step * 0.019, end + arc + 0.55 + step * 0.69,
            np.full(len(points), floor + step * 0.40),
        ]))
    band = np.stack(rows, axis=1)
    quads = ribbon_quads(band)
    colored_quads(parts, quads, [CONCRETE if i % 4 else CONCRETE_DARK for i in range(len(quads))], two_sided=True)


def tower(parts, field, definition):
    base = np.asarray(definition["center_enu_m"])
    bottom = geometry.sample_ground(field, *base)
    rise = definition["height_above_grade_m"]
    directions = np.column_stack([np.cos(np.arange(20) * np.pi * 0.1), np.sin(np.arange(20) * np.pi * 0.1)])
    shift = np.asarray(definition["tip_shift_enu_m"])
    low = definition["base_radius_m"]
    high = definition["top_radius_m"]
    rings = []
    for i, f in enumerate(np.linspace(0, 1, 11)):
        radius = low + (high - low) * f ** 1.71
        ring_xy = base + shift * f + directions * radius
        z = bottom + rise * f
        if i == 10:
            top_ring = np.column_stack([ring_xy, z - (1 - directions[:, 0]) * 1.8])
        else:
            top_ring = np.column_stack([ring_xy, np.full(len(directions), z)])
        rings.append(top_ring)
    glass_faces, colors = [], []
    for i, (lower, upper) in enumerate(zip(rings, rings[1:])):
        for side in range(len(directions)):
            nxt = (side + 1) % len(directions)
            a, b = lower[[side, nxt]]
            c, d = upper[[nxt, side]]
            glass_faces.append([a, b, c, d])
            colors.append(GLASS if (i + side) % 4 < 2 else SHADOW)
            if i % 2 == side % 2:
                tools.beam(parts, a, c, 0.31, METAL)
            else:
                tools.beam(parts, b, d, 0.31, METAL)
        beam_line(parts, np.vstack([upper, upper[0]]), 0.22, METAL)
    colored_quads(parts, glass_faces, colors, two_sided=True)
    crown = Polygon(rings[-1][:, :2])
    site.surface(parts, crown, bottom + rise - 4.2,
                 lambda e, n: bottom + rise - 1.8 + (e - base[0] - shift[0]) * 1.8 / high,
                 METAL, SKIN)
    return orient(Polygon(rings[0][:, :2])), bottom


def field_surfaces(parts, field, track):
    center, north, south = track["axis_e_m"], track["north_enu_m"], track["south_enu_m"]
    axis = LineString([(center, south), (center, north)])
    outer_radius = track["outer_radius_m"]
    lanes = track["lane_count"]
    width = track["lane_width_m"]
    first = outer_radius - width * lanes
    outer = axis.buffer(outer_radius, quad_segs=26)
    inner = axis.buffer(first, quad_segs=26)
    floor = geometry.sample_ground(field, center, (north + south) * 0.5)
    flat(parts, inner, floor - 0.62, floor + 0.11, FIELD)
    flat(parts, outer.difference(inner), floor - 0.62, floor + 0.13, TRACK)
    for lane in range(lanes + 1):
        radius = first + width * lane
        line = axis.buffer(radius + 0.038, quad_segs=26).difference(axis.buffer(radius - 0.038, quad_segs=26))
        flat(parts, line, floor + 0.13, floor + 0.144, STRIPE)
    for left in (center - 21.1, center + 2.2):
        pitch = box(left, south - 24.53, left + 19.4, south + 6.85).intersection(inner)
        flat(parts, pitch, floor + 0.10, floor + 0.143, TRACK)
    for east in (center + 20.37, center + 27.76):
        flat(parts, box(east, south - 7.1, east + 1.24, north + 7.76), floor + 0.11, floor + 0.146, TRACK)
    return outer, floor


def build(spec, manifest, config, field, graph):
    parts, ground = [], []
    track, field_z = field_surfaces(ground, field, spec["track"])
    outer, inner, heights = canopy_stations(spec)
    supports, roof = canopy(parts, field, outer, inner, heights)
    grounds = seat_bowl(parts, outer, inner, heights, track, field)
    north_open_stand(parts, spec["track"], field_z)
    tower_plan, tower_base = tower(parts, field, spec["tower"])
    grounds.append(tower_plan)
    gates = []
    for entry in spec["gates"]:
        gate, path, feet = shared.site_entry(ground, field, entry)
        gates.append(gate)
        supports.extend(feet)
    roof_plan = Polygon([*outer, *inner[::-1]])
    plazas = [Polygon(points) for points in spec["plazas"]]
    hull = union([roof_plan, *grounds, tower_plan, track]).convex_hull
    sources = {spec["building_id"], *spec["retired_ids"]}
    existing = union([Polygon(row["footprint_enu_m"]).buffer(0) for row in manifest["buildings"] if row["id"] in sources])
    routes, clearance = reference.prior.nearby.shared.graduate.shared.check_routes(
        grounds, supports, gates, existing, manifest, graph, config, sources
    )
    walkways = union([*plazas, LineString(outer).buffer(3.88, cap_style="flat")])
    reference.prior.nearby.add_paths(
        ground, field, walkways, union([track, *grounds, *supports]), PAVEMENT,
    )
    field_mesh = science.ordered_mesh(trimesh.util.concatenate(ground))
    model = trimesh.util.concatenate(parts)
    model.update_faces(model.nondegenerate_faces(height=0.00005))
    model = science.ordered_mesh(model)
    record = {
        "id": spec["building_id"], "name": "Hayward Field", "campus_id": "B0280",
        "footprint_enu_m": ring(hull), "ground_footprints_enu_m": [ring(p) for p in grounds],
        "support_collision_enu_m": [ring(p) for p in supports],
        "area_m2": round(hull.area, 3), "base_z_m": round(min(tower_base, field_z), 4),
        "roof_z_m": round(float(model.bounds[1, 1]), 4), "entrances": gates,
    }
    metrics = {
        "route_edges": routes, "route_clearance_m": round(clearance, 3),
        "canopy_m2": round(roof_plan.area, 3), "canopy_stations": len(roof),
        "tower_height_m": round(spec["tower"]["height_above_grade_m"], 4),
        "triangles": len(model.faces), "field_triangles": len(field_mesh.faces),
    }
    return model, field_mesh, record, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.spec.read_bytes())
    manifest_file = SCENE / "manifest.json"
    manifest = json.loads(manifest_file.read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    heightfield = SCENE / manifest["heightfield_url"]
    assert tools.digest(manifest_file) == data["source_manifest_sha256"]
    assert tools.digest(heightfield) == data["source_heightfield_sha256"]
    field = json.loads(heightfield.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    model, ground, record, metrics = build(data, manifest, config, field, graph)
    appearances = json.loads((geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes())
    removals = shared.frohnmayer.source_removals({"absorbed_batches": data["batch_removals"]}, config, appearances)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(exist_ok=True, parents=True)
    site_file, model_file = output / "site.json", output / "site.glb"
    site.memorial.gerlinger.export(model_file, {record["id"]: model}, ground, GROUND, "hayward-surface")
    payload = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(heightfield),
        "ground_node": GROUND, "url": f"{DIRECTORY}/site.glb", "sha256": tools.digest(model_file),
        "buildings": [record], "absorbed_ids": data["retired_ids"], "batch_removals": removals,
        "context_trees": data["context_trees"],
    }
    site_file.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    if args.stage is None:
        config["hayward_exterior_site"] = {"url": f"{DIRECTORY}/site.json", "sha256": tools.digest(site_file)}
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    args.audit.write_text(json.dumps({
        **metrics, "record": record, "batch_removals": removals,
        "glb_sha256": payload["sha256"], "descriptor_sha256": tools.digest(site_file),
    }, indent=2) + "\n", encoding="utf-8")
    print(metrics)


if __name__ == "__main__":
    main()
