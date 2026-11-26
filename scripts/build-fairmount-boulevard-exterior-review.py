# SPDX-License-Identifier: Apache-2.0
"""Export the registered Fairmount Boulevard house exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import set_precision, union_all
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


path = Path(__file__).with_name("build-east-campus-housing-exterior-review.py")
loader = spec_from_file_location(path.stem, path)
housing = module_from_spec(loader)
loader.loader.exec_module(housing)
base, geometry, chapter = housing.base, housing.geometry, housing.chapter
design, shared, approaches = housing.design, housing.shared, housing.approaches
SCENE, ROOT = housing.SCENE, housing.ROOT
PACKAGE = "fairmount-boulevard-exterior-review"
GROUND = "fairmount-boulevard-approaches"
KEY = "fairmount_boulevard_exterior_site"
SPEC = ROOT / "data/metadata/fairmount-boulevard-exterior-review.json"
BRICK = (146, 94, 76)
STONE = (164, 157, 135)


def build_porch(parts, add, point, row, center, threshold, height):
    style = row["porch"]
    depth = style["depth"]
    half = style["width"] / 2
    left, right = center-half, center+half
    trim = row["trim_color"]
    lower = threshold - 0.15
    add(left, right, -0.016, depth, lower, threshold, STONE)
    underside = min(height(point(u, .35)) for u in (left,right))-0.17
    head = underside
    if style["kind"] == "rail":
        head = max(threshold+2.17, min(underside, threshold+2.49))
        chapter.gabled_canopy(
            parts, point, center, half + .10, -0.09, depth+.16, head,
            style["rise"], row["roof_color"], trim,
        )
        for u in (left+.10, right-.10):
            add(u-.026, u+.026, .04, depth-.11, threshold+.79, threshold+.86, trim)
            for position in np.linspace(.15, depth-.13, 5):
                add(u-.013, u+.013, position-.014, position+.014,
                    threshold-.025, threshold+.82, trim)
    points = []
    for u in (left+.10,right-.10):
        p = point(u, depth-.30)
        top = height(p) - .154 if style["kind"] == "eave" else head
        points.append(approaches.supported_post(parts, p, threshold-.045, top, trim, .060))
    return points


def elevations(parts, field, row, edges, entry, door_edge, door_u, height, *, windowless=()):
    feet = []
    trim = row["trim_color"]
    siding = tuple(max(0, ch - 17) for ch in row["wall_color"])
    garage = row["garage"]
    garage_edge = design.locate_face(edges,*garage[:2]) if garage else None
    for edge in edges:
        length, add, _, point, _, _ = chapter.setup_face(parts, *edge)
        if length < 1.3:
            continue
        z0 = geometry.sample_ground(field, *point(length/2,0))
        nodes = np.linspace(.04, length-.04, max(9,round(length/.25)))
        top = [height(point(u,0)) - .17 for u in nodes]
        add(.02, length-.02, -.004, .021, z0-.13, z0+.23, STONE)
        for z in np.arange(z0+.24,max(top)-.035,.197):
            visible=[i for i,p in enumerate(top) if p >= z+.044]
            if len(visible)>1:
                cuts=np.split(np.asarray(visible),np.flatnonzero(np.diff(visible)>1)+1)
                for run in cuts:
                    if len(run)>1:
                        add(nodes[run[0]],nodes[run[-1]],-.001,.009,z,z+.014,siding)
        if edge == door_edge:
            sill0 = entry["threshold_z_m"]
            for shift, sill, width, tall in row["front_windows"]:
                u=door_u+shift
                if width/2+.06<u<length-width/2-.06:
                    cap=min(height(point(u+d,0)) for d in (-width/2,width/2))-.23
                    upper=min(sill0+sill+tall,cap)
                    if upper>sill0+sill+.30:
                        housing.trim_window(add,u,width,sill0+sill,upper,trim,ribs=3 if width>2 else 1)
            if row["porch"]:
                feet.extend(build_porch(parts,add,point,row,door_u,sill0,height))
        if edge == garage_edge:
            width = min(length-.34, garage[2])
            u = LineString(edge).project(Point(garage[0]))
            u = np.clip(u, width/2+.14, length-width/2-.14)
            ground = geometry.sample_ground(field, *point(u,.27))
            housing.garage_front(add,u,width,ground+.02,row.get("garage_color", (176,178,163)),trim)
        if edge != door_edge and edge != garage_edge and edge not in windowless and length>4.9:
            for fraction in np.linspace(.23,.77,max(2,round(length/4.4))):
                u=length*fraction
                sill=geometry.sample_ground(field,*point(u,0))+.76
                top=min(height(point(u,0))-.29,sill+1.12)
                if top>sill+.69:
                    housing.trim_window(add,u,min(length*.16,1.22),sill,top,trim)
    return feet


def roof_details(parts, row, height):
    for e,n,w,d,rise in row["chimneys"]:
        plan=box(e-w/2,n-d/2,e+w/2,n+d/2)
        base_z=min(height(p) for p in plan.exterior.coords)
        top=max(height(p) for p in plan.exterior.coords)+rise
        base.flat(parts,plan,base_z-.16,top,BRICK)
        base.flat(parts,plan.buffer(.065,join_style="mitre"),top-.09,top+.045,STONE)
        for fraction in (.30,.70) if w>.75 else (.5,):
            pipe=Point(e-w/2+fraction*w,n).buffer(.092,quad_segs=2)
            base.flat(parts,pipe,top+.043,top+.22,(106,102,90))


def open_garage(parts, ground, slot, plan, outline, height, field, row):
    grade=geometry.sample_ground(field,*slot.centroid.coords[0])
    base.flat(ground,slot,grade-.21,grade+.028,(145,143,128))
    # The roof continues over the slot. A header defines the opening.
    heading=row["entrance"]["outward_degrees"]
    edge=design.locate_face(list(shared.face_edges(outline)),slot.centroid.coords[0],heading)
    _, add, _, point, _, _=chapter.setup_face(parts,*edge)
    mouth = LineString(edge).intersection(slot.buffer(.035))
    assert mouth.geom_type=="LineString" and mouth.length>3.0, row["id"]
    start,end=sorted(LineString(edge).project(Point(p)) for p in mouth.coords)
    sill=grade+2.11
    beard=min(height(point(u,0)) for u in np.linspace(start,end,10))-.13
    assert beard>sill+.16, (row["id"],beard,sill)
    add(start,end,-.14,.14,sill,beard,row["wall_color"])
    add(start,end,-.15,.16,sill,sill+.075,row["trim_color"])
    for wall in shared.face_edges(plan):
        segment=LineString(wall).intersection(slot.buffer(.085))
        if segment.geom_type != "LineString" or segment.length < .8:
            continue
        line=LineString(wall)
        _, finish, _, _, _, _=chapter.setup_face(parts,*wall)
        a,b=sorted(line.project(Point(p)) for p in segment.coords)
        finish(a,b,.022,.032,grade-.12,sill+.03,(73,78,68))


def build(spec, manifest, config, field, graph, *, decorate=elevations):
    originals = {r["id"]:r for r in manifest["buildings"]}
    models, records, occupied, supports, entries, paving = {}, [], [], [], [], []
    for row in spec["models"]:
        id=row["id"]
        footprints = [
            orient(set_precision(Polygon(ring), .002))
            for ring in row.get("ground_footprints_enu_m", [row["footprint_enu_m"]])
        ]
        plan = footprints[0] if len(footprints) == 1 else union_all(footprints)
        outline=orient(set_precision(Polygon(
            row["roof_outline_enu_m"], row.get("roof_holes_enu_m", []),
        ),.002))
        deck=orient(set_precision(outline.buffer(row["eaves_m"],join_style="mitre"),.002))
        assert plan.is_valid and deck.covers(plan),id
        floor, _ = design.science.earlier.fit_base(field,outline)
        pieces=[]
        height=design.roof_sections(pieces,deck,plan,floor,row,grid=.0001)
        edges=[
            edge for area in geometry.sections(plan)
            for edge in shared.face_edges(orient(area))
        ]
        approach_edges = (
            [tuple(map(tuple, row["approach_wall_enu_m"]))]
            if row.get("approach_wall_enu_m") else edges
        )
        depth=row["porch"]["depth"] if row["porch"] else 0
        arrival=row | {"entrance":row["entrance"] | {
            "landing_m":row["entrance"]["landing_m"]+depth,
        }}
        entry,edge,u=approaches.entry_stair(
            pieces,paving,approach_edges,field,arrival,row.get("threshold_z_m"),
            top_run=max(.72,depth+.035),
        )
        gates = [entry]
        for hint in row.get("additional_entrances", []):
            extra, _, _ = approaches.entry_stair(
                pieces, paving, edges, field, row | {"entrance": hint}, None,
            )
            gates.append(extra)
        if len({gate["gate"] for gate in gates}) != len(gates):
            raise ValueError(f"Duplicate entrance name on {id}.")
        feet=decorate(pieces,field,row,edges,entry,edge,u,height)
        roof_details(pieces,row,height)
        if row["garage_slot_enu_m"]:
            open_garage(pieces,paving,Polygon(row["garage_slot_enu_m"]),plan,outline,height,field,row)
        mesh=trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=.000012))
        models[id]=design.science.ordered_mesh(mesh)
        occupied.append(plan)
        supports.extend(feet)
        entries.extend(gates)
        records.append({
            "id":id,"name":row["name"],"street_address":row["street_address"],
            "footprint_enu_m":base.ring(outline),
            "ground_footprints_enu_m":[base.ring(area) for area in footprints],
            **({"footprint_holes_enu_m":[list(hole.coords)[:-1] for hole in outline.interiors]}
               if outline.interiors else {}),
            "support_collision_enu_m":[base.ring(p) for p in feet],
            "base_z_m":round(floor,4),"roof_z_m":round(float(mesh.bounds[1,1]),4),
            "area_m2":round(plan.area,3),"entrances":gates,
        })
    prior=union_all([Polygon(originals[id]["footprint_enu_m"]) for id in models])
    n,clear=chapter.prior.nearby.shared.graduate.shared.check_routes(
        occupied,supports,entries,prior,manifest,graph,config,set(models),
    )
    return models,records,design.science.ordered_mesh(trimesh.util.concatenate(paving)),n,clear


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",type=Path)
    parser.add_argument("--audit",type=Path,required=True)
    args=parser.parse_args()
    export_review(
        spec_path=SPEC, package=PACKAGE, key=KEY, ground_node=GROUND,
        paving_node="fairmount-paving", builder=build, audit_path=args.audit,
        stage=args.stage,
    )


def export_review(*, spec_path, package, key, ground_node, paving_node, builder, audit_path, stage):
    spec=json.loads(spec_path.read_bytes())
    p,config_path=SCENE/"manifest.json",SCENE/"presentation.json"
    manifest,config=[json.loads(f.read_bytes()) for f in (p,config_path)]
    field_path=SCENE/manifest["heightfield_url"]
    for source, source_key in ((p,"source_manifest_sha256"),(field_path,"source_heightfield_sha256")):
        if design.tools.digest(source)!=spec[source_key]:
            raise ValueError(f"Changed registration source for {package}: {source.name}")
    meshes,records,ground,n,clear=builder(
        spec,manifest,config,json.loads(field_path.read_bytes()),
        json.loads((SCENE/"navigation.json").read_bytes()),
    )
    appearances=json.loads((ROOT/"data/metadata/campus-expansion-audit.json").read_bytes())
    targets={id:target for target,ids in appearances["context_batches"].items() for id in ids}
    patches=shared.frohnmayer.source_removals(
        {"absorbed_batches":[{"id":id,"target":targets[id]} for id in meshes]},config,appearances,
    )
    out=stage or SCENE/package
    out.mkdir(exist_ok=True,parents=True)
    model,descriptor=out/"site.glb",out/"site.json"
    design.site.memorial.gerlinger.export(model,meshes,ground,ground_node,paving_node)
    bundle={
        "source_presentation_sha256":config["asset_sha256"],
        "source_base_model_sha256":manifest["model"]["sha256"],
        "source_heightfield_sha256":spec["source_heightfield_sha256"],
        "ground_node":ground_node,"url":f"{package}/site.glb","sha256":design.tools.digest(model),
        "buildings":records,"absorbed_ids":[],"batch_removals":patches,
    }
    descriptor.write_text(json.dumps(bundle,separators=(",",":"))+"\n",encoding="utf8",newline="\n")
    digest=design.tools.digest(descriptor)
    if stage is None:
        config[key]={"url":f"{package}/site.json","sha256":digest}
        config_path.write_text(json.dumps(config,indent=2,ensure_ascii=False)+"\n",encoding="utf8",newline="\n")
    audit={
        "buildings":records,"route_edges":n,"nearest_route_m":round(clear,4),"batch_removals":patches,
        "triangles":{id:len(mesh.faces) for id,mesh in meshes.items()},
        "glb_sha256":bundle["sha256"],"descriptor_sha256":digest,
    }
    audit_path.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf8",newline="\n")
    print({k:audit[k] for k in ("route_edges","nearest_route_m","triangles","glb_sha256")})


if __name__=="__main__":
    main()
