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
knight_north = import_module("build-knight-north-plaza")
plc_east = import_module("build-plc-east-court")
dropoff = import_module("build-clinical-dropoff-landscape")
east_18th_west = import_module("build-east-18th-west-approach")
rankin_frontage = import_module("build-rankin-frontage")
wayfinding = import_module("build-northeast-campus-wayfinding")
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
        encode_coverage(
            rankin_frontage.PACKAGE,
            rankin_frontage_coverage(
                green.site.read(metadata / "rankin-frontage.json"), metadata
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
