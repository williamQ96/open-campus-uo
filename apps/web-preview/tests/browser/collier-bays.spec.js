import { readFileSync } from "node:fs";
import { splitExteriorCapture } from "./split-exterior-capture.js";
const old = readFileSync(
  new URL(
    "../../../../assets/exterior-refinement/collier-before-bays-2026-11-04.json",
    import.meta.url,
  ),
);
splitExteriorCapture({
  title:
    "Collier exterior retains campus selection, entrances, collision and draw counts",
  old,
  detail: "collier-house-detail.json",
  hash: "5ddf7032c90127d7b14dd58a89f6b622e586da7aa15c0d746941cb0cbfd27820",
  name: "Collier House",
  namePattern: /Collier House/,
  buildingId: "roof-e5accf83",
  pitch: -0.28,
  imagePrefix: "collier-bays",
  timeout: 120000,
  reducedMotion: true,
  checkConsole: true,
  views: [
    ["east", -305, 58.5, Math.PI / 2],
    ["north", -345, 22, Math.PI],
  ],
});
