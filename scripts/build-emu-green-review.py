# SPDX-License-Identifier: Apache-2.0
"""Build the unified EMU exterior and terrain-draped EMU Green review."""

import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
PARAMETERS = ROOT / "data/metadata/emu-green-site-review.json"
DIRECTORY = "emu-green-review"
OUTPUT = SCENE / DIRECTORY
GROUND = "emu-green-paving"

path = Path(__file__).with_name("build-athletic-exterior-review.py")
spec = spec_from_file_location(path.stem, path)
builder = module_from_spec(spec)
spec.loader.exec_module(builder)
sample_ground = builder.geometry.sample_ground
flat, frame, face = builder.flat, builder.frame, builder.face
BRICK = (124, 67, 52)
OLD_BRICK = (149, 89, 69)
ROOF = (186, 187, 179)
STONE = (186, 176, 157)
METAL = (113, 123, 119)
DARK = (62, 79, 84)
SKY = (81, 129, 146)
COPPER = (95, 118, 111)


def fishbowl_outline(config):
    """Interpolate the map control points along the historic glass frontage."""
    walls = config["walls_enu_m"]
    controls = config["fishbowl_control_enu_m"]
    start = walls.index(controls[0])
    assert walls[start : start + len(controls)] == controls
    points = np.asarray([walls[start - 1], *controls, walls[start + len(controls)]])
    curve = []
    for p0, p1, p2, p3 in zip(points, points[1:], points[2:], points[3:]):
        for t in (0, 1 / 3, 2 / 3):
            p = 0.5 * (
                2 * p1
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
            )
            curve.append(p.tolist())
    curve.append(controls[-1])
    return walls[:start] + curve + walls[start + len(controls) :], LineString(curve)


def roof_sections(parts, plan, config):
    covered = Polygon()
    regions = []
    for entry in config["roofs"]:
        region = plan.intersection(box(*entry["bounds"])).difference(covered)
        regions.append((region, entry["z_m"], entry["name"]))
        covered = covered.union(region)
    regions.append((plan.difference(covered), config["fallback_z_m"], "central wings"))
    for region, height, name in regions:
        wall = OLD_BRICK if name.startswith(("west", "historic", "ballroom")) else BRICK
        flat(parts, region, config["footing_z_m"], height, wall, ROOF)
    return regions


def segment_faces(parts, outline, regions, field, fishbowl):
    ring = list(orient(outline).exterior.coords)
    for corners in zip(ring, ring[1:]):
        side = LineString(corners)
        if side.difference(fishbowl).length < 0.001:
            a, b = corners
            length, panel = face(parts, a, b)
            bottom = 7.09
            panel(0, length, -0.06, 0.28, 12.94, 13.28, COPPER)
            panel(0, length, 0.012, 0.10, bottom - 0.13, bottom + 0.53, OLD_BRICK)
            frame(
                panel, 0.025, length - 0.05, bottom + 0.53, 12.82, mullions=1, rails=1
            )
            continue
        for region, top, name in regions:
            section = side.intersection(region)
            for line in getattr(section, "geoms", [section]):
                if line.geom_type != "LineString" or line.length < 2.2:
                    continue
                a, b = line.coords[0], line.coords[-1]
                if side.project(Point(a)) > side.project(Point(b)):
                    a, b = b, a
                length, panel = face(parts, a, b)
                if length < 2:
                    continue
                panel(0, length, -0.06, 0.14, top - 0.18, top + 0.05, STONE)
                e, n = line.interpolate(0.5, normalized=True).coords[0]
                grade = sample_ground(field, e, n)
                bay_count = max(1, int(length / 3.42))
                bay = length / bay_count
                tall_glass = (
                    abs(a[0] - b[0]) < 0.16
                    and -220.1 <= e <= -213
                    and -113 < n < -67
                    and length > 3
                )
                shouldered = e > -212 and n < -54 and e < -162
                if tall_glass or shouldered:
                    lower = grade + 0.85 if tall_glass else grade + 0.62
                    frame(
                        panel,
                        0.22,
                        length - 0.44,
                        lower,
                        top - 0.48,
                        mullions=max(3, round(length / 1.25)),
                        rails=2,
                    )
                    for x in np.arange(0.72, length - 0.68, 2.5):
                        high = (
                            (top - 0.5)
                            if int(x / 2.5) % 2 == 0
                            else (lower + (top - lower) * 0.35)
                        )
                        low = (
                            (lower + (top - lower) * 0.78)
                            if int(x / 2.5) % 2 == 0
                            else lower
                        )
                        panel(
                            x,
                            x + 0.49,
                            0.061,
                            0.129,
                            low,
                            high,
                            SKY if tall_glass else METAL,
                        )
                    continue
                if name.startswith("west") and (
                    n > -103
                ):  # Fishbowl glass below a raised cap
                    frame(
                        panel,
                        0.12,
                        length - 0.24,
                        grade + 0.4,
                        min(top - 0.5, grade + 5.65),
                        mullions=max(2, round(length / 1.39)),
                        rails=1,
                    )
                    continue
                for i in range(bay_count):
                    start = bay * (i + 0.15)
                    width = bay * 0.62
                    for low in (grade + 0.52, grade + 4.63, grade + 8.67):
                        upper = min(top - 0.58, low + 2.48)
                        if upper - low > 0.7:
                            frame(panel, start, width, low, upper, mullions=1)
                    if grade + 3.68 < top - 0.5:
                        panel(
                            bay * i,
                            bay * (i + 1),
                            0.009,
                            0.082,
                            grade + 3.49,
                            grade + 3.67,
                            METAL,
                        )


def resolve_entrances(config, outline):
    entries = []
    for item in config["entrances"]:
        door = {
            key: value
            for key, value in item.items()
            if key
            not in (
                "wall_at_north_m",
                "design_elevation_ft",
            )
        }
        if "wall_at_north_m" in item:
            n = item["wall_at_north_m"]
            # The painted CPFM arrows point east towards the west facade.
            section = outline.intersection(LineString([(-320, n), (-153, n)]))
            e = section.bounds[0]
            door["position_enu_m"] = [e, n]
        entries.append(door)
    return entries


def entrances(parts, entries, field, config):
    datum = config["west_evidence"]["datum_440_ft_local_z_m"]
    design = {
        door["gate"]: door["design_elevation_ft"]
        for door in config["entrances"]
        if "design_elevation_ft" in door
    }
    for door in entries:
        e, n = door["position_enu_m"]
        z = sample_ground(field, e, n)
        if door["gate"] in design:
            z = datum + (design[door["gate"]] - 440) * 0.3048
            historic = door["gate"] == "emu-historic"
            w, h = (3.95, 3.62) if historic else (3.08, 2.81)
            angle = np.deg2rad(door["outward_degrees"])
            outward = np.array([np.sin(angle), np.cos(angle)])
            half_span = np.array([-outward[1], outward[0]]) * (w / 2)
            point = np.array([e, n])
            _, add = face(parts, point - half_span, point + half_span)
            add(0, w, -0.36, 0.82, z + h - 0.17, z + h, COPPER)
            add(0, 0.30, -0.35, 0.24, z - 0.17, z + h, STONE)
            add(w - 0.30, w, -0.35, 0.24, z - 0.17, z + h, STONE)
            frame(
                add,
                0.30,
                w - 0.61,
                z + 0.035,
                z + h - 0.18,
                0.19,
                4 if historic else 2,
                1,
            )
            add(0, w, -0.42, 0.43, z - 0.23, z + 0.035, STONE)
            grade = sample_ground(field, *(point + outward * 2.5))
            drop = z - grade
            assert -0.2 < drop < 2.5, (door["gate"], drop)
            count = max(1, round(drop / 0.17))
            for i in range(count):
                front = 0.4 + (i + 1) * 0.32
                top = z - drop * (i + 1) / count
                add(
                    0.14, w - 0.28, front - 0.34, front, grade - 0.16, top + 0.06, STONE
                )
            continue
        portal = door["gate"] == "emu-hearth"
        w, h = (5.62, 7.18) if portal else (5.95, 3.63)
        _, add = face(parts, (e, n - w / 2), (e, n + w / 2))
        outset = 0.43 if portal else 0.32
        if portal:
            add(0, 0.65, -0.14, outset, z, z + h, STONE)
            add(w - 0.65, w, -0.14, outset, z, z + h, STONE)
            add(0, w, -0.1, outset, z + h - 1.48, z + h, STONE)
            frame(add, 0.72, w - 1.44, z + 0.045, z + h - 1.49, 0.09, 4, 2)
        else:
            frame(add, 0.18, w - 0.36, z + 0.055, z + h - 0.31, 0.09, 5)
            add(0, w, -0.08, 0.83, z + h - 0.19, z + h + 0.18, METAL)
            add(0, 0.17, -0.1, outset, z, z + h, STONE)
            add(w - 0.17, w, -0.1, outset, z, z + h, STONE)


def north_bay(parts):
    width, add = face(parts, (-173.8, -27.85), (-187.45, -27.85))
    add(0.05, width - 0.05, 0.015, 0.59, 9.42, 16.72, METAL)
    frame(add, 0.16, width - 0.32, 9.74, 16.44, 0.6, 15, 4)
    add(0.02, width - 0.02, -0.02, 0.76, 9.37, 9.61, STONE)
    add(0.02, width - 0.02, -0.02, 0.75, 16.43, 16.71, METAL)


def roof_features(parts, config, outline):
    west, south, east, north, low, high = config["features"]["penthouse"]
    flat(parts, box(west, south, east, north).intersection(outline), low, high, METAL)
    for y in np.arange(low + 0.26, high, 0.41):
        for a, b in (((west, south), (east, south)), ((east, north), (west, north))):
            width, add = face(parts, a, b)
            add(0.04, width - 0.04, -0.008, 0.064, y, y + 0.042, (138, 145, 142))
    a, b, c, d = config["features"]["solar_bounds"]
    for e in np.arange(a + 0.25, c - 1.0, 1.19):
        for n in np.arange(b + 0.25, d - 0.8, 1.1):
            flat(parts, box(e, n, e + 1.05, n + 0.88), 15.16, 15.4, DARK, (57, 95, 117))
    for bounds, z in [
        ((-245.5, -58.9, -239.2, -55.75), 18.91),
        ((-232.7, -44.97, -228.87, -38.3), 15.42),
    ]:
        flat(parts, box(*bounds).intersection(outline), z - 0.06, z + 0.44, METAL, SKY)


def oval(center, radii):
    phase = np.linspace(0, 2 * np.pi, 96, endpoint=False)
    return Polygon(np.column_stack((np.cos(phase), np.sin(phase))) * radii + center)


def draped_green(config, outline, field):
    lawn = config["lawn"]
    inner = oval(lawn["center_enu_m"], lawn["inner_radii_m"])
    outer = oval(lawn["center_enu_m"], lawn["outer_radii_m"])
    assert outer.intersection(outline).area < 0.001
    cleared = builder.approaches(
        [
            {"outline": list(inner.exterior.coords), "rgb": [122, 143, 91]},
        ],
        field,
        outline,
    )
    hard = builder.approaches(
        [{"outline": list(outer.exterior.coords), "rgb": [171, 160, 144]}],
        field,
        outline.union(inner),
    )
    apron = builder.approaches(
        [
            {
                "outline": [
                    [-214.75, -84],
                    [-206.7, -81],
                    [-198.3, -71],
                    [-190.8, -66.1],
                    [-211.5, -66.3],
                    [-217.0, -77.1],
                ],
                "rgb": [170, 161, 148],
            },
        ],
        field,
        outline.union(outer),
    )
    ground = trimesh.util.concatenate((cleared, hard, apron))
    ground.apply_translation((0, lawn["surface_trim_m"], 0))
    return ground, inner


def sha(file):
    return sha256(file.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args()
    authored = json.loads(PARAMETERS.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    config_path = SCENE / "presentation.json"
    cfg = json.loads(config_path.read_bytes())
    assert (
        sha(SCENE / cfg["asset_url"])
        == cfg["asset_sha256"]
        == authored["source_asset_sha256"]
    )
    terrain = SCENE / manifest["heightfield_url"]
    field = json.loads(terrain.read_bytes())
    walls, fishbowl = fishbowl_outline(authored)
    outline = Polygon(walls)
    assert outline.is_valid
    id = authored["id"]
    duplicate = authored["absorbed_id"]
    prior = {
        r["id"]: Polygon(r["footprint_enu_m"]).buffer(0) for r in manifest["buildings"]
    }
    assert prior[duplicate].intersection(outline).area / prior[duplicate].area > 0.8
    assert all(
        outline.intersection(p).area < 0.01
        for b, p in prior.items()
        if b not in (id, duplicate)
    )
    parts = []
    regions = roof_sections(parts, outline, authored)
    segment_faces(parts, outline, regions, field, fishbowl)
    north_bay(parts)
    roof_features(parts, authored, outline)
    entries = resolve_entrances(authored, outline)
    entrances(parts, entries, field, authored)
    for gate in entries:
        assert outline.boundary.distance(Point(gate["position_enu_m"])) < 0.005
    building = trimesh.util.concatenate(parts)
    ground, green = draped_green(authored, outline, field)
    stage = trimesh.Scene()
    for name, mesh in ((id, building), (GROUND, ground)):
        stage.add_geometry(mesh, node_name=name, geom_name=name)

    def mark(tree):
        tree["asset"][
            "copyright"
        ] = "Open Campus contributors. Original geometry CC BY 4.0."
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.035, "roughnessFactor": 0.88}}
        ]
        for node in tree["nodes"]:
            if node.get("name") == id:
                node["extras"] = {"asset_kind": "building", "asset_id": id}
            elif node.get("name") == GROUND:
                node["extras"] = {
                    "asset_kind": "landscape-surface",
                    "surface_layer": "paving",
                }
        for mesh in tree["meshes"]:
            mesh["primitives"][0]["material"] = 0

    OUTPUT.mkdir(exist_ok=True)
    glb = OUTPUT / "site.glb"
    glb.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage, include_normals=True, tree_postprocessor=mark
        )
    )
    reimport = trimesh.load(glb, force="scene", process=False)
    assert set(reimport.graph.nodes_geometry) == {id, GROUND}
    assert np.allclose(stage.bounds, reimport.bounds, atol=0.00005)
    data = {
        "source_presentation_sha256": cfg["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": sha(terrain),
        "url": f"{DIRECTORY}/site.glb",
        "sha256": sha(glb),
        "ground_node": GROUND,
        "absorbed_ids": [duplicate],
        "building": {
            "id": id,
            "footprint_enu_m": walls,
            "base_z_m": authored["footing_z_m"],
            "roof_z_m": round(float(building.bounds[1, 1]), 4),
            "entrances": entries,
        },
    }
    site = OUTPUT / "site.json"
    site.write_text(
        json.dumps(data, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    if entry := cfg.get("emu_green_site"):
        assert entry["url"] == f"{DIRECTORY}/site.json"
        if entry["sha256"] != sha(site):
            entry["sha256"] = sha(site)
            config_path.write_text(
                json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
                encoding="utf8",
                newline="\n",
            )
    nav = json.loads((SCENE / "navigation.json").read_bytes())
    lines = [
        LineString([nav["nodes_enu_m"][a], nav["nodes_enu_m"][b]])
        for a, b, *_ in nav["edges"]
    ]
    conflict = [
        i
        for i, line in enumerate(lines)
        if line.distance(outline) < 0.42
        and line.distance(prior[id].union(prior[duplicate])) >= 0.42
    ]
    distances = np.arange(0, outline.exterior.length, 0.45)
    minimum = min(
        sample_ground(field, *outline.exterior.interpolate(d).coords[0])
        - authored["footing_z_m"]
        for d in distances
    )
    audit = {
        "building_area_m2": round(outline.area, 2),
        "old_building_area_m2": round(prior[id].area, 2),
        "old_duplicate_area_m2": round(prior[duplicate].area, 2),
        "lawn_overlap_m2": round(outline.intersection(green).area, 2),
        "new_route_conflicts": conflict,
        "footing_samples": len(distances),
        "minimum_footing_cover_m": round(minimum, 3),
        "building_triangles": len(building.faces),
        "terrain_triangles": len(ground.faces),
        "model_sha256": sha(glb),
        "site_sha256": sha(site),
    }
    assert minimum > 0
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf8")
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
