# SPDX-License-Identifier: Apache-2.0
"""Build the registered northeast science complex exteriors."""

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-plc-lokey-tykeson-site-review.py")
loader = spec_from_file_location(source.stem, source)
prior = module_from_spec(loader)
loader.loader.exec_module(prior)
tools, site, geometry, earlier, shared = (
    prior.tools,
    prior.site,
    prior.geometry,
    prior.earlier,
    prior.shared,
)
flat, ring, union = prior.flat, prior.ring, prior.union
SCENE = prior.SCENE
SPEC = geometry.ROOT / "data/metadata/northeast-science-site-review.json"
DIRECTORY = "northeast-science-review"
GROUND = "northeast-science-grounds"

BRICK = (157, 91, 68)
BRICK_LIGHT = (168, 111, 83)
DEEP_BRICK = (111, 71, 61)
OFF_WHITE = (207, 210, 204)
CONCRETE = (165, 162, 149)
FIBER = (138, 141, 134)
STONE = (192, 184, 165)
DARK = (61, 72, 73)
GLASS = (72, 101, 109)
GLASS_PALE = (105, 132, 139)
STEEL = (167, 177, 171)
LINING = (213, 211, 194)
MEMBRANE = (175, 177, 174)
METAL_ROOF = (158, 163, 161)
WALK = (182, 177, 158)
PAVER = (158, 120, 101)
BED = (141, 150, 111)


def polygons(shape, threshold=0.035):
    return [
        p
        for p in shapely.get_parts(shape)
        if p.geom_type == "Polygon" and p.area > threshold
    ]


def raised(parts, shape, bottom, top, wall, roof):
    for p in polygons(shape.simplify(0.003)):
        flat(parts, p, bottom, top, wall, roof)


def arched_window(parts, a, b, center, width, sill, top):
    _, add = tools.face(parts, a, b)
    radius = width / 2
    spring = top - radius
    add(center - radius, center + radius, 0.035, 0.07, sill, spring, GLASS)
    for u in (center - radius, center + radius):
        add(u - 0.064, u + 0.064, 0.06, 0.13, sill - 0.062, spring, DEEP_BRICK)
    add(
        center - radius - 0.065,
        center + radius + 0.065,
        0.064,
        0.13,
        sill - 0.065,
        sill,
        STONE,
    )
    angles = np.linspace(0, np.pi, 13)
    unit_arc = np.column_stack((np.cos(angles), np.sin(angles)))
    origin = np.array([center, spring])
    inside = origin + unit_arc * radius
    outside = origin + unit_arc * (radius + 0.083)
    _, coordinate = shared.heritage.memorial.coordinate(a, b)

    def surface(triangles, offset, color):
        vertices = []
        for tri in triangles:
            for u, z in tri:
                e, n = coordinate(u, offset)
                vertices.append((e, z, -n))
        mesh = trimesh.Trimesh(
            vertices, np.arange(len(vertices)).reshape(-1, 3), process=False
        )
        mesh.visual.vertex_colors = [*color, 255]
        parts.append(mesh)

    surface(
        [(origin, start, end) for start, end in zip(inside[:-1], inside[1:])],
        0.071,
        GLASS,
    )
    frame = []
    for left, right, outer_left, outer_right in zip(
        inside[:-1], inside[1:], outside[:-1], outside[1:]
    ):
        frame.extend([(outer_left, outer_right, right), (outer_left, right, left)])
    surface(frame, 0.101, DEEP_BRICK)


def ordered_mesh(mesh):
    """Use the same index order for equivalent input triangles."""
    mesh.remove_unreferenced_vertices()
    xyz = np.round(mesh.vertices, 6)
    normals = np.round(mesh.vertex_normals, 6)
    xyz[xyz == 0] = 0
    normals[normals == 0] = 0
    values = np.column_stack((xyz, normals, mesh.visual.vertex_colors))
    vertices, lookup = np.unique(values, axis=0, return_inverse=True)
    faces = lookup[mesh.faces]
    roll = np.argmin(faces, axis=1)
    faces = np.take_along_axis(faces, (roll[:, None] + np.arange(3)) % 3, axis=1)
    order = np.lexsort(tuple(faces.T[::-1]))
    return trimesh.Trimesh(
        vertices=vertices[:, :3],
        faces=faces[order],
        vertex_normals=vertices[:, 3:6],
        vertex_colors=vertices[:, 6:].astype(np.uint8),
        process=False,
    )


def facade_runs(edges, roof, zones):
    regions = [(region.buffer(0.006), height) for region, height in zones]
    for a, b in edges:
        if not regions:
            yield a, b, roof
            continue
        edge = LineString((a, b))
        cuts = {0.0, edge.length}
        for region, _ in regions:
            for line in shapely.get_parts(edge.intersection(region)):
                if line.geom_type == "LineString":
                    cuts.update(edge.project(Point(xy)) for xy in line.coords)
        cuts = sorted(cuts)
        for start, end in zip(cuts, cuts[1:]):
            if end - start < 0.03:
                continue
            midpoint = edge.interpolate((start + end) / 2)
            height = next((z for p, z in regions if p.covers(midpoint)), roof)
            yield edge.interpolate(start).coords[0], edge.interpolate(end).coords[
                0
            ], height


def banded_windows(parts, plan, gates, datum, roof, style, zones=(), glass_faces=None):
    edges = shared.face_edges(plan)
    for a, b, z_top in facade_runs(edges, roof, zones):
        edge = LineString((a, b))
        length, add = tools.face(parts, a, b)
        if length < 0.95:
            continue
        p = edge.interpolate(0.5, normalized=True)
        if glass_faces is not None and glass_faces.covers(p):
            continue
        floor = datum + 0.40
        stories, step, wall = {
            "klamath": (4, 4.1, CONCRETE),
            "huestis": (3, 4.17, OFF_WHITE),
            "deschutes": (3, 3.2, BRICK),
            "streisinger": (4, 3.69, BRICK_LIGHT),
            "willamette": (4, 3.77, BRICK),
            "annex": (1, 3.04, OFF_WHITE),
        }[style]
        count = max(
            1,
            round(
                length
                / {"klamath": 2.60, "huestis": 2.72, "annex": 3.25}.get(style, 3.10)
            ),
        )
        pitch = length / count
        for story in range(stories):
            bottom = floor + step * story
            top = min(bottom + step * 0.83, z_top - 0.25)
            if top - bottom < 1.09:
                continue
            light = LINING if style in ("annex", "huestis", "klamath") else STONE
            band = 0.21 if style in ("klamath", "huestis") else 0.12
            if style != "annex":
                add(
                    0.03,
                    length - 0.03,
                    0.011,
                    0.13,
                    bottom - 0.06,
                    bottom + band,
                    light,
                )
            for i in range(count):
                u = (i + 0.5) * pitch
                width = pitch * (
                    0.71 if style in ("klamath", "huestis", "annex") else 0.58
                )
                if story == 0 and not prior.clear_of_entry(edge, u, width * 0.5, gates):
                    continue
                low = bottom + (0.27 if style == "annex" else 0.44)
                if style == "streisinger" and story == 0 and low + 1.35 < top:
                    arched_window(parts, a, b, u, width, low, top)
                else:
                    prior.window(
                        add,
                        u,
                        width,
                        low,
                        top,
                        light,
                        GLASS_PALE if i % 5 == 2 else GLASS,
                        3 if style == "annex" else 2,
                    )
            if style in ("klamath", "huestis"):
                depth = 0.43 if style == "klamath" else 0.26
                for i in range(count + 1):
                    u = float(np.clip(i * pitch, 0.11, length - 0.11))
                    add(
                        u - 0.101,
                        u + 0.101,
                        0.023,
                        depth,
                        bottom - 0.02,
                        top + 0.12,
                        wall,
                    )
        if length > 2.3 and style in ("deschutes", "streisinger", "willamette"):
            for y in (datum + 0.53, datum + 3.93):
                if y < z_top - 0.25:
                    add(0.03, length - 0.03, 0.013, 0.086, y, y + 0.089, STONE)
    prior.painted_doors(parts, shared.face_edges(plan), gates, STONE)


def hip(parts, shape, bottom, eave, peak, wall):
    for p in polygons(shape):
        levels = earlier.hip_planes(p.bounds, eave, peak)
        earlier.pitched(
            parts, p, p.buffer(0.16, join_style=2), levels, bottom, wall, METAL_ROOF
        )


def roof_zones(parts, plan, zones, base, wall):
    remaining = plan
    found = []
    for bounds, eave, peak in zones:
        zone = remaining.intersection(box(*bounds))
        hip(parts, zone, base, eave, peak, wall)
        found.append((zone, eave))
        remaining = remaining.difference(zone)
    return remaining, found


def onyx(parts, spec, plan, contacts, gates, field, base, datum):
    air = orient(Polygon(spec["air"]))
    west, east = spec["end_links"]
    sky = spec["clearance_floor"]
    roof = spec["roof"]
    main = air.intersection(box(west, 113, east, 133.75))
    for p in polygons(air):
        flat(parts, p, sky, roof, CONCRETE, MEMBRANE)
    for a, b in shared.face_edges(main):
        length, add = tools.face(parts, a, b)
        if length < 3 or abs(a[0] - b[0]) < abs(a[1] - b[1]):
            continue
        bays = max(1, round(length / 3.49))
        levels = np.linspace(sky + 0.87, roof - 0.40, 5)
        for i in range(bays):
            u0, u1 = i * length / bays, (i + 1) * length / bays
            for z0, z1 in zip(levels, levels[1:]):
                add(u0 + 0.045, u1 - 0.046, 0.015, 0.065, z0 + 0.10, z1 - 0.12, GLASS)
                add(
                    u0 + 0.03, u1 - 0.03, 0.013, 0.146, z1 - 0.112, z1 + 0.045, CONCRETE
                )
                corners = np.asarray(a) + (np.asarray(b) - a) * np.array(
                    [[u0 / length], [u1 / length]]
                )
                tangent = (np.asarray(b) - a) / length
                normal = np.array([tangent[1], -tangent[0]])
                p0, p1 = corners + normal * 0.24
                tools.beam(parts, (*p0, z0 + 0.08), (*p1, z1 - 0.12), 0.14, STEEL)
                tools.beam(parts, (*p1, z0 + 0.08), (*p0, z1 - 0.12), 0.14, STEEL)
            add(u0 + 0.02, u0 + 0.15, 0.035, 0.27, sky + 0.7, roof - 0.22, STEEL)
        add(0.02, length - 0.02, 0.006, 0.15, sky + 0.02, sky + 0.46, STONE)
        add(0.02, length - 0.02, 0.006, 0.14, roof - 0.23, roof + 0.18, STEEL)
    for link in (
        air.intersection(box(-270, 113, west, 132)),
        air.intersection(box(east, 118, -165.25, 126)),
    ):
        for p in polygons(link):
            for a, b in shared.face_edges(p):
                length, add = tools.face(parts, a, b)
                if length > 2.8:
                    prior.curtain(
                        add,
                        length,
                        sky + 0.59,
                        roof - 0.53,
                        max(2, round(length / 1.46)),
                        8,
                    )
    x, y, X, Y, z = spec["ridge"]
    raised(parts, box(x, y, X, Y).intersection(air), roof - 0.04, z, CONCRETE, MEMBRANE)
    for p, top in zip(contacts, [*spec["annex_roofs"], spec["core_roof"]]):
        raised(parts, p, base, top, OFF_WHITE, CONCRETE)
        banded_windows(parts, p, gates, datum, top, "annex")
    supports = []
    for x, y in spec["supports"]:
        pad = box(x - 0.35, y - 0.35, x + 0.35, y + 0.35)
        flat(
            parts,
            pad,
            geometry.sample_ground(field, x, y) - 0.2,
            sky + 0.01,
            CONCRETE,
            STONE,
        )
        supports.append(pad)
    return supports


def klamath(parts, spec, contact, entries, base, datum):
    prior.deck(parts, contact, base, (spec["roof"], spec["parapet"]), FIBER)
    for a, b, c, d, top in spec["equipment"]:
        raised(
            parts,
            contact.intersection(box(a, b, c, d)),
            spec["roof"] - 0.02,
            top,
            CONCRETE,
            MEMBRANE,
        )
    banded_windows(parts, contact, entries, datum, spec["roof"], "klamath")
    return []


def huestis(parts, spec, plan, contact, entries, base, datum):
    prior.deck(parts, contact, base, (spec["roof"], spec["parapet"]), BRICK)
    projecting = shapely.difference(plan, contact, grid_size=0.001)
    raised(parts, projecting, datum + 3.3, spec["parapet"], OFF_WHITE, MEMBRANE)
    for a, b, c, d, top in [spec["penthouse"], spec["west_tower"], *spec["end_towers"]]:
        raised(
            parts,
            box(a, b, c, d).intersection(plan),
            spec["roof"] - 0.04,
            top,
            FIBER,
            MEMBRANE,
        )
    banded_windows(parts, contact, entries, datum, spec["roof"], "huestis")
    for p in polygons(projecting):
        for a, b in shared.face_edges(p):
            length, add = tools.face(parts, a, b)
            if length > 2.8:
                prior.curtain(
                    add,
                    length,
                    datum + 3.55,
                    spec["roof"] - 0.37,
                    max(2, round(length / 1.56)),
                    5,
                )
    return []


def deschutes(parts, spec, plan, contact, gates, base, datum):
    west = box(*spec["bay"]).intersection(plan)
    # The glazed bay overhangs the recessed entry.
    raised(parts, west, datum + 3.0, spec["bay_top"], DEEP_BRICK, METAL_ROOF)
    for p in polygons(west):
        for a, b in shared.face_edges(p):
            length, add = tools.face(parts, a, b)
            if length > 1.8:
                prior.curtain(add, length, datum + 3.20, spec["bay_top"] - 0.22, 3, 4)
    hipped, zones = roof_zones(parts, contact, spec["hip_sections"], base, BRICK_LIGHT)
    prior.deck(parts, hipped, base, (spec["roof"], spec["roof"] + 0.24), BRICK)
    long = box(*spec["long_roof"]).intersection(plan)
    hip(parts, long, spec["roof"] - 0.035, 12.22, spec["ridge"], BRICK)
    a, b, c, d = spec["lightwell"]
    for bounds in (
        (a, b, c, b + 0.20),
        (a, d - 0.20, c, d),
        (a, b + 0.20, a + 0.20, d - 0.20),
        (c - 0.20, b + 0.20, c, d - 0.20),
    ):
        raised(
            parts,
            box(*bounds).intersection(contact),
            spec["roof"],
            11.90,
            CONCRETE,
            METAL_ROOF,
        )
    banded_windows(parts, contact, gates, datum, spec["roof"], "deschutes", zones)
    return []


def streisinger(parts, spec, plan, contact, entries, base, datum):
    remaining, zones = roof_zones(
        parts, contact, spec["hip_sections"], base, BRICK_LIGHT
    )
    prior.deck(parts, remaining, base, (spec["roof"], spec["roof"] + 0.32), BRICK)
    for a, b, c, d, z in spec["sills"]:
        raised(
            parts, box(a, b, c, d).intersection(contact), z - 0.23, z, STONE, MEMBRANE
        )
    passage = shapely.intersection(plan, box(*spec["west_link"]), grid_size=0.001)
    raised(parts, passage, spec["deck_floor"], 17.65, CONCRETE, METAL_ROOF)
    for area in polygons(passage):
        for a, b in shared.face_edges(area):
            length, add = tools.face(parts, a, b)
            if length > 4:
                prior.curtain(
                    add,
                    length,
                    spec["deck_floor"] + 0.53,
                    17.1,
                    max(3, round(length / 1.5)),
                    7,
                )
    banded_windows(
        parts,
        contact,
        entries,
        datum,
        spec["roof"],
        "streisinger",
        zones,
    )
    return []


def willamette(parts, spec, plan, entries, field, base, datum):
    glass = plan.intersection(box(*spec["atrium"]))
    tower = plan.intersection(box(*spec["tower"]))
    decks = [
        (plan.intersection(box(x, y, X, Y)), z) for x, y, X, Y, z in spec["flat_decks"]
    ]
    area = plan.difference(union([glass, tower, *(p for p, _ in decks)]))
    for p, z in decks:
        raised(parts, p, base, z, CONCRETE, MEMBRANE)
    remaining, zones = roof_zones(parts, area, spec["hip_sections"], base, BRICK)
    prior.deck(parts, remaining, base, (spec["roof"], spec["parapet"]), BRICK)
    hip(parts, tower, base, spec["tower_eave"], spec["tower_peak"], BRICK)
    gable = earlier.hip_planes(glass.bounds, spec["atrium_eave"], spec["atrium_peak"])
    for area, z in earlier.roof_cells(glass, gable):
        site.surface(parts, area, base, lambda x, y: z(x, y) - 0.13, BRICK, GLASS_PALE)
        earlier.roof_layer(parts, area, z, 0.13, 0.018, STEEL, GLASS_PALE)
    for p in polygons(glass):
        for a, b in shared.face_edges(p):
            length, add = tools.face(parts, a, b)
            if length > 1.6:
                prior.curtain(
                    add,
                    length,
                    datum + 0.33,
                    spec["atrium_eave"] - 0.18,
                    max(3, round(length / 1.68)),
                    9,
                )
    banded_windows(
        parts,
        plan,
        entries,
        datum,
        spec["roof"],
        "willamette",
        [*zones, *decks, (glass, spec["atrium_eave"]), (tower, spec["tower_eave"])],
        glass.buffer(0.05),
    )
    # A narrow roof and light strips identify the west covered walk.
    x, y, X, Y = spec["porch"]
    cap = datum + 4.31
    flat(parts, box(x, y, X, Y), cap - 0.16, cap, STONE, METAL_ROOF)
    for n in np.arange(y + 2.43, Y - 0.7, 4.4):
        flat(
            parts,
            box(x + 0.32, n - 0.79, X - 0.15, n + 0.79),
            cap - 0.015,
            cap + 0.041,
            STEEL,
            GLASS_PALE,
        )
    supports = []
    for n in (y + 0.51, y + 5.23, y + 8.27, y + 16.17, y + 21.05, Y - 0.48):
        e = x + 0.29
        pad = box(e - 0.21, n - 0.22, e + 0.21, n + 0.22)
        flat(
            parts,
            pad,
            geometry.sample_ground(field, e, n) - 0.14,
            cap,
            BRICK_LIGHT,
            STONE,
        )
        supports.append(pad)
    return supports


def build(spec, manifest, config, field, graph):
    meshes, records, ground_parts, solids, supports, entries, pavers = (
        {},
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for campus, row in spec["models"].items():
        plan = orient(Polygon(row["footprint_enu_m"]))
        contact = [orient(Polygon(s)) for s in row["ground_footprints_enu_m"]]
        assert plan.is_valid and all(p.is_valid for p in contact)
        base, datum = earlier.fit_base(field, plan)
        parts, gates, feet = [], [], []
        for entry in row["entrances"]:
            assert (
                min(
                    p.boundary.distance(Point(entry["position_enu_m"])) for p in contact
                )
                < 0.004
            )
            gate, walk, caps = shared.site_entry(ground_parts, field, entry)
            gates.append(gate)
            pavers.append(walk)
            feet.extend(caps)
        model = contact[0]
        if campus == "037":
            extra = onyx(parts, row, plan, contact, gates, field, base, datum)
        elif campus == "028B":
            raised(parts, model, base, row["roof"], OFF_WHITE, CONCRETE)
            banded_windows(parts, model, gates, datum, row["roof"], "annex")
            extra = []
        elif campus == "038":
            extra = klamath(parts, row, model, gates, base, datum)
        elif campus == "040":
            extra = huestis(parts, row, plan, model, gates, base, datum)
        elif campus == "044":
            extra = deschutes(parts, row, plan, model, gates, base, datum)
        elif campus == "045":
            extra = streisinger(parts, row, plan, model, gates, base, datum)
        else:
            extra = willamette(parts, row, model, gates, field, base, datum)
        feet.extend(extra)
        mesh = trimesh.util.concatenate(parts)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
        id = row["id"]
        meshes[id] = ordered_mesh(mesh)
        records.append(
            dict(
                id=id,
                name=row["name"],
                campus_id=row["campus_id"],
                footprint_enu_m=ring(plan),
                ground_footprints_enu_m=[ring(p) for p in contact],
                support_collision_enu_m=[ring(p) for p in feet],
                entrances=gates,
                base_z_m=round(base, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                area_m2=round(plan.area, 3),
            )
        )
        solids.extend(contact)
        supports.extend(feet)
        entries.extend(gates)
    known = set(meshes) | set(spec["absorbed_into"])
    prior_solids = union(
        [
            Polygon(r["footprint_enu_m"]).buffer(0)
            for r in manifest["buildings"]
            if r["id"] in known
        ]
    )
    total, separation = prior.nearby.shared.graduate.shared.check_routes(
        solids, supports, entries, prior_solids, manifest, graph, config, known
    )
    blocked = union([*solids, *supports])
    for line, width in (
        (
            [
                (-245, 114.4),
                (-223, 114.2),
                (-207.3, 114.5),
                (-193.7, 114.52),
                (-167.8, 113.9),
            ],
            2.48,
        ),
        ([(-205, 112.0), (-205, 123.2), (-205, 136.8)], 1.94),
        ([(-173.3, 77.4), (-171.3, 73.63), (-170.86, 66.77)], 2.15),
        ([(-163.5, 14.52), (-162.99, 23.47), (-162.76, 35.5)], 2.85),
        ([(-103.76, 101.7), (-104.17, 96.4), (-106.45, 92.32), (-107.3, 89.9)], 2.08),
    ):
        area = LineString(line).buffer(width * 0.5, join_style=2, cap_style=2)
        prior.nearby.add_paths(ground_parts, field, area, blocked, WALK)
    prior.nearby.add_paths(ground_parts, field, union(pavers), blocked, PAVER)
    return (
        meshes,
        records,
        ordered_mesh(trimesh.util.concatenate(ground_parts)),
        total,
        separation,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, count, separation = build(
        spec, manifest, config, field, graph
    )
    appearances = json.loads(
        (geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes()
    )
    removals = shared.frohnmayer.source_removals(spec, config, appearances)
    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    model = output / "site.glb"
    site.memorial.gerlinger.export(
        model, meshes, ground, GROUND, "northeast-science-paving"
    )
    descriptor = output / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(model),
        buildings=records,
        absorbed_ids=list(spec["absorbed_into"]),
        batch_removals=removals,
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["northeast_science_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8",
        newline="\n",
    )
    result = dict(
        areas={b["id"]: b["area_m2"] for b in records},
        entrances={b["id"]: b["entrances"] for b in records},
        triangles={id: len(m.faces) for id, m in meshes.items()},
        route_edges=count,
        nearest_route_m=round(separation, 3),
        batch_removals=removals,
        glb_sha256=payload["sha256"],
        descriptor_sha256=tools.digest(descriptor),
        underpass_m={
            f"{x},{y}": round(
                spec["models"]["037"]["clearance_floor"]
                - geometry.sample_ground(field, x, y),
                3,
            )
            for x, y in ((-218, 120), (-206, 123), (-206, 130))
        },
    )
    args.audit.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf8", newline="\n"
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "areas",
                    "triangles",
                    "route_edges",
                    "nearest_route_m",
                    "underpass_m",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
