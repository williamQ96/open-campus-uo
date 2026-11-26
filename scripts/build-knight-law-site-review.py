# SPDX-License-Identifier: Apache-2.0
"""Build the registered Knight Law Center exterior, courtyard and approaches."""

import argparse
import json
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

source = Path(__file__).with_name("build-graduate-village-site-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, geometry = shared.site, shared.tools, shared.geometry
SCENE = tools.SCENE
SPEC = geometry.ROOT / "data/metadata/knight-law-site-review.json"
DIRECTORY = "knight-law-review"
GROUND = "knight-law-approaches"
BRICK = (153, 91, 76)
BRICK_RED = (142, 83, 69)
BASE = (126, 98, 82)
STONE = (205, 192, 165)
SILL = (189, 174, 151)
FRAME = (189, 187, 169)
GLASS = (68, 102, 112)
SHADE = (61, 72, 69)
METAL = (111, 120, 119)
SEAM = (124, 131, 128)
FLASHING = (139, 147, 142)
MEMBRANE = (118, 111, 102)
PAVING = (163, 155, 138)
PRECISION = 0.001


def clipped(region):
    return shapely.set_precision(region.buffer(0), PRECISION)


def roof_planes(ridge, pitches, hips):
    e, n, de, dn, z = ridge
    axis = np.array([de, dn]) / np.hypot(de, dn)
    side = np.array([-axis[1], axis[0]])

    def plane(point, slope):
        return [*slope, z - slope @ point]

    return np.unique(
        [plane((e, n), -pitches[0] * side), plane((e, n), pitches[1] * side)]
        + [
            plane((x, y), -pitch * np.array((east, north)) / np.hypot(east, north))
            for x, y, east, north, pitch in hips
        ],
        axis=0,
    )


def build_roof(parts, area, outer, planes, base, roof, collect_seams=False):
    for polygon, height in shared.roof_cells(area, planes):
        site.surface(
            parts, clipped(polygon), base, lambda e, n: height(e, n) - 0.15, BRICK, roof
        )

    metal = roof == METAL
    roof_layer = shared.shared.shared.roof_layer
    for polygon, height in shared.roof_cells(outer, planes):
        polygon = clipped(polygon)
        roof_layer(parts, polygon, height, 0.17 if metal else 0.21, 0, FLASHING, roof)
        if not collect_seams:
            continue
        w, s, e, n = polygon.bounds
        axis = int(abs(height(0, 1) - height(0, 0)) > abs(height(1, 0) - height(0, 0)))
        for line in np.arange(w + 0.25 if axis else s + 0.25, e if axis else n, 1.02):
            strip = (
                box(line, s, line + 0.027, n) if axis else box(w, line, e, line + 0.027)
            )
            tick = clipped(polygon.intersection(strip))
            if tick.area > 0.032:
                roof_layer(parts, tick, height, 0.025, 0.022, SEAM, SEAM)

    def height(e, n):
        return float(np.min(planes @ [e, n, 1]))

    return height


def roof_zones(parts, plan, data, base):
    rest = plan
    regions = []
    for zone in data["roof_zones"]:
        metal = zone["style"] == "metal"
        domain = plan if metal else rest
        area = clipped(domain.intersection(Polygon(zone["outline_enu_m"])))
        assert area.area > 35, zone["name"]
        rest = clipped(rest.difference(area))
        overhang = area.buffer(0.29, join_style="mitre").difference(
            plan.difference(area)
        )
        outer = clipped(overhang) if metal else area
        roof = build_roof(
            parts,
            area,
            outer,
            roof_planes(zone["ridge"], zone["pitches"], zone["hips"]),
            base,
            METAL if metal else MEMBRANE,
            collect_seams=metal,
        )
        regions.append((area, roof, zone["name"]))
    low = data["low_roof_z_m"]
    site.flat(parts, rest, base, low, BRICK_RED, MEMBRANE)
    regions.append((rest, lambda e, n: low, "Lower gallery"))
    return regions


def cross_gables(parts, plan):
    regions = []
    for e, low, high in [
        (112.62, -313.38, -303.31),
        (112.63, -327.18, -316.78),
        (112.67, -340.90, -330.66),
    ]:
        middle = (low + high) / 2
        area = clipped(plan.intersection(box(e - 0.39, low, 124.55, high)))
        outer = clipped(
            area.buffer(0.31, join_style="mitre").intersection(
                box(e - 0.38, low - 0.33, 124.55, high + 0.33)
            )
        )
        z = 21.92
        roof = build_roof(
            parts,
            area,
            outer,
            roof_planes(
                (e, middle, 1, 0, z), (0.75, 0.75), [(122.4, middle, 1, 0, 0.44)]
            ),
            14.63,
            METAL,
        )
        regions.append((area, roof, "West cross-gable"))
    area = clipped(plan.intersection(box(113.45, -281.33, 121.18, -270.06)))
    outer = clipped(area.buffer(0.29, join_style="mitre"))
    roof = build_roof(
        parts,
        area,
        outer,
        roof_planes((114, -276, 1, 0, 22.77), (0.69, 0.64), ()),
        15.65,
        METAL,
    )
    regions.append((area, roof, "Agate north gable"))
    for west, east in [(117.68, 126.25), (135.98, 144.42)]:
        middle = (west + east) / 2
        area = clipped(plan.intersection(box(west, -276.1, east, -268.5)))
        outer = clipped(
            area.buffer(0.28, join_style="mitre").intersection(
                box(west - 0.27, -276.1, east + 0.27, -268.5)
            )
        )
        roof = build_roof(
            parts,
            area,
            outer,
            roof_planes((middle, -269, 0, -1, 22.35), (0.71, 0.71), ()),
            16.1,
            METAL,
        )
        regions.append((area, roof, "North cross-gable"))
    return regions


def roof_features(parts, plan, regions):
    # The curving roof terrace lies above the interior street between the east wings.
    glazing = np.array(
        [
            [132.96, -318.6],
            [134.94, -318.6],
            [134.94, -328.2],
            [134.65, -334.8],
            [134.06, -340.68],
            [132.12, -340.68],
            [132.70, -334.8],
            [132.96, -328.2],
        ]
    )
    curb = Polygon(glazing).buffer(0.29, join_style="mitre")
    site.flat(parts, curb, 15.94, 16.37, FLASHING)
    site.flat(parts, Polygon(glazing), 16.36, 16.68, FRAME, GLASS)
    for n in np.arange(-340.35, -318.66, 0.88):
        rail = Polygon(glazing).intersection(box(131, n, 137, n + 0.054))
        site.flat(parts, rail, 16.66, 16.73, FRAME)
    ridge = LineString(
        [(133.1, -340.67), (133.68, -334.8), (133.95, -328.2), (133.95, -318.61)]
    )
    site.flat(parts, ridge.buffer(0.039, cap_style="flat"), 16.65, 16.76, FLASHING)
    for w, s, e, n, z in [
        (131.1, -291.42, 138.1, -285.4, 19.19),
        (131.04, -302.2, 134.33, -296.13, 18.06),
        (135.7, -299.95, 139.07, -293.28, 19.19),
        (141.2, -286.91, 144.9, -283.2, 18.68),
    ]:
        body = box(w, s, e, n).intersection(plan)
        site.flat(parts, body, 16.21, z, FLASHING, (168, 175, 169))
        for x in np.arange(w + 0.32, e - 0.14, 0.61):
            site.flat(
                parts, box(x, s - 0.025, x + 0.22, s + 0.005), 16.56, z - 0.21, SHADE
            )

    for name, dormers in (
        ("East middle wing", [(144.6, -306.9), (161.0, -306.9), (172.0, -306.93)]),
        (
            "South angled east wing",
            [(134.1, -348.0), (147.7, -350.5), (158.4, -352.7), (168.8, -354.8)],
        ),
    ):
        area, roof, _ = next(region for region in regions if region[2] == name)
        tangent = np.array([1.0, -0.201 if name.startswith("South") else 0.0])
        tangent /= np.linalg.norm(tangent)
        outward = np.array([-tangent[1], tangent[0]])
        for center in dormers:
            start = np.asarray(center) - 2.4 * tangent
            end = np.asarray(center) + 2.4 * tangent
            outline = Polygon(
                [start - 1.48 * outward, end - 1.48 * outward, end, start]
            )
            if outline.difference(area).area > 0.01:
                continue
            contact = roof(*center)

            def top(e, n):
                return contact + 0.78 - 0.19 * ((np.array([e, n]) - center) @ outward)

            site.surface(parts, outline, contact - 0.3, top, METAL, FLASHING)
            _, add = tools.face(parts, end, start)
            tools.frame(
                add, 0.22, 4.35, contact + 0.05, contact + 0.71, mullions=4, rails=0
            )

    area, roof, _ = next(
        region for region in regions if region[2] == "Curving interior street"
    )
    ring = list(orient(area).exterior.coords)
    for a, b in zip(ring, ring[1:]):
        if not (a[1] < b[1] and min(a[0], b[0]) > 136 and a[1] > -346.5):
            continue
        length, add = tools.face(parts, a, b)
        if length < 1.5:
            continue
        z = roof(*a)
        add(0.03, length - 0.03, 0.008, 0.15, z - 0.30, z - 0.19, STONE)
        for x in np.linspace(0.85, length - 0.85, max(1, round(length / 2.16))):
            site.rectangular_window(add, x, 1.35, z - 3.13, z - 2.11, 2)


def entry_arch(parts, a, b, outline, interior, exterior, paint):
    pieces = []
    site.flat(pieces, outline, interior, exterior, paint)
    tangent = np.asarray(b) - a
    tangent /= np.linalg.norm(tangent)
    outward = np.array((tangent[1], -tangent[0]))
    for mesh in pieces:
        u, depth, height = mesh.vertices.T
        e, n = np.asarray(a)[:, None] + tangent[:, None] * u + outward[:, None] * depth
        mesh.vertices = np.column_stack((e, -height, -n))
        parts.append(mesh)


def arch_portal(parts, a, b, length, add, gate, width, base):
    heritage = tools.load_builder("build-heritage-core-site-review.py")
    center = LineString((a, b)).project(Point(gate["position_enu_m"]))
    threshold = gate["threshold_z_m"]
    inner = heritage.memorial.museum.arch(
        center, width - 0.66, threshold - 0.12, threshold + 2.07, 3.00
    )
    outer = heritage.memorial.museum.arch(
        center, width, threshold - 0.16, threshold + 2.11, 3.43
    )
    heritage.profile(parts, a, b, inner, 0.078, SHADE)
    surround = outer.difference(inner)
    entry_arch(parts, a, b, surround, 0.006, 0.65, BRICK_RED)
    entry_arch(parts, a, b, surround, 0.65, 0.85, STONE)
    site.allen.doors(add, center, gate["width_m"], threshold)
    for x in np.linspace(center - 3.24, center + 3.24, 7):
        high = threshold + 1.98 + 2.9 * np.sqrt(1 - ((x - center) / 4.07) ** 2)
        add(x - 0.027, x + 0.027, 0.079, 0.13, threshold + 0.04, high, FRAME)
    add(
        center - 3.75,
        center + 3.75,
        0.085,
        0.14,
        threshold + 2.38,
        threshold + 2.432,
        FRAME,
    )
    for low, high in [
        (threshold + 5.72, threshold + 8.0),
        (threshold + 8.38, threshold + 9.32),
        (threshold + 11.18, threshold + 12.01),
    ]:
        tools.frame(add, 0.28, length - 0.56, low, high, mullions=8)
    add(0.15, length - 0.15, 0.02, 0.46, threshold + 8.02, threshold + 8.25, STONE)
    add(0.12, length - 0.12, 0.015, 0.17, base + 0.56, base + 0.69, SILL)


def courtyard_front(parts, a, b, add, length, grade, gate):
    # The east ground floor and mezzanine read as one recessed glazed gallery.
    for low, high in ((grade + 0.13, grade + 3.13), (grade + 3.95, grade + 7.28)):
        tools.frame(
            add,
            0.03,
            max(0.05, length - 0.06),
            low,
            high,
            mullions=max(1, round(length / 0.95)),
        )
    add(0.006, length - 0.006, 0.01, 0.21, grade + 3.22, grade + 3.86, STONE)
    add(0.006, length - 0.006, 0.018, 0.58, grade + 7.43, grade + 7.80, FLASHING)
    if gate:
        # The three-metre door bay spans several chords in this curved wall.
        center = LineString((a, b)).project(Point(gate["position_enu_m"]))
        site.allen.doors(add, center, gate["width_m"], gate["threshold_z_m"])


def elevations(parts, plan, regions, gables, field, gates, arch_width):
    ring = list(plan.exterior.coords)
    for a, b in zip(ring, ring[1:]):
        edge = LineString((a, b))
        length, add = tools.face(parts, a, b)
        if length < 0.2:
            continue
        midpoint = np.asarray(edge.interpolate(0.5, normalized=True).coords[0])
        e, n = midpoint
        outward = (b[1] - a[1], a[0] - b[0])
        grade = geometry.sample_ground(field, *midpoint)
        gate = next(
            (
                entry
                for entry in gates
                if edge.distance(Point(entry["position_enu_m"])) < 0.011
            ),
            None,
        )
        if gate and gate["gate"] == "agate-street":
            arch_portal(parts, a, b, length, add, gate, arch_width, grade)
            continue
        if outward[0] > 0 and 151.18 < e < 154.25 and -340.3 < n < -324.25:
            courtyard_front(parts, a, b, add, length, grade, gate)
            continue
        courtyard = (
            outward[1] < 0
            and -324.45 < n < -322.0
            and e > 154.05
            or outward[1] > 0
            and -348 < n < -340.1
            and e > 153
        )
        if courtyard and length > 0.54:
            courtyard_front(parts, a, b, add, length, grade, None)
            continue
        if gate:
            center = edge.project(Point(gate["position_enu_m"]))
            site.allen.doors(add, center, gate["width_m"], gate["threshold_z_m"])
            add(
                center - 1.42,
                center + 1.42,
                0.04,
                0.63,
                grade + 2.75,
                grade + 2.95,
                STONE,
            )
        way = (np.asarray(b) - a) / length

        def top_at(t):
            p = np.asarray(a) + t * way
            return max(
                (
                    height(*p)
                    for area, height, _ in regions + gables
                    if area.distance(Point(p)) < 0.003
                ),
                default=12.04,
            )

        top = min(top_at(0.018), top_at(length - 0.018))
        add(0.012, length - 0.012, 0.013, 0.063, grade - 0.31, grade + 0.41, BASE)
        for z in (
            grade + 0.77,
            grade + 3.50,
            grade + 7.23,
            grade + 11.04,
            grade + 14.3,
        ):
            if z < top - 0.43:
                add(0.018, length - 0.018, 0.009, 0.091, z, z + 0.079, STONE)
        west_gable = (
            outward[0] < -2 and e < 114.25 and -341.0 < n < -270.11 and length > 7
        )
        north_lunette = west_gable and n > -282
        count = (
            1
            if west_gable
            else max(1, round(length / (3.2 if outward[0] >= 0 else 2.65)))
        )
        spacing = length / count
        if spacing < 1.36:
            continue
        for i in range(count):
            center = (i + 0.5) * spacing
            height = top_at(center)
            for z, h in [
                (grade + 1.02, 1.89),
                (grade + 3.88, 2.48),
                (grade + 7.62, 2.60),
                (grade + 11.5, 1.80),
                (grade + 14.62, 1.27),
            ]:
                if z + h > height - 0.55:
                    continue
                if (
                    gate
                    and z < grade + 2
                    and abs(center - edge.project(Point(gate["position_enu_m"]))) < 2.04
                ):
                    continue
                if north_lunette and z > grade + 14:
                    heritage = tools.load_builder("build-heritage-core-site-review.py")
                    arch = heritage.memorial.museum.arch
                    outside = arch(center, 5.97, z - 0.08, z + 0.16, 1.61)
                    inside = arch(center, 5.64, z + 0.02, z + 0.18, 1.44)
                    heritage.profile(parts, a, b, outside, 0.09, STONE)
                    heritage.profile(parts, a, b, inside, 0.105, GLASS)
                    for offset in np.linspace(-2.25, 2.25, 7):
                        y = z + 0.18 + 1.38 * np.sqrt(1 - (offset / 2.82) ** 2)
                        add(
                            center + offset - 0.024,
                            center + offset + 0.024,
                            0.104,
                            0.15,
                            z + 0.03,
                            y,
                            FRAME,
                        )
                    continue
                if west_gable:
                    width = min(spacing * 0.67, 4.18 if z > grade + 14 else 6.12)
                    if z < grade + 2:
                        width *= 0.66
                else:
                    width = min(spacing * 0.80, 2.44 if outward[0] < 0 else 2.26)
                site.rectangular_window(
                    add, center, width, z, z + h, 3 if width > 2.05 else 2
                )
                add(
                    center - width * 0.54,
                    center + width * 0.54,
                    0.075,
                    0.222,
                    z - 0.13,
                    z - 0.02,
                    SILL,
                )
    # Engaged brick piers mark the two-storey courtyard elevations.
    for e, n in [
        (152.10, -326.0),
        (152.06, -328.4),
        (151.92, -333.35),
        (151.76, -335.76),
        (151.59, -338.29),
        (157.47, -322.26),
        (162.02, -322.26),
        (168.3, -323.12),
        (173.34, -323.12),
        (158.45, -344.2),
        (162.8, -345.19),
        (167.29, -345.45),
        (171.66, -346.47),
    ]:
        wall = plan.exterior.interpolate(plan.exterior.project(Point(e, n)))
        p = Point(wall.x, wall.y)
        pier = p.buffer(0.34, cap_style="square").envelope
        z = geometry.sample_ground(field, wall.x, wall.y)
        site.flat(parts, pier, z - 0.12, z + 7.47, BRICK_RED)
        for y in (z + 0.51, z + 3.62, z + 7.17):
            site.flat(parts, pier.buffer(0.035, join_style="mitre"), y, y + 0.17, STONE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(SPEC.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    config = json.loads(config_path.read_bytes())
    field_path = SCENE / manifest["heightfield_url"]
    field = json.loads(field_path.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    plan = orient(clipped(Polygon(data["footprint_enu_m"])))
    assert plan.is_valid and plan.geom_type == "Polygon"
    base = (
        min(
            geometry.sample_ground(field, *plan.exterior.interpolate(d).coords[0])
            for d in np.arange(0, plan.exterior.length, 0.55)
        )
        - 0.38
    )
    roof, ground, approaches, gates = [], [], [], []
    for gate in data["entries"]:
        assert plan.boundary.distance(Point(gate["position_enu_m"])) < 0.002
        entry, paving = site.approach(ground, field, gate)
        gates.append(entry)
        approaches.append(dict(outline=list(paving.exterior.coords), rgb=PAVING))
    regions = roof_zones(roof, plan, data, base)
    gables = cross_gables(roof, plan)
    roof_features(roof, plan, regions)
    elevations(roof, plan, regions, gables, field, gates, data["entry_arch_width_m"])
    # Preserve grass and planted islands. Model the continuous paved apron at the west end.
    for outline in (
        [
            (152, -339.7),
            (156.1, -340.58),
            (157.5, -338.26),
            (157.58, -326.42),
            (159.95, -323.23),
            (154.50, -322.24),
        ],
        [
            (115.98, -284.61),
            (113.83, -285.19),
            (107.22, -287.1),
            (98.06, -288.10),
            (97.5, -290.16),
            (97.82, -295.32),
            (107.09, -295.82),
            (112.89, -296.29),
            (116.02, -297.30),
        ],
        [
            (143.22, -358.8),
            (150.17, -360.2),
            (150.04, -364.77),
            (148.48, -367.78),
            (145.3, -368.03),
            (144.04, -364.5),
        ],
    ):
        approaches.append(dict(outline=outline, rgb=PAVING))
    apron = shapely.union_all([Polygon(item["outline"]) for item in approaches])
    approaches = [
        dict(outline=list(area.exterior.coords), rgb=PAVING)
        for area in geometry.sections(apron)
    ]
    ground.append(tools.approaches(approaches, field, plan))
    baseline = next(b for b in manifest["buildings"] if b["id"] == data["id"])
    route_count, clearance = shared.shared.check_routes(
        [plan],
        [],
        gates,
        Polygon(baseline["footprint_enu_m"]).buffer(0),
        manifest,
        graph,
        config,
        {data["id"]},
    )
    mesh = trimesh.util.concatenate(roof)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.00005))
    meshes = {data["id"]: shared.shared.shared.shared.index_mesh(mesh)}
    out = SCENE / DIRECTORY
    out.mkdir(exist_ok=True)
    glb = out / "site.glb"
    site.memorial.gerlinger.export(
        glb, meshes, trimesh.util.concatenate(ground), GROUND, "knight-law-paving"
    )
    descriptor = out / "site.json"
    payload = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=tools.digest(field_path),
        ground_node=GROUND,
        url=f"{DIRECTORY}/site.glb",
        sha256=tools.digest(glb),
        buildings=[
            {key: data[key] for key in ("id", "name", "campus_id")}
            | dict(
                footprint_enu_m=list(plan.exterior.coords)[:-1],
                base_z_m=round(base, 4),
                roof_z_m=round(float(mesh.bounds[1, 1]), 4),
                area_m2=round(plan.area, 2),
                entrances=gates,
            )
        ],
    )
    descriptor.write_text(
        json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    config["knight_law_site"] = dict(
        url=f"{DIRECTORY}/site.json", sha256=tools.digest(descriptor)
    )
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    audit = dict(
        area_m2=round(plan.area, 2),
        roof_regions={label: round(area.area, 2) for area, _, label in regions},
        entrances=gates,
        triangles=len(mesh.faces),
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
