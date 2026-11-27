# SPDX-License-Identifier: Apache-2.0
"""Export endpoint connector coverage for surveyed walks in the southwest campus."""

import argparse
import json
from importlib import import_module
from pathlib import Path

from shapely import get_parts
from shapely.geometry import box
from shapely.ops import unary_union

cemetery = import_module("build-pioneer-cemetery-landscape-review")
green = import_module("build-southwest-campus-green")
education = import_module("build-kincaid-education-landscape")
kendall = import_module("build-kendall-plaza-landscape")
annex = import_module("build-education-annex-landscape")
knight_north = import_module("build-knight-north-plaza")
plc_east = import_module("build-plc-east-court")
dropoff = import_module("build-clinical-dropoff-landscape")
east_18th_west = import_module("build-east-18th-west-approach")
frohnmayer_drive = import_module("build-frohnmayer-east-drive")
rankin_frontage = import_module("build-rankin-frontage")
wayfinding = import_module("build-northeast-campus-wayfinding")
oregon = import_module("build-oregon-hall-southeast-landscape")
science_green = import_module("build-science-green-sundial")
cascade_access = import_module("build-cascade-courtyard-access")
cascade_north = import_module("build-cascade-courtyard-north")
onyx_green = import_module("build-onyx-green-walks")
price_courtyard = import_module("build-price-courtyard")
root = green.site.root
scene = green.site.scene


def cemetery_coverage(spec):
    roads, approach = cemetery.named_path_footprints(spec)
    frontage, _ = cemetery.rankin_frontage_footprint(spec)
    stair = spec["east_stair"]
    half = stair["width_m"] / 2
    landing = box(
        stair["top_east_m"] - 0.72,
        stair["north_m"] - half,
        stair["bottom_east_m"] + 0.75,
        stair["north_m"] + half,
    )
    return unary_union([roads, approach, frontage, landing])


def green_coverage(spec):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    buildings, _ = green.east.build_blockers(
        scene, spec, manifest, box(*spec["extent"])
    )
    _, walks, _, _ = green.surface_footprints(spec, buildings)
    return walks


def education_coverage(spec):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    buildings, _ = green.east.build_blockers(
        scene, spec, manifest, box(*spec["extent"])
    )
    brick, concrete, _, _ = education.surfaces(spec, buildings)
    return brick.union(concrete)


def kendall_coverage(spec):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    buildings, _ = kendall.blockers(spec, manifest)
    brick, concrete, _, _ = kendall.footprints(spec, buildings)
    south_paths, gravel_access, _, _, _ = kendall.south_lawn_footprints(spec, buildings)
    return unary_union([brick, concrete, south_paths, gravel_access])


def annex_coverage(spec):
    return unary_union(
        [
            annex.approach_walk(spec),
            box(*spec["porch_enu_m"]),
            *annex.ramp_footprints(spec),
        ]
    ).difference(box(*spec["body_enu_m"]))


def dropoff_coverage(spec):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    buildings, _ = green.east.build_blockers(
        scene, spec, manifest, box(*spec["extent"])
    )
    _, sidewalks, crossings, _ = dropoff.footprints(spec, buildings)
    return sidewalks.union(crossings)


def east_18th_west_coverage(spec, metadata):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    surfaces, _, _ = east_18th_west.site_footprints(spec, manifest, metadata)
    _, _, _, access, _ = surfaces
    return access


def frohnmayer_drive_coverage(spec, metadata):
    manifest, _, graph = green.east.pinned_site(scene, spec)
    drive, walks, _, _, _, _, lot = frohnmayer_drive.footprints(spec, manifest, metadata)
    drive_path = frohnmayer_drive.route_line(spec["routes"][-1]).buffer(0.76)
    return {
        **encode_coverage(
            frohnmayer_drive.PACKAGE,
            walks.union(drive.union(lot).intersection(drive_path)),
        ),
        "retired_road_segments_enu_m": frohnmayer_drive.retired_road_segments(
            spec, manifest, graph
        ),
    }


def rankin_frontage_coverage(spec, metadata):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    _, _, _, _, access, _, _ = rankin_frontage.footprints(spec, manifest, metadata)
    return access


def northeast_wayfinding_coverage(spec):
    manifest, _, _ = green.east.pinned_site(scene, spec)
    blockers = wayfinding.wayfinding_blockers(scene, spec, manifest)
    paths, crossing, _ = wayfinding.footprints(spec, blockers)
    return paths.union(crossing)


def encode_coverage(package, footprint):
    descriptor = green.site.read(scene / package / "site.json")
    assert green.site.pin(scene / package / "site.glb") == descriptor["sha256"]
    # The 13 cm registration tolerance matches the route export checks. The
    # simplified shape keeps sub-centimetre rounding out of shipped coordinates.
    shape = footprint.buffer(0.13, quad_segs=2).simplify(0.015)
    polygons = [
        [
            [[round(e, 3), round(n, 3)] for e, n in ring.coords[:-1]]
            for ring in [part.exterior, *part.interiors]
        ]
        for part in get_parts(shape.normalize())
    ]
    return {
        "package": package,
        "sha256": descriptor["sha256"],
        "polygons_enu_m": polygons,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    metadata = root / "data/metadata"
    rows = [
        encode_coverage(
            plc_east.PACKAGE,
            plc_east.paving_footprint(
                green.site.read(metadata / "plc-east-court.json")
            ),
        ),
        encode_coverage(
            knight_north.PACKAGE,
            knight_north.paving_footprint(
                green.site.read(metadata / "knight-north-plaza.json")
            ),
        ),
        encode_coverage(
            cemetery.PACKAGE,
            cemetery_coverage(green.site.read(metadata / f"{cemetery.PACKAGE}.json")),
        ),
        encode_coverage(
            green.PACKAGE,
            green_coverage(green.site.read(metadata / "southwest-campus-green.json")),
        ),
        encode_coverage(
            education.PACKAGE,
            education_coverage(
                green.site.read(metadata / "kincaid-education-landscape.json")
            ),
        ),
        encode_coverage(
            kendall.PACKAGE,
            kendall_coverage(
                green.site.read(metadata / "kendall-plaza-landscape.json")
            ),
        ),
        encode_coverage(
            annex.PACKAGE,
            annex_coverage(
                green.site.read(metadata / "education-annex-landscape.json")
            ),
        ),
        encode_coverage(
            dropoff.PACKAGE,
            dropoff_coverage(
                green.site.read(metadata / "clinical-dropoff-landscape.json")
            ),
        ),
        encode_coverage(
            east_18th_west.PACKAGE,
            east_18th_west_coverage(
                green.site.read(metadata / "east-18th-west-approach.json"), metadata
            ),
        ),
        frohnmayer_drive_coverage(
            green.site.read(metadata / "frohnmayer-east-drive.json"), metadata
        ),
        encode_coverage(
            rankin_frontage.PACKAGE,
            rankin_frontage_coverage(
                green.site.read(metadata / "rankin-frontage.json"), metadata
            ),
        ),
        encode_coverage(
            cascade_access.PACKAGE,
            cascade_access.route_coverage(
                green.site.read(metadata / "cascade-courtyard-access.json")
            ),
        ),
        encode_coverage(
            cascade_north.PACKAGE,
            cascade_north.route_coverage(
                green.site.read(metadata / "cascade-courtyard-north.json")
            ),
        ),
        encode_coverage(
            onyx_green.PACKAGE,
            onyx_green.route_coverage(
                green.site.read(metadata / "onyx-green-walks.json")
            ),
        ),
        encode_coverage(
            price_courtyard.PACKAGE,
            price_courtyard.route_coverage(
                green.site.read(metadata / "price-courtyard.json")
            ),
        ),
        encode_coverage(
            science_green.PACKAGE,
            science_green.outdoor_footprint(
                green.site.read(metadata / "science-green-sundial.json")
            )[0],
        ),
        encode_coverage(
            oregon.PACKAGE,
            oregon.route_coverage(
                green.site.read(metadata / "oregon-hall-southeast-landscape.json"),
                metadata,
            ),
        ),
        encode_coverage(
            wayfinding.PACKAGE,
            northeast_wayfinding_coverage(
                green.site.read(metadata / "northeast-campus-wayfinding.json")
            ),
        ),
    ]
    args.output.write_bytes((json.dumps(rows, separators=(",", ":")) + "\n").encode())


if __name__ == "__main__":
    main()
