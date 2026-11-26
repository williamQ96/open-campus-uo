# SPDX-License-Identifier: Apache-2.0
"""Export editable, source-pinned roof replacements for the reviewed context IDs."""

import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import Polygon, box
import trimesh

from compound_context_roofs import replacement

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "apps/web-preview/public/scene"
PARAMETERS = ROOT / "data/metadata/context-roof-refinements.json"
COMPOUND = ROOT / "data/metadata/compound-context-roofs.json"
APPEARANCE = ROOT / "data/metadata/campus-expansion-audit.json"
OUTPUT = SCENE / "context-roof-refinements.json"
geometry_path = Path(__file__).with_name("build-cascade-exterior-review.py")
geometry_spec = spec_from_file_location(geometry_path.stem, geometry_path)
geometry = module_from_spec(geometry_spec)
geometry_spec.loader.exec_module(geometry)


def digest(file):
    return sha256(file.read_bytes()).hexdigest()


def roof_color(rgb):
    srgb = np.asarray(rgb) / 255
    return 255 * ((srgb + 0.055) / 1.055) ** 2.4


def pack_roof(pieces):
    roof = trimesh.util.concatenate(pieces)
    corners = roof.faces.reshape(-1)
    cap = roof.vertices[corners]
    normals = np.repeat(roof.face_normals, 3, axis=0)
    colors = roof.visual.vertex_colors[corners, :3] / 255.0
    assert np.isfinite(normals).all() and len(cap) == len(normals) == len(colors)
    return {
        "position": np.round(cap, 5).ravel().tolist(),
        "normal": np.round(normals, 6).ravel().tolist(),
        "color": np.round(colors, 6).ravel().tolist(),
    }, round(float(roof.bounds[1, 1]), 4)


def flat_roof_cap(fit, outline, wall_color):
    eave = fit["coefficients"][0]
    face_rgb = tuple(np.rint(roof_color(fit["cap_rgb"])).astype(int))
    cap_rgb = tuple(np.rint(np.minimum(255, np.array(face_rgb) * 1.11)).astype(int))
    steps = fit.get("roof_step")
    if steps:
        west, south, east, north = outline.bounds
        cut = steps["cut_enu_m"]
        if steps["axis"] == 0:
            sides = (
                box(west - 1, south - 1, cut, north + 1),
                box(cut, south - 1, east + 1, north + 1),
            )
        else:
            sides = (
                box(west - 1, south - 1, east + 1, cut),
                box(west - 1, cut, east + 1, north + 1),
            )
        strata = [
            (outline.intersection(side), z)
            for side, z in zip(sides, steps["heights_m"], strict=True)
        ]
        assert min(z for _, z in strata) == eave
        assert all(region.area > 10 for region, _ in strata)
        assert (
            shapely.union_all([area for area, _ in strata])
            .symmetric_difference(outline)
            .area
            < 0.001
        )
    else:
        strata = [(outline, eave)]

    pieces = []
    rim = outline.difference(outline.buffer(-fit["edge_width_m"]))
    for region, deck in strata:
        for part in geometry.sections(region):
            pieces.append(
                geometry.shell(
                    part,
                    eave - 0.00125,
                    lambda e, n: deck + 0.015,
                    wall_color,
                    face_rgb,
                )
            )
        for part in geometry.sections(region.intersection(rim)):
            pieces.append(
                geometry.shell(
                    part,
                    deck,
                    lambda e, n: deck + fit["edge_cap_m"],
                    wall_color,
                    cap_rgb,
                )
            )

    if rows := fit.get("solar_rows"):
        panel_rgb = tuple(np.rint(roof_color([74, 91, 103])).astype(int))
        for row in rows:
            west, south, east, north = row["bounds_enu_m"]
            mounts = np.linspace(west, east, row["panels"] + 1)
            for left, right in zip(mounts, mounts[1:]):
                panel = box(left + 0.034, south, right - 0.034, north)
                assert outline.buffer(-0.17).covers(panel)
                (deck,) = [height for region, height in strata if region.covers(panel)]
                pieces.append(
                    geometry.shell(
                        panel,
                        deck + 0.032,
                        lambda e, n: deck + 0.13 + 0.11 * (n - south) / (north - south),
                        wall_color,
                        panel_rgb,
                    )
                )
    return pack_roof(pieces)


def roof_cap(fit, outline, wall_color):
    if fit["type"] in ("flat", "step"):
        return flat_roof_cap(fit, outline, wall_color)
    center = np.asarray(fit["centroid"])
    ul, vl = fit["dimensions_m"]
    axis = np.asarray(fit["axis"]) * ul
    normal = np.asarray(fit["normal_axis"]) * vl
    eave, rise, ridge, *ends = fit["coefficients"]
    sw, se, ne, nw = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))
    west_ridge, east_ridge = (
        ((ends[0], ridge), (ends[1], ridge))
        if ends
        else (
            (-0.5, ridge),
            (0.5, ridge),
        )
    )
    facets = [
        ([sw, se, east_ridge, west_ridge], (normal, -0.5, ridge)),
        ([ne, nw, west_ridge, east_ridge], (normal, 0.5, ridge)),
    ]
    if ends:
        facets.extend(
            [
                ([nw, sw, west_ridge], (axis, -0.5, west_ridge[0])),
                ([se, ne, east_ridge], (axis, 0.5, east_ridge[0])),
            ]
        )
    planes, faces = [], []
    color = roof_color(fit["cap_rgb"])
    for i, (points, (coordinate, zero, one)) in enumerate(facets):
        region = outline.intersection(
            Polygon([center + u * axis + v * normal for u, v in points])
        )
        tone = tuple(np.round(color * (0.93 if i % 2 else 1)).astype(int))
        inverse = coordinate / coordinate.dot(coordinate)

        def height(e, n):
            fraction = ((np.array([e, n]) - center).dot(inverse) - zero) / (one - zero)
            return eave + rise * max(0, fraction)

        for plane in geometry.sections(region):
            faces.append(
                geometry.shell(plane, eave - 0.00125, height, wall_color, tone)
            )
            planes.append(plane)
    coverage = shapely.union_all(planes)
    # Rounding the fitted frame to seven decimals can drop sub-millimetre strips
    # at the edges of the original outline.
    assert coverage.symmetric_difference(outline).area < 0.005, fit["id"]
    return pack_roof(faces)


def source_span(record, peers, mesh):
    outline = Polygon(record["footprint_enu_m"])
    probe = outline.buffer(0.29)
    assert all(not probe.intersects(other) for other in peers)
    corners = mesh.triangles
    area_match = shapely.intersects_xy(probe, corners[:, :, 0], -corners[:, :, 2])
    matches = np.flatnonzero(area_match.all(axis=1))
    assert len(matches) and np.array_equal(
        matches, np.arange(matches[0], matches[-1] + 1)
    )
    return outline, matches, corners[matches]


def anchors(body):
    return [
        [offset, np.round(body[offset // 3, offset % 3], 6).tolist()]
        for offset in (0, len(body) * 3 // 2, len(body) * 3 - 1)
    ]


def patch_for(fit, record, peers, mesh):
    outline, matches, body = source_span(record, peers, mesh)
    old_eave = fit["old_roof_wall_z_m"]
    base = record["base_z_m"]
    kept = np.flatnonzero(body[:, :, 1].min(axis=1) < old_eave - 0.49)
    assert 0 < len(kept) < len(body), fit["id"]
    assert body[kept, :, 1].max() <= old_eave + 0.002
    assert abs(body[kept, :, 1].min() - base) < 0.001
    wall_normal = abs(mesh.face_normals[matches[kept], 1]) < 0.005
    wall_faces = matches[kept[wall_normal]]
    wall_pieces = mesh.faces[wall_faces].ravel()
    source_colors = mesh.visual.vertex_attributes["color"][wall_pieces, :3]
    colors, groups = np.unique(source_colors, return_inverse=True, axis=0)
    area = np.bincount(groups, weights=np.repeat(mesh.area_faces[wall_faces], 3))
    wall_color = tuple(np.rint(colors[np.argmax(area)] * 255).astype(int))
    cap, max_z = roof_cap(fit, outline, wall_color)
    eave = fit["coefficients"][0]
    assert 0.7 < (eave - base) / (old_eave - base) < 1.6, fit["id"]
    return {
        "id": fit["id"],
        "triangles": [int(matches[0]), int(matches[-1] + 1)],
        "source_vertices": anchors(body),
        "keep_wall_triangles": kept.tolist(),
        "footing_z_m": base,
        "old_eave_z_m": old_eave,
        "new_eave_z_m": eave,
        "new_roof_z_m": max_z,
        "cap": cap,
    }


def compound_patch(fit, record, peers, mesh, field, tools, other_plans):
    _, matches, body = source_span(record, peers, mesh)
    outline, foot, peak, cap = replacement(fit, field, tools)
    overlaps = [
        (id, outline.intersection(plan).area)
        for id, plan in other_plans.items()
        if id != fit["id"] and plan.intersects(outline)
    ]
    assert not any(area > 0.20 for _, area in overlaps), (fit["id"], overlaps)
    lower = (
        fit["roof_profile"]["connectors"][0][2]
        if fit["form"] == "courtyard"
        else fit["dormers"]["side_eave_z_m"]
    )
    return {
        "id": fit["id"],
        "triangles": [int(matches[0]), int(matches[-1] + 1)],
        "source_vertices": anchors(body),
        "keep_wall_triangles": [],
        "footing_z_m": foot,
        "old_eave_z_m": record["base_z_m"] + record["wall_height_m"],
        "new_eave_z_m": lower,
        "new_roof_z_m": peak,
        "cap": cap,
        "replacement": {
            "footprint_enu_m": fit["outer_enu_m"],
            "footprint_holes_enu_m": fit["holes_enu_m"],
            "area_m2": round(outline.area, 2),
            "name": fit["name"],
            "name_source": fit["name_source"],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    args = parser.parse_args()
    params = json.loads(PARAMETERS.read_bytes())
    presentation_path = SCENE / "presentation.json"
    presentation = json.loads(presentation_path.read_bytes())
    source_path = SCENE / presentation["asset_url"]
    assert (
        digest(source_path)
        == presentation["asset_sha256"]
        == params["source_presentation_sha256"]
    )
    assert digest(SCENE / "manifest.json") == params["source_manifest_sha256"]
    assert digest(APPEARANCE) == params["source_appearance_plan_sha256"]
    appearance = json.loads(APPEARANCE.read_bytes())
    records = {row["id"]: row for row in appearance["appearance_plan"]}
    compound = json.loads(COMPOUND.read_bytes())
    manifest = json.loads((SCENE / "manifest.json").read_bytes())
    heightfield_path = SCENE / manifest["heightfield_url"]
    assert digest(heightfield_path) == compound["source_heightfield_sha256"]
    field = json.loads(heightfield_path.read_bytes())
    tools_path = Path(__file__).with_name("build-athletic-exterior-review.py")
    tools_spec = spec_from_file_location(tools_path.stem, tools_path)
    tools = module_from_spec(tools_spec)
    tools_spec.loader.exec_module(tools)
    other_plans = {
        row["id"]: Polygon(row["footprint_enu_m"]).buffer(0)
        for row in manifest["buildings"]
    }
    authored = trimesh.load(source_path, force="scene", process=False)
    batches = {}
    audit = {}
    for fit in [*params["fits"], *compound["buildings"]]:
        building = fit["id"]
        name = fit["batch"]
        members = appearance["context_batches"][name]
        assert (
            building in members
            and building not in audit
            and not records[building]["name"]
        )
        xf, key = authored.graph[name]
        assert np.array_equal(xf, np.eye(4))
        mesh = authored.geometry[key]
        peers = [
            Polygon(records[peer]["footprint_enu_m"]).buffer(0.28)
            for peer in members
            if peer != building
        ]
        patch = (
            compound_patch(
                fit, records[building], peers, mesh, field, tools, other_plans
            )
            if "form" in fit
            else patch_for(fit, records[building], peers, mesh)
        )
        batch = batches.setdefault(
            name,
            {
                "target": name,
                "source_triangle_count": len(mesh.faces),
                "buildings": [],
            },
        )
        batch["buildings"].append(patch)
        audit[building] = {
            "batch": name,
            "former_member_triangles": patch["triangles"][1] - patch["triangles"][0],
            "retained_wall_triangles": len(patch["keep_wall_triangles"]),
            "cap_triangles": len(patch["cap"]["position"]) // 9,
            "eave_z_m": patch["new_eave_z_m"],
            "peak_z_m": patch["new_roof_z_m"],
        }
        if patch.get("replacement"):
            audit[building]["footprint_m2"] = patch["replacement"]["area_m2"]
            audit[building]["courtyard_m2"] = round(
                sum(
                    Polygon(hole).area
                    for hole in patch["replacement"]["footprint_holes_enu_m"]
                ),
                2,
            )
    for batch in batches.values():
        items = batch["buildings"]
        items.sort(key=lambda item: item["triangles"][0])
        assert all(
            a["triangles"][1] <= b["triangles"][0] for a, b in zip(items, items[1:])
        )
    OUTPUT.write_text(
        json.dumps(
            {
                "version": 1,
                "source_presentation_sha256": params["source_presentation_sha256"],
                "source_manifest_sha256": params["source_manifest_sha256"],
                "batches": list(batches.values()),
            },
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    recipe_sha = digest(OUTPUT)
    if link := presentation.get("context_roof_refinements"):
        assert link["url"] == OUTPUT.name
        if link["sha256"] != recipe_sha:
            link["sha256"] = recipe_sha
            presentation_path.write_text(
                json.dumps(presentation, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    args.audit.write_text(
        json.dumps(
            {
                "recipe_sha256": recipe_sha,
                "recipe_bytes": OUTPUT.stat().st_size,
                "batch_count": len(batches),
                "buildings": audit,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"Built roof shapes and wall fit for {len(audit)} members of {len(batches)} existing batches."
    )


if __name__ == "__main__":
    main()
