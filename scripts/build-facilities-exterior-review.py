# SPDX-License-Identifier: Apache-2.0
"""Build registered UO facilities and the Romania showroom and warehouse."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


source = Path(__file__).with_name("build-campus-frontage-review.py")
loader = spec_from_file_location(source.stem, source)
shared = module_from_spec(loader)
loader.loader.exec_module(shared)
site, tools, science, geometry, prior = shared.site, shared.tools, shared.science, shared.geometry, shared.prior
SCENE = shared.SCENE
SPEC = geometry.ROOT / "data/metadata/facilities-exterior-review.json"
DIRECTORY = "facilities-exterior-review"
GROUND = "facilities-exterior-approaches"
PRECISION = 0.001

PALETTE = {
    "charcoal": (113, 124, 126),
    "cream": (206, 201, 181),
    "membrane": (204, 205, 192),
    "weathered": (178, 164, 150),
    "metal": (158, 170, 161),
    "zinc": (193, 199, 191),
    "slate": (136, 148, 147),
    "pale": (188, 193, 181),
}
GLASS = (88, 118, 127)
SEA = (92, 131, 144)
TRIM = (178, 190, 184)
FOUNDATION = (169, 165, 149)
FASCIA = (100, 120, 118)
DARK = (78, 96, 95)
PAVING = (175, 167, 152)
WHITE = (216, 216, 204)


def precise(plan):
    return set_precision(plan, PRECISION)


def height_function(profile, axis):
    stations, heights = np.asarray(profile).T
    return lambda e, n: np.interp((e, n)[axis], stations, heights)


def profile_slices(region, axis, profile):
    bounds = region.bounds
    breaks = [bounds[axis], *[x for x, _ in profile if bounds[axis] < x < bounds[axis+2]], bounds[axis+2]]
    for left, right in zip(breaks, breaks[1:]):
        crop = box(left, bounds[1], right, bounds[3]) if axis == 0 else box(bounds[0], left, bounds[2], right)
        section = precise(region.intersection(crop))
        if section.area > 0.0005:
            yield section


def roof_geometry(parts, plan, zones, floor):
    remaining = plan
    surfaces = []
    for zone in zones:
        section = precise(remaining.intersection(box(*zone["bounds"])))
        if section.area <= 0.001:
            continue
        remaining = precise(remaining.difference(section))
        axis, profile = zone["axis"], zone["profile"]
        top = height_function(profile, axis)
        roof, wall = PALETTE[zone["roof"]], PALETTE[zone["wall"]]
        thickness = 0.24 if zone["label"] == "showroom" else 0.15
        shape = precise(section.buffer(zone["overhang_m"], join_style="round").difference(plan.difference(section)))
        for segment in profile_slices(section, axis, profile):
            site.surface(parts, segment, floor, lambda e, n: top(e, n)-thickness+0.022, wall, roof)
        for segment in profile_slices(shape, axis, profile):
            science.earlier.roof_layer(parts, segment, top, thickness, 0, FASCIA, roof)
        surfaces.append((section, top, axis, profile, zone["label"]))
    if remaining.area > 0.02:
        raise ValueError(f"Roof zones leave {remaining.area:.4f} square meters uncovered")
    return surfaces


def roof_seams(parts, region, top, axis, profile, spacing):
    low, high = region.bounds[1-axis], region.bounds[3-axis]
    for station in np.arange(low+spacing*.64, high-.22, spacing):
        west, south, east, north = region.bounds
        swath = box(west, station-.022, east, station+.022) if axis == 0 else box(station-.022, south, station+.022, north)
        band = precise(region.intersection(swath))
        if band.is_empty or band.area < 0.005:
            continue
        for segment in profile_slices(band, axis, profile):
            science.earlier.roof_layer(parts, segment, top, 0.028, 0.028, TRIM, TRIM)


def long_warehouse(parts, plan, surfaces, row, field, gates):
    style = row["facade"]
    sector, top, axis, profile, _ = next(item for item in surfaces if item[-1] == "warehouse")
    for station in style["roof_strips_n"]:
        for west, east in style["roof_strip_intervals_e"]:
            rectangle = box(west, station-.12, east, station+.12).intersection(sector)
            science.earlier.roof_layer(parts, rectangle, top, .065, .074, DARK, (141, 156, 157))
    for side, add, count, pitch in shared.bays(parts, plan, style["bay_m"]):
        a, b = side.coords
        north = (a[0] - b[0]) > side.length * 0.8 and max(a[1], b[1]) > 381
        for i in range(count):
            u = (i+.5)*pitch
            e, n = side.interpolate(u).coords[0]
            datum = geometry.sample_ground(field, e, n)
            z = shared.elevation([(p,h) for p,h,*_ in surfaces], e, n)
            add(u-.058,u+.058,-.012,.072,datum+.11,z-.24,FOUNDATION)
            add(u-pitch*.47,u+pitch*.47,.004,.045,datum-.08,datum+.46,FOUNDATION)
            add(u-pitch*.48,u+pitch*.48,.008,.08,z-1.01,z-.84,TRIM)
            if north and (i + 2) % 3 != 0 and not shared.row_covered(side,u,pitch*.40,gates):
                shutter(add,u,pitch*.57,datum+.04,datum+3.23)
            elif pitch > 2.25 and i % 2 == 1 and not shared.row_covered(side,u,pitch*.45,gates):
                prior.window(add,u,pitch*.43,datum+2.55,datum+3.82,TRIM,GLASS,3)


def shutter(add, u, width, bottom, top):
    lo, hi = u-width*.5, u+width*.5
    if top - bottom < 0.7:
        return
    add(lo-.08,hi+.08,.007,.089,bottom,top+.11,TRIM)
    add(lo,hi,.091,.135,bottom,top,SEA)
    for z in np.arange(bottom+.26, top-.70, .34):
        add(lo,hi,.136,.148,z,z+.018,DARK)
    prior.window(add,u,width*.91,top-.66,top-.12,SEA,GLASS,4)


def quonset(parts, plan, surfaces, row, field, gates):
    style = row["facade"]
    axis = style["axis"]
    lookup = [(p,h) for p,h,*_ in surfaces]
    for region, top, _, profile, name in surfaces:
        if name.endswith("arch"):
            roof_seams(parts, region, top, axis, profile, style["seam_m"])
    for side, add, count, pitch in shared.bays(parts, plan, 3.15, lower=0.75):
        a, b = np.asarray(side.coords)
        end = abs((b-a)[axis]) > side.length*.90
        for i in range(count):
            u = (i+.5)*pitch
            e,n = side.interpolate(u).coords[0]
            grade = geometry.sample_ground(field,e,n)
            cap = shared.elevation(lookup,e,n)
            if cap > grade+.56:
                add(u-.038,u+.038,-.011,.047,grade,cap-.31,TRIM)
                add(u-pitch*.47,u+pitch*.47,.006,.047,grade-.09,grade+.23,FOUNDATION)
            if not end or shared.row_covered(side,u,pitch*.44,gates) or cap-grade < 2.35:
                continue
            door_end = style.get("garage_end")
            near = e > plan.bounds[2]-1.25 if door_end=="east" else e < plan.bounds[0]+1.25
            if door_end and near and cap-grade>4.7 and i==count//2:
                shutter(add,u,min(3.23,pitch*.92),grade+.04,min(cap-.57,grade+3.12))
            elif style.get("office") or cap-grade>3.9:
                prior.window(add,u,pitch*.63,grade+1.23,min(grade+2.85,cap-.55),TRIM,GLASS,2)
                if style.get("office") and cap-grade>4.72:
                    prior.window(add,u,pitch*.57,grade+3.32,min(grade+4.45,cap-.38),TRIM,GLASS,2)


def romania_facade(parts, plan, surfaces, row, field, gates):
    style = row["facade"]
    lookup = [(p,h) for p,h,*_ in surfaces]
    for side, add, count, pitch in shared.bays(parts, plan, style["bay_m"], lower=.55):
        for i in range(count):
            u = (i+.5)*pitch
            e,n = side.interpolate(u).coords[0]
            z = shared.elevation(lookup,e,n)
            grade = geometry.sample_ground(field,e,n)
            left,right = u-pitch*.49,u+pitch*.49
            blocked = shared.row_covered(side,u,pitch*.46,gates)
            if n > style["glazed_front_above_n"]:
                if not blocked:
                    add(left,right,.006,.056,grade+.43,grade+2.16,WHITE)
                    prior.window(add,u,pitch*.97,grade+2.17,z-.33,TRIM,GLASS,3)
                add(left,right,.024,.16,grade+.18,grade+.37,FOUNDATION)
            elif not blocked and z-grade > 3.8:
                east_yard = e > 687 and -176<n<-121
                west_yard = e < 655 and -196<n<-119
                if (east_yard or west_yard) and i%2==0 and pitch>3.1:
                    shutter(add,u,pitch*.78,grade+.025,grade+style["warehouse_loading_height_m"])
                elif pitch>1.42 and i%2==1:
                    prior.window(add,u,pitch*.61,grade+1.55,grade+2.94,TRIM,GLASS,3)


FACADES = {"warehouse": long_warehouse, "quonset": quonset, "romania": romania_facade}


def build(spec, manifest, config, field, graph):
    meshes, records, ground = {}, [], []
    plans, gates, supports = [], [], []
    for row in spec["buildings"]:
        plan = orient(Polygon(row["footprint_enu_m"]))
        if not plan.is_valid:
            raise ValueError(f"Invalid registered plan for {row['name']}")
        floor, _ = science.earlier.fit_base(field, plan)
        pieces, gates_for_plan, support_for_plan = [], [], []
        for entrance in row["entrances"]:
            gate, _, blocks = shared.shared.site_entry(ground, field, entrance)
            gates_for_plan.append(gate)
            support_for_plan.extend(blocks)
        surfaces = roof_geometry(pieces, plan, row["zones"], floor)
        FACADES[row["facade"]["kind"]](pieces, plan, surfaces, row, field, gates_for_plan)
        prior.painted_doors(pieces, list(shared.shared.face_edges(plan)), gates_for_plan, TRIM, DARK)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=.00008))
        meshes[row["id"]] = science.ordered_mesh(mesh)
        plans.append(plan)
        gates.extend(gates_for_plan)
        supports.extend(support_for_plan)
        records.append({
            "id": row["id"], "name": row["name"], "campus_id": row["campus_id"],
            "footprint_enu_m": shared.ring(plan), "area_m2": round(plan.area,3),
            "support_collision_enu_m": [shared.ring(block) for block in support_for_plan],
            "entrances": gates_for_plan, "base_z_m": round(floor,4),
            "roof_z_m": round(float(mesh.bounds[1,1]),4),
        })
    baselines = shared.union([
        Polygon(row["footprint_enu_m"]).buffer(0) for row in manifest["buildings"] if row["id"] in meshes
    ])
    edges, clearance = prior.nearby.shared.graduate.shared.check_routes(
        plans, supports, gates, baselines, manifest, graph, config, set(meshes),
    )
    return meshes, records, science.ordered_mesh(trimesh.util.concatenate(ground)), edges, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    manifest_path = SCENE / "manifest.json"
    config_path = SCENE / "presentation.json"
    spec, manifest, config = [json.loads(path.read_bytes()) for path in (args.spec, manifest_path, config_path)]
    terrain = SCENE / manifest["heightfield_url"]
    assert tools.digest(manifest_path) == spec["source_manifest_sha256"]
    assert tools.digest(terrain) == spec["source_heightfield_sha256"]
    field = json.loads(terrain.read_bytes())
    graph = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, edges, clearance = build(spec, manifest, config, field, graph)
    appearances = json.loads((geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes())
    removals = shared.shared.frohnmayer.source_removals({"absorbed_batches":spec["source_ranges"]},config,appearances)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    site.memorial.gerlinger.export(model,meshes,ground,GROUND,"facilities-paving")
    package = {
        "source_presentation_sha256": config["asset_sha256"],
        "source_base_model_sha256": manifest["model"]["sha256"],
        "source_heightfield_sha256": tools.digest(terrain), "ground_node": GROUND,
        "url": f"{DIRECTORY}/site.glb", "sha256": tools.digest(model),
        "buildings": records, "absorbed_ids": [], "batch_removals": removals,
    }
    descriptor.write_text(json.dumps(package,separators=(",",":"))+"\n",encoding="utf-8",newline="\n")
    if not args.stage:
        config["facilities_exterior_site"] = {"url":f"{DIRECTORY}/site.json","sha256":tools.digest(descriptor)}
        config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    audit = {
        "buildings": records, "route_edges": edges, "nearest_route_m": round(clearance,4),
        "triangles": {key: len(mesh.faces) for key,mesh in meshes.items()}, "batch_removals": removals,
        "glb_sha256": package["sha256"], "descriptor_sha256": tools.digest(descriptor),
    }
    args.audit.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8",newline="\n")
    print({key: audit[key] for key in ("route_edges","nearest_route_m","triangles","glb_sha256")})


if __name__ == "__main__":
    main()
