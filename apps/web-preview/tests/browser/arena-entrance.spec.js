import { test, expect } from "@playwright/test";
test("arena placeholder entrance position and walkability stay unchanged", async ({
  browser,
}) => {
  const entries = [];
  for (const before of [true, false]) {
    const page = await browser.newPage();
    if (before)
      await page.route("**/scene/presentation.json", async (route) => {
        const response = await route.fetch(),
          data = await response.json();
        data.exterior_details = data.exterior_details.filter(
          (e) => e.url !== "arena-north-detail.json",
        );
        await route.fulfill({ response, json: data });
      });
    await page.goto("/");
    await page.waitForFunction(() => window.__campus?.getState().ready);
    entries.push(
      await page.evaluate(() =>
        __campus.entranceInfo().find((e) => e.id === "context-b0074"),
      ),
    );
    await page.close();
  }
  expect(entries[0].walkable).toBe(true);
  expect(entries[1]).toEqual(entries[0]);
});
