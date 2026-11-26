# SPDX-License-Identifier: Apache-2.0
"""Register the pilot Knight Library exterior to the campus footprint."""

import argparse
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

geometry = import_module("build-cascade-exterior-review")
ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
SPEC = ROOT / "data/metadata/knight-library-exterior.json"
DIRECTORY = "knight-library-review"
PALETTE = {"heritage": (124, 41, 23), "red": (116, 56, 40), "silver": (175, 174, 169)}
STONE = (198, 171, 127, 255)
SOUTH_STONE = (176, 126, 98, 255)
SOUTH_GLASS = (43, 66, 62, 255)
SOUTH_METAL = (107, 123, 112, 255)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def colored(vertices, faces, color):
    mesh = trimesh.Trimesh(vertices, faces, process=False)
    mesh.visual.vertex_colors = color
    return mesh


def prism(parts, polygon, base, top, wall, roof):
    for piece in geometry.sections(polygon):
        parts.append(geometry.shell(piece, base, lambda *_: top, wall, roof))


def roofs(spec, outline):
    parts = []
    covered = Polygon()
    for zone in spec["roof_zones"]:
        region = outline.intersection(box(*zone["bounds_enu_m"])).difference(covered)
        assert region.area > 1, zone["label"]
        prism(
            parts,
            region,
            spec["footing_z_m"],
            zone["height_z_m"],
            PALETTE[zone["wall"]],
            PALETTE[zone["roof"]],
        )
        covered = covered.union(region)
    prism(
        parts,
        outline.difference(covered),
        spec["footing_z_m"],
        21.7,
        PALETTE["red"],
        PALETTE["silver"],
    )
    return parts


def pavilion_roof(piece, sides):
    e, n = piece["center_enu_m"]
    rx, rn = piece["radii_m"]
    angles = np.linspace(np.pi / 4, 2 * np.pi + np.pi / 4, sides, endpoint=False)
    if sides == 4:
        rx *= np.sqrt(2)
        rn *= np.sqrt(2)
    bottom = [
        (e + rx * np.cos(a), piece["eave_z_m"], -n - rn * np.sin(a)) for a in angles
    ]
    peak = (e, piece["peak_z_m"], -n)
    faces = [(i, (i + 1) % sides, sides) for i in range(sides)]
    return colored([*bottom, peak], faces, (62, 65, 62, 255))


def register(vertices, section, source_base):
    result = vertices.copy()
    lo, hi = section["source_east_m"]
    a, b = section["target_east_m"]
    result[:, 0] = a + (result[:, 0] - lo) * ((b - a) / (hi - lo))
    result[:, 1] = (
        section["base_z_m"] + (result[:, 1] - source_base) * section["height_scale"]
    )
    result[:, 2] += section["south_m"]
    return result


def front_from_source(source, bid, spec, source_base):
    parts, counts = [], {}
    allowed = {
        "brick",
        "brick-dark",
        "stone",
        "metal",
        "glass",
        "glass-light",
        "cream",
        "bronze",
    }
    for node in source.graph.nodes_geometry:
        if not node.startswith(bid + "_"):
            continue
        matrix, name = source.graph[node]
        mesh = source.geometry[name]
        material = mesh.visual.material
        if material.name not in allowed:
            continue
        triangles = trimesh.transform_points(
            mesh.triangles.reshape(-1, 3), matrix
        ).reshape(-1, 3, 3)
        front = triangles[triangles[:, :, 2].max(axis=1) <= 193.235]
        for section in spec["north_sections"]:
            a, b = section["source_east_m"]
            selected = front[
                (front[:, :, 0].min(axis=1) >= a) & (front[:, :, 0].max(axis=1) <= b)
            ]
            if not len(selected):
                continue
            vertices = register(selected.reshape(-1, 3), section, source_base)
            parts.append(
                colored(
                    vertices,
                    np.arange(len(vertices)).reshape(-1, 3),
                    material.baseColorFactor,
                )
            )
            label = section["label"]
            counts[label] = counts.get(label, 0) + len(selected)
    assert all(
        counts.get(section["label"], 0) > 200 for section in spec["north_sections"]
    )
    return parts, counts


def front_detail(parts, spec, config, bid, source_base):
    section = next(item for item in spec["north_sections"] if item["label"] == "middle")
    counts = {}
    for name, expected_sha in spec["source_detail_sha256"].items():
        path = SCENE / name
        assert digest(path) == expected_sha
        detail = read(path)
        assert (
            detail["building_id"] == bid
            and detail["base_asset_sha256"] == config["asset_sha256"]
        )
        for item in detail["objects"]:
            x, y, z = item["position"]
            if item["shape"] == "box":
                mesh = trimesh.creation.box(extents=item["size"])
                mesh.apply_translation([x, y, z])
            else:
                assert item["shape"] == "hip" and np.allclose(
                    item["rotation"], [np.pi, 0, 0]
                )
                w, h, d = item["size"]
                mesh = pavilion_roof(
                    dict(
                        center_enu_m=[x, -z],
                        radii_m=[w / 2, d / 2],
                        eave_z_m=y + h / 2,
                        peak_z_m=y - h / 2,
                    ),
                    4,
                )
                # The inverted roof is the visible underside of the balcony.
                mesh.invert()
            color = STONE if item["material"] == "stone" else (124, 41, 23, 255)
            parts.append(
                colored(
                    register(mesh.vertices, section, source_base), mesh.faces, color
                )
            )
            counts[item["role"]] = counts.get(item["role"], 0) + 1
    return counts


def cornices(parts):
    stripes = [
        (-573.7, -520.25, -202.58, 20.74),
        (-585.0, -574.0, -195.67, 12.25),
        (-520.02, -509.25, -196.12, 12.21),
    ]
    for west, east, front, height in stripes:
        for width, depth, dz in ((0.14, 0.22, -0.22), (0.23, 0.34, 0.02)):
            trim = trimesh.creation.box(extents=[east - west, width, depth])
            trim.apply_translation([(west + east) / 2, height + dz, -front])
            parts.append(colored(trim.vertices, trim.faces, STONE))


def south_facades(parts, outline):
    """Retain the photographed glazing cadence and two stone bands on the south addition."""
    ring = list(orient(outline).exterior.coords)
    for a, b in zip(ring, ring[1:]):
        edge = np.asarray(b) - a
        length = np.linalg.norm(edge)
        if length < 2.6 or max(a[1], b[1]) > -311:
            continue
        direction = edge / length
        outward = np.array([direction[1], -direction[0]])
        tower = min(a[0], b[0]) < -572.5 or max(a[0], b[0]) > -539.0
        if not tower and outward[1] > -0.7:
            continue
        matrix = np.eye(4)
        matrix[:3, 0] = [direction[0], 0, -direction[1]]
        matrix[:3, 2] = [outward[0], 0, -outward[1]]

        def element(along, depth, z, width, thickness, height, color):
            trim = trimesh.creation.box(extents=[width, height, thickness])
            e, n = np.asarray(a) + direction * along + outward * depth
            matrix[:3, 3] = [e, z, -n]
            trim.apply_transform(matrix)
            parts.append(colored(trim.vertices, trim.faces, color))

        bands = (14.45, 20.8) if tower else (14.45, 17.23)
        for z in bands:
            element(length / 2, 0.06, z, length + 0.015, 0.17, 0.47, SOUTH_STONE)
        cells = max(1, round(length / 3.6))
        for along in (np.arange(cells) + 0.5) * length / cells:
            span = min(2.24, 0.63 * length / cells)
            columns = (10.95, 17.25) if tower else (10.95,)
            for z in columns:
                height = 4.65 if z < 12 else 3.35
                element(along, 0.021, z, span + 0.19, 0.13, height + 0.21, SOUTH_STONE)
                element(along, 0.083, z, span, 0.027, height, SOUTH_GLASS)
                element(along, 0.105, z, 0.082, 0.02, height, SOUTH_METAL)
                for level in (-height / 4, 0, height / 4):
                    element(along, 0.106, z + level, span, 0.021, 0.067, SOUTH_METAL)

    # The south photograph shows a standing-seam upper face around the clerestory.
    cladding = trimesh.creation.box(extents=[54.98, 4.55, 0.10])
    cladding.apply_translation([-555.4, 24.77, 303.02])
    parts.append(colored(cladding.vertices, cladding.faces, (66, 96, 90, 255)))
    for e in np.arange(-582.65, -528, 1.08):
        if -560.1 < e < -550.7:
            continue
        seam = trimesh.creation.box(extents=[0.041, 4.55, 0.047])
        seam.apply_translation([e, 24.77, 303.077])
        parts.append(colored(seam.vertices, seam.faces, (55, 78, 75, 255)))
    for e in (-559.1, -557.25, -555.4, -553.55, -551.7):
        window = trimesh.creation.box(extents=[1.67, 2.08, 0.09])
        window.apply_translation([e, 24.52, 303.11])
        parts.append(colored(window.vertices, window.faces, SOUTH_GLASS))


def route_audit(outline, old, neighbors, field, entries):
    nav = read(SCENE / "navigation.json")
    lines = [
        LineString([nav["nodes_enu_m"][a], nav["nodes_enu_m"][b]])
        for a, b, *_ in nav["edges"]
    ]
    conflicts = [
        index
        for index, line in enumerate(lines)
        if line.distance(outline) < 0.42 <= line.distance(old)
    ]
    for gate in entries:
        x, n = gate["position_enu_m"]
        point = Point(x, n + 2.5)
        assert outline.boundary.distance(Point(x, n)) < 0.5
        assert outline.distance(point) > 0.5
        assert all(neighbor.distance(point) > 0.5 for neighbor in neighbors)
    samples = [
        outline.exterior.interpolate(d)
        for d in np.arange(0, outline.exterior.length, 0.45)
    ]
    ground = [geometry.sample_ground(field, p.x, p.y) for p in samples]
    return dict(
        routes=len(lines),
        new_route_conflicts=conflicts,
        terrain_samples=len(ground),
        minimum_grade_m=round(min(ground), 3),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    spec = read(SPEC)
    manifest_file = SCENE / "manifest.json"
    manifest = read(manifest_file)
    config = read(SCENE / "presentation.json")
    field_path = SCENE / manifest["heightfield_url"]
    art = SCENE / config["asset_url"]
    assert digest(manifest_file) == spec["source_manifest_sha256"]
    assert digest(field_path) == spec["source_heightfield_sha256"]
    assert digest(art) == spec["source_presentation_sha256"] == config["asset_sha256"]
    bid = spec["asset_id"]
    record = next(item for item in manifest["buildings"] if item["id"] == bid)
    outline = Polygon(spec["walls_enu_m"])
    assert outline.is_valid
    parts = roofs(spec, outline)
    parts.extend(pavilion_roof(section, 8) for section in spec["south_pavilions"])
    parts.append(pavilion_roof(spec["western_pavilion"], 8))
    front, counts = front_from_source(
        trimesh.load(art, force="scene", process=False), bid, spec, record["base_z_m"]
    )
    parts.extend(front)
    details = front_detail(parts, spec, config, bid, record["base_z_m"])
    cornices(parts)
    south_facades(parts, outline)
    building = trimesh.util.concatenate(parts)
    stage = trimesh.Scene()
    stage.add_geometry(building, node_name=bid, geom_name=bid)

    def metadata(tree):
        tree["asset"][
            "copyright"
        ] = "Open Campus contributors. Original geometry CC BY 4.0."
        tree["materials"] = [
            {"pbrMetallicRoughness": {"metallicFactor": 0.02, "roughnessFactor": 0.88}}
        ]
        tree["meshes"][0]["primitives"][0]["material"] = 0
        node = next(node for node in tree["nodes"] if node.get("name") == bid)
        node["extras"] = {"asset_id": bid, "asset_kind": "building"}

    entries = [
        dict(
            gate=gate,
            position_enu_m=[x, n],
            outward_degrees=0,
            estimated=True,
            snap_to_facade=False,
        )
        for gate, x, n in zip(
            ("memorial-west", "memorial-east"),
            spec["entry_east_enu_m"],
            (-195.23, -195.63),
        )
    ]
    audit = route_audit(
        outline,
        Polygon(record["footprint_enu_m"]),
        [
            Polygon(item["footprint_enu_m"]).buffer(0)
            for item in manifest["buildings"]
            if item["id"] != bid
        ],
        read(field_path),
        entries,
    )
    assert audit["minimum_grade_m"] > spec["footing_z_m"]
    output = SCENE / DIRECTORY
    output.mkdir(exist_ok=True)
    asset = output / "site.glb"
    asset.write_bytes(
        trimesh.exchange.gltf.export_glb(
            stage, include_normals=True, tree_postprocessor=metadata
        )
    )
    assert np.allclose(
        trimesh.load(asset, force="scene").bounds, stage.bounds, atol=0.00005
    )
    site = dict(
        source_presentation_sha256=config["asset_sha256"],
        source_base_model_sha256=manifest["model"]["sha256"],
        source_heightfield_sha256=spec["source_heightfield_sha256"],
        url=f"{DIRECTORY}/site.glb",
        sha256=digest(asset),
        building=dict(
            id=bid,
            footprint_enu_m=spec["walls_enu_m"],
            area_m2=round(outline.area, 2),
            base_z_m=spec["footing_z_m"],
            roof_z_m=float(building.bounds[1, 1]),
            entrances=entries,
        ),
    )
    path = output / "site.json"
    path.write_text(json.dumps(site, separators=(",", ":")) + "\n", encoding="utf-8")
    audit.update(
        area_m2=round(outline.area, 2),
        north_source_faces=counts,
        north_detail_parts=details,
        triangles=len(building.faces),
        model_sha256=digest(asset),
        site_sha256=digest(path),
    )
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit))


if __name__ == "__main__":
    main()
