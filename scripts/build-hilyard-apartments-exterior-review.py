# SPDX-License-Identifier: Apache-2.0
"""Build the registered 973 Hilyard exterior omitted from the source scene."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient

source = Path(__file__).with_name("build-alder-millrace-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)

ROOT, SCENE = shared.ROOT, shared.SCENE
PACKAGE = "hilyard-apartments-exterior-review"
GROUND = "hilyard-apartments-approach"
KEY = "hilyard_apartments_exterior_site"
TRIM = (220, 214, 196)
AWNING = (42, 75, 110)


def elevations(parts, field, spec, edges, height, gate):
    fronts = {"west": 270, "north": 0, "south": 180}
    for edge in edges:
        span, add, outward, position, _, _ = shared.chapter.setup_face(parts, *edge)
        grade = shared.geometry.sample_ground(field, *position(span / 2, 0))
        top = min(height(position(u, 0)) for u in (0.03, span / 2, span - 0.03))
        if top > grade + 0.55:
            add(
                0.01,
                span - 0.01,
                0.003,
                0.022,
                grade - 0.08,
                grade + 0.40,
                (142, 129, 115),
            )
        for level in np.arange(grade + 0.45, top - 0.075, 0.114):
            add(0.025, span - 0.025, 0.003, 0.013, level, level + 0.013, (124, 72, 59))
        if top > grade + 3.02:
            add(
                0.01,
                span - 0.01,
                0.003,
                0.053,
                grade + 2.73,
                grade + 2.81,
                (167, 123, 103),
            )
        if top > grade + 1.4:
            add(0.005, span - 0.005, 0.002, 0.08, top - 0.13, top, TRIM)

        direction = float(np.degrees(np.arctan2(*outward))) % 360
        for name, bearing in fronts.items():
            if abs((direction - bearing + 180) % 360 - 180) > 6:
                continue
            row = spec["window_rows"][name]
            for station in next(
                values for key, values in row.items() if key.startswith("stations")
            ):
                x, n = position(span / 2, 0)
                chosen = (x, station) if name == "west" else (station, n)
                if name == "west" and abs(station - gate["position_enu_m"][1]) < 1.45:
                    continue
                midpoint = LineString(edge).project(Point(chosen))
                width = row["width_m"]
                if not width / 2 + 0.08 < midpoint < span - width / 2 - 0.08:
                    continue
                for sill in (grade + 0.94, grade + 3.52):
                    a, b = midpoint - width / 2, midpoint + width / 2
                    head = min(
                        sill + 1.18,
                        height(position(a, 0)) - 0.28,
                        height(position(b, 0)) - 0.28,
                    )
                    if head > sill + 0.55:
                        shared.chapter.prior.window(
                            add,
                            midpoint,
                            width,
                            sill,
                            head,
                            TRIM,
                            shared.design.GLASS,
                            ribs=2,
                        )
                        add(
                            a - 0.11,
                            b + 0.11,
                            -0.006,
                            0.13,
                            sill - 0.07,
                            sill + 0.006,
                            TRIM,
                        )


def awning(parts, edge, center, threshold):
    _, add, outward, point, _, _ = shared.chapter.setup_face(parts, *edge)
    a, b = center - 1.30, center + 1.30
    shape = Polygon(
        [point(u, d) for u, d in ((a, -0.026), (b, -0.026), (b, 1.34), (a, 1.34))]
    )

    origin = point(center, 0)

    def plane(e, n):
        return threshold + 2.83 - 0.34 * (np.array([e, n]) - origin) @ outward

    body = shared.geometry.shell(shape, threshold + 2.23, plane, AWNING, AWNING)
    lows = np.isclose(body.vertices[:, 1], threshold + 2.23, atol=0.00001, rtol=0)
    body.vertices[lows, 1] = [plane(e, -z) - 0.078 for e, _, z in body.vertices[lows]]
    parts.append(body)
    add(a, b, 1.32, 1.36, threshold + 2.20, threshold + 2.37, AWNING)
    for u in (a + 0.13, b - 0.13):
        add(
            u - 0.023,
            u + 0.023,
            -0.017,
            1.28,
            threshold + 2.33,
            threshold + 2.37,
            (76, 82, 83),
        )
    add(
        center - 0.29,
        center + 0.29,
        0.015,
        0.06,
        threshold + 2.92,
        threshold + 3.09,
        (223, 216, 195),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(
        (ROOT / "data/metadata/hilyard-apartments-exterior-review.json").read_bytes()
    )
    manifest_file, config_file = SCENE / "manifest.json", SCENE / "presentation.json"
    manifest, config = [
        json.loads(path.read_bytes()) for path in (manifest_file, config_file)
    ]
    field_file = SCENE / manifest["heightfield_url"]
    digest = shared.design.tools.digest
    assert digest(manifest_file) == spec["source_manifest_sha256"]
    assert digest(field_file) == spec["source_heightfield_sha256"]
    field = json.loads(field_file.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())

    roof_outline = orient(Polygon(spec["city_outline_enu_m"]))
    assert roof_outline.is_valid
    plan = orient(roof_outline.buffer(-0.30, join_style="mitre"))
    floor, _ = shared.design.science.earlier.fit_base(field, plan)
    edges = list(shared.design.shared.face_edges(plan))
    pieces, paving = [], []
    height = shared.design.roof_sections(
        pieces, roof_outline, plan, floor, spec, grid=0.0001
    )
    gate, face, center = shared.entry_stair(pieces, paving, edges, field, spec, None)
    elevations(pieces, field, spec, edges, height, gate)
    awning(pieces, face, center, gate["threshold_z_m"])
    mesh = trimesh.util.concatenate(pieces)
    mesh.update_faces(mesh.nondegenerate_faces(height=0.00002))
    mesh = shared.design.science.ordered_mesh(mesh)
    paving = shared.design.science.ordered_mesh(trimesh.util.concatenate(paving))
    building_id = spec["id"]
    assert not any(record["id"] == building_id for record in manifest["buildings"])
    scanned, clearance = (
        shared.chapter.prior.nearby.shared.graduate.shared.check_routes(
            [plan], [], [gate], Polygon(), manifest, graph, config, {building_id}
        )
    )
    out = args.stage or SCENE / PACKAGE
    out.mkdir(parents=True, exist_ok=True)
    model, descriptor = out / "site.glb", out / "site.json"
    shared.design.site.memorial.gerlinger.export(
        model, {building_id: mesh}, paving, GROUND, "hilyard-apartments-paving"
    )
    record = {
        "id": building_id,
        "name": spec["name"],
        "street_address": spec["street_address"],
        "footprint_enu_m": shared.base.ring(plan),
        "base_z_m": round(floor, 4),
        "roof_z_m": round(float(mesh.bounds[1, 1]), 4),
        "area_m2": round(plan.area, 3),
        "entrances": [gate],
    }
    pack = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": spec["source_heightfield_sha256"],
        "ground_node": GROUND,
        "url": f"{PACKAGE}/site.glb",
        "sha256": digest(model),
        "buildings": [record],
        "new_building_ids": [building_id],
    }
    descriptor.write_text(
        json.dumps(pack, separators=(",", ":")) + "\n", encoding="utf8", newline="\n"
    )
    descriptor_sha = digest(descriptor)
    if args.stage is None:
        config[KEY] = {"url": f"{PACKAGE}/site.json", "sha256": descriptor_sha}
        config_file.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf8",
            newline="\n",
        )
    audit = {
        "building": record,
        "triangles": len(mesh.faces),
        "route_edges": scanned,
        "closest_route_m": round(clearance, 4),
        "glb_sha256": pack["sha256"],
        "descriptor_sha256": descriptor_sha,
    }
    args.audit.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        encoding="utf8",
        newline="\n",
    )
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == "__main__":
    main()
