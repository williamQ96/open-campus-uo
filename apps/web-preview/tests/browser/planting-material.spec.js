import { test, expect } from "@playwright/test";
test("source-shared planting stays green and canopy retains tone in both render modes", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const result = await page.evaluate(async () => {
    const { loadPresentation } = await import("/src/presentation.js");
    const manifest = await (await fetch("/scene/manifest.json")).json();
    const pres = await loadPresentation(
      "/scene/",
      "presentation.json",
      new Set(manifest.buildings.map((b) => b.id)),
    );
    const planting = pres.root.getObjectByName("planting"),
      canopy = pres.root.getObjectByName("vegetation_2");
    const read = () => ({
      plantVertexColors: planting.material.vertexColors,
      plantHasColors: !!planting.geometry.attributes.color,
      plantColorCount: planting.geometry.attributes.color?.count,
      plantColor: planting.material.color.getHexString(),
      plantCount: planting.geometry.attributes.position.count,
      canopyVertexColors: canopy.material.vertexColors,
      canopyColorCount: canopy.geometry.attributes.color.count,
      distinct: planting.material !== canopy.material,
    });
    const toon = read();
    pres.setToon(false);
    const pbr = read();
    return { toon, pbr };
  });
  for (const state of [result.toon, result.pbr]) {
    expect(state.plantVertexColors).toBe(true);
    expect(state.plantHasColors).toBe(true);
    expect(state.plantColorCount).toBe(8640);
    expect(state.plantColor).toBe("658b54");
    expect(state.plantCount).toBe(8640);
    expect(state.canopyVertexColors && state.distinct).toBe(true);
    expect(state.canopyColorCount).toBe(66528);
  }
  expect(errors).toEqual([]);
});
