# SPDX-License-Identifier: Apache-2.0
"""Build six individually registered East Campus housing exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


path = Path(__file__).with_name("build-alder-millrace-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
approaches = module_from_spec(loader)
loader.loader.exec_module(approaches)
design = approaches.design
base, geometry, chapter = design.base, design.geometry, design.chapter
neighbor, shared, residential = design.neighbor, design.shared, design.residential
ROOT, SCENE = design.ROOT, design.SCENE
SPEC = ROOT / "data/metadata/east-campus-housing-exterior-review.json"
PACKAGE = "east-campus-housing-exterior-review"
KEY = "east_campus_housing_exterior_site"
GROUND = "east-campus-housing-approaches"
GLASS = (78, 103, 108)
FOOTING = (152, 146, 128)
BRICK = (143, 93, 77)


def trim_window(add, u, width, sill, top, trim, ribs=1):
    chapter.prior.window(add, u, width, sill, top, trim, GLASS, ribs=ribs)
    add(u - width * 0.56, u + width * 0.56, -0.001, 0.123, sill - 0.055, sill, trim)


def porch(parts, add, point, height, field, row, center, threshold):
    style = row["porch"]
    if style is None:
        if row["details"].get("door_awning"):
            add(center - 0.78, center + 0.78, -0.01, 0.36, threshold + 2.27,
                threshold + 2.38, row["trim_color"])
        return []
    left, right = center - style["span_m"] / 2, center + style["span_m"] / 2
    depth = style["depth_m"]
    trim = row["trim_color"]
    color = BRICK if style["posts"] == "brick" else FOOTING
    lower = min(geometry.sample_ground(field, *point(u, depth)) for u in (left, right))
    add(left, right, -0.022, depth + 0.045, lower - 0.14, threshold, color)
    head = threshold + 2.40
    if style.get("attached_roof", True):
        front = Polygon([point(u, d) for u, d in (
            (left, depth - 0.12), (right, depth - 0.12),
            (right, depth - 0.04), (left, depth - 0.04),
        )])
        limit = min(height(p) for p in front.exterior.coords) - 0.17
        head = min(head, limit - 0.06)
        if limit - head > 0.05:
            parts.append(geometry.shell(front, head, lambda e, n: max(head + 0.03, height((e, n)) - 0.16),
                                        row["wall_color"], trim))
    else:
        chapter.gabled_canopy(parts, point, center, style["span_m"] / 2 + 0.08,
                               -0.04, depth + 0.12, head, style["rise_m"], row["roof_color"], trim)
    add(left, right, depth - 0.21, depth + 0.03, head - 0.19, head - 0.02, trim)
    feet = []
    for u in (left + 0.13, right - 0.13):
        p = point(u, depth - 0.13)
        post_floor = threshold - 0.043
        post = 0.078 if style["posts"] == "wood" else 0.088
        if style["posts"] == "brick":
            feet.append(approaches.supported_post(parts, p, lower - 0.14, threshold + 0.54, BRICK, 0.22))
            post_floor = threshold + 0.51
        else:
            feet.append(Point(p).buffer(post, cap_style="square"))
        approaches.supported_post(parts, p, post_floor, head - 0.08, trim, post)
    return feet


def garage_front(add, u, width, z, door, trim):
    add(u - width/2 - 0.062, u + width/2 + 0.062, -0.01, 0.052, z, z + 2.14, trim)
    for i in range(5):
        low = z + 0.05 + 0.397 * i
        add(u - width/2, u + width/2, 0.048, 0.086, low, low + 0.376, door)


def elevations(parts, field, edges, height, row, gate, door_edge, u_door):
    supports = []
    trim = row["trim_color"]
    siding = tuple(max(0, x - 19) for x in row["wall_color"])
    garage = row["details"].get("garage")
    garage_edge = design.locate_face(edges, *garage[:2]) if garage else None
    for edge in edges:
        length, add, _, point, _, _ = chapter.setup_face(parts, *edge)
        if length < 1.02:
            continue
        mid = point(length / 2, 0)
        z0 = geometry.sample_ground(field, *mid)
        eave = min(height(point(u, 0)) for u in (0.0, length)) - 0.15
        wall_top = max(height(point(u, 0)) for u in np.linspace(0.02, length - 0.02, 13)) - 0.15
        vertical = row["details"].get("vertical_siding")
        if vertical:
            for u in np.arange(0.15, length - 0.10, 0.25):
                high = height(point(u, 0)) - 0.17
                if high > z0 + 0.35:
                    add(u, u + 0.013, -0.001, 0.018, z0 + 0.24, high, siding)
        else:
            for level in np.arange(z0 + 0.29, wall_top - 0.09, 0.16):
                # Continue the courses into a gable where the roof clears them.
                samples = np.linspace(0.03, length - 0.03, 40)
                visible = [u for u in samples if level + 0.09 < height(point(u, 0)) - 0.15]
                if len(visible) > 1:
                    add(visible[0], visible[-1], -0.002, 0.012, level, level + 0.014, siding)
        add(0.006, length - 0.006, -0.004, 0.032, z0 - 0.06, z0 + 0.23, FOOTING)
        if edge == door_edge:
            for dx, sill, width, ht in row["front_windows"]:
                u = u_door + dx
                if width / 2 + 0.09 < u < length - width / 2 - 0.09:
                    bottom = gate["threshold_z_m"] + sill
                    trim_window(add, u, width, bottom, bottom + ht, trim, ribs=2)
            if row["details"].get("entry_facing") == "transom":
                trim_window(add, u_door, 0.89, gate["threshold_z_m"] + 2.28,
                            gate["threshold_z_m"] + 2.53, trim)
            if row["details"].get("entry_facing") == "sidelight":
                trim_window(add, u_door + 0.72, 0.26, gate["threshold_z_m"] + 0.71,
                            gate["threshold_z_m"] + 1.99, trim)
            supports.extend(porch(parts, add, point, height, field, row, u_door, gate["threshold_z_m"]))
        elif edge == garage_edge:
            u = LineString(edge).project(Point(garage[0]))
            u = np.clip(u, garage[2] / 2 + 0.1, length - garage[2] / 2 - 0.1)
            garage_front(add, u, garage[2], z0 + 0.03, row["door_color"], trim)
        elif length > 3.18:
            for fraction in np.linspace(0.23, 0.77, max(2, round(length/4.4))):
                u = fraction * length
                local_z = geometry.sample_ground(field, *point(u, 0))
                bottom = local_z + 1.06
                top = min(bottom + 1.15, height(point(u, 0)) - 0.35)
                if top > bottom + 0.65:
                    trim_window(add, u, min(length*.20, 1.26), bottom, top, trim)
        if eave > z0 + 2.15:
            add(0.02, length - 0.02, -0.002, 0.025, z0 + 0.27, z0 + 0.29, trim)
    return supports


def roof_and_yard_details(parts, field, row, height, floor):
    details = row["details"]
    color, trim = row["wall_color"], row["trim_color"]
    accessory = []
    if stack := details.get("chimney"):
        e, n, width, length, top = stack
        plan = box(e-width/2, n-length/2, e+width/2, n+length/2)
        low = min(height(p) for p in plan.exterior.coords) - 0.33
        base.flat(parts, plan, low, top, (195, 183, 154))
        base.flat(parts, plan.buffer(0.04, join_style="mitre"), top-0.055, top+0.039, FOOTING)
    if dormer := details.get("dormer"):
        e, n, sill, width, tall = dormer
        length, add = design.tools.face(parts, (e, n-width/2), (e, n+width/2))
        trim_window(add, length/2, width-0.37, sill, sill+tall, trim, ribs=2)
    if garage := details.get("detached_garage"):
        w, s, e, n, eave, peak = garage
        shell = box(w,s,e,n)
        accessory.append(shell)
        roof = shell.buffer(0.14, join_style="mitre")
        ridge = (s+n)/2
        for side in (box(w-1,s-1,e+1,ridge), box(w-1,ridge,e+1,n+1)):
            area = roof.intersection(side)
            body = shell.intersection(side)

            def z_at(x, y):
                return peak - (peak-eave)*abs(y-ridge)/((n-s)/2)

            parts.append(geometry.shell(body, floor, lambda x, y: z_at(x,y)-.12, color, color))
            bottom = min(z_at(*p) for p in area.exterior.coords)-0.19
            panel = geometry.shell(area, bottom, z_at, trim, row["roof_color"])
            below = np.isclose(panel.vertices[:,1],bottom,rtol=0,atol=1e-6)
            panel.vertices[below, 1] = [z_at(x,-zz)-.14 for x,_,zz in panel.vertices[below]]
            parts.append(panel)
        length, add = design.tools.face(parts, (e,s), (e,n))
        local = geometry.sample_ground(field, e, ridge)
        garage_front(add, length/2, 2.45, local+.026, row["door_color"], trim)
    return accessory


def build(spec, manifest, config, field, graph):
    original = {row["id"]:row for row in manifest["buildings"]}
    models, records, plans, feet, entries, paving = {}, [], [], [], [], []
    for row in spec["models"]:
        id = row["id"]
        plan = orient(set_precision(Polygon(row["footprint_enu_m"]), 0.002))
        roof_plan = orient(set_precision(Polygon(row["roof_outline_enu_m"]).buffer(
            row["eaves_m"], join_style="mitre"
        ),0.002))
        assert plan.is_valid and roof_plan.covers(plan), id
        floor, _ = design.science.earlier.fit_base(field, roof_plan)
        pieces = []
        height = design.roof_sections(pieces, roof_plan, plan, floor, row)
        edges = list(shared.face_edges(plan))
        landing = row["porch"]["depth_m"] if row["porch"] else 0
        with_landing = row | {"entrance": row["entrance"] | {
            "landing_m": row["entrance"]["landing_m"] + landing,
        }}
        gate, edge, u = approaches.entry_stair(
            pieces, paving, edges, field, with_landing, None,
            top_run=max(0.72, landing + 0.055),
        )
        supports = elevations(pieces, field, edges, height, row, gate, edge, u)
        accessory = roof_and_yard_details(pieces, field, row, height, floor)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=0.000012))
        models[id] = design.science.ordered_mesh(mesh)
        entries.append(gate)
        plans.extend([plan, *accessory])
        feet.extend(supports)
        records.append({
            "id":id, "name":row["name"], "campus_id":row["campus_id"],
            "footprint_enu_m":base.ring(plan),
            "ground_footprints_enu_m":[base.ring(p) for p in [plan, *accessory]],
            "support_collision_enu_m":[base.ring(p) for p in supports],
            "base_z_m":round(floor,4), "roof_z_m":round(float(mesh.bounds[1,1]),4),
            "area_m2":round(sum(p.area for p in [plan, *accessory]),3), "entrances":[gate],
        })
    old = union_all([Polygon(original[id]["footprint_enu_m"]) for id in models])
    count, clearance = chapter.prior.nearby.shared.graduate.shared.check_routes(
        plans, feet, entries, old, manifest, graph, config, set(models)
    )
    grounds = design.science.ordered_mesh(trimesh.util.concatenate(paving))
    return models, records, grounds, count, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_bytes())
    manifest_path, config_path = SCENE/"manifest.json", SCENE/"presentation.json"
    manifest, config = [json.loads(p.read_bytes()) for p in (manifest_path, config_path)]
    terrain = SCENE/manifest["heightfield_url"]
    for p,key in ((manifest_path,"source_manifest_sha256"),(terrain,"source_heightfield_sha256")):
        if design.tools.digest(p) != spec[key]:
            raise ValueError(f"Changed East Campus registration source: {p.name}")
    models, records, ground, edges, clearance = build(
        spec, manifest, config, json.loads(terrain.read_bytes()),
        json.loads((SCENE/"navigation.json").read_bytes()),
    )
    appearances = json.loads((ROOT/"data/metadata/campus-expansion-audit.json").read_bytes())
    targets = {id:target for target, ids in appearances["context_batches"].items() for id in ids}
    patches = shared.frohnmayer.source_removals(
        {"absorbed_batches":[{"id":id,"target":targets[id]} for id in models]},config,appearances,
    )
    out = args.stage or SCENE/PACKAGE
    out.mkdir(parents=True,exist_ok=True)
    model, descriptor = out/"site.glb", out/"site.json"
    design.site.memorial.gerlinger.export(model,models,ground,GROUND,"east-campus-housing-paving")
    bundle = {
        "source_presentation_sha256":config["asset_sha256"],
        "source_base_model_sha256":manifest["model"]["sha256"],
        "source_heightfield_sha256":spec["source_heightfield_sha256"],
        "ground_node":GROUND, "url":f"{PACKAGE}/site.glb", "sha256":design.tools.digest(model),
        "buildings":records, "absorbed_ids":[], "batch_removals":patches,
    }
    descriptor.write_text(json.dumps(bundle,separators=(",",":"))+"\n",encoding="utf8",newline="\n")
    digest = design.tools.digest(descriptor)
    if args.stage is None:
        config[KEY] = {"url":f"{PACKAGE}/site.json","sha256":digest}
        config_path.write_text(json.dumps(config,indent=2,ensure_ascii=False)+"\n",encoding="utf8",newline="\n")
    audit = {
        "buildings":records, "route_edges":edges, "nearest_route_m":round(clearance,4),
        "triangles":{id:len(mesh.faces) for id,mesh in models.items()},
        "batch_removals":patches, "glb_sha256":bundle["sha256"],"descriptor_sha256":digest,
    }
    args.audit.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf8",newline="\n")
    print({k:audit[k] for k in ("route_edges","nearest_route_m","triangles","glb_sha256")})


if __name__ == "__main__":
    main()
