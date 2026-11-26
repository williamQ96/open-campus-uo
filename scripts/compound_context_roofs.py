# SPDX-License-Identifier: Apache-2.0
"""Original massing for the Canterbury Court and Millrace 3 context members."""

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

CANOPY_TRIM = (185, 180, 168)
MEMBRANE = (193, 190, 177)
SIDING = (175, 154, 132)
BATTEN = (159, 138, 118)
SHINGLE = (121, 107, 97)
GLAZING = (92, 121, 128)
CASING = (209, 197, 178)
COURTYARD_STUCCO = (205, 190, 162)
SASH = (175, 175, 155)
FASCIA = (177, 163, 141)
BASE = (158, 146, 130)
PAVING = (173, 167, 150)
RAIL = (181, 157, 70)


def canterbury_frontage(pieces, site, plan, field, tools):
    settings = site["frontage"]
    building = orient(plan)
    for ring_index, ring in enumerate((building.exterior, *building.interiors)):
        court_side = ring_index > 0
        for a, b in zip(ring.coords, list(ring.coords)[1:]):
            edge = LineString((a, b))
            if edge.length < 2.35:
                continue
            length = edge.length
            tangent = (np.asarray(b) - a) / length
            outward = np.array([tangent[1], -tangent[0]])
            vertices, indices, colors = [], [], []

            def panel(left, right, offset, low, top, color):
                origin = np.asarray(a) + outward * offset
                i = len(vertices)
                for u, z in ((left, low), (right, low), (right, top), (left, top)):
                    e, n = origin + tangent * u
                    vertices.append((e, z, -n))
                    colors.append((*color, 255))
                indices.extend(((i, i + 1, i + 2), (i, i + 2, i + 3)))

            intervals = max(1, round(length / (3.13 if court_side else 3.81)))
            bay = length / intervals
            doors = [edge.project(Point(e, n)) for e, n in settings["door_marks_enu_m"]
                     if edge.distance(Point(e, n)) < 0.38]
            for i in range(intervals):
                left, right = i * bay + 0.04, (i + 1) * bay - 0.04
                center = edge.interpolate((i + 0.5) * bay)
                grade = tools.geometry.sample_ground(field, center.x, center.y)
                panel(left, right, 0.036, grade - 0.06, grade + 0.37, BASE)
                panel(left, right, 0.054, grade + 2.64, grade + 2.78, FASCIA)
                width = min(1.56 if court_side else 1.91, bay * 0.65)
                x = (i + 0.5) * bay - width * 0.5
                for height in (0.97, 3.52):
                    door = next((u for u in doors if left - 0.04 <= u < right + 0.04), None)
                    if door is not None and height == 0.97:
                        grade = tools.geometry.sample_ground(field, *edge.interpolate(door).coords[0])
                        panel(door - 0.81, door + 0.81, 0.062, grade + 0.06, grade + 2.32, SASH)
                        panel(door - 0.73, door + 0.73, 0.077, grade + 0.10, grade + 2.22, (85, 106, 103))
                        panel(door - 0.016, door + 0.016, 0.093, grade + 0.12, grade + 2.20, SASH)
                        continue
                    sill = grade + height
                    top = grade + height + 1.20
                    panel(x - 0.057, x + width + 0.057, 0.044, sill - 0.052, top + 0.046, SASH)
                    for low, high in ((x, x + width / 2 - 0.028), (x + width / 2 + 0.028, x + width)):
                        panel(low, high, 0.065, sill, top, GLAZING)
                    panel(x - 0.061, x + width + 0.061, 0.099, sill - 0.096, sill - 0.043, FASCIA)
                if court_side and length > 9 and i in {0, intervals - 1}:
                    post = i * bay + 0.28
                    panel(post - 0.05, post + 0.05, 0.106, grade + 0.36, grade + 5.10, SASH)
            facade = trimesh.Trimesh(vertices=vertices, faces=indices, process=False)
            facade.visual.vertex_colors = np.asarray(colors)
            pieces.append(facade)

    for start, end in settings["eave_trim_segments_enu_m"]:
        length, add = tools.face(pieces, start, end)
        e = (start[0] + end[0]) * 0.5
        wing_name = "west" if e < -846.74 else "east"
        wing = site["roof_profile"][wing_name]
        elevation = wing["z_m"] - wing["pitch"] * abs(e - wing["ridge_e_m"])
        add(0.018, length - 0.018, -0.018, 0.106, elevation - 0.17, elevation - 0.035, CASING)

    west, south, east, north = settings["ramp_enu_m"]
    samples = (west, east)
    ramps = []
    for e in samples:
        low = tools.geometry.sample_ground(field, e, south) + 0.04
        top = tools.geometry.sample_ground(field, e, north) + 0.19
        ramps.append((low, top))
        rail_z = min(low, top) + 0.77
        tools.beam(pieces, (e, south + 0.38, rail_z), (e, north - 0.28, top + 0.77), 0.058, RAIL)
        for n in (south + 0.38, (south + north) * 0.5, north - 0.28):
            z = low + (top - low) * (n - south) / (north - south)
            tools.beam(pieces, (e, n, z), (e, n, z + 0.79), 0.058, RAIL)
    low, top = np.mean(ramps, axis=0)
    bottom = min(value for pair in ramps for value in pair) - 0.34

    def slope(e, n):
        return low + (top - low) * (n - south) / (north - south)

    for section in tools.geometry.sections(box(west, south, east, north).difference(plan)):
        pieces.append(tools.geometry.shell(section, bottom, slope, BASE, PAVING))


def canterbury(site, plan, footing, field, tools):
    pieces = []
    west, south, east, north = plan.bounds
    profile = site["roof_profile"]
    for flank, interval in (
        ("west", (west - 1, profile["west"]["limit_e_m"])),
        ("east", (profile["east"]["limit_e_m"], east + 1)),
    ):
        wing = profile[flank]
        crest, peak, slope = wing["ridge_e_m"], wing["z_m"], wing["pitch"]

        def height(e, n):
            return peak - slope * abs(e - crest)

        for low, high in ((interval[0], crest), (crest, interval[1])):
            region = plan.intersection(box(low, south - 1, high, north + 1))
            for section in tools.geometry.sections(region):
                pieces.append(
                    tools.geometry.shell(section, footing, height, COURTYARD_STUCCO, MEMBRANE)
                )
    for lo, hi, height in profile["connectors"]:
        tools.flat(
            pieces,
            plan.intersection(box(lo, south - 1, hi, north + 1)),
            footing,
            height,
            COURTYARD_STUCCO,
            CANOPY_TRIM,
        )

    court = Polygon(plan.interiors[0])
    path = (
        LineString(site["path_center_enu_m"])
        .buffer(site["path_width_m"] / 2, cap_style="flat", quad_segs=3)
        .intersection(court)
    )
    turf = tools.approaches(
        [{"outline": list(court.exterior.coords), "rgb": site["reference_ground_rgb"]}],
        field,
        plan.union(path),
    )
    paved = tools.approaches(
        [{"outline": list(path.exterior.coords), "rgb": site["reference_path_rgb"]}],
        field,
        plan,
    )
    for ground in (turf, paved):
        ground.apply_translation((0, 0.04, 0))
        pieces.append(ground)
    if "frontage" in site:
        canterbury_frontage(pieces, site, plan, field, tools)
    return pieces


def millrace(site, plan, footing, field, tools):
    pieces = []
    west, south, east, north = plan.bounds
    main = site["main_roof"]
    ridge_n, ridge_z = main["ridge_n_m"], main["ridge_z_m"]

    def height(e, n):
        pitch = main["pitch_north"] if n >= ridge_n else main["pitch_south"]
        return ridge_z - pitch * abs(n - ridge_n)

    for low, high in ((south - 1, ridge_n), (ridge_n, north + 1)):
        section = plan.intersection(box(west - 1, low, east + 1, high))
        pieces.append(tools.geometry.shell(section, footing, height, SIDING, SHINGLE))

    spec = site["dormers"]
    half = spec["width_m"] / 2
    eave = spec["side_eave_z_m"]
    peak = spec["ridge_z_m"]
    occupied = []
    for side in ("south", "north"):
        face = spec[f"{side}_face_n_m"]
        back = spec[f"{side}_back_n_m"]
        depth = (min(face, back), max(face, back))
        for position in spec["eastings_m"]:
            left, right = position - half, position + half
            occupied.append(box(left, depth[0], right, depth[1]))

            def dormer_z(e, n):
                return peak - (peak - eave) * abs(e - position) / half

            for start, end in ((left, position), (position, right)):
                section = box(start, depth[0], end, depth[1]).intersection(plan)
                pieces.append(
                    tools.geometry.shell(
                        section,
                        height(position, face) - 0.14,
                        dormer_z,
                        SIDING,
                        SHINGLE,
                    )
                )
            a, b = (left, right) if side == "south" else (right, left)
            width, add = tools.face(pieces, (a, face), (b, face))
            # The university photograph shows a tall pane grid up to the gable.
            sill = eave - (3.42 if side == "south" else 2.05)
            if side == "south":
                add(0.20, width - 0.20, -0.015, 0.034, sill - 0.10, eave, CASING)
            tools.frame(
                add,
                0.34,
                width - 0.68,
                sill,
                eave - 0.06,
                inset=0.027,
                mullions=4,
                rails=2,
            )
            add(0.22, width - 0.22, 0.015, 0.13, sill - 0.11, sill + 0.005, CASING)
            for e1, e2 in ((left, position), (position, right)):
                outward = -0.04 if side == "south" else 0.04
                tools.beam(
                    pieces,
                    (e1, face + outward, dormer_z(e1, face)),
                    (e2, face + outward, dormer_z(e2, face)),
                    0.12,
                    CASING,
                )
    assert all(plan.buffer(0.0001).covers(section) for section in occupied), (
        "Dormer projected beyond the main roof"
    )

    for start, end in zip(
        orient(plan).exterior.coords, list(orient(plan).exterior.coords)[1:]
    ):
        length, add = tools.face(pieces, start, end)
        for x in np.arange(0.42, length - 0.1, 0.81):
            fraction = x / length
            east_at = (1 - fraction) * start[0] + fraction * end[0]
            north_at = (1 - fraction) * start[1] + fraction * end[1]
            add(
                x - 0.025,
                x + 0.025,
                0,
                0.042,
                footing + 0.12,
                height(east_at, north_at) - 0.04,
                BATTEN,
            )

    # Historic courtyard-facing photograph documents two broad lower glazing
    # banks and a narrower central entrance bank. Positions are registered
    # approximately to the dormer spacing, independent of the runtime portals.
    _, south_face = tools.face(pieces, (west, south), (east, south))
    grade = tools.geometry.sample_ground(field, (west + east) / 2, south - 0.24)
    entry = site["entry_frame"]
    e = entry["center_e_m"]
    for center, width, sill in (
        (-105.8, 3.25, 0.89),
        (e, 2.00, 0.15),
        (-83.8, 3.45, 0.27),
    ):
        left = center - west - width / 2
        tools.frame(
            south_face,
            left,
            width,
            grade + sill,
            grade + 2.62,
            inset=0.049,
            mullions=4,
            rails=1,
        )
        south_face(
            left - 0.1,
            left + width + 0.1,
            0.025,
            0.13,
            grade + 2.61,
            grade + 2.74,
            CASING,
        )
        south_face(left - 0.12, left + width + 0.12, 0, 0.19,
                   grade + sill - 0.10, grade + sill + 0.01, CASING)

    # The photographed base is lap cladding below the vertical wall boards.
    for a, b in ((0, e - 1 - west), (e + 1 - west, -85.525 - west),
                 (-82.075 - west, east - west)):
        south_face(a, b, -0.01, 0.085, grade - 0.07, grade + 0.72, SIDING)
        for z in np.arange(grade + 0.115, grade + 0.72, 0.16):
            south_face(a, b, 0.08, 0.11, z, z + 0.026, BATTEN)

    west_post, east_post = e - entry["half_width_m"], e + entry["half_width_m"]
    rail_n = south - entry["depth_m"]
    top = tools.geometry.sample_ground(field, e, rail_n) + entry["height_m"]
    for x in (west_post, east_post):
        foot = tools.geometry.sample_ground(field, x, rail_n) - 0.045
        tools.beam(pieces, (x, rail_n, foot), (x, rail_n, top), 0.14, CASING)
        tools.beam(pieces, (x, rail_n, top), (x, south + 0.01, top), 0.11, CASING)
    tools.beam(pieces, (west_post, rail_n, top), (east_post, rail_n, top), 0.14, CASING)
    for x in np.linspace(west_post + 0.15, east_post - 0.15, 6):
        tools.beam(pieces, (x, rail_n, top + 0.09), (x, south + 0.01, top + 0.09),
                   0.085, CASING)
    apron = [
        (west_post - 0.28, south), (east_post + 0.28, south),
        (east_post + 0.28, rail_n - 0.65), (west_post - 0.28, rail_n - 0.65),
    ]
    pieces.append(tools.approaches([{"outline": apron, "rgb": (162, 153, 139)}],
                                   field, plan))

    lights = site["skylights"]
    for side in ("south", "north"):
        n = lights[f"{side}_n_m"]
        for e in lights[f"{side}_e_m"]:
            for panel in (e - 0.41, e + 0.41):
                polygon = box(panel - 0.29, n - 0.36, panel + 0.29, n + 0.36)
                assert plan.contains(polygon)
                bottom = min(height(x, y) for x, y in polygon.exterior.coords) - 0.09
                pieces.append(
                    tools.geometry.shell(
                        polygon,
                        bottom,
                        lambda x, y: height(x, y) + 0.075,
                        SHINGLE,
                        GLAZING,
                    )
                )
    return pieces


def replacement(site, field, tools):
    outline = Polygon(site["outer_enu_m"], site["holes_enu_m"])
    assert outline.is_valid
    rings = (outline.exterior, *outline.interiors)
    probes = [
        tools.geometry.sample_ground(field, point.x, point.y)
        for ring in rings
        for point in (
            ring.interpolate(d)
            for d in np.linspace(0, ring.length, int(ring.length * 4) + 1)
        )
    ]
    footing = round(min(probes) - 0.39, 3)
    if site["form"] == "courtyard":
        pieces = canterbury(site, outline, footing, field, tools)
    else:
        assert site["form"] == "dormers"
        pieces = millrace(site, outline, footing, field, tools)
    merged = trimesh.util.concatenate(pieces)
    # Drop sub-millimetre slivers from profile boundaries and clipped ground triangles.
    merged.vertices = np.round(merged.vertices, 5)
    merged.update_faces(merged.nondegenerate_faces(height=0.0001))
    position = merged.vertices[merged.faces.reshape(-1)]
    normals = np.repeat(merged.face_normals, 3, axis=0)
    rgb = merged.visual.vertex_colors[merged.faces.reshape(-1), :3] / 255
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    assert np.isfinite(position).all() and np.isfinite(normals).all()
    assert np.all(np.linalg.norm(normals, axis=1) > 0.99)
    above_grade = position[position[:, 1] > 3.0]
    roof_projection = np.unique(
        np.column_stack((above_grade[:, 0], -above_grade[:, 2])), axis=0
    )
    assert outline.buffer(0.26).covers(shapely.MultiPoint(roof_projection)), site["id"]
    return (
        outline,
        footing,
        round(float(np.max(position[:, 1])), 4),
        {
            "position": np.round(position, 5).ravel().tolist(),
            "normal": np.round(normals, 6).ravel().tolist(),
            "color": np.round(linear, 6).ravel().tolist(),
        },
    )
