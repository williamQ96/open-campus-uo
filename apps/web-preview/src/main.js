import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { createCharacter } from "./character.js";
import { sampleGround, isBlocked, movePlayer } from "./world.js";
import "@fontsource-variable/dm-sans";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import "./style.css";

const $ = (s) => document.querySelector(s);
const viewport = $("#viewport");
const viewNames = ["third", "first", "aerial"];
const keys = new Set();
let view = "aerial",
  yaw = Math.PI * 0.14,
  pitch = 0.17,
  drag = null,
  manifest,
  field,
  half,
  model,
  buildings = [],
  terrainMesh;
let elapsed = 0,
  moving = false,
  lastTime = 0,
  frames = 0,
  fps = 0,
  lastFps = 0;
const player = new THREE.Vector3();
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe8e9e3);
scene.fog = new THREE.Fog(0xe8e9e3, 420, 1100);
const camera = new THREE.PerspectiveCamera(45, 1, 0.08, 1600);
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.17;
viewport.append(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8e9986, 2.4));
const sun = new THREE.DirectionalLight(0xfffaf0, 3.1);
sun.position.set(-120, 220, 90);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, {
  left: -235,
  right: 235,
  top: 235,
  bottom: -235,
  near: 1,
  far: 600,
});
sun.shadow.bias = -0.0003;
sun.shadow.normalBias = 0.15;
scene.add(sun);
const orbit = new OrbitControls(camera, renderer.domElement);
orbit.enableDamping = true;
orbit.dampingFactor = 0.07;
orbit.minDistance = 15;
orbit.maxDistance = 650;
orbit.maxPolarAngle = Math.PI * 0.48;
orbit.target.set(0, 0, 0);
const character = createCharacter();
scene.add(character.root);
const raycaster = new THREE.Raycaster();
const cameraRay = new THREE.Raycaster();
let selected;
const collisionMeshes = [];

function resize() {
  const w = viewport.clientWidth,
    h = viewport.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener("resize", resize);
resize();

function setView(next) {
  if (!viewNames.includes(next)) return;
  view = next;
  orbit.enabled = view === "aerial";
  character.root.visible = view !== "first";
  keys.clear();
  document
    .querySelectorAll("[data-view]")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.view === view)),
    );
  if (view === "aerial") {
    orbit.target.copy(player).add(new THREE.Vector3(0, 2, 0));
    camera.position.copy(player).add(new THREE.Vector3(250, 270, 285));
    orbit.update();
  } else if (view === "first") {
    pitch = 0;
    camera.position.copy(player).add(new THREE.Vector3(0, 1.58, 0));
  } else {
    pitch = 0.08;
    camera.position
      .copy(player)
      .add(
        new THREE.Vector3(
          Math.sin(yaw) * 7.5,
          2.58 + pitch * 3,
          Math.cos(yaw) * 7.5,
        ),
      );
    camera.lookAt(player.clone().add(new THREE.Vector3(0, 1.58, 0)));
  }
}
document
  .querySelectorAll("[data-view]")
  .forEach((button) =>
    button.addEventListener("click", () => setView(button.dataset.view)),
  );
$("#reset").addEventListener("click", () => {
  resetPlayer();
  setView(view);
});
$("#source-toggle").addEventListener("click", () => {
  const open = $("#source-details").hidden;
  $("#source-details").hidden = !open;
  $("#source-toggle").setAttribute("aria-expanded", String(open));
});
$("#wireframe").addEventListener("click", () => {
  const enabled = $("#wireframe").getAttribute("aria-pressed") !== "true";
  $("#wireframe").setAttribute("aria-pressed", String(enabled));
  model?.traverse((o) => {
    if (o.isMesh) {
      for (const m of Array.isArray(o.material) ? o.material : [o.material])
        m.wireframe = enabled;
    }
  });
});
function resetPlayer() {
  if (!manifest) return;
  player.set(manifest.spawn_enu_m[0], 0, -manifest.spawn_enu_m[1]);
  if (isBlocked(player.x, player.z, buildings, half)) {
    // Deterministically find walkable ground if a later model covers the previous spawn.
    let found = false;
    for (let r = 2; r < half && !found; r += 2)
      for (let a = 0; a < Math.PI * 2; a += Math.PI / 12) {
        const x = Math.cos(a) * r,
          z = Math.sin(a) * r;
        if (!isBlocked(x, z, buildings, half)) {
          player.set(x, 0, z);
          found = true;
          break;
        }
      }
    if (!found) throw new Error("试验区没有可用的角色出生点");
  }
  player.y = sampleGround(field, player.x, player.z);
  character.root.position.copy(player);
  yaw = Math.PI * 0.14;
}

addEventListener("keydown", (event) => {
  if (
    ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName) ||
    event.ctrlKey ||
    event.metaKey ||
    event.altKey
  )
    return;
  if (
    [
      "KeyW",
      "KeyA",
      "KeyS",
      "KeyD",
      "ArrowUp",
      "ArrowDown",
      "ArrowLeft",
      "ArrowRight",
      "Space",
    ].includes(event.code)
  )
    event.preventDefault();
  keys.add(event.code);
  if (!event.repeat) {
    if (event.code === "KeyV")
      setView(viewNames[(viewNames.indexOf(view) + 1) % 3]);
    if (["Digit1", "Digit2", "Digit3"].includes(event.code))
      setView(viewNames[Number(event.code.slice(-1)) - 1]);
  }
});
addEventListener("keyup", (event) => keys.delete(event.code));
addEventListener("blur", () => {
  keys.clear();
  drag = null;
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    keys.clear();
    drag = null;
  }
});
renderer.domElement.addEventListener("pointerdown", (event) => {
  viewport.focus({ preventScroll: true });
  drag = {
    x: event.clientX,
    y: event.clientY,
    startX: event.clientX,
    startY: event.clientY,
  };
  if (view !== "aerial") renderer.domElement.setPointerCapture(event.pointerId);
});
renderer.domElement.addEventListener("pointermove", (event) => {
  if (!drag || view === "aerial") return;
  yaw -= (event.clientX - drag.x) * 0.004;
  pitch = THREE.MathUtils.clamp(
    pitch + (event.clientY - drag.y) * 0.003,
    -0.7,
    0.9,
  );
  drag.x = event.clientX;
  drag.y = event.clientY;
});
renderer.domElement.addEventListener("pointerup", (event) => {
  if (
    drag &&
    Math.hypot(event.clientX - drag.startX, event.clientY - drag.startY) < 5
  )
    selectAt(event);
  drag = null;
});
renderer.domElement.addEventListener("pointercancel", () => {
  drag = null;
});
function selectAt(event) {
  const box = renderer.domElement.getBoundingClientRect();
  raycaster.setFromCamera(
    new THREE.Vector2(
      ((event.clientX - box.left) / box.width) * 2 - 1,
      (-(event.clientY - box.top) / box.height) * 2 + 1,
    ),
    camera,
  );
  const hit = raycaster
    .intersectObjects(model?.children || [], true)
    .find((h) => h.object.userData.asset_kind === "building");
  if (selected) {
    selected.material.emissive.setHex(0);
    selected = null;
  }
  $("#selection").hidden = !hit;
  if (!hit) return;
  selected = hit.object;
  selected.material.emissive.setHex(0x304b24);
  const record = buildings.find((b) => b.id === selected.name);
  $("#selection").replaceChildren();
  const title = document.createElement("strong");
  title.textContent = record?.id || selected.name;
  const detail = document.createElement("span");
  detail.textContent = `建筑候选 · 估算高度 ${record?.height_m ?? "—"} m · 尚未细化`;
  $("#selection").append(title, detail);
}

function updatePlayer(dt) {
  const forward =
    (keys.has("KeyW") || keys.has("ArrowUp") ? 1 : 0) -
    (keys.has("KeyS") || keys.has("ArrowDown") ? 1 : 0);
  const right =
    (keys.has("KeyD") || keys.has("ArrowRight") ? 1 : 0) -
    (keys.has("KeyA") || keys.has("ArrowLeft") ? 1 : 0);
  moving = !!(forward || right);
  if (moving) {
    const heading =
      view === "aerial"
        ? Math.atan2(
            camera.position.x - orbit.target.x,
            camera.position.z - orbit.target.z,
          )
        : yaw;
    const speed =
      ((keys.has("ShiftLeft") || keys.has("ShiftRight") ? 7 : 3) * dt) /
      Math.max(1, Math.hypot(forward, right));
    const delta = {
      x: (-Math.sin(heading) * forward + Math.cos(heading) * right) * speed,
      z: (-Math.cos(heading) * forward - Math.sin(heading) * right) * speed,
    };
    const before = player.clone();
    movePlayer(player, delta, buildings, half, field);
    character.root.rotation.y = Math.atan2(
      player.x - before.x,
      player.z - before.z,
    );
  }
  character.root.position.copy(player);
  character.animate(elapsed, moving);
}

function updateCamera(dt) {
  if (view === "aerial") {
    orbit.update();
    return;
  }
  const eye = player.clone().add(new THREE.Vector3(0, 1.58, 0));
  const facing = new THREE.Vector3(
    -Math.sin(yaw) * Math.cos(pitch),
    -Math.sin(pitch),
    -Math.cos(yaw) * Math.cos(pitch),
  );
  if (view === "first") {
    camera.position.copy(eye);
    camera.lookAt(eye.clone().add(facing));
    return;
  }
  const desired = eye
    .clone()
    .add(
      new THREE.Vector3(
        Math.sin(yaw) * 7.5,
        1 + pitch * 3,
        Math.cos(yaw) * 7.5,
      ),
    );
  // Keep the follow camera out of walls and above the sampled terrain.
  const direction = desired.clone().sub(eye);
  const distance = direction.length();
  cameraRay.set(eye, direction.normalize());
  cameraRay.far = distance;
  const obstacle = cameraRay.intersectObjects(collisionMeshes, false)[0];
  if (obstacle)
    desired
      .copy(eye)
      .addScaledVector(direction, Math.max(0.5, obstacle.distance - 0.3));
  desired.y = Math.max(
    desired.y,
    sampleGround(field, desired.x, desired.z) + 0.4,
  );
  camera.position.lerp(desired, 1 - Math.exp(-dt * 12));
  camera.lookAt(eye);
}

const map = $("#minimap"),
  ctx = map.getContext("2d");
function drawMap() {
  const n = map.width,
    scale = n / (half * 2),
    point = (x, north) => [(x + half) * scale, (half - north) * scale];
  ctx.clearRect(0, 0, n, n);
  ctx.fillStyle = "#e7e9df";
  ctx.fillRect(0, 0, n, n);
  ctx.strokeStyle = "#cbd2c5";
  ctx.lineWidth = 0.5;
  for (let i = 0; i <= 6; i++) {
    ctx.beginPath();
    ctx.moveTo((i * n) / 6, 0);
    ctx.lineTo((i * n) / 6, n);
    ctx.moveTo(0, (i * n) / 6);
    ctx.lineTo(n, (i * n) / 6);
    ctx.stroke();
  }
  for (const b of buildings) {
    ctx.beginPath();
    b.footprint_enu_m.forEach(([x, y], i) => {
      const p = point(x, y);
      i ? ctx.lineTo(...p) : ctx.moveTo(...p);
    });
    ctx.closePath();
    ctx.fillStyle = "#bcc4b5";
    ctx.fill();
    ctx.strokeStyle = "#aab5a5";
    ctx.stroke();
  }
  const [px, py] = point(player.x, -player.z);
  ctx.beginPath();
  ctx.arc(px, py, 4, 0, Math.PI * 2);
  ctx.fillStyle = "#24573e";
  ctx.fill();
  ctx.strokeStyle = "#fff";
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(px, py);
  ctx.lineTo(px - Math.sin(yaw) * 12, py - Math.cos(yaw) * 12);
  ctx.strokeStyle = "#24573e";
  ctx.lineWidth = 1.5;
  ctx.stroke();
}

async function loadJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}
try {
  const base = `${import.meta.env.BASE_URL}scene/`;
  manifest = await loadJson(`${base}manifest.json`);
  if (manifest.schema_version !== 1) throw new Error("不支持的场景清单版本");
  field = await loadJson(`${base}${manifest.heightfield_url}`);
  half = manifest.aoi_size_m / 2;
  buildings = manifest.buildings;
  if (field.heights_m.length !== field.nx * field.ny)
    throw new Error("地形高度数据不完整");
  const gltf = await new GLTFLoader().loadAsync(`${base}${manifest.model.url}`);
  model = gltf.scene;
  model.traverse((o) => {
    if (!o.isMesh) return;
    o.castShadow = o.userData.asset_kind === "building";
    o.receiveShadow = true;
    if (o.userData.asset_kind === "building") collisionMeshes.push(o);
    o.material = o.material.clone();
    if (o.userData.asset_kind === "terrain") terrainMesh = o;
  });
  if (!terrainMesh) throw new Error("GLB 缺少地形");
  scene.add(model);
  // A skirt grounds the cutout without changing the real topographic mesh.
  const skirt = new THREE.Mesh(
    new THREE.BoxGeometry(half * 2, 4, half * 2),
    new THREE.MeshStandardMaterial({ color: 0xbcc3b3, roughness: 1 }),
  );
  skirt.position.y = manifest.quality.terrain_range_local_m[0] - 2.2;
  skirt.receiveShadow = true;
  scene.add(skirt);
  const grid = new THREE.GridHelper(1200, 60, 0xc5cec0, 0xd7ddd2);
  grid.position.y = skirt.position.y - 2.05;
  scene.add(grid);
  resetPlayer();
  setView("aerial");
  $("#building-count").textContent = String(buildings.length);
  $("#source-year").textContent = manifest.source_dates[0].slice(0, 4);
  $("#source-date").textContent =
    `使用瓦片：${manifest.source_dates.join(" / ")}。地形与占位建筑来自同一份历史点云。`;
  $("#terrain-quality").textContent =
    `地形：${field.spacing_m} m 网格。内部留出插值 RMSE ${manifest.quality.holdout_rmse_m} m；尚无独立测量精度验证。`;
  $("#loading").hidden = true;
  renderer.setAnimationLoop((now) => {
    const dt = Math.min((now - lastTime) / 1000 || 0, 0.05);
    lastTime = now;
    elapsed += dt;
    updatePlayer(dt);
    updateCamera(dt);
    renderer.render(scene, camera);
    frames++;
    if (now - lastFps > 1000) {
      fps = Math.round((frames * 1000) / (now - lastFps));
      frames = 0;
      lastFps = now;
    }
    drawMap();
    const heading = new THREE.Vector3();
    camera.getWorldDirection(heading);
    $(".compass i").style.transform =
      `rotate(${Math.atan2(heading.x, -heading.z)}rad)`;
    $("#position").textContent =
      `E ${player.x.toFixed(1)} / N ${(-player.z).toFixed(1)} / H ${player.y.toFixed(1)} m`;
  });
  // Read-only snapshots plus explicit view/reset hooks for integration checks.
  window.__campus = {
    getState: () => ({
      ready: true,
      view,
      player: player.toArray(),
      camera: camera.position.toArray(),
      fps,
      buildings: buildings.length,
      blocked: isBlocked(player.x, player.z, buildings, half),
      ground: sampleGround(field, player.x, player.z),
      drawCalls: renderer.info.render.calls,
    }),
    setView,
    reset: resetPlayer,
    terrainCheck: (x, z) => {
      const ray = new THREE.Raycaster(
        new THREE.Vector3(x, 200, z),
        new THREE.Vector3(0, -1, 0),
      );
      const hit = ray.intersectObject(terrainMesh, true)[0];
      return { mesh: hit?.point.y, sampled: sampleGround(field, x, z) };
    },
  };
} catch (error) {
  console.error(error);
  $("#loading").hidden = true;
  $("#error").hidden = false;
  $("#error p").textContent =
    `${error.message}。请先运行重建流水线生成 public/scene 中的资产。`;
}
