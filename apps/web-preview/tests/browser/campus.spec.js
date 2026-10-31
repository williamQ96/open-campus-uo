import {test,expect} from '@playwright/test';

test('real GLB loads, matches geographic heights, and supports walking and all views',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');await page.waitForFunction(()=>window.__campus?.getState().ready);
  await expect(page.locator('#error')).toBeHidden();
  const state=()=>page.evaluate(()=>window.__campus.getState());
  expect((await state()).buildings).toBeGreaterThan(0);
  expect((await state()).blocked).toBe(false);
  for(const [x,z] of [[0,0],[50.3,-60.7],[-80.6,70.4]]){
    const heights=await page.evaluate(([x,z])=>window.__campus.terrainCheck(x,z),[x,z]);
    expect(heights.mesh).toBeDefined();expect(Math.abs(heights.mesh-heights.sampled)).toBeLessThan(.001);
  }
  await page.screenshot({path:'../../artifacts/overview.png'});
  await page.getByRole('button',{name:/跟随/}).click();
  expect((await state()).view).toBe('third');
  const before=(await state()).player;
  await page.keyboard.down('KeyW');
  await expect.poll(async()=>{const after=(await state()).player;return Math.hypot(after[0]-before[0],after[2]-before[2]);}).toBeGreaterThan(.5);
  await page.keyboard.up('KeyW');
  let current=await state();expect(Math.abs(current.player[1]-current.ground)).toBeLessThan(.01);expect(current.blocked).toBe(false);
  await page.screenshot({path:'../../artifacts/third-person.png'});
  await page.keyboard.press('Digit2');expect((await state()).view).toBe('first');
  await page.mouse.move(750,500);await page.mouse.down();await page.mouse.move(850,550,{steps:5});await page.mouse.up();
  await page.screenshot({path:'../../artifacts/first-person.png'});
  await page.keyboard.press('KeyV');expect((await state()).view).toBe('aerial');
  await page.getByRole('button',{name:/线框/}).click();await expect(page.locator('#wireframe')).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:/数据来源/}).click();await expect(page.locator('#source-details')).toBeVisible();
  await expect(page.locator('#source-details')).toContainText('2008-08-31');
  await page.getByRole('button',{name:/回到起点/}).click();
  expect((await state()).player[0]).toBeCloseTo(0,2);expect((await state()).player[2]).toBeCloseTo(0,2);
  expect(errors).toEqual([]);
});

test('small viewport keeps camera controls reachable and clears movement on focus loss',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('/');await page.waitForFunction(()=>window.__campus?.getState().ready);
  await expect(page.getByRole('button',{name:/跟随/})).toBeInViewport();
  await expect(page.getByRole('button',{name:/第一人称/})).toBeInViewport();
  await page.screenshot({path:'../../artifacts/mobile.png'});
  await page.getByRole('button',{name:/第一人称/}).click();
  await page.keyboard.down('KeyW');
  await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
  const before=await page.evaluate(()=>window.__campus.getState().player);
  await page.waitForTimeout(600);
  expect(await page.evaluate(()=>window.__campus.getState().player)).toEqual(before);
  await page.keyboard.up('KeyW');
});
