// SPDX-License-Identifier: Apache-2.0
// Export the nine existing benches as individually pivoted groups, with original supports.
import { chromium } from "@playwright/test";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
const [output] = process.argv.slice(2);
if (
  process.argv.length !== 3 ||
  !output ||
  path.extname(output).toLowerCase() !== ".glb" ||
  fs.existsSync(output)
)
  throw Error("Supply one new GLB output; no overwrite.");
const sha = (b) => createHash("sha256").update(b).digest("hex");
const dir = "public/scene/",
  configPath = dir + "presentation.json",
  cfgBytes = fs.readFileSync(configPath),
  cfg = JSON.parse(cfgBytes);
const files = [
  "pilot-bench-detail.json",
  "pilot-bench-back-suppression.json",
  "pilot-bench-seat-suppression.json",
];
const buffers = files.map((f) => fs.readFileSync(dir + f)),
  specs = buffers.map((b) => JSON.parse(b));
const pin = (list, n) => list?.find((e) => e.url === n)?.sha256;
if (
  sha(buffers[0]) !== pin(cfg.exterior_details, files[0]) ||
  sha(buffers[1]) !== cfg.furniture_patch_sha256 ||
  sha(buffers[2]) !== pin(cfg.additional_environment_patches, files[2]) ||
  specs.some((s) => s.base_asset_sha256 !== cfg.asset_sha256)
)
  throw Error("Bench sources or dependencies changed.");
const sourcePath = dir + cfg.asset_url,
  baseBytes = fs.readFileSync(sourcePath),
  generator = "src/exterior-detail.js",
  generatorBytes = fs.readFileSync(generator);
if (
  sha(baseBytes) !== cfg.asset_sha256 ||
  specs[0].objects.length !== 180 ||
  specs[0].merge_target !== "furniture_1"
)
  throw Error("Bench base contract changed.");
const browser = await chromium.launch({
  channel: "chrome",
  headless: true,
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
try {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:5173/");
  const result = await page.evaluate(
    async ({ spec, digests, baseSha, genSha }) => {
      const THREE = await import("/node_modules/three/build/three.module.js");
      const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js");
      const { GLTFExporter } =
        await import("/node_modules/three/examples/jsm/exporters/GLTFExporter.js");
      const { createExteriorDetail } = await import("/src/exterior-detail.js");
      const base = await new GLTFLoader().loadAsync(
        "/scene/campus-expanded.glb",
      );
      base.scene.updateMatrixWorld(true);
      const wood = base.scene.getObjectByName("furniture_1"),
        metal = base.scene.getObjectByName("furniture_2");
      if (
        !wood?.isMesh ||
        !metal?.isMesh ||
        wood.material.color.getHexString() !== "77634f" ||
        metal.material.color.getHexString() !== "3f514b" ||
        metal.geometry.attributes.position.count !== 960 ||
        !metal.geometry.index ||
        !metal.matrixWorld.equals(new THREE.Matrix4())
      )
        throw Error("Original furniture layout or material changed.");
      const g = metal.geometry,
        pos = g.attributes.position,
        norm = g.attributes.normal,
        idx = g.index;
      if (!norm || idx.count < 648) throw Error("Support topology missing.");
      for (let i = 0; i < 9; i++) {
        const anchor = spec.objects[i * 17 + 11].position;
        for (let side = 0; side < 2; side++) {
          const n = i * 2 + side,
            lo = [Infinity, Infinity, Infinity],
            hi = [-Infinity, -Infinity, -Infinity];
          for (let j = 0; j < 24; j++) {
            const k = n * 24 + j,
              v = [pos.getX(k), pos.getY(k), pos.getZ(k)];
            for (let a = 0; a < 3; a++) {
              lo[a] = Math.min(lo[a], v[a]);
              hi[a] = Math.max(hi[a], v[a]);
            }
          }
          const expected = [
              anchor[0] + (side ? 1.1 : -1.1),
              anchor[1] - 0.44,
              anchor[2] + 0.4,
            ],
            size = [0.12, 0.6, 0.7];
          for (let a = 0; a < 3; a++)
            if (
              Math.abs((lo[a] + hi[a]) / 2 - expected[a]) > 0.002 ||
              Math.abs(hi[a] - lo[a] - size[a]) > 0.002
            )
              throw Error(`Support ${n} no longer aligns with bench ${i}`);
          for (let j = 0; j < 36; j++) {
            const k = idx.getX(n * 36 + j);
            if (k < n * 24 || k >= (n + 1) * 24)
              throw Error("Support topology is not isolated");
          }
        }
      }
      const group = new THREE.Group();
      group.name = "pilot-benches-nine-individual";
      const originals = [];
      for (let i = 0; i < 9; i++) {
        const anchor = spec.objects[i * 17 + 11].position;
        const pivot = new THREE.Vector3(
          Math.round(anchor[0]),
          Math.round(anchor[1]),
          Math.round(anchor[2] + 0.4),
        );
        const support = new THREE.BufferGeometry();
        for (const name of ["position", "normal"]) {
          const a = g.attributes[name];
          support.setAttribute(
            name,
            new THREE.BufferAttribute(
              a.array.slice(i * 48 * 3, (i + 1) * 48 * 3),
              3,
            ),
          );
        }
        support.setIndex(
          Array.from(idx.array.slice(i * 72, (i + 1) * 72), (n) => n - i * 48),
        );
        const localSpec = {
          ...spec,
          objects: [
            ...spec.objects.slice(i * 17, i * 17 + 17),
            ...spec.objects.slice(153 + i * 3, 156 + i * 3),
          ],
        };
        const detail = createExteriorDetail(localSpec, baseSha, new Set());
        if (detail.children.length !== 1 || !detail.children[0].isMesh)
          throw Error("Unexpected bench overlay");
        const boards = detail.children[0];
        boards.material = wood.material.clone();
        boards.geometry.deleteAttribute("color");
        const leg = new THREE.Mesh(support, metal.material.clone());
        leg.name = `bench-${i + 1}-supports`;
        boards.name = `bench-${i + 1}-wood`;
        const bench = new THREE.Group();
        bench.name = `bench-${i + 1}`;
        bench.position.copy(pivot);
        for (const mesh of [leg, boards]) {
          const world = mesh.geometry.attributes.position.array.slice();
          mesh.geometry.translate(-pivot.x, -pivot.y, -pivot.z);
          originals.push({ mesh, pivot, world });
          bench.add(mesh);
        }
        group.add(bench);
      }
      group.userData = {
        base_asset_sha256: baseSha,
        overlay_sha256: digests[0],
        back_suppression_sha256: digests[1],
        seat_suppression_sha256: digests[2],
        generator_sha256: genSha,
        scope: "nine-pilot-benches-individual",
      };
      const raw = await new GLTFExporter().parseAsync(group, {
        binary: true,
        copyright:
          "Copyright 2026 Zhongyi William Qiu and Open Campus contributors; original model output CC BY 4.0.",
      });
      const again = await new GLTFLoader().parseAsync(raw, "");
      again.scene.updateMatrixWorld(true);
      const stats = {};
      for (const { mesh, pivot, world } of originals) {
        const copy = again.scene.getObjectByName(mesh.name);
        if (!copy?.isMesh || copy.parent.name !== mesh.parent.name)
          throw Error("Missing or incorrectly grouped mesh");
        for (const key of ["position", "normal"]) {
          const a = mesh.geometry.attributes[key],
            b = copy.geometry.attributes[key];
          if (!a || !b || a.count !== b.count)
            throw Error("Attribute mismatch");
          let max = 0;
          for (let j = 0; j < a.array.length; j++)
            max = Math.max(max, Math.abs(a.array[j] - b.array[j]));
          if (max > 1e-6) throw Error("Attribute precision mismatch");
          stats[`${mesh.name}-${key}`] = { count: a.count, max };
        }
        const pos = copy.geometry.attributes.position,
          v = new THREE.Vector3();
        let worldMax = 0;
        for (let j = 0; j < pos.count; j++) {
          v.fromBufferAttribute(pos, j).applyMatrix4(copy.matrixWorld);
          for (let k = 0; k < 3; k++)
            worldMax = Math.max(
              worldMax,
              Math.abs(v.getComponent(k) - world[j * 3 + k]),
            );
        }
        if (worldMax > 0.0001)
          throw Error(`World position mismatch ${mesh.name}: ${worldMax}`);
        const a = mesh.geometry.index,
          b = copy.geometry.index;
        if (
          Boolean(a) !== Boolean(b) ||
          (a &&
            (a.count !== b.count || a.array.some((v, i) => v !== b.array[i])))
        )
          throw Error("Index mismatch");
        if (
          copy.material.color.getHexString() !==
          mesh.material.color.getHexString()
        )
          throw Error("Material mismatch");
        stats[`${mesh.name}-world-max`] = worldMax;
      }
      return { bytes: Array.from(new Uint8Array(raw)), stats };
    },
    {
      spec: specs[0],
      digests: buffers.map(sha),
      baseSha: cfg.asset_sha256,
      genSha: sha(generatorBytes),
    },
  );
  if (
    sha(fs.readFileSync(configPath)) !== sha(cfgBytes) ||
    sha(fs.readFileSync(sourcePath)) !== sha(baseBytes) ||
    sha(fs.readFileSync(generator)) !== sha(generatorBytes) ||
    files.some((f, i) => sha(fs.readFileSync(dir + f)) !== sha(buffers[i]))
  )
    throw Error("Inputs changed during export; no output written.");
  const bytes = Buffer.from(result.bytes);
  fs.writeFileSync(output, bytes, { flag: "wx" });
  console.log(
    JSON.stringify({
      output,
      sha256: sha(bytes),
      bytes: bytes.length,
      stats: result.stats,
    }),
  );
} finally {
  await browser.close();
}
