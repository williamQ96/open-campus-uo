# SPDX-License-Identifier: Apache-2.0
"""Build the georeferenced McArthur Court, Esslinger Hall and SRC exterior review."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

from importlib.util import module_from_spec, spec_from_file_location


def load_builder(filename):
    path = Path(__file__).with_name(filename)
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


geometry = load_builder("build-cascade-exterior-review.py")
facade_box = load_builder("build-ford-arena-review.py").facade_box
SCENE = geometry.SCENE
SPEC = geometry.ROOT / "data/metadata/athletic-exterior-review.json"
DIRECTORY = "athletic-exterior-review"
OUTPUT = SCENE / DIRECTORY
GROUND = "athletic-approaches"
STUCCO = (191, 154, 123)
WARM_TRIM = (171, 133, 103)
FOUNDATION = (134, 125, 112)
METAL = (120, 126, 125)
SLATE = (96, 100, 100)
STEEL = (79, 83, 81)
GLASS = (52, 78, 84)
FRAME = (85, 106, 108)
PALE = (172, 170, 155)
CONCRETE = (166, 167, 156)
BRICK = (148, 82, 63)
MEMBRANE = (183, 185, 180)
ROOF_LIGHT = (209, 211, 208)


def flat(parts, footprint, bottom, top, wall, roof=None):
    for plan in geometry.sections(footprint):
        parts.append(geometry.shell(plan, bottom, lambda e, n: top, wall, roof or wall))


def face(parts, start, end):
    origin = np.asarray(start)
    unit = np.asarray(end) - origin
    width = np.linalg.norm(unit)
    unit = unit / width
    outside = np.array((unit[1], -unit[0]))

    def add(left, right, inside, outset, low, high, material):
        parts.append(
            facade_box(
                origin, unit, outside, left, right, inside, outset, low, high, material
            )
        )

    return width, add


def frame(add, x, width, bottom, top, inset=0.0, mullions=2, rails=1):
    end = x + width
    add(x, end, inset + 0.012, inset + 0.055, bottom, top, GLASS)
    for u in np.linspace(x, end, mullions + 1):
        add(u - 0.036, u + 0.036, inset + 0.056, inset + 0.115, bottom, top, FRAME)
    for z in np.linspace(bottom, top, rails + 2):
        add(x, end, inset + 0.053, inset + 0.119, z - 0.038, z + 0.038, FRAME)


def beam(parts, a, b, width, color):
    a, b = (np.array((e, z, -n)) for e, n, z in (a, b))
    transform = trimesh.geometry.align_vectors([0, 0, 1], b - a)
    transform[:3, 3] = (a + b) / 2
    mesh = trimesh.creation.box([width, width, np.linalg.norm(b - a)], transform)
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = [*color, 255]
    parts.append(mesh)


def court_east_stairs(parts, field, e, a, b):
    supports = []
    for end, direction in ((a, 1), (b, -1)):
        landing_edge = end + direction * 2.55
        stair_end = landing_edge + direction * 4.62
        ground = geometry.sample_ground(field, e + 1.2, stair_end)
        lower, upper = sorted((end, stair_end))
        supports.append(box(e, lower, e + 1.82, upper))
        lo, hi = sorted((end, landing_edge))
        flat(
            parts, box(e - 0.02, lo, e + 1.82, hi),
            ground + 2.43, ground + 2.68, CONCRETE,
        )
        _, door = face(parts, (e, lo), (e, hi))
        door(0.49, 2.07, 0.0, 0.13, ground + 2.68, ground + 4.89, STEEL)
        frame(door, 0.71, 1.14, ground + 3.98, ground + 4.65, 0.13, 2, 1)
        beam(parts, (e + 1.70, end, ground + 2.66),
             (e + 1.70, end, ground + 3.65), 0.075, STEEL)
        for brace in (lo + 0.35, hi - 0.35):
            beam(parts, (e + 0.01, brace, ground + 1.57),
                 (e + 1.71, brace, ground + 2.47), 0.13, STEEL)
        for i in range(14):
            low, high = sorted((
                stair_end - direction * (i + 1) * 0.33,
                stair_end - direction * i * 0.33,
            ))
            top = ground + (i + 1) * 0.185
            flat(parts, box(e + 0.05, low, e + 1.76, high), top - 0.12, top, STEEL)
        for x in (e + 0.10, e + 1.70):
            start = (x, stair_end, ground)
            upper_step = (x, landing_edge, ground + 2.65)
            beam(parts, start, upper_step, 0.11, STEEL)
            for t in (0.0, 0.33, 0.66, 1.0):
                n = stair_end + (landing_edge - stair_end) * t
                z = ground + (2.65 * t)
                beam(parts, (x, n, z), (x, n, z + 1.0), 0.075, STEEL)
            beam(parts, (x, stair_end, ground + 1.0),
                 (x, landing_edge, ground + 3.65), 0.07, STEEL)
        beam(parts, (e + 1.70, landing_edge, ground + 3.65),
             (e + 1.70, end, ground + 3.65), 0.07, STEEL)
    return supports


def mcarthur(spec, outline, field):
    parts = []
    base, eave = spec["footing_z_m"], spec["eave_z_m"]
    roof = spec["roof"]
    ridge = roof["ridge_e_m"]

    def vault(e, n):
        return roof["ridge_z_m"] - roof["slope"] * abs(e - ridge)

    core = box(
        roof["west_end_e_m"], roof["south_n_m"], roof["east_end_e_m"], roof["north_n_m"]
    )
    flat(parts, outline.difference(core), base, eave, STUCCO, METAL)
    for west, east in ((core.bounds[0], ridge), (ridge, core.bounds[2])):
        half = box(west, core.bounds[1], east, core.bounds[3])
        parts.append(geometry.shell(half, base, vault, STUCCO, SLATE))
        for n in np.arange(core.bounds[1] + 0.4, core.bounds[3], 1.65):
            beam(
                parts,
                (west, n, vault(west, n) + 0.025),
                (east, n, vault(east, n) + 0.025),
                0.046,
                METAL,
            )

    truss = spec["truss"]
    ns = np.linspace(*truss["n_range_m"], 9)
    zs = (
        eave
        + 0.48
        + (truss["peak_z_m"] - eave - 0.48) * (1 - (np.linspace(-1, 1, 9) ** 2))
    )
    for e in truss["eastings_m"]:
        for i, (n, z) in enumerate(zip(ns, zs)):
            if i not in (0, 8):
                beam(parts, (e, n, eave + 0.62), (e, n, z), 0.23, STEEL)
            if i:
                last_n, last_z = ns[i - 1], zs[i - 1]
                beam(parts, (e, last_n, last_z), (e, n, z), 0.29, STEEL)
                beam(parts, (e, last_n, eave + 0.58), (e, n, eave + 0.58), 0.27, STEEL)
                beam(parts, (e, last_n, last_z), (e, n, eave + 0.58), 0.18, STEEL)
        for n, z in zip(ns[1:-1], zs[1:-1]):
            offset = 2.9 if e < ridge else -2.9
            beam(
                parts,
                (e, n, z),
                (e + offset, n, vault(e + offset, n) + 0.02),
                0.16,
                STEEL,
            )

    ring = list(orient(outline).exterior.coords)
    supports = []
    for a, b in zip(ring, ring[1:]):
        width, add = face(parts, a, b)
        if width < 10:
            add(0.02, width - 0.02, 0.006, 0.24, base, eave + 0.58, METAL)
            for x in np.arange(0.3, width, 0.39):
                add(x - 0.027, x + 0.027, 0.233, 0.29, base + 3.5, eave + 0.58, PALE)
            add(0, width, -0.08, 0.31, eave + 0.49, eave + 0.65, PALE)
            continue
        ground = geometry.sample_ground(field, *(np.asarray(a) + np.asarray(b)) / 2)
        long_side = width > 50
        west_entry = long_side and a[0] < -290
        east_stairs = long_side and a[0] > -245
        count = 7 if long_side else 5
        start, step = 6.3, (width - 12.6) / count
        add(0, width, -0.006, 0.095, base, max(base + 0.5, ground + 0.34), FOUNDATION)
        add(0, width, -0.02, 0.24, eave - 0.26, eave + 0.03, WARM_TRIM)
        add(0, width, -0.025, 0.22, 19.28, 19.62, WARM_TRIM)
        if east_stairs:
            supports = court_east_stairs(parts, field, a[0], a[1], b[1])
        unit = (np.array(b) - a) / width
        outside = np.array((unit[1], -unit[0]))
        for setback in (3.5, width - 3.5):
            if long_side:
                frame(add, setback - 0.38, 0.76, 21.30, 27.02, mullions=2, rails=5)
            add(setback - 0.52, setback + 0.52, 0.045, 0.12,
                eave - 0.98, eave - 0.18, WARM_TRIM)
            mid = np.array(a) + unit * setback + outside * 0.14
            left, right = mid - unit * 0.31, mid + unit * 0.31
            diamond = [(*left, eave - 0.58), (*mid, eave - 0.29),
                       (*right, eave - 0.58), (*mid, eave - 0.87)]
            for u, v in zip(diamond, diamond[1:] + diamond[:1]):
                beam(parts, u, v, 0.04, PALE)
        for i in range(count + 1):
            x = start + i * step
            add(x - 0.32, x + 0.32, 0.003, 0.38, ground + 0.55, eave - 0.38, WARM_TRIM)
            add(x - 0.44, x + 0.44, 0.01, 0.48, eave - 1.0, eave - 0.67, STUCCO)
            if i == count:
                continue
            for x0 in (x + 0.92, x + step - 2.05):
                frame(add, x0, 1.15, 20.52, 27.03, mullions=2, rails=5)
                add(x0 - 0.05, x0 + 1.21, 0.02, 0.165, 20.49, 20.62, WARM_TRIM)
            middle = x + step * 0.5
            door = west_entry and 2 <= i <= 4
            frame(
                add,
                middle - 1.38,
                2.76,
                ground + (0.02 if door else 1.38),
                ground + 2.78,
                mullions=2,
                rails=1,
            )
            # A shallow segmented archivolt follows the rectangular door opening.
            for j in range(9):
                t = (j + 0.5) / 9 * 2 - 1
                x0 = middle - 1.78 + j * (3.56 / 9)
                z = ground + 3.55 + 0.52 * (1 - t * t)
                add(x0, x0 + 3.56 / 9, 0.01, 0.15, z, z + 0.11, WARM_TRIM)
        if west_entry:
            add(
                width / 2 - 8.5,
                width / 2 + 8.5,
                -0.04,
                2.1,
                ground + 3.34,
                ground + 3.65,
                STEEL,
            )
            add(
                width / 2 - 1.65,
                width / 2 + 1.65,
                0.18,
                0.56,
                ground + 4.15,
                ground + 4.85,
                STEEL,
            )
    return parts, outline, supports


def roof_sections(parts, outline, footing, roofs, wall, material, fallback):
    covered = Polygon()
    for roof in roofs:
        region = outline.intersection(box(*roof["bounds"])).difference(covered)
        finish = ROOF_LIGHT if roof.get("finish") == "light membrane" else material
        flat(parts, region, footing, roof["z_m"], wall, finish)
        covered = covered.union(region)
    flat(parts, outline.difference(covered), footing, fallback, wall, material)


def esslinger(spec, outline, field):
    parts = []
    roof_sections(
        parts,
        outline,
        spec["footing_z_m"],
        spec["roofs"],
        CONCRETE,
        SLATE,
        spec["core_z_m"],
    )
    e, n = spec["entrances"][0]["position_enu_m"]
    ground = geometry.sample_ground(field, e, n)
    _, entrance = face(parts, (e, n + 2.65), (e, n - 2.65))
    entrance(0, 5.3, -0.02, 0.18, ground, ground + 4.35, PALE)
    entrance(0.24, 1.01, 0.14, 0.32, ground, ground + 4.61, CONCRETE)
    entrance(4.29, 5.06, 0.14, 0.32, ground, ground + 4.61, CONCRETE)
    entrance(0.24, 5.06, 0.1, 0.42, ground + 4.32, ground + 4.63, CONCRETE)
    entrance(0.08, 5.22, 0.0, 0.55, ground + 4.62, ground + 4.79, PALE)
    entrance(1.02, 4.28, 0.18, 0.25, ground + 2.5, ground + 4.03, (166, 152, 127))
    frame(entrance, 1.12, 3.06, ground + 0.06, ground + 2.45, 0.19, 3, 2)
    # The surveyed three door leaves each carry four octagonal grilles.
    for u in (1.63, 2.65, 3.67):
        for z in (0.38, 0.93, 1.49, 2.08):
            ring = [
                (e - 0.34, n + 2.65 - u + 0.19 * np.cos(theta),
                 ground + z + 0.19 * np.sin(theta))
                for theta in np.linspace(0, 2 * np.pi, 9)
            ]
            for a, b in zip(ring, ring[1:]):
                beam(parts, a, b, 0.035, PALE)
            beam(parts, (e - 0.34, n + 2.65 - u, ground + z - 0.17),
                 (e - 0.34, n + 2.65 - u, ground + z + 0.17), 0.032, PALE)
    for u in (0.58, 4.71):
        p = (e - 0.73, n + 2.65 - u)
        parts.append(trimmed_cylinder(p, ground, 0.3, 0.39, PALE, 12))
        parts.append(trimmed_cylinder(p, ground + 0.39, 0.43, 0.33, PALE, 12))
    for x, low, high in [
        (-290.45, -382.0, -347),
        (-282.55, -346.6, -314),
        (-275.86, -306.4, -264),
    ]:
        width, windows = face(parts, (x, high), (x, low))
        for t in np.arange(2.5, width - 2.4, 4.02):
            ground = geometry.sample_ground(field, x, high - t)
            frame(
                windows, t - 1.3, 2.6, ground + 1.06, ground + 2.54, mullions=4, rails=2
            )
            windows(t - 1.42, t + 1.42, 0.0, 0.19,
                    ground + 0.98, ground + 1.09, PALE)
        windows(0.08, width - 0.08, 0.01, 0.14, 14.4, 14.56, PALE)
    for x, y in (
        (-264.3, -349.5),
        (-243.5, -367.4),
        (-222.9, -343.1),
        (-264.1, -326.0),
    ):
        point = Point(x, y)
        roof = next(
            (
                roof["z_m"]
                for roof in spec["roofs"]
                if box(*roof["bounds"]).covers(point)
            ),
            spec["core_z_m"],
        )
        if roof < 20.8:
            flat(
                parts,
                box(x - 0.65, y - 0.44, x + 0.65, y + 0.44),
                roof - 0.01,
                roof + 0.51,
                CONCRETE,
                PALE,
            )
    return parts, outline, []


def trimmed_cylinder(point, bottom, radius, height, color, sides=16):
    e, n = point
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sides)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    mesh.apply_translation((e, bottom + height / 2, -n))
    mesh.unmerge_vertices()
    mesh.visual.vertex_colors = [*color, 255]
    return mesh


def recreation(spec, outline, field):
    parts = []
    cantilever = spec["cantilever"]
    canopy = outline.intersection(box(*cantilever["bounds"]))
    walls = outline.difference(canopy)
    base, soffit = spec["footing_z_m"], cantilever["soffit_z_m"]
    roof_sections(parts, walls, base, spec["roofs"], BRICK, MEMBRANE, spec["core_z_m"])
    east_roof = next(
        roof["z_m"] for roof in spec["roofs"] if roof["kind"] == "east glass"
    )
    flat(parts, canopy, soffit, east_roof, STEEL, MEMBRANE)
    gable = spec["gable"]
    west, east = gable["easting_limits_m"]
    for key, bottom in (
        ("shoulder_profile_nz_m", 16.75),
        ("clerestory_profile_nz_m", 20.36),
    ):
        profile = gable[key]
        for (a, az), (b, bz) in zip(profile, profile[1:]):
            cap = outline.intersection(box(west, a, east, b))
            for p in geometry.sections(cap):
                parts.append(
                    geometry.shell(
                        p,
                        bottom,
                        lambda e, n: az + (bz - az) * (n - a) / (b - a),
                        PALE,
                        MEMBRANE,
                    )
                )
    columns = []
    for n in np.arange(-368.5, -324.5, 6.2):
        e = -140.26 if n > -351.1 else -145.2
        p = Point(e, n)
        assert canopy.covers(p)
        z = geometry.sample_ground(field, e, n)
        parts.append(
            trimmed_cylinder((e, n), z - 0.12, 0.28, soffit - z + 0.13, CONCRETE)
        )
        columns.append(p.buffer(0.29, quad_segs=2))
    canopy_ring = list(orient(canopy).exterior.coords)
    inner_east = cantilever["west_e_m"]
    for a, b in zip(canopy_ring, canopy_ring[1:]):
        if a[0] < inner_east + 0.02 and b[0] < inner_east + 0.02:
            continue
        width, add = face(parts, a, b)
        if width < 3:
            continue
        add(0, width, 0, 0.26, soffit - 0.1, soffit + 0.52, PALE)
        add(0, width, 0, 0.48, east_roof - 0.47, east_roof + 0.09, METAL)
        add(0.08, width - 0.08, 0.06, 0.25, 12.34, 13.23, (53, 105, 119))
        for lower, upper in ((soffit + 0.45, 12.34), (13.23, east_roof - 0.46)):
            frame(
                add, 0.1, width - 0.2, lower, upper, 0.07, max(2, round(width / 1.35))
            )
        for t in np.arange(1.0, width - 0.5, 3.04):
            add(
                t - 0.055, t + 0.055, 0.16, 0.49, soffit + 0.22, east_roof - 0.37, STEEL
            )
            if a[0] > -148 and b[0] > -148:
                for height in np.arange(soffit + 0.76, east_roof - 0.55, 0.37):
                    add(t - 0.26, t + 0.26, 0.24, 0.48,
                        height, height + 0.045, STEEL)
    e = cantilever["west_e_m"]
    width, lower = face(parts, (e, -373.55), (e, -322.17))
    for t in np.arange(1.8, width - 2.3, 3.9):
        n = -373.55 + t
        z = geometry.sample_ground(field, e, n)
        frame(lower, t - 1.35, 2.7, z + 0.19, soffit - 0.25, mullions=2)
    e, n = spec["entrances"][0]["position_enu_m"]
    ground = geometry.sample_ground(field, e, n)
    _, lobby = face(parts, (e, n - 3.98), (e, n + 3.98))
    frame(lobby, 0.38, 7.2, ground + 0.07, ground + 3.35, mullions=6)
    frame(lobby, 0.8, 6.36, ground + 4.28, ground + 6.22, mullions=4)
    frame(lobby, 0.8, 6.36, ground + 7.05, ground + 8.73, mullions=4)
    lobby(0.1, 7.85, -0.025, 0.9, ground + 3.4, ground + 3.68, CONCRETE)
    _, gym_end = face(parts, (-139.29, -297.8), (-139.29, -277.8))
    gym_end(0, 20, 0.005, 0.12, 8.4, 17.05, CONCRETE)
    frame(gym_end, 0.95, 18.0, 14.25, 16.35, 0.13, 10, 1)
    # Clock on the existing north gym, visible across the recreation field.
    clock = trimesh.creation.cylinder(radius=0.68, height=0.15, sections=24)
    clock.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    clock.apply_translation((-139.18, 23.02, 287.35))
    clock.unmerge_vertices()
    clock.visual.vertex_colors = (236, 229, 199, 255)
    parts.append(clock)
    for n, z in ((-287.62, 23.25), (-287.31, 23.34)):
        beam(parts, (-139.095, -287.35, 23.02), (-139.095, n, z), 0.045, STEEL)
    return parts, walls, columns


def approaches(entries, field, blocked):
    result = []
    step = field["spacing_m"]
    x0, y0 = field["min_east_m"], field["min_north_m"]
    for entry in entries:
        area = Polygon(entry["outline"]).difference(blocked)
        assert area.is_valid and area.area > 0
        xmin, ymin, xmax, ymax = area.bounds
        vertices = []
        for i in range(int((xmin - x0) / step), int((xmax - x0) / step) + 1):
            for j in range(int((ymin - y0) / step), int((ymax - y0) / step) + 1):
                x, y = x0 + i * step, y0 + j * step
                south, east = (x, y), (x + step, y)
                west, north = (x, y + step), (x + step, y + step)
                for corners in ((south, east, north), (south, north, west)):
                    for region in geometry.sections(
                        area.intersection(Polygon(corners))
                    ):
                        for triangle in shapely.constrained_delaunay_triangles(
                            region
                        ).geoms:
                            vertices.extend(
                                (e, geometry.sample_ground(field, e, n) + 0.085, -n)
                                for e, n in list(orient(triangle).exterior.coords)[:3]
                            )
        mesh = trimesh.Trimesh(
            vertices,
            np.arange(len(vertices)).reshape(-1, 3),
            process=False,
        )
        mesh.visual.vertex_colors = [*entry["rgb"], 255]
        result.append(mesh)
    return trimesh.util.concatenate(result)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest_file = SCENE / "manifest.json"
    presentation_path = SCENE / "presentation.json"
    presentation = json.loads(presentation_path.read_bytes())
    assert digest(manifest_file) == spec["source_manifest_sha256"]
    assert (
        digest(SCENE / presentation["asset_url"]) == spec["source_presentation_sha256"]
    )
    manifest = json.loads(manifest_file.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    old = {
        record["id"]: Polygon(record["footprint_enu_m"]).buffer(0)
        for record in manifest["buildings"]
    }
    report, records, collision = {}, [], []
    stage = trimesh.Scene()
    for build in (mcarthur, esslinger, recreation):
        entry = spec[build.__name__]
        rid = entry["id"]
        outline = Polygon(entry["walls_enu_m"])
        assert outline.is_valid and rid in old
        parts, walls, supports = build(entry, outline, field)
        assert walls.geom_type == "Polygon" and walls.is_valid
        assert all(walls.intersection(other).area < 0.001 for other in collision)
        collision.extend([walls, *supports])
        mesh = trimesh.util.concatenate(parts)
        stage.add_geometry(mesh, node_name=rid, geom_name=rid)
        distances = np.arange(0, walls.exterior.length, 0.45)
        footprint_z = min(
            geometry.sample_ground(field, *walls.exterior.interpolate(d).coords[0])
            for d in distances
        )
        assert footprint_z > entry["footing_z_m"], (rid, footprint_z)
        entries = {}
        for gate in entry["entrances"]:
            point = Point(gate["position_enu_m"])
            assert point.distance(walls.boundary) < 0.005
            entries[gate["gate"]] = geometry.sample_ground(field, point.x, point.y)
        records.append(
            {
                "id": rid,
                "footprint_enu_m": list(walls.exterior.coords)[:-1],
                "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
                "base_z_m": entry["footing_z_m"],
                "entrances": entry["entrances"],
                "support_collision_enu_m": [
                    list(p.exterior.coords)[:-1] for p in supports
                ],
            }
        )
        report[rid] = {
            "triangles": len(mesh.faces),
            "old_area_m2": round(old[rid].area, 2),
            "roof_plan_area_m2": round(outline.area, 2),
            "collision_area_m2": round(walls.area, 2),
            "roof_z_m": records[-1]["roof_z_m"],
            "footing_samples": len(distances),
            "min_footing_cover_m": round(footprint_z - entry["footing_z_m"], 3),
            "entry_ground_z_m": entries,
        }

    routes = json.loads((SCENE / "navigation.json").read_bytes())
    former = [old[item["id"]] for item in records]
    conflicts = []
    for i, (a, b, *_) in enumerate(routes["edges"]):
        line = LineString([routes["nodes_enu_m"][a], routes["nodes_enu_m"][b]])
        if (
            min(p.distance(line) for p in collision)
            < 0.42
            <= min(p.distance(line) for p in former)
        ):
            conflicts.append(i)
    assert not conflicts, f"Athletic route conflicts: {conflicts}"

    approach_mesh = approaches(spec["approaches"], field, shapely.union_all(collision))
    stage.add_geometry(approach_mesh, node_name=GROUND, geom_name=GROUND)

    def mark(tree):
        tree["asset"]["copyright"] = (
            "Open Campus contributors. Original geometry CC BY 4.0."
        )
        tree["materials"] = [
            {
                "pbrMetallicRoughness": {
                    "metallicFactor": 0.035,
                    "roughnessFactor": 0.88,
                }
            }
        ]
        ids = {record["id"] for record in records}
        for node in tree["nodes"]:
            if node.get("name") in ids:
                node["extras"] = {"asset_kind": "building", "asset_id": node["name"]}
            elif node.get("name") == GROUND:
                node["extras"] = {
                    "asset_kind": "landscape-surface",
                    "surface_layer": "athletic-paving",
                }
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    OUTPUT.mkdir(exist_ok=True)
    glb = OUTPUT / "site.glb"
    glb.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage,
            include_normals=True,
            tree_postprocessor=mark,
        )
    )
    reloaded = trimesh.load(glb, force="scene", process=False)
    assert set(reloaded.graph.nodes_geometry) == {GROUND, *(r["id"] for r in records)}
    assert np.allclose(reloaded.bounds, stage.bounds, atol=0.00005)
    site = OUTPUT / "site.json"
    site.write_text(
        json.dumps(
            {
                "source_presentation_sha256": spec["source_presentation_sha256"],
                "source_base_model_sha256": manifest["model"]["sha256"],
                "source_heightfield_sha256": digest(field_path),
                "url": f"{DIRECTORY}/site.glb",
                "sha256": digest(glb),
                "buildings": records,
                "ground_node": GROUND,
                "context_tree": spec["context_tree"],
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if descriptor := presentation.get("athletic_site_review"):
        assert descriptor["url"] == f"{DIRECTORY}/site.json"
        if descriptor["sha256"] != digest(site):
            descriptor["sha256"] = digest(site)
            presentation_path.write_text(
                json.dumps(presentation, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    result = {
        "buildings": report,
        "model_sha256": digest(glb),
        "site_sha256": digest(site),
        "route_edges": len(routes["edges"]),
        "new_route_conflicts": conflicts,
        "approach_triangles": len(approach_mesh.faces),
    }
    args.audit.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
