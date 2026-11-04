import { test, expect } from "@playwright/test";
test("clinical roof preserves source positions below roof and building selection", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const response = page.waitForResponse((r) =>
    r.url().endsWith("/clinical-roof-slope.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await response).status()).toBe(200);
  const result = await page.evaluate(async () => {
    const { GLTFLoader } =
        await import("/node_modules/three/examples/jsm/loaders/GLTFLoader.js"),
      { loadPresentation } = await import("/src/presentation.js");
    const cfg = await (await fetch("/scene/presentation.json")).json(),
      spec = await (await fetch("/scene/clinical-roof-slope.json")).json(),
      manifest = await (await fetch("/scene/manifest.json")).json(),
      raw = await new GLTFLoader().loadAsync("/scene/" + cfg.asset_url),
      scene = await loadPresentation(
        "/scene/",
        "presentation.json",
        new Set(manifest.buildings.map((x) => x.id)),
      );
    const a = raw.scene.getObjectByName(spec.building_id).geometry,
      b = scene.root.getObjectByName(spec.building_id).geometry,
      p = a.attributes.position,
      q = b.attributes.position,
      c = a.attributes.color,
      d = b.attributes.color,
      n = a.attributes.normal,
      m = b.attributes.normal;
    let selected = 0,
      errors = 0,
      maxDelta = 0;
    for (let i = 0; i < p.count; i++) {
      const rgb = [c.getX(i), c.getY(i), c.getZ(i)].map((v) =>
          Math.round(v * 255),
        ),
        on =
          p.getY(i) >= spec.minimum_y ||
          rgb.every((v, k) => v === spec.roof_feature_rgb8[k]);
      const dy = on ? spec.slope * (p.getX(i) - spec.origin_x) : 0;
      if (on) selected++;
      if (
        p.getX(i) !== q.getX(i) ||
        p.getZ(i) !== q.getZ(i) ||
        Math.abs(q.getY(i) - p.getY(i) - dy) > 1e-5
      )
        errors++;
      if (!on)
        for (let k = 0; k < 3; k++)
          if (n.array[i * 3 + k] !== m.array[i * 3 + k]) errors++;
      for (let k = 0; k < 3; k++)
        if (
          c.array[i * 3 + k] !== d.array[i * 3 + k] ||
          !Number.isFinite(m.array[i * 3 + k])
        )
          errors++;
      maxDelta = Math.max(maxDelta, Math.abs(q.getY(i) - p.getY(i)));
    }
    return {
      count: p.count,
      selected,
      errors,
      maxDelta,
      indexBefore: a.index.count,
      indexAfter: b.index.count,
    };
  });
  expect(result).toMatchObject({ count: 3968, selected: 2218, errors: 0 });
  expect(result.indexAfter).toBe(result.indexBefore);
  expect(result.maxDelta).toBeLessThanOrEqual(0.9);
  await page
    .getByRole("combobox", { name: "Search buildings" })
    .fill("Clinical Services Building");
  await page
    .getByRole("option", { name: /Clinical Services Building/ })
    .first()
    .click();
  await expect
    .poll(async () =>
      page.evaluate(() => window.__campus.getState().selectedBuilding),
    )
    .toBe("roof-c1ff8b83");
  await page.locator("#settings-open").click();
  let toon = page.getByLabel("Architectural toon", { exact: false });
  await toon.uncheck();
  await toon.check();
  await page.getByRole("slider", { name: "Campus activity density" }).fill("0");
  await page.locator("#settings-close").click();
  await expect
    .poll(async () => page.evaluate(() => window.__campus.getState().drawCalls))
    .toBeLessThan(180);
  expect(errors).toEqual([]);
});
