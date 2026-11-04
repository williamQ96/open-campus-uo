import { test, expect } from "@playwright/test";
test("source-pinned fern grouping loads in the full campus", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const p = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-fern-suppression.json"),
  );
  const d = page.waitForResponse((r) =>
    r.url().endsWith("/pilot-fern-detail.json"),
  );
  await page.goto("/");
  await page.waitForFunction(() => window.__campus?.getState().ready);
  expect((await p).status()).toBe(200);
  expect((await d).status()).toBe(200);
  expect(errors).toEqual([]);
});
