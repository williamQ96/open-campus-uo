import { test, expect } from "@playwright/test";
test("keyboard-focused person remains paused when pointer leaves its label", async ({
  page,
}) => {
  await page.addInitScript(() =>
    sessionStorage.setItem(
      "explorer:outdoor-return:v1",
      JSON.stringify({
        version: 1,
        buildingId: "roof-0ca67b60",
        player: [-42, 0.2, -41],
        view: "first",
        yaw: 0,
        pitch: 0.13,
        followDistance: 7.5,
        density: 0,
        motionLevel: 0,
      }),
    ),
  );
  await page.goto("/?return=1");
  await page.waitForFunction(
    () => window.__campus?.getState().ready && __campus.fixedNpcInfo(),
  );
  const label = page.getByRole("button", { name: "View Dan Carrere profile" });
  await expect(label).toBeVisible();
  await label.focus();
  const box = await label.boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.move(10, 10);
  await expect(label).toBeFocused();
  expect(await page.evaluate(() => __campus.fixedNpcInfo().hovered)).toBe(true);
  const before = await page.evaluate(() => __campus.fixedNpcInfo().position3);
  await page.waitForTimeout(350);
  expect(await page.evaluate(() => __campus.fixedNpcInfo().position3)).toEqual(
    before,
  );
  // Conversely, blur must not erase a pointer that still rests on the label.
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.locator("#viewport").focus();
  expect(await page.evaluate(() => __campus.fixedNpcInfo().hovered)).toBe(true);
  await page.mouse.move(10, 10);
  expect(await page.evaluate(() => __campus.fixedNpcInfo().hovered)).toBe(
    false,
  );
  await label.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog", { name: "Dan Carrere" })).toBeVisible();
});

test("hidden and disposed person clears hover without stealing another input focus", async ({
  page,
}) => {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  const result = await page.evaluate(async () => {
    const THREE = await import("/node_modules/three/build/three.module.js");
    const { createFixedNpc } = await import("/src/fixed-npc.js");
    const viewport = document.createElement("div");
    viewport.tabIndex = 0;
    viewport.style.cssText = "position:fixed;inset:0;width:500px;height:500px";
    document.body.append(viewport);
    const input = document.createElement("input");
    viewport.append(input);
    const scene = new THREE.Scene(),
      camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
    camera.position.set(0, 2, 10);
    camera.lookAt(0, 1, 0);
    camera.updateMatrixWorld(true);
    const material = new THREE.MeshStandardMaterial({ emissive: 0x000000 });
    const root = new THREE.Group();
    root.add(new THREE.Mesh(new THREE.BoxGeometry(), material));
    let disposed = false;
    const npc = createFixedNpc({
      scene,
      viewport,
      camera,
      studentFactory: () => ({
        root,
        animate() {},
        dispose() {
          disposed = true;
        },
      }),
      ground: () => 0,
      config: {
        name: "Test person",
        role: "Test",
        path: [[0, 0]],
        speed: 0,
        pauseSeconds: 0,
      },
    });
    const player = new THREE.Vector3(0, 0, 3);
    npc.update(0, player);
    const label = viewport.querySelector(".fixed-person-label");
    label.focus();
    npc.hover(true);
    camera.lookAt(0, 2, 30);
    camera.updateMatrixWorld(true);
    npc.update(0, player);
    const hidden = {
      hovered: npc.state().hovered,
      hidden: label.hidden,
      safeFocus: document.activeElement === viewport,
      emissive: material.emissive.toArray(),
    };
    input.focus();
    npc.hover(true);
    npc.update(0, player);
    const inputKept = document.activeElement === input;
    npc.hover(true);
    npc.dispose();
    const after = {
      hovered: npc.state().hovered,
      inputKept: document.activeElement === input,
      disposed,
      emissive: material.emissive.toArray(),
    };
    viewport.remove();
    root.children[0].geometry.dispose();
    material.dispose();
    return { hidden, inputKept, after };
  });
  expect(result.hidden).toEqual({
    hovered: false,
    hidden: true,
    safeFocus: true,
    emissive: [0, 0, 0],
  });
  expect(result.inputKept).toBe(true);
  expect(result.after).toEqual({
    hovered: false,
    inputKept: true,
    disposed: true,
    emissive: [0, 0, 0],
  });
});
