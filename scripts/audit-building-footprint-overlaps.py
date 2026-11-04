"""Screen named building footprints against other manifest footprints (2D only)."""
import argparse
import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon


def polygon(record):
    result = Polygon(record["footprint_enu_m"])
    return result if result.is_valid else result.buffer(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("apps/web-preview/public/scene/manifest.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.manifest.read_bytes()
    buildings = json.loads(raw)["buildings"]
    shapes = [(b, polygon(b)) for b in buildings if len(b.get("footprint_enu_m", [])) >= 3]
    findings = []
    for building, shape in shapes:
        if not building.get("name") or shape.area == 0:
            continue
        overlaps = []
        for other, other_shape in shapes:
            if other is building or not shape.intersects(other_shape):
                continue
            area = shape.intersection(other_shape).area
            if area >= 1:
                overlaps.append({"id": other["id"], "name": other.get("name"), "area_m2": round(area, 2), "fraction_of_subject": round(area / shape.area, 4)})
        if overlaps:
            findings.append({"id": building["id"], "name": building["name"], "name_match": building.get("name_match"), "status": building.get("status"), "footprint_area_m2": round(shape.area, 2), "overlaps": sorted(overlaps, key=lambda x: x["id"])})
    result = {"manifest": args.manifest.as_posix(), "manifest_sha256": hashlib.sha256(raw).hexdigest(), "screen": "2D footprint intersection >= 1 m2; not a building identity, mesh, clearance, height or current-conditions verification", "named_buildings_screened": sum(bool(b.get("name")) for b, _ in shapes), "findings": sorted(findings, key=lambda x: x["id"])}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Screened {result['named_buildings_screened']} named candidates; {len(findings)} have potential overlaps.")


if __name__ == "__main__":
    main()
