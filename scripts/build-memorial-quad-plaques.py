# SPDX-License-Identifier: Apache-2.0
"""Build the three mapped Memorial Quadrangle sidewalk plaques."""

import argparse
from importlib import import_module
from pathlib import Path

import numpy as np
from shapely.geometry import box

green = import_module("build-southwest-campus-green")
site = green.site
paving = import_module("build-paving-corridors-l2")
PACKAGE = "memorial-quad-plaques-review"
DETAIL = "memorial-quad-plaques"


def support_triangles(asset, name):
    document, binary = paving.gltf(site.scene / asset)
    positions, indices = paving.source.mesh_arrays(
        document, binary, paving.locate(document, name)
    )
    return positions[indices].astype(float)


def surface_height(triangles, e, n):
    points = triangles[:, :, [0, 2]] * [1, -1]
    origin = points[:, 0]
    a = points[:, 1] - origin
    b = points[:, 2] - origin
    offset = np.array([e, n]) - origin
    det = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    valid = np.abs(det) > 1e-9
    u = np.divide(
        offset[:, 0] * b[:, 1] - offset[:, 1] * b[:, 0],
        det,
        out=np.full(len(det), np.inf),
        where=valid,
    )
    v = np.divide(
        a[:, 0] * offset[:, 1] - a[:, 1] * offset[:, 0],
        det,
        out=np.full(len(det), np.inf),
        where=valid,
    )
    inside = (u >= -1e-5) & (v >= -1e-5) & (u + v <= 1.00001)
    z = triangles[inside, :, 1]
    u, v = u[inside], v[inside]
    return max((1 - u - v) * z[:, 0] + u * z[:, 1] + v * z[:, 2])


def plate(field, row, support):
    e, n = row["position_enu_m"]
    width, depth = row["size_enu_m"]
    outline = box(-width / 2, -depth / 2, width / 2, depth / 2)
    bed = outline.buffer(0.023, join_style="mitre")
    error = []
    lift = row["support_lift_m"]
    for x, y in [(0, 0), *bed.exterior.coords[:-1]]:
        x, y = x + e, y + n
        actual = surface_height(support, x, y)
        error.append(abs(actual - site.ground_height(field, x, y) - lift))
    assert max(error) < 0.003, (row["id"], error)

    parts = []
    bronze = (109, 98, 76) if row["id"].startswith("gilbert") else (117, 92, 62)
    site.solid(parts, bed, -0.008, 0.002, (105, 110, 105))
    site.solid(parts, outline, 0.001, 0.006, bronze)
    bezel = outline.buffer(-0.009)
    site.solid(parts, bezel.difference(bezel.buffer(-0.012)), 0.005, 0.009, (151, 133, 101))
    margin = 0.027
    count = len(row["caption_lines"])
    row_height = (depth - 2 * margin) / (count + 1)
    for index, line in enumerate(row["caption_lines"]):
        glyph = min(row_height * 0.46, (width - 2 * margin) / (1.23 * len(line)))
        baseline = depth / 2 - margin - (index + 1) * row_height
        site.text_strokes(
            parts,
            line,
            lambda x, y: (x, baseline + y, 0.0082),
            glyph,
            glyph * 1.34,
            (178, 158, 123),
        )
    for mesh in parts:
        for vertex in mesh.vertices:
            vertex[0] += e
            vertex[2] -= n
            vertex[1] += site.ground_height(field, vertex[0], -vertex[2]) + lift
    return parts, round(max(error), 6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()
    spec = site.read(site.root / "data/metadata/memorial-quad-plaques.json")
    _, field, _ = green.east.pinned_site(site.scene, spec)
    quad_path = "paving-corridors-l2/surfaces.json"
    assert site.pin(site.scene / quad_path) == spec["pins"]["paving_quad"]
    quad = site.read(site.scene / quad_path)
    street = site.read(site.scene / "east-thirteenth-west-gateway-review/site.json")
    for descriptor in (quad, street):
        assert site.pin(site.scene / descriptor["url"]) == descriptor["sha256"]
    north = support_triangles(street["url"], "east-thirteenth-west-paving")
    east = support_triangles(quad["url"], "quad-landscape-paving")
    details, registrations = [], []
    for row in spec["plaques"]:
        surface = north if row["id"].startswith("gilbert") else east
        parts, error = plate(field, row, surface)
        details.extend(parts)
        registrations.append({"id": row["id"], "support_max_error_m": error})
    args.stage.mkdir(parents=True, exist_ok=True)
    asset, descriptor = (args.stage / file for file in ("site.glb", "site.json"))
    faces = site.export(
        asset, (DETAIL, details, "landscape-detail"), surface_layer=DETAIL
    )
    pins = spec["pins"]
    site.fairmount.write_json(
        descriptor,
        {
            "source_presentation_sha256": pins["presentation"],
            "source_base_model_sha256": pins["model"],
            "source_heightfield_sha256": pins["heightfield"],
            "prerequisite_site_sha256": pins["sites"]["east-thirteenth-west-gateway-review"],
            "url": f"{PACKAGE}/site.glb",
            "ground_node": DETAIL,
            "sha256": site.pin(asset),
            "buildings": [],
        },
        compact=True,
    )
    audit = {
        "registrations": registrations,
        "faces": faces,
        "asset_sha256": site.pin(asset),
        "descriptor_sha256": site.pin(descriptor),
    }
    site.fairmount.write_json(args.stage / "audit.json", audit)
    print(audit)


if __name__ == "__main__":
    main()
