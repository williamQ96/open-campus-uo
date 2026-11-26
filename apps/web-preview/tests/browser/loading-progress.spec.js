import { test, expect } from "@playwright/test";

test("the campus loading bar advances on a phone and clears when the viewer renders", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  let releaseManifest;
  const manifestReady = new Promise((resolve) => {
    releaseManifest = resolve;
  });
  let releaseActivity;
  const activityReady = new Promise((resolve) => {
    releaseActivity = resolve;
  });
  await page.route("**/scene/manifest.json", async (route) => {
    await manifestReady;
    await route.continue();
  });
  await page.route("**/scene/activity.json", async (route) => {
    await activityReady;
    await route.continue();
  });
  await page.goto("/", { waitUntil: "commit" });
  const progress = page.getByRole("progressbar", { name: /loading/i });
  try {
    await expect(progress).toBeVisible();
    await expect(progress).toHaveAttribute("value", "6");
    releaseManifest();
    await expect(progress).toHaveAttribute("value", "85", { timeout: 45000 });
  } finally {
    releaseManifest();
    releaseActivity();
  }
  await expect(progress).toBeHidden();
  await expect(page.locator("#loading-progress")).toHaveAttribute(
    "value",
    "100",
  );
  await expect(page.locator("#viewport canvas")).toBeVisible();
});

test("a failed campus startup replaces the progress bar with the retry panel", async ({
  page,
}) => {
  await page.route("**/scene/manifest.json", (route) =>
    route.fulfill({ status: 503 }),
  );
  await page.goto("/", { waitUntil: "commit" });
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("progressbar")).toBeHidden();
  await expect(page.getByRole("button", { name: "Try again" })).toBeVisible();
});
