import { readFileSync } from "node:fs";
import { splitExteriorCapture } from "./split-exterior-capture.js";
const old = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/gerlinger-before-portico-2026-11-04.json",
    import.meta.url,
  ),
);
splitExteriorCapture({
  title:
    "Gerlinger portico preserves campus selection, entrances and collision",
  old,
  detail: "gerlinger-east-detail.json",
  hash: "86b2ef379efde7ae1d1c0f930a92ce8fc550b8fcdfa2014ff603b59360f78255",
  name: "Gerlinger Hall",
  namePattern: /Gerlinger Hall/,
  buildingId: "roof-9ac93ab7",
  pitch: -0.25,
  imagePrefix: "gerlinger-portico",
  timeout: 90000,
  checkCamera: true,
  views: [
    ["front", -338, 210, Math.PI / 2],
    ["oblique", -342, 195, 2.3],
    ["south", -370, 240, 0],
  ],
});
