# SPDX-License-Identifier: Apache-2.0
"""Build five registered UO office and service exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
from shapely import distance, points, set_precision
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
import trimesh


path = Path(__file__).with_name("build-campus-frontage-review.py")
loader = spec_from_file_location(path.stem, path)
base = module_from_spec(loader)
loader.loader.exec_module(base)
tools, site, science, geometry, shared, prior = base.tools, base.site, base.science, base.geometry, base.shared, base.prior
SCENE = base.SCENE
ROOT = geometry.ROOT
SPEC = ROOT / "data/metadata/office-exterior-review.json"
DIRECTORY = "office-exterior-review"
GROUND = "office-exterior-approaches"

COLORS = {
    "annex": (195,190,170), "shingle": (120,129,122), "brown": (165,146,129),
    "sand": (162,148,126), "utility": (172,175,163), "zinc": (193,199,189),
    "sandstone": (187,164,135), "teal": (87,138,144), "pale": (204,205,189),
    "franklin": (167,152,130), "slate": (136,144,137),
}
FRAME = (181,176,154)
FASCIA = (159,166,154)
TRIM = (211,205,185)
DARK = (69,88,89)
GLASS = (85,111,118)
STOREFRONT = (104,135,103)
BLOCK = (159,154,138)
BRICK = (158,121,102)
PALE = (197,203,188)


def quantize(plan):
    return set_precision(plan, .001)


def place(plan, origin, yaw):
    return orient(translate(rotate(plan,yaw,origin=(0,0)),*origin))


def to_local(coordinates, origin, yaw):
    e,n = np.asarray(coordinates) - np.asarray(origin)
    c,s = np.cos(np.deg2rad(yaw)),np.sin(np.deg2rad(yaw))
    return [c*e+s*n, -s*e+c*n]


def place_mesh(mesh, origin, yaw):
    c,s = np.cos(np.deg2rad(yaw)),np.sin(np.deg2rad(yaw))
    east,north = origin
    mesh.apply_transform(np.array([[c,0,s,east],[0,1,0,0],[-s,0,c,-north],[0,0,0,1]]))
    return mesh


def mansard_height(outer, inner, params):
    high, low = params["inner_z_m"], params["outer_z_m"]
    def height(e,n):
        samples = points(e,n)
        outer_dist,inner_dist = distance(outer,samples),distance(inner,samples)
        ratio = outer_dist/np.maximum(outer_dist+inner_dist,0.001)
        return low+(high-low)*ratio
    return height


def roof_shells(parts, plan, levels, floor):
    rest = plan
    lookup = []
    for row in levels:
        region = rest if row["clip"] is None else quantize(rest.intersection(Polygon(row["clip"])))
        if region.area <= .001:
            continue
        rest = quantize(rest.difference(region))
        wall = COLORS[row["wall"]]
        roof = COLORS[row["finish"]]
        eaves = quantize(region.buffer(row["overhang_m"],join_style="mitre").difference(plan.difference(region)))
        if "mansard" in row:
            outline = quantize(plan.intersection(Polygon(row["clip"]))).exterior
            height = mansard_height(outline,Polygon(row["mansard"]["inside"]).exterior,row["mansard"])
            skins = [(eaves,height)]
            walls = [(region,height)]
        else:
            planes = np.asarray(row["planes"])
            height = lambda x,y,p=planes: np.minimum.reduce([a*x+b*y+c for a,b,c in p])
            skins = list(science.earlier.roof_cells(eaves,planes))
            walls = list(science.earlier.roof_cells(region,planes))
        for facet, surface in walls:
            site.surface(parts,facet,floor,lambda x,y:surface(x,y)-.13,wall,roof)
        for facet, surface in skins:
            science.earlier.roof_layer(parts,facet,surface,.16,.01,FASCIA,roof)
        lookup.append((region,height))
    if rest.area > .015:
        raise ValueError(f"Office roof sections leave {rest.area:.3f} square meters uncovered.")
    return lookup


def roof_at(lookup, point):
    return base.elevation(lookup,*point)


def low_band(add, u, stride, grade, color=BLOCK):
    add(u-stride*.47,u+stride*.47,.006,.066,grade-.12,grade+.39,color)


def exposed_bays(parts, plan, pitch):
    for side,add,count,stride in base.bays(parts,plan,pitch,lower=1.10):
        for i in range(count):
            u = (i+.5)*stride
            yield side,add,u,stride,side.interpolate(u).coords[0]


def annex(parts, plan, roofs, style, grade_at, gates):
    for x0,y0,x1,y1,top in style["stack"]:
        position = ((x0+x1)*.5,(y0+y1)*.5)
        z = roof_at(roofs,position)
        base.flat(parts,box(x0,y0,x1,y1),z-.21,top,BRICK,BRICK)
        base.flat(parts,box(x0-.05,y0-.05,x1+.05,y1+.05),top-.035,top+.04,BLOCK,BLOCK)
    for side,add,u,stride,point in exposed_bays(parts,plan,style["bay_m"]):
        grade = grade_at(*point)
        z = roof_at(roofs,point)
        low_band(add,u,stride,grade)
        add(u-stride*.47,u+stride*.47,.015,.09,grade+3.25,grade+3.43,TRIM)
        if not base.row_covered(side,u,stride*.40,gates):
            prior.window(add,u,stride*.48,grade+1.05,grade+2.77,TRIM,GLASS,2)
        prior.window(add,u,stride*.44,grade+4.17,min(grade+5.89,z-.53),TRIM,GLASS,2)


def rainier(parts, plan, roofs, style, grade_at, gates):
    x0,y0,x1,y1,peak = style["monitor"]
    roof_low=16.57
    base.flat(parts,box(x0,y0,x1,y1),roof_low,peak,PALE,COLORS["sand"])
    base.flat(parts,box(x0-.12,y0-.12,x1+.12,y1+.12),peak-.07,peak+.11,FRAME,PALE)
    for a,b in shared.face_edges(box(x0,y0,x1,y1)):
        length,add=tools.face(parts,a,b)
        for x in np.arange(.77,length-.55,1.09):
            add(x-.34,x+.34,.018,.076,peak-.77,peak-.23,FRAME)
    for side,add,u,stride,point in exposed_bays(parts,plan,style["bay_m"]):
        grade = grade_at(*point)
        z = roof_at(roofs,point)
        low_band(add,u,stride,grade,BRICK)
        add(u-stride*.47,u+stride*.47,.015,.11,grade+3.45,grade+3.61,TRIM)
        add(u-stride*.47,u+stride*.47,.012,.078,z-.49,z-.31,FRAME)
        if not base.row_covered(side,u,stride*.39,gates):
            prior.window(add,u,stride*.72,grade+1.01,grade+2.85,FRAME,GLASS,2)
        prior.window(add,u,stride*.76,grade+4.43,min(grade+6.55,z-.65),FRAME,GLASS,2)


def utility(parts, plan, roofs, style, grade_at, gates):
    xmin,_,xmax,_=plan.bounds
    for y in style["roof_strips"]:
        stripe = box(xmin+.65,y-.068,xmax-.72,y+.068)
        science.earlier.roof_layer(parts,stripe,roofs[0][1],.039,.045,PALE,PALE)
    for side,add,u,stride,point in exposed_bays(parts,plan,style["bay_m"]):
        grade=grade_at(*point)
        z=roof_at(roofs,point)
        low_band(add,u,stride,grade)
        for v in np.arange(u-stride*.43,u+stride*.47,.35):
            add(v-.016,v+.016,.008,.04,grade+.42,z-.19,FRAME)
        if not base.row_covered(side,u,stride*.46,gates):
            prior.window(add,u,stride*.48,grade+1.29,min(grade+2.47,z-.40),FRAME,GLASS,2)


def arched_panel(parts, x, n, radius, bottom, shoulder, start, finish, color):
    arc = [(x+radius*np.cos(theta),shoulder+radius*np.sin(theta))
           for theta in np.linspace(0,np.pi,25)]
    profile = Polygon([(x-radius,bottom),(x+radius,bottom),*arc])
    mesh = geometry.shell(profile,-finish,lambda x,y:-start,color,color)
    mesh.apply_transform(np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,-n],[0,0,0,1]]))
    parts.append(mesh)


def business(parts, plan, roofs, style, grade_at, gates):
    front_y=style["front_y"]
    for side,add,u,stride,point in exposed_bays(parts,plan,style["bay_m"]):
        x,n=point
        if abs(n-front_y) < .04:
            continue
        grade=grade_at(x,n)
        top=roof_at(roofs,point)
        low_band(add,u,stride,grade)
        for level in (2.68,3.05,3.49,4.13):
            add(u-stride*.49,u+stride*.49,.02,.11,grade+level,grade+level+.09,BRICK)
        if x>0 and n<5.5:
            for y0,y1 in ((1.19,2.54),(5.21,7.16),(8.62,10.64)):
                high=min(grade+y1,top-.52)
                if high>grade+y0+.43:
                    prior.window(add,u,stride*.56,grade+y0,high,FRAME,GLASS,2)

    east=plan.bounds[2]-1.47
    west=plan.bounds[0]
    length, paint = tools.face(parts,(east,front_y),(west,front_y))
    ground = grade_at(style["arch_center"],front_y)
    for lo,high,shade in ((.08,.51,BLOCK),(3.09,3.33,BRICK),(3.35,3.65,TRIM),(7.23,7.43,TRIM)):
        paint(.04,length-.04,.021,.15,ground+lo,ground+high,shade)
    for x in style["front_bay_centers"]:
        u=east-x
        for low,high in ((4.12,6.44),(8.62,10.93)):
            prior.window(paint,u,1.52,ground+low,ground+high,FRAME,GLASS,2)
    for x in (-7.95,-5.9,-3.85,-1.8,.25,2.3):
        u=east-x
        if not base.row_covered(LineString(((east,front_y),(west,front_y))),u,.95,gates):
            prior.window(paint,u,1.94,ground+.22,ground+2.93,TRIM,STOREFRONT,2)
    center, radius=style["arch_center"],style["arch_radius"]
    arched_panel(parts,center,front_y,radius+.125,ground+7.72,ground+11.17,.008,.103,TRIM)
    arched_panel(parts,center,front_y,radius,ground+7.86,ground+11.17,.105,.145,GLASS)
    u=east-center
    for distance in (-.76,0,.76):
        peak=ground+11.17+np.sqrt(radius*radius-distance*distance)
        paint(u+distance-.026,u+distance+.026,.145,.171,ground+7.88,peak-.032,DARK)
    paint(u-radius,u+radius,.145,.173,ground+10.52,ground+10.59,DARK)
    paint(u-radius,u+radius,.145,.173,ground+11.16,ground+11.22,DARK)
    for end in (u-radius-.23,u+radius+.23):
        paint(end-.052,end+.052,.021,.095,ground+3.82,ground+10.66,TRIM)


def franklin(parts, plan, roofs, style, grade_at, gates):
    for side,add,u,stride,point in exposed_bays(parts,plan,style["bay_m"]):
        e,n=point
        grade=grade_at(e,n)
        z=roof_at(roofs,point)
        low_band(add,u,stride,grade)
        add(u-stride*.46,u+stride*.46,.01,.13,z-.47,z-.24,FRAME)
        add(u-stride*.48,u-stride*.42,.012,.126,grade+.41,z-.46,BRICK)
        if not base.row_covered(side,u,stride*.42,gates):
            prior.window(add,u,stride*.63,grade+1.03,min(grade+2.82,z-.69),TRIM,GLASS,2)
        if n>-.08 and z-grade>7.0:
            add(u-stride*.46,u+stride*.46,.017,.112,grade+3.57,grade+3.83,FRAME)
            prior.window(add,u,stride*.58,grade+4.39,min(grade+6.46,z-.78),TRIM,GLASS,2)


FACADES={"annex":annex,"rainier":rainier,"utility":utility,"business":business,"franklin":franklin}


def build_models(spec,manifest,config,field,graph):
    entries,pads,plans,supports=[],[],[],[]
    records,models=[],{}
    for row in spec["models"]:
        origin,yaw=row["origin_enu_m"],row["yaw_degrees"]
        plan=orient(Polygon(row["plan"]))
        placement=place(plan,origin,yaw)
        floor,_=science.earlier.fit_base(field,placement)
        pieces,gates,blocks=[],[],[]
        for hint in row["entrances"]:
            gate,_,extra=shared.site_entry(pads,field,hint)
            gates.append(gate)
            blocks.extend(extra)
        lookup=roof_shells(pieces,plan,row["roofs"],floor)
        c,s=np.cos(np.deg2rad(yaw)),np.sin(np.deg2rad(yaw))
        def grade(e,n):
            return geometry.sample_ground(field,origin[0]+c*e-s*n,origin[1]+s*e+c*n)
        local_gates=[dict(gate,position_enu_m=to_local(gate["position_enu_m"],origin,yaw)) for gate in gates]
        style=row["appearance"]
        FACADES[style["kind"]](pieces,plan,lookup,style,grade,local_gates)
        for x0,y0,x1,y1,z in style.get("equipment",[]):
            at=((x0+x1)*.5,(y0+y1)*.5)
            body=box(x0,y0,x1,y1).intersection(plan)
            lower=roof_at(lookup,at)-.04
            if z>lower+.025:
                base.flat(pieces,body,lower,z,FASCIA,PALE)
        prior.painted_doors(pieces,list(shared.face_edges(plan)),local_gates,FRAME,DARK)
        mesh=trimesh.util.concatenate(pieces)
        mesh.update_faces(mesh.nondegenerate_faces(height=.00006))
        models[row["id"]]=science.ordered_mesh(place_mesh(mesh,origin,yaw))
        entries.extend(gates)
        plans.append(placement)
        supports.extend(blocks)
        records.append({
            "id":row["id"],"name":row["name"],"campus_id":row["campus_id"],
            "footprint_enu_m":base.ring(placement),"area_m2":round(placement.area,3),
            "support_collision_enu_m":[base.ring(block) for block in blocks],
            "entrances":gates,"base_z_m":round(floor,4),"roof_z_m":round(float(mesh.bounds[1,1]),4),
        })
    previous=base.union([Polygon(row["footprint_enu_m"]).buffer(0) for row in manifest["buildings"] if row["id"] in models])
    edges,clearance=prior.nearby.shared.graduate.shared.check_routes(
        plans,supports,entries,previous,manifest,graph,config,set(models),
    )
    return models,records,science.ordered_mesh(trimesh.util.concatenate(pads)),edges,clearance


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit",type=Path,required=True)
    parser.add_argument("--stage",type=Path)
    parser.add_argument("--spec",type=Path,default=SPEC)
    args=parser.parse_args()
    manifest_path,config_path=SCENE/"manifest.json",SCENE/"presentation.json"
    spec,manifest,config=[json.loads(f.read_bytes()) for f in (args.spec,manifest_path,config_path)]
    terrain=SCENE/manifest["heightfield_url"]
    if tools.digest(manifest_path)!=spec["source_manifest_sha256"] or tools.digest(terrain)!=spec["source_heightfield_sha256"]:
        raise ValueError("Office exteriors no longer match the campus source and terrain.")
    field=json.loads(terrain.read_bytes())
    graph=json.loads((SCENE/"navigation.json").read_bytes())
    models,records,ground,edges,clearance=build_models(spec,manifest,config,field,graph)
    appearances=json.loads((ROOT/"data/metadata/campus-expansion-audit.json").read_bytes())
    removals=shared.frohnmayer.source_removals({"absorbed_batches":spec["source_ranges"]},config,appearances)
    output=args.stage or SCENE/DIRECTORY
    output.mkdir(parents=True,exist_ok=True)
    model,descriptor=output/"site.glb",output/"site.json"
    site.memorial.gerlinger.export(model,models,ground,GROUND,"office-paving")
    package={
        "source_presentation_sha256":config["asset_sha256"],"source_base_model_sha256":manifest["model"]["sha256"],
        "source_heightfield_sha256":tools.digest(terrain),"ground_node":GROUND,
        "url":f"{DIRECTORY}/site.glb","sha256":tools.digest(model),"buildings":records,
        "absorbed_ids":[],"batch_removals":removals,
    }
    descriptor.write_text(json.dumps(package,separators=(",",":"))+"\n",encoding="utf-8",newline="\n")
    if args.stage is None:
        config["office_exterior_site"]={"url":f"{DIRECTORY}/site.json","sha256":tools.digest(descriptor)}
        config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    audit={
        "buildings":records,"route_edges":edges,"nearest_route_m":round(clearance,4),
        "triangles":{key:len(mesh.faces) for key,mesh in models.items()},"batch_removals":removals,
        "glb_sha256":package["sha256"],"descriptor_sha256":tools.digest(descriptor),
    }
    args.audit.write_text(json.dumps(audit,indent=2)+"\n",encoding="utf8",newline="\n")
    print({key:audit[key] for key in ("route_edges","nearest_route_m","triangles","glb_sha256")})


if __name__=="__main__":
    main()
