# SPDX-License-Identifier: Apache-2.0
"""Export the East 12th–15th blocks from registered exterior geometry."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
import trimesh
from shapely import intersects_xy, set_precision
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

southwest = import_module("build-southwest-exterior-review")
agate, fairmount, garden, geometry, hilyard, older = (
    southwest.agate,
    southwest.fairmount,
    southwest.garden,
    southwest.geometry,
    southwest.hilyard,
    southwest.older,
)
PACKAGE = "northwest-blocks-review"
PAVING = "northwest-blocks-paving"


def frontage(parts, wall, world, side, target, stations):
    edge, view = hilyard.face_on(parts, wall, world, side, target)
    left, right = hilyard.span_on(
        edge, world, {"side": side, "target": target, "span": stations}
    )
    return view, max(left, 0.08), min(right, view[0] - 0.08)


def storefronts(parts, row, wall, world):
    for side, target, stations, level, top in row["stores"]:
        view, left, right = frontage(parts, wall, world, side, target, stations)
        _, add, _, _, _, _ = view
        count = max(1, round((right - left) / 3.20))
        for lo, hi in zip(
            np.linspace(left, right, count + 1)[:-1],
            np.linspace(left, right, count + 1)[1:],
        ):
            hilyard.glazed(
                add, lo + 0.08, hi - 0.08, level + 0.40, top, row["trim_color"]
            )
        for u in np.linspace(left, right, count + 1)[1:-1]:
            add(u - 0.065, u + 0.065, 0.031, 0.18, level, top + 0.24, row["trim_color"])
        add(left, right, 0.012, 0.33, top + 0.12, top + 0.34, row["trim_color"])


def recessed_parking(parts, row, wall, world, field):
    side, target, center, width, _, _ = row["bounded_bay"]
    _, (_, add, _, plan, _, _) = hilyard.face_on(
        parts, wall, world, side, (target[0], target[1] + row["bounded_bay"][4])
    )
    # The grille sits at the rear of the shallow alley recess.
    left = center + 0.09
    right = center + width - 0.11
    span = width - 0.20
    ground = hilyard.grade(field, plan(left + span / 2, 0))
    top = row["bounded_bay"][5]
    add(left, right, 0.018, 0.05, ground, top, (71, 72, 68))
    for y in np.arange(ground + 0.13, top - 0.07, 0.14):
        add(left, right, 0.051, 0.069, y, y + 0.024, (131, 124, 106))


def arched_facade(parts, row, wall, world):
    side, target, stations, bottom, top = row["arch_strip"]
    (_, add, _, _, _, panel), left, right = frontage(
        parts, wall, world, side, target, stations
    )
    depth = right - left
    count = max(1, round(depth / 2.13))
    for u in left + (np.arange(count) + 0.5) * depth / count:
        hilyard.arch_panel(
            panel,
            u,
            min(1.64, 0.79 * depth / count),
            bottom,
            top,
            row["trim_color"],
            (84, 89, 79),
        )
        add(
            u - 0.019,
            u + 0.019,
            0.101,
            0.114,
            bottom + 0.19,
            top - 0.38,
            (177, 170, 142),
        )
    add(left, right, 0.006, 0.11, top + 0.42, top + 0.66, row["trim_color"])


def slat_screen(parts, row, wall, world):
    side, target, stations, bottom, top = row["screen"]
    (_, add, _, _, _, _), left, right = frontage(
        parts, wall, world, side, target, stations
    )
    for z in np.arange(bottom, top, 0.214):
        add(left, right, 0.12, 0.35, z, z + 0.043, row["trim_color"])
    for u in np.linspace(left, right, 6):
        add(u - 0.025, u + 0.025, 0.14, 0.38, bottom - 0.10, top, (99, 100, 88))


def timber_facade(parts, row, wall, world):
    side, target, stations, bottom, top = row["timber"]
    (_, add, _, _, _, panel), left, right = frontage(
        parts, wall, world, side, target, stations
    )
    if right - left < 0.50:
        return
    trim = row["trim_color"]
    add(left, right, 0.016, 0.068, bottom, top, (191, 182, 148))
    bays = np.linspace(left, right, max(2, round((right - left) / 1.42) + 1))
    for a, b in zip(bays[:-1], bays[1:]):
        add(a, a + 0.055, 0.072, 0.124, bottom, top, trim)
        panel(
            orient(
                Polygon([(a, bottom), (a + 0.12, bottom), (b, top), (b - 0.12, top)])
            ),
            0.071,
            0.103,
            trim,
        )
        panel(
            orient(
                Polygon([(a, top), (a + 0.12, top), (b, bottom), (b - 0.12, bottom)])
            ),
            0.071,
            0.103,
            trim,
        )
    add(left, right, 0.072, 0.125, top - 0.10, top, trim)


def bands(parts, row, wall, roof_at):
    for side, bottom, top, color in row.get("wall_bands", []):
        direction = np.asarray(hilyard.DIRECTION[side])
        for _, (span, add, normal, plan, _, _) in fairmount.views(parts, wall):
            if direction @ normal < 0.92 or span < 1.3:
                continue
            cap = min(
                top, roof_at(plan(0.1, 0)) - 0.15, roof_at(plan(span - 0.1, 0)) - 0.15
            )
            if cap > bottom + 0.11:
                add(0.09, span - 0.09, 0.006, 0.028, bottom, cap, color)


def east_court_walks(parts, row, patch, shape):
    for limits in row["court_walks"]:
        plate = orient(patch(limits).intersection(shape).buffer(-0.01))
        if plate.is_empty:
            continue
        for top in row["levels_z_m"][1:]:
            parts.append(
                geometry.shell(
                    plate,
                    top - 0.16,
                    lambda *_: top,
                    row["trim_color"],
                    row["trim_color"],
                )
            )
    # Vertical blue cladding and alternating light bands on the visible central end.
    _, (span, add, _, _, _, _) = hilyard.face_on(
        parts, shape, older.transforms(row)[2], "E", (10.8, 0)
    )
    colors = ((113, 153, 164), (90, 129, 145), (160, 174, 172), (76, 107, 121))
    for index, z in enumerate(np.arange(4.99, 13.25, 0.87)):
        for bay, u in enumerate(np.arange(0.12, span - 0.18, 2.7)):
            add(
                u,
                min(u + 2.5, span - 0.055),
                0.016,
                0.039,
                z,
                min(z + 0.61, 13.37),
                colors[(index + bay) % len(colors)],
            )


def build(row, field, paving):
    style = row.get("treatment")
    if style is None:
        return hilyard.build(row, field, paving)

    patch, _, world = older.transforms(row)
    roof = orient(
        set_precision(
            Polygon(row["outline_enu_m"], row["courtyard_rings_enu_m"]), 0.002
        )
    )
    if style == "three-wings":
        outline = roof
        roof = orient(
            roof.difference(
                unary_union([patch(bounds) for bounds in row["roof_slots"]])
            )
        )
    nominal = orient(roof.buffer(-row["eaves_m"], join_style="mitre"))
    wall = nominal
    if "bounded_bay" in row:
        _, target, center, width, distance, head = row["bounded_bay"]
        x, y = target
        opening = patch((x - width / 2, y - 1, x + width / 2, y + distance))
        wall = orient(nominal.difference(opening))
        row = {
            **row,
            "raised_wall_enu_m": list(nominal.exterior.coords)[:-1],
            "raised_wall_bottom_z_m": head,
        }
    parts = []
    roof_at = garden.roof_sections(parts, roof, wall, row["base_z_m"], row, grid=0.0002)
    southwest.pattern_facade(
        parts,
        row,
        nominal,
        field,
        roof_at,
        raised=(opening, head) if "bounded_bay" in row else None,
    )
    if "stores" in row:
        storefronts(parts, row, nominal, world)
    if "bounded_bay" in row:
        recessed_parking(parts, row, wall, world, field)
    if style == "arcaded":
        arched_facade(parts, row, wall, world)
    if style == "slat-screen":
        slat_screen(parts, row, wall, world)
    if style == "tudor":
        timber_facade(parts, row, wall, world)
    if style == "three-wings":
        east_court_walks(parts, row, patch, outline)
    bands(parts, row, wall, roof_at)
    older.roof_equipment(parts, row, roof, roof_at, patch)
    return agate.output(parts, row, roof, set_precision(wall, 0), [], [])


def source_removals(spec, config, audit):
    touching = spec["touching_source_ranges"]
    shared = garden.shared.frohnmayer.source_removals
    ordinary = [r for r in spec["source_ranges"] if r["id"] not in touching]
    removals = shared({"absorbed_batches": ordinary}, config, audit)

    scene_file = fairmount.SCENE / config["asset_url"]
    assert garden.tools.digest(scene_file) == spec["touching_source_sha256"]
    source = trimesh.load(scene_file, force="scene", process=False)
    adjacent = [r for r in spec["source_ranges"] if r["id"] in touching]
    target = adjacent[0]["target"]
    assert {r["target"] for r in adjacent} == {target}
    transform, key = source.graph[target]
    assert np.array_equal(transform, np.eye(4))
    triangles = source.geometry[key].triangles
    plans = {r["id"]: Polygon(r["footprint_enu_m"]) for r in audit["appearance_plan"]}
    spans = sorted(tuple(v) for v in touching.values())
    assert len(spans) == 2 and 0 <= spans[0][0] < spans[0][1] == spans[1][0] < spans[1][
        1
    ] <= len(triangles)
    for row in adjacent:
        ident = row["id"]
        assert ident in audit["context_batches"][target]
        start, end = touching[ident]
        mask = intersects_xy(
            plans[ident].buffer(0.29), triangles[:, :, 0], -triangles[:, :, 2]
        ).all(axis=1)
        assert mask[start:end].all()
        mask[spans[0][0] : spans[-1][1]] = False
        assert not mask.any()
        corners = triangles[start:end].reshape(-1, 3)
        removals.append(
            {
                **row,
                "triangles": [start, end],
                "source_triangle_count": len(triangles),
                "source_vertices": [
                    [i, corners[i].round(6).tolist()]
                    for i in (0, len(corners) // 2, len(corners) - 1)
                ],
            }
        )
    return removals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    fairmount.export_review(
        parser.parse_args(),
        PACKAGE,
        PAVING,
        "northwest_blocks_site",
        build,
        source_removals=source_removals,
    )


if __name__ == "__main__":
    main()
