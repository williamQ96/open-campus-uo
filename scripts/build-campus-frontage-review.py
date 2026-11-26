# SPDX-License-Identifier: Apache-2.0
"""Build five registered UO exteriors from editable footprint and roof sections."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh

file = Path(__file__).with_name("build-public-building-exterior-review.py")
loader = spec_from_file_location(file.stem, file)
site_tools = module_from_spec(loader)
loader.loader.exec_module(site_tools)
site, tools, science, shared, prior = (
    site_tools.site, site_tools.tools, site_tools.science, site_tools.shared, site_tools.prior,
)
flat, ring, union, geometry = site_tools.flat, site_tools.ring, site_tools.union, site_tools.geometry
SCENE = site_tools.SCENE
SPEC = geometry.ROOT / "data/metadata/campus-frontage-review.json"
DIRECTORY = "campus-frontage-review"
GROUND = "campus-frontage-approaches"

BLUE = (80, 115, 128)
DARK = (54, 70, 70)
GLASS = (93, 127, 139)
SILL = (182, 181, 164)
SILVER = (173, 185, 182)
PALE = (209, 208, 191)
WHITE = (220, 217, 198)
BRICK = (158, 102, 82)
BASE = (162, 155, 137)
METAL = (186, 189, 176)
SEAM = (169, 176, 169)
PAVING = (177, 166, 149)
SURFACES = {
    "membrane": (206, 204, 187),
    "zinc": METAL,
    "shingle": (119, 124, 111),
    "brick": BRICK,
    "clay": (142, 103, 89),
    "dark-metal": (94, 119, 123),
    "silver": SILVER,
    "masonry": WHITE,
    "hall": (166, 171, 161),
}


def make_plane(values):
    x, y, h = values
    return lambda e, n: x * e + y * n + h


def model_plan(row):
    return [orient(Polygon(part["ring"], part["holes"])) for part in row["parts"]]


def shells(parts, row, outlines, floor):
    capacity = outlines.copy()
    painted = []
    for zone in row["roofs"]:
        index = zone["part"]
        plan = set_precision(capacity[index].intersection(box(*zone["bounds"])), 0.001)
        if plan.area <= 0.0001:
            continue
        capacity[index] = set_precision(capacity[index].difference(plan), 0.001)
        masonry = SURFACES[zone["wall"]]
        finish = SURFACES[zone["finish"]]
        top = make_plane(zone["height_plane"])
        site.surface(parts, plan, floor, lambda e, n: top(e, n) - 0.17, masonry, finish)
        eaves = set_precision(plan.buffer(0.22, join_style="mitre").difference(outlines[index].difference(plan)), 0.001)
        science.earlier.roof_layer(parts, eaves, top, 0.19, 0.016, SILVER, finish)
        painted.append((plan, top))
    if sum(poly.area for poly in capacity) > 0.018:
        raise ValueError(f"Roof plan misses part of {row['name']}.")
    return painted


def elevation(at, e, n):
    return site_tools.roof_at(at, e, n)


def bays(parts, outline, along, lower=1.6, inner=False):
    rings = [outline.exterior, *outline.interiors] if inner else [outline.exterior]
    for contour in rings:
        for start, stop in zip(contour.coords, list(contour.coords)[1:]):
            length, add = tools.face(parts, start, stop)
            if length < lower:
                continue
            count = max(1, round(length / along))
            yield LineString((start, stop)), add, count, length / count


def row_covered(edge, pos, half, entries):
    return site_tools.entry_width(edge, entries, (pos, half)) is not None


def health_facade(parts, row, outline, at, floor, datum, gates):
    for side, add, count, pitch in bays(parts, outline, 3.62, inner=True):
        for i in range(count):
            u = (i + 0.5) * pitch
            pos = side.interpolate(u)
            cap = elevation(at, pos.x, pos.y)
            start, end = u - pitch * 0.43, u + pitch * 0.43
            add(start, end, 0.007, 0.058, datum + 0.08, datum + 0.38, BASE)
            if cap > 11.6:
                if not row_covered(side, u, pitch * 0.46, gates):
                    prior.window(add, u, pitch * 0.46, datum + 0.8, datum + 3.01, DARK, BLUE, 2)
                prior.window(add, u, pitch * 0.45, datum + 3.91, cap - 0.69, DARK, GLASS, 2)
                add(u-pitch*.218, u+pitch*.218, 0.13, 0.158, datum+6.89, datum+7.78, PALE)
                add(start, end, -0.034, 0.119, cap-0.244, cap-.105, SILVER)
            elif cap > 6.0:
                if not row_covered(side, u, pitch * 0.46, gates):
                    prior.window(add, u, pitch*.65, datum + 0.79, datum + 2.79, BASE, DARK, 2)
                high = min(cap - 0.59, datum + 6.74)
                prior.window(add, u, pitch*.72, datum+3.81, high, SILL, GLASS, 3)
                add(start, end, -0.01, 0.139, datum+3.26, datum+3.46, SILL)
            elif not row_covered(side, u, pitch * 0.43, gates):
                prior.window(add, u, pitch*.58, datum+1.07, min(datum+3.61,cap-.25), SILL, GLASS, 2)
    for gate in gates:
        point = Point(gate["position_enu_m"])
        cover = box(point.x - 1.95, point.y - 0.02, point.x + 1.95, point.y + 1.32)
        if gate["gate"] == "health-west-side":
            cover = box(point.x - 1.22, point.y - 1.35, point.x + 0.02, point.y + 1.35)
        flat(parts, cover, gate["threshold_z_m"] + 2.77, gate["threshold_z_m"] + 3.04, DARK, SILVER)


def power_facade(parts, row, outline, at, floor, datum, gates):
    for side, add, count, pitch in bays(parts, outline, 4.65):
        length = side.length
        a, b = side.coords
        is_east = (b[1] - a[1]) / length > 0.62
        for i in range(count):
            u = (i + 0.5) * pitch
            pos = side.interpolate(u)
            cap = elevation(at, pos.x, pos.y)
            left, right = u - pitch*.477, u + pitch*.477
            add(left, right, 0.005, 0.05, datum-0.15, datum+3.09, (101,119,119))
            if is_east and cap > 10.9:
                for h in (datum + 4.27, datum + 7.15):
                    prior.window(add, u, pitch*.76, h, min(h+1.46,cap-.15), SILVER, (160,182,181), 5)
                for x in np.linspace(left+0.1, right-0.1, 7):
                    add(x-.015,x+.015,.005,.031,datum+3.11,cap-.24,SILVER)
            elif is_east:
                prior.window(add, u, pitch * .77, datum + 3.96, min(datum+7.25,cap-.37), SILVER, GLASS, 4)
                if i % 2 == 0:
                    prior.window(add, u,pitch*.34,datum+.74,datum+2.92, BASE,BLUE,2)


def riley_facade(parts, row, outline, at, floor, datum, gates):
    for side, add, count, pitch in bays(parts, outline, row["upper_frame_pitch_m"], inner=True):
        for i in range(count):
            u = (i + 0.5) * pitch
            start, end = u - pitch * .493, u + pitch * .493
            center = side.interpolate(u)
            cap = elevation(at, center.x, center.y)
            if cap < datum + 4.7:
                continue
            for h in (datum+.64, datum+3.13):
                if row_covered(side, u, pitch * .37, gates) and h < datum + 1:
                    continue
                bottom, top = h + .42, min(h+1.91,cap-.23)
                prior.window(add, u, pitch * .82, bottom, top, WHITE, GLASS, 3)
                add(start,end,-.03,.15,h,h+.37,PALE)
                add(start,end,-.02,.109,top+.01,top+.13,WHITE)
            add(start,start+.14,-.03,.17,datum+.51,cap-.17,WHITE)
            if i % 2 == 0:
                add(start+.57,end-.49,.01,.067,floor+.81,datum+.32,BASE)
    line = LineString(row["north_low_wall"])
    wall = line.buffer(0.139, cap_style="flat")
    flat(parts, wall, datum - .66, datum + .61, BRICK, BASE)
    return [wall]


def tennis_facade(parts, row, outline, at, floor, datum, gates):
    for side, add, panels, pitch in bays(parts, outline, row["metal_seam_pitch_m"]):
        for i in range(panels):
            u = (i+.5)*pitch
            point = side.interpolate(u)
            cap = elevation(at, point.x, point.y)
            add(u-.026,u+.026,.002,.073,datum+1.1,cap-.26,SEAM)
            add(u-pitch*.492,u+pitch*.492,.014,.057,datum+.15,datum+.83,BASE)
    west,south,east,north = outline.bounds
    for n in (-444.5,-424.4,-464.5):
        z = elevation(at, (west+east)*.5, n)
        tools.beam(parts,(west-.14,n,z+.1),(east+.14,n,z+.1),.154,SILVER)
    for edge in (west, east):
        for n in np.linspace(south + 1.1, north - 1.1, 30):
            cap = elevation(at, edge, n)
            face = Point(edge,n).distance(outline.boundary) < 0.4
            if face and cap > datum+3.05:
                trim_e = edge - 0.075 if edge == west else edge + 0.075
                tools.beam(parts,(trim_e,n,cap-.152),(trim_e,n,cap-.9),.088,SEAM)


def alder_facade(parts, row, outline, at, floor, datum, gates, field):
    for side, add, count, pitch in bays(parts, outline, 3.81):
        for i in range(count):
            u = (i + .5) * pitch
            center = side.interpolate(u)
            cap = elevation(at, center.x, center.y)
            for base in (datum+1.05,datum+3.74):
                if not row_covered(side, u, pitch*.44,gates):
                    prior.window(add, u, pitch*.43, base, min(base+1.43,cap-.35), PALE, BLUE, 2)
            add(u-pitch*.48,u+pitch*.48,.004,.073,datum+.04,datum+.25,BASE)
    porch = Polygon(row["porch"]["outline"])
    top = row["porch"]["top_m"]
    flat(parts, porch.buffer(.18,join_style="mitre"), top-.30, top, WHITE, SILVER)
    soles = []
    for e,n in row["porch"]["posts"]:
        post = box(e-.15,n-.15,e+.15,n+.15)
        base = geometry.sample_ground(field,e,n)
        flat(parts,post,base-.19,top-.24,WHITE)
        flat(parts,post.buffer(.055,join_style="mitre"),base-.15,base+.25,PALE)
        soles.append(post)
    gate = gates[0]
    e,n = gate["position_enu_m"]
    sill = gate["threshold_z_m"]
    first, last = (e + 3.6,n),(e - 3.6,n)
    width, add = tools.face(parts,first,last)
    midpoint = width/2
    angles = np.linspace(0,np.pi,21)
    beam = [(e + .94*np.cos(t), n+.13, sill+1.98+.83*np.sin(t)) for t in angles]
    line = [(e + .84*np.cos(t), n+.148, sill+1.97+.73*np.sin(t)) for t in angles]
    for chain,color,radius in ((beam,(63,99,86),.16),(line,WHITE,.059)):
        for p,q in zip(chain,chain[1:]):
            tools.beam(parts,p,q,radius,color)
    for offset in (-2.26,2.26):
        oval = [(e+offset+.34*np.cos(t),n+.12,sill+1.61+.48*np.sin(t)) for t in np.linspace(0,2*np.pi,25)]
        for p,q in zip(oval,oval[1:]):
            tools.beam(parts,p,q,.085,(63,99,86))
        add(midpoint-offset-.21,midpoint-offset+.21,.02,.071,sill+1.22,sill+1.99,GLASS)
    return soles


def add_roof_accents(parts, row, at, plan):
    for west,south,east,north,cap in row.get("roof_accents",[]):
        part = box(west,south,east,north).intersection(plan.buffer(-.045))
        if part.area <= .1:
            continue
        z = elevation(at, *part.representative_point().coords[0])
        if z < cap - .16:
            flat(parts, part, z - .11, cap, SILVER, METAL)


def build(spec, manifest, config, field, graph):
    meshes, records, ground, solids, feet, gates, pads = {}, [], [], [], [], [], []
    for code, row in spec["models"].items():
        outlines = model_plan(row)
        main = outlines[0]
        floor, datum = science.earlier.fit_base(field, main)
        pieces, inspected, supports = [], [], []
        for entrance in row["entrances"]:
            assert main.boundary.distance(Point(entrance["position_enu_m"])) < .005
            gate, pad, blocks = shared.site_entry(ground, field, entrance)
            inspected.append(gate)
            pads.append(pad)
            supports.extend(blocks)
        elevations = shells(pieces, row, outlines, floor)
        if code == "014":
            health_facade(pieces,row,main,elevations,floor,datum,inspected)
        elif code == "032":
            power_facade(pieces,row,main,elevations,floor,datum,inspected)
        elif code == "086":
            supports.extend(riley_facade(pieces,row,main,elevations,floor,datum,inspected))
        elif code == "139":
            tennis_facade(pieces,row,main,elevations,floor,datum,inspected)
        else:
            supports.extend(alder_facade(pieces,row,main,elevations,floor,datum,inspected,field))
        painted = [*shared.face_edges(main)]
        prior.painted_doors(pieces, painted, inspected, WHITE if code=="200" else BASE,DARK)
        add_roof_accents(pieces,row,elevations,main)
        mesh = trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=.00005))
        meshes[row["id"]] = science.ordered_mesh(mesh)
        solids.extend(outlines)
        feet.extend(supports)
        gates.extend(inspected)
        records.append({
            "id":row["id"],"name":row["name"],"campus_id":row["campus_id"],
            "footprint_enu_m":ring(main),
            "footprint_holes_enu_m":[list(hole.coords[:-1]) for hole in main.interiors],
            "support_collision_enu_m":[ring(poly) for poly in [*supports,*outlines[1:]]],
            "entrances":inspected,"base_z_m":round(floor,4),"roof_z_m":round(float(mesh.bounds[1,1]),4),
            "area_m2":round(sum(poly.area for poly in outlines),3),
        })
    older = union([Polygon(row["footprint_enu_m"]).buffer(0) for row in manifest["buildings"] if row["id"] in meshes])
    edges, clearance = prior.nearby.shared.graduate.shared.check_routes(solids, feet, gates, older, manifest, graph, config, set(meshes))
    paving = [LineString(row["line"]).buffer(row["width"]/2,cap_style="flat",join_style="mitre") for row in spec["paths"]]
    prior.nearby.add_paths(ground,field,union([*paving,*pads]),union([*solids,*feet]),PAVING)
    return meshes, records, science.ordered_mesh(trimesh.util.concatenate(ground)), edges, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--spec", type=Path, default=SPEC)
    args = parser.parse_args()
    manifest_path, config_path = SCENE / "manifest.json", SCENE / "presentation.json"
    spec, manifest, config = [json.loads(path.read_bytes()) for path in (args.spec, manifest_path, config_path)]
    terrain = SCENE / manifest["heightfield_url"]
    assert tools.digest(manifest_path) == spec["source_manifest_sha256"]
    assert tools.digest(terrain) == spec["source_heightfield_sha256"]
    field = json.loads(terrain.read_bytes())
    navigation = json.loads((SCENE / "navigation.json").read_bytes())
    meshes, records, ground, edges, clearance = build(spec, manifest, config, field, navigation)
    appearances = json.loads((geometry.ROOT / "data/metadata/campus-expansion-audit.json").read_bytes())
    removals = shared.frohnmayer.source_removals({"absorbed_batches":spec["source_ranges"]},config,appearances)
    output = args.stage or SCENE / DIRECTORY
    output.mkdir(parents=True, exist_ok=True)
    model, descriptor = output / "site.glb", output / "site.json"
    site.memorial.gerlinger.export(model,meshes,ground,GROUND,"campus-frontage-paving")
    payload = {
        "source_presentation_sha256":config["asset_sha256"],
        "source_base_model_sha256":manifest["model"]["sha256"],
        "source_heightfield_sha256":tools.digest(terrain),
        "ground_node":GROUND,"url":f"{DIRECTORY}/site.glb","sha256":tools.digest(model),
        "buildings":records,"absorbed_ids":[],"batch_removals":removals,
    }
    descriptor.write_text(json.dumps(payload,separators=(",",":"))+"\n",encoding="utf8",newline="\n")
    if args.stage is None:
        config["campus_frontage_site"] = {"url":f"{DIRECTORY}/site.json","sha256":tools.digest(descriptor)}
        config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    audit = {"buildings":records,"route_edges":edges,"nearest_route_m":round(clearance,4),
             "triangles":{key:len(mesh.faces) for key,mesh in meshes.items()},
             "batch_removals":removals,"glb_sha256":payload["sha256"],"descriptor_sha256":tools.digest(descriptor)}
    args.audit.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf8",newline="\n")
    print({key:audit[key] for key in ("route_edges","nearest_route_m","triangles","glb_sha256")})


if __name__ == "__main__":
    main()
