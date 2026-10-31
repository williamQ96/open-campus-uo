// SPDX-License-Identifier: Apache-2.0
// Local visual evidence and diagnostic timings; not a device performance claim.
import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
const out = fileURLToPath(new URL("../../../artifacts/visual-pilot/", import.meta.url));
await mkdir(out, {recursive:true});
const browser = await chromium.launch({channel:"chrome",args:["--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
const page = await browser.newPage({viewport:{width:1440,height:960}});
const errors=[]; page.on("pageerror",e=>errors.push(e.message));
const start=Date.now();
await page.goto(process.argv[2] || "http://127.0.0.1:5173/");
await page.waitForFunction(()=>window.__campus?.getState().ready);
const readyMs=Date.now()-start;
const painted = () => page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
await painted();
await page.screenshot({path:out+"/overview.png"});
const measurements=[];
for (const mode of ["Digit1","Digit2","Digit3"]) {
  await page.keyboard.press(mode);
  const timing=await page.evaluate(async()=>{
    const frames=[];let previous;
    await new Promise(resolve=>{
      function sample(now) {if(previous)frames.push(now-previous);previous=now;if(frames.length<60)requestAnimationFrame(sample);else resolve();}
      requestAnimationFrame(sample);
    });
    frames.sort((a,b)=>a-b);
    return {medianMs:frames[30],p95Ms:frames[57],...window.__campus.getState()};
  });
  measurements.push(timing);
}
for (const [query,name] of [["Knight Library","knight"],["Johnson Hall","johnson"],["EMU","emu"]]) {
  const search=page.getByRole("combobox",{name:"Search buildings"});
  await search.fill(query);await search.press("ArrowDown");await search.press("Enter");
  await page.waitForFunction(()=>!window.__campus.getState().cameraTransition);
  await painted();
  await page.screenshot({path:out+"/"+name+".png"});
}
await page.getByRole("button",{name:/Follow/}).click();
await page.waitForFunction(()=>window.__campus.getState().view==="third");await painted();await page.screenshot({path:out+"/follow.png"});
await page.getByRole("button",{name:/First person/}).click();
await page.waitForFunction(()=>window.__campus.getState().view==="first");await painted();await page.screenshot({path:out+"/first-person.png"});
const result={url:page.url(),date:new Date().toISOString(),userAgent:await page.evaluate(()=>navigator.userAgent),renderer:"Chrome / ANGLE SwiftShader software rendering",viewport:{width:1440,height:960},readyMs,measurements,errors};
await writeFile(out+"/diagnostics.json",JSON.stringify(result,null,2));
console.log(JSON.stringify({readyMs,measurements:measurements.map(({view,medianMs,p95Ms,drawCalls,triangles})=>({view,medianMs,p95Ms,drawCalls,triangles})),errors}));
await browser.close();
