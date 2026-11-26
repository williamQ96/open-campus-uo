# SPDX-License-Identifier: Apache-2.0
"""Export the address-registered Bardell Avenue exteriors."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon

source = Path(__file__).with_name("build-fairmount-boulevard-exterior-review.py")
loader = spec_from_file_location(source.stem, source)
houses = module_from_spec(loader)
loader.loader.exec_module(houses)
chapter, design = houses.chapter, houses.design
housing, approaches, geometry = houses.housing, houses.approaches, houses.geometry

PACKAGE = "bardell-avenue-exterior-review"
SPEC = houses.ROOT / "data/metadata/bardell-avenue-exterior-review.json"
CONCRETE = (161, 157, 141)
GLASS = (93, 121, 127)


def facade_edges(edges, positions):
    located = {}
    for detail in positions:
        edge = design.locate_face(edges, detail["near_enu_m"], detail["bearing"])
        located.setdefault(edge, []).append(detail)
    return located


def framed_window(add, center, width, sill, head, trim, ribs=2):
    chapter.prior.window(add, center, width, sill, head, trim, GLASS, ribs=ribs)


def arch(span, base, rise, center):
    return [
        (center + span / 2 * float(np.cos(t)), base + rise * float(np.sin(t)))
        for t in np.linspace(0, np.pi, 11)
    ]


def finish_gable(slab, add, grade, samples, caps, color):
    spring = grade + 2.17
    top = np.maximum(caps, spring + 0.03)
    profile = Polygon(
        [(samples[0], spring), (samples[-1], spring), *zip(samples[::-1], top[::-1])]
    )
    slab(profile, 0.006, 0.030, color)
    seam = tuple(max(0, c - 18) for c in color)
    for level in np.arange(spring + 0.16, top.max() - 0.07, 0.19):
        visible = samples[top > level + 0.034]
        if len(visible) > 1:
            add(visible[0], visible[-1], 0.029, 0.043, level, level + 0.012, seam)


def reclad(parts, field, row, edges, gate, door_edge, door_at, height):
    supports = []
    trim = row["trim_color"]
    wall = row["wall_color"]
    coursing = tuple(max(0, c - 21) for c in wall)
    garages = facade_edges(edges, row["garages"])
    windows = facade_edges(edges, row["windows"])
    for edge in edges:
        span, add, _, plan, _, slab = chapter.setup_face(parts, *edge)
        if span < 1.15:
            continue
        grade = geometry.sample_ground(field, *plan(span / 2, 0.04))
        samples = np.linspace(0.025, span - 0.025, max(5, round(span / 0.28)))
        caps = np.array([height(plan(u, 0)) - 0.18 for u in samples])
        add(0.018, span - 0.018, -0.003, 0.035, grade - 0.09, grade + 0.25, CONCRETE)
        for level in np.arange(grade + 0.28, caps.max() - 0.11, row["course_height_m"]):
            visible = np.flatnonzero(caps > level + 0.11)
            for segment in np.split(visible, np.flatnonzero(np.diff(visible) > 1) + 1):
                if len(segment) > 1:
                    add(
                        samples[segment[0]],
                        samples[segment[-1]],
                        -0.003,
                        0.012,
                        level,
                        level + 0.013,
                        coursing,
                    )

        if edge in garages:
            if row.get("garage_gable_color"):
                finish_gable(slab, add, grade, samples, caps, row["garage_gable_color"])
            for garage in garages[edge]:
                center = LineString(edge).project(Point(garage["near_enu_m"]))
                width = min(garage["width_m"], span - 0.26)
                center = np.clip(center, width / 2 + 0.12, span - width / 2 - 0.12)
                floor = geometry.sample_ground(field, *plan(center, 0.29)) + 0.02
                top = (
                    min(
                        height(plan(u, 0))
                        for u in (center - width / 2, center + width / 2)
                    )
                    - 0.18
                )
                if top - floor < 2.13:
                    raise ValueError(
                        f"Garage opening does not fit {row['id']} at {garage['near_enu_m']}."
                    )
                housing.garage_front(
                    add, center, width, floor, tuple(garage["color"]), trim
                )
                if garage["style"] == "window-strip":
                    for x in np.linspace(
                        center - width * 0.32, center + width * 0.32, garage["panels"]
                    ):
                        add(
                            x - 0.16,
                            x + 0.16,
                            0.086,
                            0.102,
                            floor + 1.79,
                            floor + 1.97,
                            GLASS,
                        )
                if garage["style"] == "arched":
                    panel = (width - 0.028) / garage["panels"]
                    for x in (
                        center
                        + (np.arange(garage["panels"]) - (garage["panels"] - 1) / 2)
                        * panel
                    ):
                        curve = arch(panel - 0.14, floor + 1.83, 0.21, x)
                        profile = Polygon(
                            [
                                (curve[0][0], floor + 0.10),
                                *curve,
                                (curve[-1][0], floor + 0.10),
                            ]
                        )
                        slab(profile, 0.083, 0.110, garage["color"])
                        outer = profile.buffer(0.035, join_style="round").difference(
                            profile
                        )
                        slab(outer, 0.102, 0.126, trim)

        for window in windows.get(edge, []):
            width = min(span - 0.19, window["width_m"])
            center = LineString(edge).project(Point(window["near_enu_m"]))
            center = np.clip(center, width / 2 + 0.09, span - width / 2 - 0.09)
            local = geometry.sample_ground(field, *plan(center, 0.02))
            requested = local + window["sill_m"]
            cap = (
                min(
                    height(plan(u, 0)) for u in (center - width / 2, center + width / 2)
                )
                - 0.25
            )
            sill = min(requested, cap - 0.57)
            head = min(cap, sill + window["height_m"])
            if sill >= local + 0.35 and head > sill + 0.45:
                framed_window(add, center, width, sill, head, trim, window["ribs"])

        if edge == door_edge:
            supports.extend(
                portico(parts, row, gate, door_at, span, add, slab, plan, height)
            )
        elif edge not in windows and edge not in garages and span > 4.65:
            for u in np.linspace(0.25, 0.75, max(2, round(span / 4.8))) * span:
                terrain = geometry.sample_ground(field, *plan(u, 0.02))
                sill = terrain + 0.89
                head = min(height(plan(u, 0)) - 0.36, sill + 1.15)
                if head - sill > 0.61:
                    framed_window(add, u, min(1.3, span * 0.21), sill, head, trim)
    return supports


def portico(parts, row, gate, u, span, add, slab, plan, height):
    ref = row["entry_trim"]
    trim, pier = row["trim_color"], ref["pier_color"]
    half = min(ref["half_width_m"], u - 0.10, span - u - 0.10)
    depth = ref["depth_m"]
    z = gate["threshold_z_m"]
    if half < 0.69:
        raise ValueError(f"Entry cover does not fit {row['id']}.")
    eave = min(height(plan(x, 0.02)) for x in (u - half, u, u + half)) - 0.19
    head = min(z + ref["head_above_threshold_m"], eave - 0.11)
    if head < z + 2.17:
        raise ValueError(f"Entry head conflicts with roof {row['id']}.")
    # The exterior slab meets the entry stair, with square pier footprints.
    landing = Polygon(
        [
            plan(x, y)
            for x, y in (
                (u - half, 0),
                (u + half, 0),
                (u + half, depth),
                (u - half, depth),
            )
        ]
    )
    houses.base.flat(parts, landing, z - 0.17, z, CONCRETE)
    if ref["shape"] == "gable":
        chapter.gabled_canopy(
            parts,
            plan,
            u,
            half + 0.055,
            -0.035,
            depth + 0.09,
            head,
            ref["roof_rise_m"],
            row["roof_color"],
            trim,
        )
    else:
        add(
            u - half - 0.06,
            u + half + 0.06,
            -0.04,
            depth + 0.09,
            head - 0.11,
            head + 0.065,
            trim,
        )
    feet = []
    pier_half = ref["pier_half_width_m"]
    for x in (u - half + pier_half + 0.05, u + half - pier_half - 0.05):
        if pier_half and abs(x - u) > 0.69 + pier_half:
            p = plan(x, depth - pier_half - 0.02)
            feet.append(
                approaches.supported_post(parts, p, z - 0.05, head, pier, pier_half)
            )
            add(
                x - pier_half - 0.036,
                x + pier_half + 0.036,
                depth - 2 * pier_half - 0.064,
                depth + 0.011,
                head - 0.14,
                head - 0.045,
                trim,
            )
    if ref.get("sidelights") and half > 1.10:
        for side in (-1, 1):
            framed_window(add, u + side * 0.866, 0.29, z + 0.29, z + 2.04, trim, 1)
    if ref["arched_transom"]:
        pane = Polygon(arch(1.01, z + 2.02, 0.36, u))
        slab(pane.buffer(0.061, join_style="round"), 0.014, 0.073, trim)
        slab(pane, 0.072, 0.084, GLASS)
    return feet


def build(spec, manifest, configuration, heightfield, graph):
    return houses.build(
        spec, manifest, configuration, heightfield, graph, decorate=reclad
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()
    houses.export_review(
        spec_path=SPEC,
        package=PACKAGE,
        key="bardell_avenue_exterior_site",
        ground_node="bardell-avenue-approaches",
        paving_node="bardell-avenue-paving",
        builder=build,
        audit_path=args.audit,
        stage=args.stage,
    )


if __name__ == "__main__":
    main()
