import { test, expect } from "@playwright/test";
const state = (page) => page.evaluate(() => __campus.getState());
async function ready(page) {
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
}

test("sound defaults on, master mute works, and real walking drives footsteps and optional first-person sway", async ({
  page,
}) => {
  await ready(page);
  expect((await state(page)).audio.enabled).toBe(true);
  await page.getByRole("button", { name: "Mute sound", exact: true }).click();
  expect((await state(page)).audio).toMatchObject({
    enabled: false,
    musicPlaying: false,
  });
  await page.getByRole("button", { name: "Enable sound", exact: true }).click();
  await expect
    .poll(async () => (await state(page)).audio.musicPlaying)
    .toBe(true);
  await page.evaluate(() => __campus.setView("first"));
  await page.locator("#viewport").focus();
  await page.keyboard.down("KeyW");
  await expect
    .poll(async () => (await state(page)).walkMotion.walking)
    .toBe(true);
  await expect
    .poll(async () => Math.abs((await state(page)).walkMotion.bobY))
    .toBeGreaterThan(0.0001);
  await expect
    .poll(async () => (await state(page)).audio.stepsPlayed)
    .toBeGreaterThan(0);
  const synchronized = await state(page);
  expect(synchronized.heroGait.phase).toBe(synchronized.walkMotion.phase);
  expect(synchronized.heroGait.phaseOffset).toBe(0.15625);
  expect(Math.abs(synchronized.walkMotion.bobY)).toBeLessThanOrEqual(0.003);
  expect(synchronized.walkMotion.roll).toBe(0);
  await page.keyboard.up("KeyW");
  await expect
    .poll(async () => Math.abs((await state(page)).walkMotion.bobY))
    .toBeLessThan(0.0001);
  const stopped = (await state(page)).audio.stepsPlayed;
  await page.waitForTimeout(200);
  expect((await state(page)).audio.stepsPlayed).toBe(stopped);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.keyboard.down("KeyS");
  await expect
    .poll(async () => (await state(page)).audio.stepsPlayed)
    .toBeGreaterThan(stopped);
  expect((await state(page)).walkMotion).toMatchObject({
    bobX: 0,
    bobY: 0,
    roll: 0,
  });
  await page.keyboard.up("KeyS");
  await page.evaluate(() => __campus.setView("third"));
  const thirdStart = (await state(page)).audio.stepsPlayed;
  await page.keyboard.down("KeyW");
  await expect
    .poll(async () => (await state(page)).audio.stepsPlayed)
    .toBeGreaterThan(thirdStart);
  await page.keyboard.up("KeyW");
  await page.getByRole("button", { name: "Mute sound", exact: true }).click();
  const muted = (await state(page)).audio.stepsPlayed;
  await page.locator("#viewport").focus();
  await page.keyboard.down("KeyS");
  await page.waitForTimeout(700);
  await page.keyboard.up("KeyS");
  expect((await state(page)).audio.stepsPlayed).toBe(muted);
});

test("feedback retains drafts, requires content, leaves coordinates optional, and opens a downstream GitHub confirmation", async ({
  page,
}) => {
  await page.addInitScript(() => {
    window.open = (url) => {
      window.lastIssueDraft = url;
      return null;
    };
  });
  await ready(page);
  await page.evaluate(() => __campus.setView("first"));
  await page.getByRole("button", { name: "Feedback", exact: true }).click();
  await expect(page.locator("#feedback-dialog")).toBeVisible();
  const before = (await state(page)).player;
  await page
    .getByRole("button", { name: "Continue on GitHub ↗", exact: true })
    .click();
  expect(await page.evaluate(() => window.lastIssueDraft)).toBeUndefined();
  await page
    .locator("#feedback-content")
    .fill("The entrance could use a ramp & clearer paths.");
  await page
    .getByRole("button", { name: "Continue on GitHub ↗", exact: true })
    .click();
  const url = new URL(await page.evaluate(() => window.lastIssueDraft));
  expect(url.pathname).toBe("/williamQ96/open-campus-uo/issues/new");
  expect(url.searchParams.get("title")).toMatch(
    /^Feedback #\d+ · iteration 14$/,
  );
  expect(url.searchParams.get("body")).toContain("entrance could use a ramp");
  expect(url.searchParams.get("body")).not.toContain("Coordinates");
  await expect(page.locator("#feedback-status")).toContainText(
    "confirm issue creation",
  );
  await page.locator("#feedback-position").click();
  await expect(page.locator("#feedback-coordinates")).not.toBeEmpty();
  await page.locator("#feedback-title").fill("Entrance correction");
  await page
    .getByRole("button", { name: "Continue on GitHub ↗", exact: true })
    .click();
  const located = new URL(await page.evaluate(() => window.lastIssueDraft));
  expect(located.searchParams.get("title")).toBe("Entrance correction");
  expect(located.searchParams.get("body")).toContain(
    "Coordinates (provided by reporter)",
  );
  expect((await state(page)).player).toEqual(before);
  await page.locator("#feedback-close").click();
  await page.getByRole("button", { name: "Feedback", exact: true }).click();
  await expect(page.locator("#feedback-content")).toHaveValue(
    "The entrance could use a ramp & clearer paths.",
  );
});

test("compact header and feedback fit a narrow phone", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 640 });
  await ready(page);
  for (const id of [
    "directions-open",
    "sound-toggle",
    "feedback-open",
    "settings-open",
  ]) {
    const box = await page.locator("#" + id).boundingBox();
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.x).toBeGreaterThanOrEqual(0);
    expect(box.x + box.width).toBeLessThanOrEqual(320);
  }
  await page.getByRole("button", { name: "Feedback", exact: true }).click();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(
    320,
  );
  await expect(page.locator("#feedback-content")).toBeVisible();
});
