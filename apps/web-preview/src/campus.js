// SPDX-License-Identifier: Apache-2.0
import { applyBuildingIdentities } from "./building-identities.js";
import {
  attachCollisionBoxes,
  segmentHitsBoxes,
} from "./collision-supplement.js";
import * as THREE from "three";
import { installWorldLifecycle } from "./world-lifecycle.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { createCharacter } from "./character.js";
import { applyFoundationGrade } from "./foundation-l2.js";
import {
  installPavingCorridors,
  updateQuadActivity,
} from "./paving-corridors-l2.js";
import {
  sampleGround,
  isBlocked,
  movePlayer,
  movementFrameSeconds,
  startJump,
  stepVertical,
} from "./world.js";
import { createBuildingLabels } from "./labels.js";
import { createBuildingCard } from "./building-card.js";
import {
  createBuildingHighlight,
  resolveBuildingHit,
} from "./building-highlight.js";
import { createMinimap } from "./minimap.js";
import { createBuildingSearch } from "./search.js";
import {
  loadPresentation,
  setEmissive,
  sceneAssetUrl,
} from "./presentation.js";
import {
  createTouchControls,
  movementInput,
  RUN_SPEED,
  RUN_THRESHOLD,
} from "./touch.js";
import { createEntrances } from "./entrances.js";
import { readReturn, enterInterior, RETURN_KEY } from "./scene-transition.js";
import { createAnalytics } from "./analytics.js";
import { loadStudentFactory } from "./student.js";
import { createFixedNpc } from "./fixed-npc.js";
import { danCarrereAppearance, styleDanCarrere } from "./dan-carrere-style.js";
import { createRouter, distance } from "./routing.js";
import { createNavigation } from "./navigation.js";
import { createEugeneSky } from "./eugene-sky.js";
import {
  createOverviewDepth,
  freezeStaticTransforms,
} from "./render-stability.js";
import { createDeathFlow } from "./death.js";
import { applySurfaceGrain } from "./surface-grain.js";
import { createBetaRegistry } from "./beta.js";
import { createZombieSchool } from "./zombie-school.js";
import { createDeveloperTools } from "./developer.js";
import { createCampusLife } from "./life.js";
import { loadWildlifeFactory } from "./wildlife.js";
import { createWalkMotion, DENSITY_NAMES } from "./ambience.js";
import { createSound } from "./sound.js";
import { createFeedback } from "./feedback.js";
import { applyProfile } from "./profile.js";
import { loadFordArenaReview } from "./ford-arena-review.js";
import { loadCascadeVolcanologyReview } from "./cascade-volcanology-review.js";
import { loadBuildingSiteReview } from "./building-site-review.js";
import "@fontsource-variable/dm-sans";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import "./style.css";

let navigation,
  life,
  studentFactory,
  fixedNpc,
  squirrelFactory,
  zombies,
  outdoorRouter,
  betaRegistry,
  entrances;
let sound = { step() {}, state: () => ({ enabled: false }) };
const walkMotion = createWalkMotion();
let motion = { bobX: 0, bobY: 0, roll: 0, walking: false, steps: 0 };
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
let analytics = { event() {} };
const $ = (selector) => document.querySelector(selector);
const viewport = $("#viewport"),
  dialog = $("#settings-dialog");
const death = createDeathFlow({
  pause: () => {
    keys.clear();
    drag = null;
    touchControls.reset();
    walkMotion.reset();
  },
});
const modalOpen = () => dialog.open || $("#feedback-dialog").open || death.dead;
const developer = createDeveloperTools({
  getLife: () => ({
    inspect: (id) => life?.inspect(id) || zombies?.inspect(id),
  }),
});
const views = ["third", "first", "aerial"],
  keys = new Set();
let view = "aerial",
  yaw = Math.PI * 0.14,
  pitch = 0.08,
  followDistance = 7.5,
  drag = null,
  manifest,
  profile,
  viewerSettings,
  field,
  half,
  model,
  terrainMesh,
  drawMap,
  presentation;
let buildings = [],
  outdoorObstacleBoxes = [],
  elapsed = 0,
  lastTime = 0,
  frames = 0,
  lastFps = 0,
  fps = 0,
  moving = false,
  selected = null,
  selectedId = null,
  searchFocusId = null,
  focusCameraTarget = null,
  cameraTransition = null,
  selectedMapTarget = null;
const player = new THREE.Vector3(),
  vertical = { velocity: 0, grounded: true };
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe3e5e4);
scene.fog = new THREE.Fog(0xe3e5e4, 3500, 7500);
const camera = new THREE.PerspectiveCamera(45, 1, 0.08, 9000);
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.shadowMap.autoUpdate = false;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.02;
viewport.append(renderer.domElement);
installWorldLifecycle(renderer, scene);
const touchControls = createTouchControls(renderer.domElement, {
  enabled: () => view !== "aerial" && !modalOpen() && !!field,
  onLook: (dx, dy) => {
    focusCameraTarget = null;
    yaw -= dx * 0.004;
    pitch = THREE.MathUtils.clamp(pitch + dy * 0.003, -0.7, 0.9);
  },
  onTap: selectAt,
  onMove: () => {
    analytics.event("touch-walk");
    focusCameraTarget = null;
    cancelCameraTransition();
  },
});
const touchHint = document.createElement("p");
touchHint.className = "touch-hint";
touchHint.textContent =
  "Lower half: drag to walk / run · Upper half: drag to look";
$("#app").append(touchHint);
const sky = createEugeneSky(scene);
scene.add(new THREE.HemisphereLight(0xffffff, 0x929b94, 1.9));
const sun = new THREE.DirectionalLight(0xfff9ef, 2.4);
sun.position.set(-1400, 2400, 1300);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, {
  left: -1450,
  right: 1450,
  top: 1450,
  bottom: -1450,
  near: 1,
  far: 6500,
});
sun.shadow.bias = -0.0002;
sun.shadow.normalBias = 0.3;
scene.add(sun);
const orbit = new OrbitControls(camera, renderer.domElement);
orbit.enableDamping = true;
orbit.dampingFactor = 0.07;
orbit.minDistance = 12;
orbit.maxDistance = 6000;
orbit.maxPolarAngle = Math.PI * 0.48;
let character = createCharacter();
character.root.traverse((object) => {
  if (object.isMesh) object.castShadow = false;
});
scene.add(character.root);
const contactShadow = new THREE.Mesh(
  new THREE.CircleGeometry(0.4, 24),
  new THREE.MeshBasicMaterial({
    color: 0x344039,
    transparent: true,
    opacity: 0.16,
    depthWrite: false,
  }),
);
contactShadow.rotation.x = -Math.PI / 2;
scene.add(contactShadow);
const meshesById = new Map(),
  collisionMeshes = [];
const buildingRecords = new Map();
const buildingHighlight = createBuildingHighlight(
  scene,
  meshesById,
  buildingRecords,
);
let hoverPointer = null,
  hoverPending = false,
  lastHover = 0;
const buildingCard = createBuildingCard(viewport, camera, {
  onEnter: enterBuilding,
  onClose: clearSelection,
});
const raycaster = new THREE.Raycaster(),
  cameraRay = new THREE.Raycaster();
const labels = createBuildingLabels(
  scene,
  viewport,
  camera,
  selectBuilding,
  (id) => buildingHighlight.hover(id),
);
const buildingSearch = createBuildingSearch($("#building-search"), {
  onSelect: focusBuilding,
  onClear: clearSelection,
  onFocus: () => {
    keys.clear();
    drag = null;
    touchControls.reset();
  },
});
orbit.addEventListener("start", cancelCameraTransition);
function resize() {
  touchControls.reset();
  const w = viewport.clientWidth,
    h = viewport.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  labels.resize(w, h);
}
addEventListener("resize", resize);
resize();

function setView(next) {
  walkMotion.reset();
  motion = { ...motion, bobX: 0, bobY: 0, roll: 0, walking: false };
  if (!views.includes(next)) return;
  if (next !== view) analytics.event("view-" + next);
  cancelCameraTransition();
  focusCameraTarget = null;
  touchControls.reset();
  drag = null;
  view = next;
  $("#app").dataset.view = view;
  orbit.enabled = view === "aerial";
  character.root.visible = view !== "first";
  keys.clear();
  document
    .querySelectorAll("[data-view]")
    .forEach((button) =>
      button.setAttribute("aria-pressed", String(button.dataset.view === view)),
    );
  if (view === "aerial") {
    const overview = presentation?.config.overview;
    orbit.target.fromArray(
      overview?.target || [0, field ? sampleGround(field, 0, 0) + 5 : 0, 0],
    );
    const scale = half || 1000;
    camera.position
      .copy(orbit.target)
      .add(
        new THREE.Vector3(
          ...(overview?.offset || [scale * 1.5, scale * 2, scale * 1.65]),
        ),
      );
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
          Math.sin(yaw) * followDistance,
          1.58 + (1 + pitch * 3) * (followDistance / 7.5),
          Math.cos(yaw) * followDistance,
        ),
      );
    camera.lookAt(player.clone().add(new THREE.Vector3(0, 1.58, 0)));
  }
  if (searchFocusId) focusBuilding(searchFocusId, { animate: false });
  navigation?.modeChanged();
  syncBuildingCard();
}
document
  .querySelectorAll("[data-view]")
  .forEach((button) =>
    button.addEventListener("click", () => setView(button.dataset.view)),
  );
function isOutdoorObstacle(x, z) {
  const point = [x, -z];
  return segmentHitsBoxes(point, point, outdoorObstacleBoxes, 0.42);
}
function standingGround(x, z) {
  const ground = sampleGround(field, x, z);
  return Math.max(ground, presentation?.hardscape?.height(x, z) ?? ground);
}
function blocksHardscapeStep(x, z, y) {
  const nextSurface = presentation?.hardscape?.height(x, z);
  if (nextSurface === undefined) return false;
  const footing = vertical.grounded ? standingGround(player.x, player.z) : y;
  return nextSurface - footing > 0.28;
}
function resetPlayer() {
  if (!manifest) return;
  clearSelection();
  player.set(manifest.spawn_enu_m[0], 0, -manifest.spawn_enu_m[1]);
  if (
    isBlocked(player.x, player.z, buildings, half) ||
    isOutdoorObstacle(player.x, player.z)
  ) {
    const origin = player.clone();
    let found = false;
    for (let r = 2; r < 100 && !found; r += 2)
      for (let a = 0; a < Math.PI * 2; a += Math.PI / 12) {
        const x = origin.x + Math.cos(a) * r,
          z = origin.z + Math.sin(a) * r;
        if (!isBlocked(x, z, buildings, half) && !isOutdoorObstacle(x, z)) {
          player.set(x, 0, z);
          found = true;
          break;
        }
      }
    if (!found) throw new Error("No walkable starting point was found.");
  }
  player.y = standingGround(player.x, player.z);
  vertical.velocity = 0;
  vertical.grounded = true;
  character.root.position.copy(player);
  const target = viewerSettings?.spawn_look_at_enu_m;
  yaw = target
    ? Math.atan2(player.x - target[0], player.z + target[1])
    : Math.PI * 0.14;
  // The character's chest faces local +Z; the camera looks along -Z.
  character.root.rotation.y = yaw + Math.PI;
  followDistance = 7.5;
}
$("#reset").addEventListener("click", () => {
  analytics.event("return-to-start");
  resetPlayer();
  setView(view);
});
function setSettingsTab(tab) {
  for (const name of ["settings", "beta", "about"]) {
    $("#" + name + "-panel").hidden = name !== tab;
    $("#" + name + "-tab").setAttribute("aria-selected", String(name === tab));
  }
}
$("#settings-open").addEventListener("click", () => {
  analytics.event("settings-open");
  keys.clear();
  drag = null;
  touchControls.reset();
  walkMotion.reset();
  motion = { ...motion, bobX: 0, bobY: 0, roll: 0, walking: false };
  dialog.showModal();
});
$("#settings-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("close", () => viewport.focus({ preventScroll: true }));
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) {
    const box = dialog.getBoundingClientRect();
    if (
      event.clientX < box.left ||
      event.clientX > box.right ||
      event.clientY < box.top ||
      event.clientY > box.bottom
    )
      dialog.close();
  }
});
$("#settings-tab").addEventListener("click", () => setSettingsTab("settings"));
$("#beta-tab").addEventListener("click", () => setSettingsTab("beta"));
$("#motion-setting").addEventListener("input", (e) => {
  const name = DENSITY_NAMES[Number(e.target.value)];
  $("#motion-value").textContent = name;
  e.target.setAttribute("aria-valuetext", name);
});
$("#about-tab").addEventListener("click", () => setSettingsTab("about"));
$("#show-labels").addEventListener("change", (event) =>
  labels.setEnabled(event.target.checked),
);
$("#wireframe-setting").addEventListener("change", (event) =>
  model?.traverse((object) => {
    if (object.isMesh)
      for (const material of Array.isArray(object.material)
        ? object.material
        : [object.material])
        material.wireframe = event.target.checked;
  }),
);
$("#shadows-setting").addEventListener("change", (event) => {
  renderer.shadowMap.enabled = event.target.checked;
  renderer.shadowMap.needsUpdate = true;
  model?.traverse((object) => {
    if (object.isMesh) object.material.needsUpdate = true;
  });
});

addEventListener("keydown", (event) => {
  // Native buttons own Space activation; other movement shortcuts stay available.
  if (event.code === "Space" && event.target.closest?.("button")) return;
  if (
    modalOpen() ||
    ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName) ||
    event.ctrlKey ||
    event.metaKey ||
    event.altKey
  )
    return;
  if (event.code === "Slash") {
    event.preventDefault();
    $("#building-search-input").focus();
    return;
  }
  if (event.code === "Escape" && selectedId) {
    clearSelection();
    return;
  }
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
    if (event.code === "KeyE") {
      event.preventDefault();
      entrances?.activate();
    }
    if (event.code === "Space") startJump(vertical);
    if (event.code === "KeyV") setView(views[(views.indexOf(view) + 1) % 3]);
    if (["Digit1", "Digit2", "Digit3"].includes(event.code))
      setView(views[Number(event.code.slice(-1)) - 1]);
  }
});
addEventListener("keyup", (event) => keys.delete(event.code));
addEventListener("blur", () => {
  keys.clear();
  drag = null;
  touchControls.reset();
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    keys.clear();
    drag = null;
    touchControls.reset();
  }
});
renderer.domElement.addEventListener("pointerdown", (event) => {
  buildingHighlight.hover(null);
  focusCameraTarget = null;
  cancelCameraTransition();
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
  if (event.pointerType === "mouse" && !drag) {
    hoverPointer = { clientX: event.clientX, clientY: event.clientY };
    hoverPending = true;
  }
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
  touchControls.reset();
});
renderer.domElement.addEventListener("pointerleave", () => {
  if (!drag) {
    fixedNpc?.hover(false);
    hoverPointer = null;
    hoverPending = false;
    buildingHighlight.hover(null);
  }
});
renderer.domElement.addEventListener("pointercancel", () => {
  drag = null;
  touchControls.reset();
});
viewport.addEventListener(
  "wheel",
  (event) => {
    // Scene labels sit above the canvas. Keep their click behavior while
    // forwarding overview wheel input to the same OrbitControls handler.
    if (
      view === "aerial" &&
      event.target instanceof Element &&
      event.target.closest(".building-label, .fixed-person-label")
    ) {
      event.preventDefault();
      renderer.domElement.dispatchEvent(
        new WheelEvent("wheel", {
          deltaX: event.deltaX,
          deltaY: event.deltaY,
          deltaMode: event.deltaMode,
          clientX: event.clientX,
          clientY: event.clientY,
          ctrlKey: event.ctrlKey,
          shiftKey: event.shiftKey,
          altKey: event.altKey,
          metaKey: event.metaKey,
          cancelable: true,
        }),
      );
      return;
    }
    if (view !== "third" || modalOpen() || event.ctrlKey || event.metaKey)
      return;
    event.preventDefault();
    const delta =
      event.deltaY *
      (event.deltaMode === 1
        ? 16
        : event.deltaMode === 2
          ? viewport.clientHeight
          : 1);
    followDistance = THREE.MathUtils.clamp(
      followDistance * Math.exp(THREE.MathUtils.clamp(delta * 0.0015, -1, 1)),
      2.5,
      30,
    );
  },
  { passive: false },
);
renderer.domElement.addEventListener("pointerleave", () => {
  hoverPointer = null;
  hoverPending = false;
  buildingHighlight.hover(null);
  renderer.domElement.style.cursor = "";
});
orbit.addEventListener("start", () => {
  buildingHighlight.hover(null);
  hoverPending = false;
});
orbit.addEventListener("end", () => {
  hoverPending = !!hoverPointer;
});
function buildingAnchor(record) {
  const ring = record.footprint_enu_m;
  return new THREE.Vector3(
    ring.reduce((sum, p) => sum + p[0], 0) / ring.length,
    record.roof_z_m + 3,
    -ring.reduce((sum, p) => sum + p[1], 0) / ring.length,
  );
}
function cancelCameraTransition() {
  cameraTransition = null;
  orbit.enableDamping = true;
}
function clearSelection() {
  buildingHighlight.select(null);
  selected = null;
  selectedId = searchFocusId = null;
  focusCameraTarget = selectedMapTarget = null;
  cancelCameraTransition();
  labels.setSelected(null);
  buildingSearch.setSelection(null);
  $("#selection").hidden = true;
  buildingCard.hide();
  labels.setSuppressed(null);
}
function selectBuilding(id, { fromSearch = false } = {}) {
  const record = buildings.find((building) => building.id === id);
  if (!record) {
    clearSelection();
    return;
  }
  cancelCameraTransition();
  focusCameraTarget = null;
  selected = meshesById.get(id) || null;
  selectedId = id;
  searchFocusId = fromSearch ? id : null;
  selectedMapTarget = buildingAnchor(record);
  labels.setSelected(record.name ? id : null);
  buildingSearch.setSelection(record);
  $("#selection").hidden = false;
  buildingHighlight.select(id);
  const title = document.createElement("strong");
  title.textContent = record.name || "Unidentified structure";
  const detail = document.createElement("span");
  detail.textContent =
    (presentation?.config.replaces_building_ids.includes(id)
      ? presentation.config.landmark_building_ids?.includes(id)
        ? "Photo-informed art model · Approximate dimensions"
        : "Stylized historical envelope"
      : record.status === "approximate-context-placeholder"
        ? "Approximate building envelope"
        : "Historical roof estimate") +
    " · " +
    record.height_m.toFixed(1) +
    " m";
  $("#selection").replaceChildren(title, detail);
  syncBuildingCard();
}
function syncBuildingCard() {
  const record = buildingRecords.get(selectedId);
  const shown = view === "aerial" && !!record;
  if (shown) buildingCard.show(record, buildingAnchor(record));
  else buildingCard.hide();
  labels.setSuppressed(shown ? selectedId : null);
  $("#selection").hidden = !record || shown;
}
function focusBuilding(id, { animate = true } = {}) {
  const record = buildings.find((building) => building.id === id);
  if (!record?.name) return;
  analytics.event("building-search-selected");
  keys.clear();
  drag = null;
  touchControls.reset();
  selectBuilding(id, { fromSearch: true });
  navigation?.acceptBuilding(record);
  const anchor = buildingAnchor(record);
  if (view === "aerial") {
    const target = anchor.clone();
    target.y = (record.base_z_m + record.roof_z_m) / 2;
    const ring = record.footprint_enu_m;
    const width =
      Math.max(...ring.map((p) => p[0])) - Math.min(...ring.map((p) => p[0]));
    const depth =
      Math.max(...ring.map((p) => p[1])) - Math.min(...ring.map((p) => p[1]));
    const radius = Math.hypot(width, depth, record.height_m) / 2;
    const halfAngle = Math.min(
      THREE.MathUtils.degToRad(camera.fov) / 2,
      Math.atan(
        Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) * camera.aspect,
      ),
    );
    let horizontal =
      Math.max(70, (radius / Math.sin(halfAngle)) * 1.2) / Math.SQRT2;
    const direction = camera.position.clone().sub(orbit.target).setY(0);
    if (direction.lengthSq() < 0.001) direction.set(1, 0, 1);
    direction.normalize();
    const position = target.clone();
    for (let i = 0; i < 8; i++) {
      position.copy(target).addScaledVector(direction, horizontal);
      position.y += horizontal;
      if (position.y > sampleGround(field, position.x, position.z) + 5) break;
      horizontal *= 1.25;
    }
    orbit.enableDamping = false;
    orbit.update();
    if (animate && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
      cameraTransition = {
        fromPosition: camera.position.clone(),
        fromTarget: orbit.target.clone(),
        position,
        target,
        start: performance.now(),
      };
    } else {
      camera.position.copy(position);
      orbit.target.copy(target);
      orbit.update();
      orbit.enableDamping = true;
    }
  } else {
    focusCameraTarget = anchor.clone();
    focusCameraTarget.y = (record.base_z_m + record.roof_z_m) / 2;
    yaw = Math.atan2(player.x - anchor.x, player.z - anchor.z);
    const distance = Math.hypot(anchor.x - player.x, anchor.z - player.z);
    pitch = THREE.MathUtils.clamp(
      -Math.atan2(focusCameraTarget.y - player.y - 1.58, distance),
      -0.7,
      0.9,
    );
    character.root.rotation.y = yaw + Math.PI;
    updateCamera(0, true);
  }
  viewport.focus({ preventScroll: true });
}
function selectAt(event) {
  if (navigation?.picking) {
    const rect = renderer.domElement.getBoundingClientRect();
    raycaster.setFromCamera(
      new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        (-(event.clientY - rect.top) / rect.height) * 2 + 1,
      ),
      camera,
    );
    const hit = raycaster.intersectObject(terrainMesh, true)[0];
    if (hit) navigation.pin([hit.point.x, -hit.point.z]);
    return;
  }

  const box = renderer.domElement.getBoundingClientRect();
  raycaster.setFromCamera(
    new THREE.Vector2(
      ((event.clientX - box.left) / box.width) * 2 - 1,
      (-(event.clientY - box.top) / box.height) * 2 + 1,
    ),
    camera,
  );
  const hit = raycaster.intersectObjects(collisionMeshes, false)[0];
  const personHit =
    fixedNpc && raycaster.intersectObject(fixedNpc.root, true)[0];
  if (personHit && (!hit || personHit.distance < hit.distance)) {
    fixedNpc.open();
    return;
  }
  if (entrances?.pick(raycaster, hit?.distance)) return;
  if (developer.enabled && (life || zombies)) {
    const npc = raycaster.intersectObjects(
      [...(life?.pickables() || []), ...(zombies?.pickables() || [])],
      true,
    )[0];
    if (npc && (!hit || npc.distance < hit.distance)) {
      let root = npc.object;
      while (root && !root.userData.npcId) root = root.parent;
      if (root && developer.inspect(root.userData.npcId)) return;
    }
  }
  if (hit) selectBuilding(resolveBuildingHit(hit, buildingRecords));
  else clearSelection();
}
function updatePlayer(dt, movementDt = dt) {
  const previous = player.clone();
  const forward =
    (keys.has("KeyW") || keys.has("ArrowUp") ? 1 : 0) -
    (keys.has("KeyS") || keys.has("ArrowDown") ? 1 : 0);
  const right =
    (keys.has("KeyD") || keys.has("ArrowRight") ? 1 : 0) -
    (keys.has("KeyA") || keys.has("ArrowLeft") ? 1 : 0);
  const input = movementInput(
    forward,
    right,
    keys.has("ShiftLeft") || keys.has("ShiftRight"),
    view !== "aerial" ? touchControls.axes : undefined,
  );
  moving = input.speed > 0;
  if (moving) {
    focusCameraTarget = null;
    const heading =
      view === "aerial"
        ? Math.atan2(
            camera.position.x - orbit.target.x,
            camera.position.z - orbit.target.z,
          )
        : yaw;
    const delta = {
      x:
        (-Math.sin(heading) * input.forward + Math.cos(heading) * input.right) *
        movementDt,
      z:
        (-Math.cos(heading) * input.forward - Math.sin(heading) * input.right) *
        movementDt,
    };
    const before = player.clone();
    movePlayer(
      player,
      delta,
      buildings,
      half,
      field,
      false,
      (x, z, y) =>
        isOutdoorObstacle(x, z) ||
        blocksHardscapeStep(x, z, y) ||
        life?.blockedPlayer(x, z, y) ||
        zombies?.blockedPlayer(x, z, y) ||
        false,
    );
    character.root.rotation.y = Math.atan2(
      player.x - before.x,
      player.z - before.z,
    );
  }
  const ground = standingGround(player.x, player.z);
  stepVertical(player, vertical, dt, ground);
  const travelled = Math.hypot(player.x - previous.x, player.z - previous.z);
  moving = travelled > 0.0001;
  motion = walkMotion.update(dt, travelled, {
    grounded: vertical.grounded,
    enabled: view !== "aerial",
    reducedMotion: reducedMotion.matches,
    motionLevel: Number($("#motion-setting").value),
    running: travelled / Math.max(movementDt, 0.001) > RUN_THRESHOLD,
  });
  if (motion.step) sound.step();
  character.root.position.copy(player);
  character.animate(elapsed, moving && vertical.grounded, motion);
  contactShadow.position.set(player.x, ground + 0.035, player.z);
  const altitude = player.y - ground;
  contactShadow.material.opacity = 0.16 / (1 + altitude);
  contactShadow.scale.setScalar(1 + altitude * 0.2);
}
function updateCamera(dt, snap = false) {
  if (view === "aerial") {
    if (cameraTransition) {
      const t = Math.min(1, (performance.now() - cameraTransition.start) / 650);
      const ease = t * t * (3 - 2 * t);
      camera.position.lerpVectors(
        cameraTransition.fromPosition,
        cameraTransition.position,
        ease,
      );
      orbit.target.lerpVectors(
        cameraTransition.fromTarget,
        cameraTransition.target,
        ease,
      );
      if (t === 1) {
        cameraTransition = null;
        orbit.enableDamping = true;
      }
    }
    orbit.update();
    return;
  }
  const eye = player.clone().add(new THREE.Vector3(0, 1.58, 0));
  if (view === "first") {
    eye.x += Math.cos(yaw) * motion.bobX;
    eye.z -= Math.sin(yaw) * motion.bobX;
    eye.y += motion.bobY;
    camera.position.copy(eye);
    if (focusCameraTarget) {
      camera.lookAt(focusCameraTarget);
      return;
    }
    camera.lookAt(
      eye
        .clone()
        .add(
          new THREE.Vector3(
            -Math.sin(yaw) * Math.cos(pitch),
            -Math.sin(pitch),
            -Math.cos(yaw) * Math.cos(pitch),
          ),
        ),
    );

    return;
  }
  const desired = eye
    .clone()
    .add(
      new THREE.Vector3(
        Math.sin(yaw) * followDistance,
        (1 + pitch * 3) * (followDistance / 7.5),
        Math.cos(yaw) * followDistance,
      ),
    );
  const direction = desired.clone().sub(eye),
    distance = direction.length();
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
  camera.position.lerp(desired, snap ? 1 : 1 - Math.exp(-dt * 12));
  camera.lookAt(focusCameraTarget || eye);
}
function enterBuilding(entry) {
  if (modalOpen()) return;
  const record = buildings.find((b) => b.id === entry.id);
  keys.clear();
  touchControls.reset();
  enterInterior(record, {
    interiorMode: view === "aerial" ? "overview" : "visit",
    player: player.toArray(),
    heroYaw: character.root.rotation.y,
    cameraPosition: camera.position.toArray(),
    orbitTarget: orbit.target.toArray(),
    yaw,
    pitch,
    followDistance,
    view,
    density: life?.state().densityLevel ?? 2,
    motionLevel: Number($("#motion-setting").value),
    soundEnabled: sound.state().enabled,
    settings: Object.fromEntries(
      [
        "show-labels",
        "shadows-setting",
        "toon-setting",
        "context-fog-setting",
        "wireframe-setting",
      ].map((id) => [id, $("#" + id).checked]),
    ),
  });
}
async function loadJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(url + ": HTTP " + response.status);
  return response.json();
}

const loading = $("#loading");
const loadingProgress = $("#loading-progress");

async function loadCampusScene(base, manifest, settings) {
  const name = settings.presentation_url;
  const config = name ? await loadJson(sceneAssetUrl(base, name)) : null;
  const ids = new Set(manifest.buildings.map(({ id }) => id));
  const modelUrl = base + manifest.model.url;
  const reviewMode = import.meta.env.DEV
    ? new URLSearchParams(location.search).get("exterior-review")
    : null;
  const cascadeLoad =
    config?.cascade_volcanology_site &&
    reviewMode !== "cascade-volcanology-baseline"
      ? loadCascadeVolcanologyReview(base, manifest, config).catch((error) => {
          console.warn(
            "Cascade courtyard review unavailable; using the prior site.",
            error,
          );
          return null;
        })
      : null;
  const hilyardWestAddresses = {
    "roof-a3d5625f": ["Catherine Cornwall Townhouses", "978 Hilyard St"],
    "roof-ca59da4d": ["Hilyard House", "725 E 14th Ave"],
    "roof-dcc94271": ["Campus Studios", "735 E 14th Ave"],
    "roof-ae986c58": ["Bushnell University · 722 E 11th Ave", "722 E 11th Ave"],
  };
  const universityDistrictAddresses = {
    "roof-62a81026": ["Bushnell University · 770 E 11th Ave", "770 E 11th Ave"],
    "roof-19858777": ["633 E 12th Avenue Parking Garage", "633 E 12th Ave"],
    "roof-bdbcb4fc": [
      "666 E 13th Avenue Parking Garage & Retail",
      "666 E 13th Ave",
    ],
  };
  const districtClinicAddresses = {
    "roof-4c79682d": [
      "PeaceHealth University District Clinic",
      "1200 Hilyard St",
    ],
    "university-district-650-e-12th-garage": [
      "University District South Parking Garage",
      "650 E 12th Ave",
    ],
    "roof-4a7d9b5a": ["University District North Building", "677 E 12th Ave"],
  };
  const treatedRoofAddresses = {
    "roof-76af1329": ["1951 Onyx Alley", "1951 Onyx Alley"],
    "roof-f447a8a6": ["1772 Hilyard St", "1772 Hilyard St"],
    "roof-57dfe898": ["Spencer Apartments", "735 E 19th Alley"],
    "roof-efbfe809": ["Eugene Institute of Religion", "768 E 16th Ave"],
    "roof-aae8fc07": [
      "1010–1020 E 18th Ave",
      "1010 E 18th Ave; 1020 E 18th Ave",
    ],
    "roof-f1651047": ["1010 E 20th Ave", "1010 E 20th Ave"],
  };
  const fairmountResidentialAddresses = {
    "roof-41f5448c": ["1705 Fairmount Blvd", "1705 Fairmount Blvd"],
    "roof-57f699be": ["1799 Fairmount Blvd", "1799 Fairmount Blvd"],
    "roof-8aa49f9b": ["1834 Fairmount Blvd", "1834 Fairmount Blvd"],
    "roof-e057643a": ["1892 Fairmount Blvd", "1892 Fairmount Blvd"],
    "roof-7bb19f64": ["1925 Fairmount Blvd", "1925 Fairmount Blvd"],
    "roof-72b4d323": ["2055 Fairmount Blvd", "2055 Fairmount Blvd"],
    "roof-78a95ac1": ["2094 Fairmount Blvd", "2094 Fairmount Blvd"],
  };
  const broadwayOrchardAddresses = {
    "roof-b40f786d": ["652 E Broadway", "652 E Broadway"],
    "roof-f8b27077": ["659 E Broadway", "659 E Broadway"],
    "roof-060ab58a": ["686 E Broadway", "686 E Broadway"],
    "roof-6c97d6b4": ["782 E Broadway", "782 E Broadway"],
    "roof-b3252193": ["1432 Orchard St", "1432 Orchard St"],
    "roof-bb9ee65a": ["1468–1476 Orchard Aly", "1468–1476 Orchard Aly"],
    "roof-a8a115d2": ["1505 Orchard St", "1505 Orchard St"],
    "roof-846446eb": ["1838 Orchard St", "1838 Orchard St"],
    "roof-8eff0cee": ["2059 Orchard St", "2059 Orchard St"],
  };
  const franklinComplexAddresses = {
    "roof-b59639cc": ["Womack Hall", "850 Franklin Blvd"],
    "roof-fc0fcc2e": ["1920–1960 Franklin Blvd", "1920–1960 Franklin Blvd"],
  };
  const franklinBoulevardAddresses = {
    "roof-5e02b3d2": ["1675 Franklin Blvd", "1675 Franklin Blvd"],
    "roof-fd64edbd": ["1809 Franklin Blvd", "1809 Franklin Blvd"],
    "roof-1587e3e1": ["1895 Franklin Blvd", "1895 Franklin Blvd"],
    "roof-b1290409": ["1917 Franklin Blvd", "1917 Franklin Blvd"],
    "roof-0dc3fa8a": ["1933 Franklin Blvd", "1933 Franklin Blvd"],
    "roof-4b8868e0": ["2091 Franklin Blvd", "2091 Franklin Blvd"],
  };
  const bardellAvenueAddresses = {
    "roof-3415fe97": ["3324 Bardell Ave", "3324 Bardell Ave"],
    "roof-119eb630": ["3330 Bardell Ave", "3330 Bardell Ave"],
    "roof-892a3891": ["3336 Bardell Ave", "3336 Bardell Ave"],
    "roof-57234f59": ["3344 Bardell Ave", "3344 Bardell Ave"],
    "roof-045d51bb": ["3345 Bardell Ave", "3345 Bardell Ave"],
    "roof-6b824894": ["3355 Bardell Ave", "3355 Bardell Ave"],
  };
  const villardStreetAddresses = {
    "roof-efd78630": ["1401 Villard St", "1401 Villard St"],
    "roof-d3e38b75": ["1599 Villard St", "1599 Villard St"],
    "roof-bb028710": ["1637 Villard St", "1637 Villard St"],
    "roof-5f1e62f1": ["1801 Villard St", "1801 Villard St"],
    "roof-45158580": ["1969 Villard St", "1969 Villard St"],
    "roof-c2d79893": ["1979 Villard St", "1979 Villard St"],
  };
  const gardenAvenueAddresses = {
    "roof-3ac532c7": ["1848 Garden Ave", "1848 Garden Ave"],
    "roof-9c95368e": [
      "Riverview Business Park (1901 Garden)",
      "1901 Garden Ave",
    ],
    "roof-f2c952e3": ["1976 Garden Ave", "1976 Garden Ave"],
    "roof-1a10907d": ["Millrace Gardens South Building", "2001 Garden Ave"],
    "roof-e3c224a3": ["Millrace Gardens North Building", "2001 Garden Ave"],
  };
  const fairmountAddresses = {
    "roof-41959677": ["1610 Fairmount Blvd", "1610 Fairmount Blvd"],
    "roof-4c44850e": ["1720 Fairmount Blvd", "1720 Fairmount Blvd"],
    "roof-c60174af": ["1740 Fairmount Blvd", "1740 Fairmount Blvd"],
    "roof-333eb38f": ["1780 Fairmount Blvd", "1780 Fairmount Blvd"],
    "roof-8d9a1132": ["1800 Fairmount Blvd", "1800 Fairmount Blvd"],
    "roof-29f81172": ["1820 Fairmount Blvd", "1820 Fairmount Blvd"],
    "roof-9cf9957b": ["1956 Fairmount Blvd", "1956 Fairmount Blvd"],
  };
  const campusNeighborAddresses = {
    "roof-4286ad30": ["Coho Townhouses (South)", "633 E 14th Ave"],
    "roof-2cbfcd06": ["Pi Kappa Alpha House", "1472 Kincaid St"],
    "roof-e17be27c": ["Christus House", "1834 Potter St"],
    "roof-f89a9211": ["St. Thomas More Newman Center", "1850 Emerald St"],
    "roof-cea1e466": ["Hayward House Apartments", "1290 E 18th Ave"],
    "roof-04683fef": ["Aldersgate Apartments", "1436 Alder St"],
    "roof-5e7ce49c": ["The 1840", "1840 Agate St"],
  };
  const reviewOptions = {
    knight: {
      descriptor: config?.knight_library_site,
      directory: "knight-library-review",
      ids: ["roof-6684e091"],
      replacedDetails: [
        "knight-library-balcony-detail.json",
        "knight-library-window-reveals.json",
      ],
    },
    hedco: {
      descriptor: config?.hedco_site_review,
      directory: "hedco-exterior-review",
      ids: ["context-b0010"],
      groundNode: "hedco-courtyard",
    },
    athletic: {
      descriptor: config?.athletic_site_review,
      directory: "athletic-exterior-review",
      ids: ["context-b0020", "roof-a5ff3d5a", "roof-af9a4442"],
      groundNode: "athletic-approaches",
    },
    emu: {
      descriptor: config?.emu_green_site,
      directory: "emu-green-review",
      ids: ["roof-266f13fd"],
      absorbedIds: ["roof-39f81f68"],
      groundNode: "emu-green-paving",
    },
    music: {
      descriptor: config?.frohnmayer_site,
      directory: "frohnmayer-exterior-review",
      ids: ["roof-e4a5429f"],
      absorbedIds: ["roof-cd7b6d76", "roof-fcd40d9f"],
      groundNode: "frohnmayer-approaches",
    },
    museum: {
      descriptor: config?.museum_site_review,
      directory: "museum-exterior-review",
      ids: ["roof-16751515"],
      groundNode: "museum-approaches",
      replacedDetails: ["museum-west-detail.json"],
    },
    gerlinger: {
      descriptor: config?.gerlinger_site_review,
      directory: "gerlinger-site-review",
      ids: ["roof-9ac93ab7", "roof-f0b575d6"],
      groundNode: "gerlinger-approaches",
      replacedDetails: [
        "gerlinger-east-detail.json",
        "gerlinger-east-masonry-detail.json",
        "gerlinger-annex-correction.json",
      ],
    },
    womens: {
      descriptor: config?.womens_quad_site,
      directory: "womens-quad-review",
      ids: ["roof-fd061857", "roof-e145c222"],
      absorbedIds: ["roof-6cd16f5c"],
      groundNode: "womens-quad-approaches",
      replacedDetails: ["susan-roof-detail.json"],
    },
    memorial: {
      descriptor: config?.memorial_quad_site,
      directory: "memorial-quad-review",
      ids: ["roof-f5cea51d", "roof-7ffcf31b"],
      groundNode: "memorial-quad-approaches",
      replacedDetails: ["chapman-west-detail.json", "condon-east-detail.json"],
    },
    fenton: {
      descriptor: config?.fenton_site_review,
      directory: "fenton-site-review",
      ids: ["roof-4f0c798e"],
      groundNode: "fenton-approaches",
      replacedDetails: ["fenton-south-detail.json"],
    },
    allen: {
      descriptor: config?.allen_site_review,
      directory: "allen-site-review",
      ids: ["roof-7b7893d6"],
      groundNode: "allen-approaches",
      replacedDetails: ["allen-west-detail.json"],
    },
    science: {
      descriptor: config?.lawrence_science_site,
      directory: "lawrence-science-review",
      ids: ["roof-57a37f8e", "uo-035", "uo-036"],
      groundNode: "lawrence-science-approaches",
      absorbedIds: ["roof-21450e38"],
      identityMoves: { "roof-4041562c": "uo-035", "roof-64589bec": "uo-036" },
    },
    straub: {
      descriptor: config?.straub_earl_site,
      directory: "straub-earl-review",
      ids: ["roof-5ded2bf0", "roof-f01c8434"],
      groundNode: "straub-earl-approaches",
      absorbedIds: ["roof-303d99fd", "roof-aedc356a"],
      replacedDetails: ["straub-west-detail.json"],
    },
    kalapuya: {
      descriptor: config?.kalapuya_site,
      directory: "kalapuya-review",
      ids: ["roof-b36ba733"],
      groundNode: "kalapuya-approaches",
      registeredNames: { "roof-b36ba733": "Kalapuya Ilihi Hall" },
      sourceBatchIds: ["roof-b36ba733"],
      corridorId: "tiger-1104264146938-0-0-0",
      navigationUrl: settings.navigation_url,
    },
    longhouse: {
      descriptor: config?.longhouse_site,
      directory: "longhouse-review",
      ids: ["roof-f736712f"],
      groundNode: "longhouse-approach",
      registeredNames: { "roof-f736712f": "Many Nations Longhouse" },
      sourceBatchIds: ["roof-f736712f"],
      replacedDetails: ["longhouse-south-provisional-detail.json"],
    },
    scholars: {
      descriptor: config?.global_scholars_site,
      directory: "global-scholars-review",
      ids: ["context-b0158"],
      groundNode: "global-scholars-approaches",
    },
    moss: {
      descriptor: config?.moss_street_site,
      directory: "moss-street-review",
      ids: ["roof-72c79877"],
      groundNode: "moss-street-approach",
      registeredNames: {
        "roof-72c79877": "Moss Street Children's Center",
      },
      sourceBatchIds: ["roof-72c79877"],
      absorbedIds: ["roof-7b325cb8"],
    },
    olum: {
      descriptor: config?.vivian_olum_site,
      directory: "vivian-olum-review",
      ids: ["roof-1c631d7c", "roof-1d1be960"],
      groundNode: "vivian-olum-approaches",
      registeredNames: {
        "roof-1c631d7c": "Vivian Olum Child Development Center",
        "roof-1d1be960": "Vivian Olum Child Development Center Annex",
      },
      sourceBatchIds: ["roof-1c631d7c", "roof-1d1be960"],
    },
    graduates: {
      descriptor: config?.graduate_village_site,
      directory: "graduate-village-review",
      ids: ["roof-311b157f", "roof-03ecaaba"],
      groundNode: "graduate-village-approaches",
      registeredNames: {
        "roof-311b157f": "East Campus Graduate Village West",
        "roof-03ecaaba": "East Campus Graduate Village East",
      },
      sourceBatchIds: ["roof-311b157f", "roof-03ecaaba"],
    },
    "knight-law": {
      descriptor: config?.knight_law_site,
      directory: "knight-law-review",
      ids: ["roof-f52041e8"],
      groundNode: "knight-law-approaches",
      replacedDetails: ["knight-law-west-detail.json"],
    },
    "bean-unthank": {
      descriptor: config?.bean_unthank_site,
      directory: "bean-unthank-review",
      ids: ["roof-0de7fadb", "context-oc-unthank"],
      groundNode: "bean-unthank-approaches",
      replacedDetails: [
        "bean-exterior-detail.json",
        "unthank-west-detail.json",
      ],
    },
    "cedar-yasui": {
      descriptor: config?.cedar_yasui_site,
      directory: "cedar-yasui-review",
      ids: ["context-oc-cedar", "context-oc-yasui"],
      groundNode: "cedar-yasui-courtyards",
      absorbedIds: ["roof-1fde9ce4", "roof-1d1803a6", "roof-7974be11"],
    },
    "carson-llc": {
      descriptor: config?.carson_llc_site,
      directory: "carson-llc-review",
      ids: ["roof-2cd1068b", "roof-d2f88f9e", "roof-453966d5"],
      groundNode: "carson-llc-grounds",
      replacedDetails: [
        "carson-exterior-detail.json",
        "llc-north-detail.json",
        "llc-south-detail.json",
      ],
    },
    "oregon-jaqua": {
      descriptor: config?.oregon_jaqua_site,
      directory: "oregon-jaqua-review",
      ids: ["roof-11d15952", "context-b0067"],
      groundNode: "oregon-jaqua-grounds",
      replacedDetails: [
        "oregon-south-detail.json",
        "oregon-planter-detail.json",
        "jaqua-exterior-detail.json",
      ],
    },
    "lillis-complex": {
      descriptor: config?.lillis_complex_site,
      directory: "lillis-complex-review",
      ids: [
        "roof-1afe792e",
        "roof-0a498bf7",
        "roof-75e776d0",
        "roof-86754ad7",
        "context-b0039",
      ],
      groundNode: "lillis-complex-courtyards",
      absorbedIds: ["roof-7fee2881"],
      replacedDetails: [
        "anstett-south-detail.json",
        "anstett-lamps-detail.json",
        "peterson-south-detail.json",
        "lillis-south-detail.json",
      ],
    },
    "friendly-collier-mckenzie": {
      descriptor: config?.friendly_collier_mckenzie_site,
      directory: "friendly-collier-mckenzie-review",
      ids: ["roof-556799cc", "roof-e5accf83", "roof-f61e9b20"],
      groundNode: "friendly-collier-mckenzie-grounds",
      replacedDetails: [
        "friendly-west-detail.json",
        "collier-house-detail.json",
        "mckenzie-exterior-detail.json",
      ],
    },
    "plc-lokey-tykeson": {
      descriptor: config?.plc_lokey_tykeson_site,
      directory: "plc-lokey-tykeson-review",
      ids: ["roof-8f611273", "roof-74ecc113", "roof-5bbb5fd1", "context-b0103"],
      groundNode: "plc-lokey-tykeson-grounds",
      registeredNames: { "roof-5bbb5fd1": "Lokey Education Building (C)" },
      sourceBatchIds: ["roof-5bbb5fd1"],
      absorbedIds: ["roof-30574cc0", "roof-4f014745", "roof-9346417e"],
      replacedDetails: ["plc-tower-detail.json", "tykeson-north-detail.json"],
    },
    "northeast-science": {
      descriptor: config?.northeast_science_site,
      directory: "northeast-science-review",
      ids: [
        "roof-a5a51275",
        "roof-0f5fbbd5",
        "context-b0038",
        "context-b0040",
        "roof-0ca67b60",
        "context-b0045",
        "roof-34f891de",
      ],
      groundNode: "northeast-science-grounds",
      registeredNames: { "roof-0f5fbbd5": "Cascade Annex East" },
      sourceBatchIds: ["roof-0f5fbbd5"],
      absorbedIds: ["roof-4041562c", "roof-77c44142", "roof-e495d9f5"],
      prerequisiteIds: ["uo-035"],
    },
    "knight-campus": {
      descriptor: config?.knight_campus_site,
      directory: "knight-campus-review",
      ids: ["context-oc-knight-1", "context-oc-knight-2"],
      groundNode: "knight-campus-grounds",
      absorbedIds: ["roof-a79ff330"],
      replacedDetails: [
        "knight-campus1-south-detail.json",
        "knight-campus2-east-detail.json",
      ],
    },
    "northsite-millrace": {
      descriptor: config?.northsite_millrace_site,
      directory: "northsite-millrace-review",
      groundNode: "northsite-millrace-grounds",
      ids: ["roof-f37c4e05", "roof-1f65a447", "roof-4071cebd", "roof-37a3afa0"],
      sourceBatchIds: [
        "roof-f37c4e05",
        "roof-1f65a447",
        "roof-4071cebd",
        "roof-37a3afa0",
      ],
      registeredNames: {
        "roof-f37c4e05": "Fine Arts Studios Sculpture",
        "roof-1f65a447": "Fine Arts Studios Ceramics",
        "roof-4071cebd": "Fine Arts Studios Metalsmith/Jewelry",
        "roof-37a3afa0": "1600 Millrace Drive",
      },
    },
    "public-building-exterior": {
      descriptor: config?.public_building_exterior_site,
      directory: "public-building-exterior-review",
      groundNode: "public-building-exterior-approaches",
      ids: ["roof-c1ff8b83", "roof-e11ec58d", "roof-a997a75f", "roof-b068940e"],
      sourceBatchIds: ["roof-b068940e"],
      registeredNames: { "roof-b068940e": "Agate Hall" },
      replacedDetails: [
        "natural-museum-detail.json",
        "barn-solar-detail.json",
        "agate-west-provisional-detail.json",
      ],
    },
    "hayward-exterior": {
      descriptor: config?.hayward_exterior_site,
      directory: "hayward-exterior-review",
      groundNode: "hayward-exterior-ground",
      ids: ["context-oc-hayward"],
      absorbedIds: ["roof-64589bec", "roof-f7af1b95"],
      prerequisiteIds: ["uo-036"],
    },
    "campus-frontage": {
      descriptor: config?.campus_frontage_site,
      directory: "campus-frontage-review",
      groundNode: "campus-frontage-approaches",
      ids: [
        "roof-29dae856",
        "roof-2518e2a2",
        "roof-5fd54bd8",
        "roof-a55aea46",
        "roof-ee63827c",
      ],
      sourceBatchIds: [
        "roof-29dae856",
        "roof-5fd54bd8",
        "roof-a55aea46",
        "roof-ee63827c",
      ],
      registeredNames: {
        "roof-29dae856": "University Health Services",
        "roof-5fd54bd8": "Riley Hall",
        "roof-a55aea46": "Student Tennis Center",
        "roof-ee63827c": "Alder Building",
      },
      replacedDetails: [
        "power-station-detail.json",
        "alder-north-provisional-detail.json",
      ],
    },
    "facilities-exterior": {
      descriptor: config?.facilities_exterior_site,
      directory: "facilities-exterior-review",
      groundNode: "facilities-exterior-approaches",
      ids: [
        "roof-2975e487",
        "roof-3b3ed882",
        "roof-4c8ea72b",
        "roof-b5543048",
        "roof-0151b728",
      ],
      sourceBatchIds: [
        "roof-2975e487",
        "roof-3b3ed882",
        "roof-4c8ea72b",
        "roof-b5543048",
        "roof-0151b728",
      ],
      registeredNames: {
        "roof-2975e487": "CPFM Warehouse and Shops",
        "roof-3b3ed882": "Facilities Services Miscellaneous Quonset",
        "roof-4c8ea72b": "Facilities Services Recycling Quonset",
        "roof-b5543048": "CPFM Administration",
        "roof-0151b728": "Romania Warehouse and Showroom",
      },
    },
    "office-exterior": {
      descriptor: config?.office_exterior_site,
      directory: "office-exterior-review",
      groundNode: "office-exterior-approaches",
      ids: [
        "roof-17c233f0",
        "roof-b8f94f8e",
        "roof-3c2b8bdc",
        "roof-7c1c7fb1",
        "roof-bb20ea46",
      ],
      sourceBatchIds: [
        "roof-17c233f0",
        "roof-b8f94f8e",
        "roof-3c2b8bdc",
        "roof-7c1c7fb1",
        "roof-bb20ea46",
      ],
      registeredNames: {
        "roof-17c233f0": "UO Annex",
        "roof-b8f94f8e": "Rainier Building",
        "roof-3c2b8bdc": "1311 Franklin",
        "roof-7c1c7fb1": "University Business Operations Center",
        "roof-bb20ea46": "1715 Franklin",
      },
    },
    "residential-exterior": {
      descriptor: config?.residential_exterior_site,
      directory: "residential-exterior-review",
      groundNode: "residential-approaches",
      ids: [
        "roof-5f1a5ce2",
        "roof-4cb05afd",
        "roof-175d8088",
        "roof-57cd5529",
        "roof-4855fc7e",
      ],
      sourceBatchIds: [
        "roof-5f1a5ce2",
        "roof-4cb05afd",
        "roof-175d8088",
        "roof-57cd5529",
        "roof-4855fc7e",
      ],
      registeredAddresses: {
        "roof-5f1a5ce2": ["The Lewis", "1414 E 18th Ave"],
        "roof-4cb05afd": ["The Clark", "1424 E 18th Ave"],
        "roof-175d8088": ["Student Manor Apartments", "1442 E 18th Ave"],
        "roof-57cd5529": ["Royal Terrace", "625 E 16th Ave"],
        "roof-4855fc7e": ["Coho Townhouses (North)", "622 E 13th Alley"],
      },
    },
    "campus-neighbor-exterior": {
      descriptor: config?.campus_neighbor_exterior_site,
      directory: "campus-neighbor-exterior-review",
      groundNode: "campus-neighbor-approaches",
      ids: Object.keys(campusNeighborAddresses),
      sourceBatchIds: Object.keys(campusNeighborAddresses),
      registeredAddresses: campusNeighborAddresses,
    },
    "chapter-house-exterior": {
      descriptor: config?.chapter_house_exterior_site,
      directory: "chapter-house-exterior-review",
      groundNode: "chapter-house-approaches",
      ids: ["roof-c85e8e54", "state-1841241"],
      sourceBatchIds: ["roof-c85e8e54"],
      splitBuildings: { "state-1841241": "roof-c85e8e54" },
      registeredAddresses: {
        "roof-c85e8e54": ["Delta Delta Delta House", "851 E 15th Ave"],
        "state-1841241": ["Chi Omega House", "1461 Alder St"],
      },
    },
    "villard-garden-exterior": {
      descriptor: config?.villard_garden_exterior_site,
      directory: "villard-garden-exterior-review",
      groundNode: "villard-garden-approaches",
      ids: [
        "roof-5d371770",
        "state-1841280",
        "roof-a0566b7b",
        "state-1830735",
        "roof-3ce27cdc",
        "state-1841318",
      ],
      sourceBatchIds: ["roof-5d371770", "roof-a0566b7b", "roof-3ce27cdc"],
      splitBuildings: {
        "state-1841280": "roof-5d371770",
        "state-1830735": "roof-a0566b7b",
        "state-1841318": "roof-3ce27cdc",
      },
      registeredAddresses: {
        "roof-5d371770": ["1848 Villard St", "1848 Villard St"],
        "state-1841280": ["1878 Villard St", "1878 Villard St"],
        "roof-a0566b7b": ["1989 Villard St", "1989 Villard St"],
        "state-1830735": ["1991 Villard St", "1991 Villard St"],
        "roof-3ce27cdc": ["1923 Garden Ave", "1923 Garden Ave"],
        "state-1841318": ["Treetops Apartments", "1933 Garden Ave"],
      },
    },
    "alder-millrace-exterior": {
      descriptor: config?.alder_millrace_exterior_site,
      directory: "alder-millrace-exterior-review",
      groundNode: "alder-millrace-approaches",
      ids: ["roof-4fa203d9", "roof-7dcf2f03", "roof-77a7eb6c"],
      sourceBatchIds: ["roof-4fa203d9", "roof-7dcf2f03", "roof-77a7eb6c"],
      registeredAddresses: {
        "roof-4fa203d9": ["1915 Alder St", "1915 Alder St"],
        "roof-7dcf2f03": ["Hess Apartments", "1390 Alder St"],
        "roof-77a7eb6c": ["Millrace Apartments", "1805 Garden Ave"],
      },
    },
    "east-campus-housing": {
      descriptor: config?.east_campus_housing_exterior_site,
      directory: "east-campus-housing-exterior-review",
      groundNode: "east-campus-housing-approaches",
      ids: [
        "roof-bef4cf29",
        "roof-7dd08283",
        "roof-e086d515",
        "roof-9fdf719c",
        "roof-fb6ac47a",
        "roof-6f41ba80",
      ],
      sourceBatchIds: [
        "roof-bef4cf29",
        "roof-7dd08283",
        "roof-e086d515",
        "roof-9fdf719c",
        "roof-fb6ac47a",
        "roof-6f41ba80",
      ],
      registeredNames: {
        "roof-bef4cf29": "1841 E 15th Ave",
        "roof-7dd08283": "1602 Villard St",
        "roof-e086d515": "1778 Villard St",
        "roof-9fdf719c": "1795 Moss St",
        "roof-fb6ac47a": "1800 Columbia St",
        "roof-6f41ba80": "1848 Moss St",
      },
    },
    "hilyard-west-exterior": {
      descriptor: config?.hilyard_west_exterior_site,
      directory: "hilyard-west-exterior-review",
      groundNode: "hilyard-west-approaches",
      ids: Object.keys(hilyardWestAddresses),
      sourceBatchIds: Object.keys(hilyardWestAddresses),
      registeredAddresses: hilyardWestAddresses,
    },
    "university-district-exterior": {
      descriptor: config?.university_district_exterior_site,
      directory: "university-district-exterior-review",
      groundNode: "university-district-approaches",
      ids: Object.keys(universityDistrictAddresses),
      sourceBatchIds: Object.keys(universityDistrictAddresses),
      registeredAddresses: universityDistrictAddresses,
      prerequisiteIds: ["roof-ae986c58"],
    },
    "university-district-clinic": {
      descriptor: config?.university_district_clinic_site,
      directory: "university-district-clinic-review",
      groundNode: "university-district-clinic-approaches",
      ids: Object.keys(districtClinicAddresses),
      sourceBatchIds: ["roof-4c79682d", "roof-4a7d9b5a"],
      splitBuildings: {
        "university-district-650-e-12th-garage": "roof-4c79682d",
      },
      registeredAddresses: districtClinicAddresses,
    },
    "former-hospital-site": {
      descriptor: config?.former_hospital_site,
      directory: "former-hospital-site-review",
      groundNode: "former-hospital-construction",
      ids: [],
      absorbedIds: [
        "roof-a3f76ab6",
        "roof-eb5ba9b8",
        "roof-8caa7792",
        "roof-6d2ad952",
        "roof-8e0e504c",
      ],
    },
    "zirc-exterior": {
      descriptor: config?.zirc_exterior_site,
      directory: "zirc-exterior-review",
      groundNode: "zirc-exterior-approaches",
      ids: ["roof-f0cd697a"],
      sourceBatchIds: ["roof-f0cd697a"],
      registeredNames: {
        "roof-f0cd697a": "Zebrafish International Resource Center",
      },
    },
    "hilyard-central-exterior": {
      descriptor: config?.hilyard_central_exterior_site,
      directory: "hilyard-central-exterior-review",
      groundNode: "hilyard-central-approaches",
      ids: ["roof-9feed235", "hilyard-apartments-971", "roof-eab27ea2"],
      sourceBatchIds: ["roof-9feed235", "roof-eab27ea2"],
      splitBuildings: { "hilyard-apartments-971": "roof-9feed235" },
      registeredAddresses: {
        "roof-9feed235": ["Hilyard Apartments · 957 Hilyard", "957 Hilyard St"],
        "hilyard-apartments-971": [
          "Hilyard Apartments · 971 Hilyard",
          "971 Hilyard St",
        ],
        "roof-eab27ea2": ["975 Hilyard St", "975 Hilyard St"],
      },
    },
    "e-fifteenth-pair-exterior": {
      descriptor: config?.e_fifteenth_pair_site,
      directory: "e-fifteenth-pair-exterior-review",
      groundNode: "e-fifteenth-pair-approaches",
      ids: ["roof-0c745864", "east-fifteenth-alley-apartments"],
      sourceBatchIds: ["roof-0c745864"],
      newBuildingIds: ["east-fifteenth-alley-apartments"],
      registeredAddresses: {
        "roof-0c745864": ["E 15th Apartments · Street Building", "E 15th Ave"],
        "east-fifteenth-alley-apartments": [
          "E 15th Apartments · Alley Building",
          "E 15th Alley",
        ],
      },
    },
    "rive-eugene-exterior": {
      descriptor: config?.rive_eugene_exterior_site,
      directory: "rive-eugene-exterior-review",
      groundNode: "rive-eugene-approaches",
      routeToApproaches: true,
      ids: ["roof-513d7fee"],
      sourceBatchIds: ["roof-513d7fee"],
      registeredAddresses: {
        "roof-513d7fee": ["The Rive Eugene", "700 E Broadway"],
      },
    },
    "alder-thirteenth-exterior": {
      descriptor: config?.alder_thirteenth_exterior_site,
      directory: "alder-thirteenth-exterior-review",
      groundNode: "alder-thirteenth-ground",
      routeToApproaches: true,
      ids: [
        "alder-thirteenth-corner",
        "alder-gopuran",
        "roof-5ed4d412",
        "alder-duck-store",
      ],
      sourceBatchIds: ["roof-5ed4d412"],
      absorbedIds: ["roof-f6be07b4"],
      splitBuildings: {
        "alder-thirteenth-corner": "roof-5ed4d412",
        "alder-gopuran": "roof-5ed4d412",
        "alder-duck-store": "roof-5ed4d412",
      },
      registeredAddresses: {
        "alder-thirteenth-corner": [
          "Alder & 13th Corner Shops",
          "1285 Alder St",
        ],
        "alder-gopuran": [
          "Gopuran Building · Webfoot Bar & Grill",
          "839 E 13th Ave",
        ],
        "roof-5ed4d412": ["Flock13", "871 E 13th Ave"],
        "alder-duck-store": ["The Duck Store", "895 E 13th Ave"],
      },
    },
    "millrace-fairmount-exterior": {
      descriptor: config?.millrace_fairmount_exterior_site,
      directory: "millrace-fairmount-exterior-review",
      groundNode: "millrace-fairmount-approaches",
      routeToApproaches: true,
      ids: ["roof-4bcb9296", "roof-01c76e05", "roof-e7592432", "roof-f9fb8501"],
      sourceBatchIds: [
        "roof-4bcb9296",
        "roof-01c76e05",
        "roof-e7592432",
        "roof-f9fb8501",
      ],
      registeredAddresses: {
        "roof-4bcb9296": ["Alpha Tau Omega Chapter House", "1000 Alder St"],
        "roof-01c76e05": ["1956 E 15th Avenue", "1956 E 15th Ave"],
        "roof-e7592432": ["1871 E 19th Avenue", "1871 E 19th Ave"],
        "roof-f9fb8501": ["Walnut Alley Garage Building", "Walnut Aly"],
      },
    },
    "fairmount-kincaid-exterior": {
      descriptor: config?.fairmount_kincaid_exterior_site,
      directory: "fairmount-kincaid-exterior-review",
      groundNode: "fairmount-kincaid-approaches",
      routeToApproaches: true,
      ids: [
        "roof-046adce7",
        "roof-58551b68",
        "roof-622a75af",
        "roof-c4396bfc",
        "roof-d427a5ce",
        "roof-c54987d3",
        "roof-d6ddd6ae",
        "roof-f414e967",
      ],
      sourceBatchIds: [
        "roof-046adce7",
        "roof-58551b68",
        "roof-622a75af",
        "roof-c4396bfc",
        "roof-d427a5ce",
        "roof-c54987d3",
        "roof-d6ddd6ae",
        "roof-f414e967",
      ],
      registeredAddresses: {
        "roof-046adce7": ["1517 Walnut Street", "1517 Walnut St"],
        "roof-58551b68": ["1680 Walnut Street", "1680 Walnut St"],
        "roof-622a75af": ["1671 Walnut Street", "1671 Walnut St"],
        "roof-c4396bfc": ["1991 E 19th Avenue", "1991 E 19th Ave"],
        "roof-d427a5ce": ["1931 Moss Street", "1931 Moss St"],
        "roof-c54987d3": ["1879 Moss Street", "1879 Moss St"],
        "roof-d6ddd6ae": ["Pi Beta Phi Chapter House", "1518 Kincaid St"],
        "roof-f414e967": ["Alpha Chi Omega Chapter House", "850 E 15th Ave"],
      },
    },
    "southeast-fairmount-exterior": {
      descriptor: config?.southeast_fairmount_exterior_site,
      directory: "southeast-fairmount-exterior-review",
      groundNode: "southeast-fairmount-approaches",
      routeToApproaches: true,
      ids: [
        "roof-e0d560b4",
        "roof-169a7b78",
        "roof-699d6c1e",
        "roof-22175da6",
        "roof-05727176",
        "roof-b2800bfe",
      ],
      sourceBatchIds: [
        "roof-e0d560b4",
        "roof-169a7b78",
        "roof-699d6c1e",
        "roof-22175da6",
        "roof-05727176",
        "roof-b2800bfe",
      ],
      registeredAddresses: {
        "roof-e0d560b4": ["281 Sunset Drive", "281 Sunset Dr"],
        "roof-169a7b78": ["365 Sunset Drive", "365 Sunset Dr"],
        "roof-699d6c1e": ["366 Sunset Drive", "366 Sunset Dr"],
        "roof-22175da6": ["2281 Rose Lane", "2281 Rose Ln"],
        "roof-05727176": ["2275 Rose Lane", "2275 Rose Ln"],
        "roof-b2800bfe": ["2293 Birch Lane", "2293 Birch Ln"],
      },
    },
    "northwest-infill-exterior": {
      descriptor: config?.northwest_infill_exterior_site,
      directory: "northwest-infill-exterior-review",
      groundNode: "northwest-infill-approaches",
      routeToApproaches: true,
      ids: ["roof-8007cb2f", "roof-3961d925", "roof-d830368a", "roof-ec27d788"],
      sourceBatchIds: [
        "roof-8007cb2f",
        "roof-3961d925",
        "roof-d830368a",
        "roof-ec27d788",
      ],
      registeredAddresses: {
        "roof-8007cb2f": ["Phi Kappa Psi Chapter House", "729 E 11th Ave"],
        "roof-3961d925": ["642 East 8th Avenue", "642 E 8th Ave"],
        "roof-d830368a": [
          "1414 Alder Street / 790 E 14th Ave",
          "1414 Alder St",
        ],
        "roof-ec27d788": ["Eugene Steam Plant", "701 Annie Mims Ln"],
      },
    },
    "fairmount-summit-hamble": {
      descriptor: config?.fairmount_summit_hamble_site,
      directory: "fairmount-summit-hamble-review",
      groundNode: "fairmount-summit-hamble-approaches",
      routeToApproaches: true,
      ids: [
        "roof-0b345e8f",
        "roof-3d7a4503",
        "roof-61b268c3",
        "roof-d709354e",
        "roof-8d4cf396",
        "roof-3466a919",
        "roof-b8804a72",
        "roof-efd79ec7",
        "roof-d25e3df8",
        "roof-636f0355",
        "roof-b2bced50",
        "roof-99cda8af",
        "roof-f5434b03",
      ],
      sourceBatchIds: [
        "roof-0b345e8f",
        "roof-3d7a4503",
        "roof-61b268c3",
        "roof-d709354e",
        "roof-8d4cf396",
        "roof-3466a919",
        "roof-b8804a72",
        "roof-efd79ec7",
        "roof-d25e3df8",
        "roof-636f0355",
        "roof-b2bced50",
        "roof-99cda8af",
        "roof-f5434b03",
      ],
      registeredAddresses: {
        "roof-0b345e8f": [
          "2081 Fairmount Boulevard",
          "2081 Fairmount Boulevard",
        ],
        "roof-3d7a4503": [
          "2091 Fairmount Boulevard",
          "2091 Fairmount Boulevard",
        ],
        "roof-61b268c3": [
          "2095 Fairmount Boulevard",
          "2095 Fairmount Boulevard",
        ],
        "roof-d709354e": [
          "2105 Fairmount Boulevard",
          "2105 Fairmount Boulevard",
        ],
        "roof-8d4cf396": [
          "2125 Fairmount Boulevard",
          "2125 Fairmount Boulevard",
        ],
        "roof-3466a919": [
          "2209 Fairmount Boulevard",
          "2209 Fairmount Boulevard",
        ],
        "roof-b8804a72": ["2130 Summit Avenue", "2130 Summit Avenue"],
        "roof-efd79ec7": ["2195 Summit Avenue", "2195 Summit Avenue"],
        "roof-d25e3df8": ["2197 Summit Avenue", "2197 Summit Avenue"],
        "roof-636f0355": ["2110 Hamble Avenue", "2110 Hamble Avenue"],
        "roof-b2bced50": ["2140 Hamble Avenue", "2140 Hamble Avenue"],
        "roof-99cda8af": ["2171 Hamble Avenue", "2171 Hamble Avenue"],
        "roof-f5434b03": ["2010 Hubbard Lane", "2010 Hubbard Lane"],
      },
    },
    "orchard-villard-hillside": {
      descriptor: config?.orchard_villard_hillside_site,
      directory: "orchard-villard-hillside-review",
      groundNode: "orchard-villard-approaches",
      routeToApproaches: true,
      ids: [
        "roof-6133a11a",
        "east-nineteenth-1978",
        "roof-28a8e5f0",
        "orchard-1966",
        "roof-29aaebb6",
        "orchard-1994",
        "roof-7e12343c",
        "villard-1963",
        "roof-2cb36f2e",
        "villard-1946",
        "roof-b315719c",
        "villard-outbuilding-171184",
        "roof-d4f7e70c",
        "roof-a53a0c57",
        "roof-b23b2dec",
        "roof-31f27b04",
      ],
      sourceBatchIds: [
        "roof-6133a11a",
        "roof-28a8e5f0",
        "roof-29aaebb6",
        "roof-7e12343c",
        "roof-2cb36f2e",
        "roof-b315719c",
        "roof-d4f7e70c",
        "roof-a53a0c57",
        "roof-b23b2dec",
        "roof-31f27b04",
      ],
      splitBuildings: {
        "east-nineteenth-1978": "roof-6133a11a",
        "orchard-1966": "roof-29aaebb6",
        "orchard-1994": "roof-7e12343c",
        "villard-1963": "roof-2cb36f2e",
        "villard-1946": "roof-b315719c",
        "villard-outbuilding-171184": "roof-d4f7e70c",
      },
      registeredAddresses: {
        "roof-6133a11a": ["1910 / 1924 Orchard Street", "1910 Orchard Street"],
        "east-nineteenth-1978": [
          "1978 East 19th Avenue",
          "1978 East 19th Avenue",
        ],
        "roof-28a8e5f0": ["1935 / 1937 Orchard Street", "1937 Orchard Street"],
        "orchard-1966": [
          "1966 Orchard Street / 1965 Orchard Alley",
          "1966 Orchard Street",
        ],
        "roof-29aaebb6": ["1950 Orchard Street", "1950 Orchard Street"],
        "orchard-1994": [
          "1994 Orchard Street / 1991 Orchard Alley",
          "1994 Orchard Street",
        ],
        "roof-7e12343c": ["1990 Orchard Street", "1990 Orchard Street"],
        "villard-1963": ["1963 Villard Street", "1963 Villard Street"],
        "roof-2cb36f2e": ["1947 Villard Street", "1947 Villard Street"],
        "villard-1946": ["1946 Villard Street", "1946 Villard Street"],
        "roof-b315719c": ["1964 Villard Street", "1964 Villard Street"],
        "villard-outbuilding-171184": [
          "Detached outbuilding near 1996 Villard",
          "1996 Villard Street",
        ],
        "roof-d4f7e70c": ["1996 Villard Street", "1996 Villard Street"],
        "roof-a53a0c57": ["2012 Villard Street", "2012 Villard Street"],
        "roof-b23b2dec": ["2075 Villard Street", "2075 Villard Street"],
        "roof-31f27b04": [
          "1999 Fairmount Boulevard",
          "1999 Fairmount Boulevard",
        ],
      },
    },
    "fairmount-moss-slope": {
      descriptor: config?.fairmount_moss_slope_site,
      directory: "fairmount-moss-slope-review",
      groundNode: "fairmount-moss-slope-approaches",
      routeToApproaches: true,
      ids: [
        "roof-b8fa3497",
        "roof-6a4f93e6",
        "roof-100b2613",
        "roof-136be56b",
        "roof-f6bcefaf",
        "roof-5245ef5e",
        "roof-daca02ed",
        "roof-d5a8b80c",
        "roof-b62a90ef",
        "east19-1836",
        "fairmount-2241",
      ],
      newBuildingIds: ["east19-1836", "fairmount-2241"],
      sourceBatchIds: [
        "roof-b8fa3497",
        "roof-6a4f93e6",
        "roof-100b2613",
        "roof-136be56b",
        "roof-f6bcefaf",
        "roof-5245ef5e",
        "roof-daca02ed",
        "roof-d5a8b80c",
        "roof-b62a90ef",
      ],
      registeredAddresses: {
        "roof-b8fa3497": ["1864 Moss Street", "1864 Moss Street"],
        "roof-6a4f93e6": ["1926 Moss Street", "1926 Moss Street"],
        "roof-100b2613": [
          "1911 Moss Street / 1820 East 19th Avenue",
          "1911 Moss Street",
        ],
        "roof-136be56b": ["2303 McMorran Avenue", "2303 McMorran Avenue"],
        "roof-f6bcefaf": [
          "2288 Fairmount Boulevard",
          "2288 Fairmount Boulevard",
        ],
        "roof-5245ef5e": [
          "2309 Fairmount Boulevard",
          "2309 Fairmount Boulevard",
        ],
        "roof-daca02ed": [
          "2323 Fairmount Boulevard",
          "2323 Fairmount Boulevard",
        ],
        "roof-d5a8b80c": [
          "2275 Fairmount Boulevard",
          "2275 Fairmount Boulevard",
        ],
        "roof-b62a90ef": [
          "2415 Fairmount Boulevard",
          "2415 Fairmount Boulevard",
        ],
        "east19-1836": ["1836 East 19th Avenue", "1836 East 19th Avenue"],
        "fairmount-2241": [
          "2241 Fairmount Boulevard",
          "2241 Fairmount Boulevard",
        ],
      },
    },
    "columbia-moss-frontages": {
      descriptor: config?.columbia_moss_frontages_site,
      directory: "columbia-moss-frontages-review",
      groundNode: "columbia-moss-approaches",
      routeToApproaches: true,
      ids: [
        "roof-99c1fdae",
        "east18-alley-1472",
        "east19-1473",
        "roof-bf2551ce",
        "emerald-apartments-north",
        "roof-825d1e23",
        "east19-1445",
        "roof-2d8c25c4",
        "roof-c0961aa0",
        "roof-424f6339",
        "roof-f262cbec",
        "columbia-2003",
        "roof-c03b3a5d",
        "roof-7cc5046c",
      ],
      newBuildingIds: ["columbia-2003"],
      sourceBatchIds: [
        "roof-99c1fdae",
        "roof-bf2551ce",
        "roof-825d1e23",
        "roof-2d8c25c4",
        "roof-c0961aa0",
        "roof-424f6339",
        "roof-f262cbec",
        "roof-c03b3a5d",
        "roof-7cc5046c",
      ],
      splitBuildings: {
        "east18-alley-1472": "roof-99c1fdae",
        "east19-1473": "roof-99c1fdae",
        "emerald-apartments-north": "roof-825d1e23",
        "east19-1445": "roof-825d1e23",
      },
      registeredAddresses: {
        "roof-99c1fdae": ["McMenamins East 19th Café", "1485 East 19th Avenue"],
        "east18-alley-1472": ["1472 East 18th Alley", "1472 East 18th Alley"],
        "east19-1473": ["Studio One Café", "1473 East 19th Avenue"],
        "roof-bf2551ce": [
          "Prince Puckler's / Sweet Life Petite",
          "1605 East 19th Avenue",
        ],
        "emerald-apartments-north": [
          "Emerald Apartments — North Building",
          "1877 Emerald Street",
        ],
        "roof-825d1e23": [
          "Emerald Apartments — South Building",
          "1877 Emerald Street",
        ],
        "east19-1445": ["1445 East 19th Avenue", "1445 East 19th Avenue"],
        "roof-2d8c25c4": ["1980 Columbia Street", "1980 Columbia Street"],
        "roof-c0961aa0": ["1935 Columbia Street", "1935 Columbia Street"],
        "roof-424f6339": ["1895 Columbia Street", "1895 Columbia Street"],
        "roof-f262cbec": ["1969 Columbia Street", "1969 Columbia Street"],
        "columbia-2003": ["2003 Columbia Street", "2003 Columbia Street"],
        "roof-c03b3a5d": [
          "2367 Fairmount Boulevard",
          "2367 Fairmount Boulevard",
        ],
        "roof-7cc5046c": ["1964 Moss Street", "1964 Moss Street"],
      },
    },
    "agate-emerald-frontages": {
      descriptor: config?.agate_emerald_frontages_site,
      directory: "agate-emerald-frontages-review",
      groundNode: "agate-emerald-approaches",
      routeToApproaches: true,
      ids: [
        "roof-a40877e3",
        "roof-a7890474",
        "roof-aba1513b",
        "roof-28502c01",
        "east20-1470",
        "roof-06636962",
        "roof-58d0ebc7",
        "roof-5a32e480",
      ],
      sourceBatchIds: [
        "roof-a40877e3",
        "roof-a7890474",
        "roof-aba1513b",
        "roof-28502c01",
        "roof-06636962",
        "roof-58d0ebc7",
        "roof-5a32e480",
      ],
      absorbedIds: ["roof-879f17f5"],
      splitBuildings: { "east20-1470": "roof-28502c01" },
      registeredAddresses: {
        "roof-a40877e3": ["The Studies at 19th", "1370 East 19th Avenue"],
        "roof-a7890474": ["Tom's Market", "1490 East 19th Avenue"],
        "roof-aba1513b": ["1442 East 20th Avenue", "1442 East 20th Avenue"],
        "roof-28502c01": ["1460 East 20th Avenue", "1460 East 20th Avenue"],
        "east20-1470": ["1470 East 20th Avenue", "1470 East 20th Avenue"],
        "roof-06636962": ["1473 East 20th Avenue", "1473 East 20th Avenue"],
        "roof-58d0ebc7": [
          "1495 East 21st Avenue / 2092 Agate Street",
          "1495 East 21st Avenue",
        ],
        "roof-5a32e480": ["1370 East 21st Avenue", "1370 East 21st Avenue"],
      },
    },
    "emerald-onyx-frontages": {
      descriptor: config?.emerald_onyx_frontages_site,
      directory: "emerald-onyx-frontages-review",
      groundNode: "emerald-onyx-approaches",
      routeToApproaches: true,
      ids: [
        "roof-9752966f",
        "onyx-1959-west",
        "roof-b1caff97",
        "roof-b7484145",
        "emerald-alley-1946",
        "emerald-alley-1940",
        "roof-b36b0ddb",
        "roof-c0e5df84",
        "roof-90b1b81e",
        "roof-4ad5629d",
        "east20-1425",
      ],
      newBuildingIds: ["emerald-alley-1940"],
      sourceBatchIds: [
        "roof-9752966f",
        "roof-b1caff97",
        "roof-b7484145",
        "roof-b36b0ddb",
        "roof-c0e5df84",
        "roof-90b1b81e",
        "roof-4ad5629d",
      ],
      splitBuildings: {
        "onyx-1959-west": "roof-9752966f",
        "emerald-alley-1946": "roof-b7484145",
        "east20-1425": "roof-4ad5629d",
      },
      registeredAddresses: {
        "roof-9752966f": ["1975–1981 Onyx Street", "1975 Onyx Street"],
        "onyx-1959-west": [
          "1959 Onyx Street – West Building",
          "1959 Onyx Street",
        ],
        "roof-b1caff97": ["1314 East 21st Avenue", "1314 East 21st Avenue"],
        "roof-b7484145": [
          "1959 Onyx Street – Alley Building",
          "1959 Onyx Street",
        ],
        "emerald-alley-1946": ["1946 Emerald Alley", "1946 Emerald Alley"],
        "emerald-alley-1940": ["1940 Emerald Alley", "1940 Emerald Alley"],
        "roof-b36b0ddb": ["1361 East 21st Avenue", "1361 East 21st Avenue"],
        "roof-c0e5df84": ["2072 Emerald Street", "2072 Emerald Street"],
        "roof-90b1b81e": [
          "1407 East 21st Avenue / 2087 Emerald Street",
          "1407 East 21st Avenue",
        ],
        "roof-4ad5629d": ["1405 East 20th Avenue", "1405 East 20th Avenue"],
        "east20-1425": ["1425 East 20th Avenue", "1425 East 20th Avenue"],
      },
    },
    "onyx-university-frontages": {
      descriptor: config?.onyx_university_frontages_site,
      directory: "onyx-university-frontages-review",
      groundNode: "onyx-university-approaches",
      routeToApproaches: true,
      ids: [
        "roof-14401667",
        "east20-1256",
        "roof-e01f1a78",
        "roof-a1c68f4b",
        "roof-df1012d3",
        "roof-bece0173",
        "east19-1262",
        "roof-96f32dee",
      ],
      sourceBatchIds: [
        "roof-14401667",
        "roof-e01f1a78",
        "roof-a1c68f4b",
        "roof-df1012d3",
        "roof-bece0173",
        "roof-96f32dee",
      ],
      splitBuildings: {
        "east20-1256": "roof-e01f1a78",
        "east19-1262": "roof-96f32dee",
      },
      registeredAddresses: {
        "roof-14401667": ["Trinity House", "1987 University Street"],
        "east20-1256": ["1256 East 20th Avenue", "1256 East 20th Avenue"],
        "roof-e01f1a78": [
          "1276 East 20th Avenue / 2008 Onyx Street",
          "1276 East 20th Avenue",
        ],
        "roof-a1c68f4b": ["1237 East 21st Avenue", "1237 East 21st Avenue"],
        "roof-df1012d3": ["2066 University Street", "2066 University Street"],
        "roof-bece0173": ["1136 East 20th Avenue", "1136 East 20th Avenue"],
        "east19-1262": ["1262 East 19th Avenue", "1262 East 19th Avenue"],
        "roof-96f32dee": ["1931 Onyx Alley", "1931 Onyx Alley"],
      },
    },
    "southern-boundary-exterior": {
      descriptor: config?.southern_boundary_exterior_site,
      directory: "southern-boundary-exterior-review",
      groundNode: "southern-boundary-approaches",
      routeToApproaches: true,
      ids: [
        "harris-2061",
        "roof-6594bfe8",
        "roof-d44341e6",
        "roof-24910633",
        "roof-8d87ddf2",
        "roof-496beafd",
        "university-2028-rear",
        "roof-7873e057",
      ],
      sourceBatchIds: [
        "roof-6594bfe8",
        "roof-d44341e6",
        "roof-24910633",
        "roof-8d87ddf2",
        "roof-496beafd",
        "roof-7873e057",
      ],
      splitBuildings: {
        "harris-2061": "roof-6594bfe8",
        "university-2028-rear": "roof-7873e057",
      },
      registeredAddresses: {
        "harris-2061": ["2061 Harris Street", "2061 Harris Street"],
        "roof-6594bfe8": ["2039 Harris Street", "2039 Harris Street"],
        "roof-d44341e6": ["1025 East 21st Avenue", "1025 East 21st Avenue"],
        "roof-24910633": ["2086 Potter Street", "2086 Potter Street"],
        "roof-8d87ddf2": ["2089 Potter Street", "2089 Potter Street"],
        "roof-496beafd": ["2000 University Street", "2000 University Street"],
        "university-2028-rear": [
          "2028 University Rear Building",
          "2028 University Street",
        ],
        "roof-7873e057": ["2028 University Street", "2028 University Street"],
      },
    },
    "harris-potter-exterior": {
      descriptor: config?.harris_potter_exterior_site,
      directory: "harris-potter-exterior-review",
      groundNode: "harris-potter-approaches",
      routeToApproaches: true,
      ids: [
        "roof-5be21a96",
        "potter-1938",
        "potter-1976",
        "roof-b0798c1b",
        "roof-ae77fb78",
        "roof-da8142c0",
        "harris-1911",
        "roof-84ccdaf5",
        "harris-1941",
        "roof-7e72b4ca",
      ],
      sourceBatchIds: [
        "roof-5be21a96",
        "roof-b0798c1b",
        "roof-ae77fb78",
        "roof-da8142c0",
        "roof-84ccdaf5",
        "roof-7e72b4ca",
      ],
      splitBuildings: {
        "potter-1938": "roof-5be21a96",
        "potter-1976": "roof-b0798c1b",
        "harris-1911": "roof-84ccdaf5",
        "harris-1941": "roof-7e72b4ca",
      },
      registeredAddresses: {
        "roof-5be21a96": ["1926 Potter Street", "1926 Potter Street"],
        "potter-1938": ["1938 Potter Street", "1938 Potter Street"],
        "potter-1976": ["1976 Potter Street", "1976 Potter Street"],
        "roof-b0798c1b": ["1992–1994 Potter Street", "1992 Potter Street"],
        "roof-ae77fb78": ["1045 East 20th Avenue", "1045 East 20th Avenue"],
        "roof-da8142c0": ["1096 East 20th Avenue", "1096 East 20th Avenue"],
        "harris-1911": ["1911 Harris Street", "1911 Harris Street"],
        "roof-84ccdaf5": ["1925 Harris Street", "1925 Harris Street"],
        "harris-1941": ["1941 Harris Street", "1941 Harris Street"],
        "roof-7e72b4ca": ["1959 Harris Street", "1959 Harris Street"],
      },
    },
    "potter-university-exterior": {
      descriptor: config?.potter_university_exterior_site,
      directory: "potter-university-exterior-review",
      groundNode: "potter-university-approaches",
      routeToApproaches: true,
      ids: [
        "roof-c82780ef",
        "roof-77b9b163",
        "roof-09fb4f67",
        "roof-b6ce8f92",
        "roof-b74469f2",
        "university-1940",
        "university-1960",
        "university-1976",
      ],
      sourceBatchIds: [
        "roof-c82780ef",
        "roof-77b9b163",
        "roof-09fb4f67",
        "roof-b6ce8f92",
        "roof-b74469f2",
      ],
      absorbedIds: ["roof-7b05979c"],
      splitBuildings: {
        "university-1940": "roof-b74469f2",
        "university-1960": "roof-b74469f2",
        "university-1976": "roof-b74469f2",
      },
      registeredAddresses: {
        "roof-c82780ef": ["Central Lutheran Church", "1857 Potter Street"],
        "roof-77b9b163": [
          "1081–1083 East 19th Avenue",
          "1081 East 19th Avenue",
        ],
        "roof-09fb4f67": [
          "1085–1089 East 19th Avenue",
          "1085 East 19th Avenue",
        ],
        "roof-b6ce8f92": ["1136 East 19th Avenue", "1136 East 19th Avenue"],
        "roof-b74469f2": ["1910 University Street", "1910 University Street"],
        "university-1940": ["1940 University Street", "1940 University Street"],
        "university-1960": ["1960 University Street", "1960 University Street"],
        "university-1976": ["1976 University Street", "1976 University Street"],
      },
    },
    "south-campus-frontages": {
      descriptor: config?.south_campus_frontages_site,
      directory: "south-campus-frontages-review",
      groundNode: "south-campus-frontage-walks",
      routeToApproaches: true,
      ids: [
        "roof-213417ee",
        "roof-649a6455",
        "roof-35a23996",
        "roof-7b1d50e1",
        "roof-16023474",
        "roof-b3d39b2f",
      ],
      sourceBatchIds: [
        "roof-213417ee",
        "roof-649a6455",
        "roof-35a23996",
        "roof-7b1d50e1",
        "roof-16023474",
        "roof-b3d39b2f",
      ],
      registeredAddresses: {
        "roof-213417ee": ["Theta Chi Chapter House", "1125 East 19th Avenue"],
        "roof-649a6455": [
          "Delta Tau Delta Chapter House",
          "1886 University Street",
        ],
        "roof-35a23996": ["1860 Potter Street", "1860 Potter Street"],
        "roof-7b1d50e1": ["1930 Onyx Street", "1930 Onyx Street"],
        "roof-16023474": ["1941 University Street", "1941 University Street"],
        "roof-b3d39b2f": ["1976 Onyx Street", "1976 Onyx Street"],
      },
    },
    "onyx-university-split-exterior": {
      descriptor: config?.onyx_university_split_site,
      directory: "onyx-university-split-exterior-review",
      groundNode: "onyx-university-walks",
      routeToApproaches: true,
      ids: [
        "roof-b0cb5ef5",
        "onyx-1870-west",
        "roof-48d494fc",
        "e19-1208-rear-garage",
        "roof-27720a8d",
        "onyx-alley-1840",
      ],
      sourceBatchIds: ["roof-b0cb5ef5", "roof-48d494fc", "roof-27720a8d"],
      splitBuildings: {
        "onyx-1870-west": "roof-b0cb5ef5",
        "e19-1208-rear-garage": "roof-48d494fc",
        "onyx-alley-1840": "roof-27720a8d",
      },
      registeredAddresses: {
        "roof-b0cb5ef5": ["1866 Onyx Street", "1866 Onyx Street"],
        "onyx-1870-west": ["1870 Onyx Street", "1870 Onyx Street"],
        "roof-48d494fc": ["1208 East 19th House", "1208 East 19th Avenue"],
        "e19-1208-rear-garage": [
          "1208 East 19th Rear Garage",
          "1208 East 19th Avenue",
        ],
        "roof-27720a8d": ["1825 University Street", "1825 University Street"],
        "onyx-alley-1840": ["1840 Onyx Alley", "1840 Onyx Alley"],
      },
    },
    "south-university-exterior": {
      descriptor: config?.south_university_exterior_site,
      directory: "south-university-exterior-review",
      groundNode: "south-university-entry-walks",
      routeToApproaches: true,
      ids: ["roof-b048deca", "roof-82ccbe9b", "roof-e0385ede"],
      sourceBatchIds: ["roof-b048deca", "roof-82ccbe9b", "roof-e0385ede"],
      registeredAddresses: {
        "roof-b048deca": ["Sigma Nu Chapter House", "1851 Onyx Street"],
        "roof-82ccbe9b": ["1306 East 18th Avenue", "1306 East 18th Avenue"],
        "roof-e0385ede": ["1874 Emerald Street", "1874 Emerald Street"],
      },
    },
    "onyx-house-exterior": {
      descriptor: config?.onyx_house_exterior_site,
      directory: "onyx-house-exterior-review",
      groundNode: "onyx-house-approaches",
      routeToApproaches: true,
      ids: ["roof-9dfbc1af"],
      sourceBatchIds: ["roof-9dfbc1af"],
      registeredAddresses: {
        "roof-9dfbc1af": ["Onyx House", "1850 Onyx Street"],
      },
    },
    "east-nineteenth-court-exterior": {
      descriptor: config?.east_nineteenth_court_site,
      directory: "east-nineteenth-court-exterior-review",
      groundNode: "east-nineteenth-court-approach",
      routeToApproaches: true,
      ids: ["roof-0eb55b68"],
      sourceBatchIds: ["roof-0eb55b68"],
      registeredAddresses: {
        "roof-0eb55b68": ["1340 East 19th Apartments", "1340 East 19th Avenue"],
      },
    },
    "alton-franklin-exterior": {
      descriptor: config?.alton_franklin_exterior_site,
      directory: "alton-franklin-exterior-review",
      groundNode: "alton-franklin-paving",
      ids: ["roof-abe13121", "alton-baker-shelter-one", "roof-4b32d15b"],
      sourceBatchIds: ["roof-abe13121", "roof-4b32d15b"],
      newBuildingIds: ["alton-baker-shelter-one"],
      absorbedIds: ["roof-885f60ba", "roof-6dc8ed19"],
      registeredAddresses: {
        "roof-abe13121": ["Alton Baker Park Shelter 2", "632 Day Island Road"],
        "alton-baker-shelter-one": [
          "Alton Baker Park Shelter 1",
          "632 Day Island Road",
        ],
        "roof-4b32d15b": [
          "Best Western New Oregon · Franklin Wing",
          "1655 Franklin Boulevard",
        ],
      },
    },
    "west-boundary-exterior": {
      descriptor: config?.west_boundary_exterior_site,
      directory: "west-boundary-exterior-review",
      groundNode: "west-boundary-approaches",
      routeToApproaches: true,
      ids: [
        "roof-dcd48157",
        "e16-alley-634-640",
        "e16-alley-630-632",
        "roof-4dff8a97",
      ],
      sourceBatchIds: ["roof-dcd48157", "roof-4dff8a97"],
      splitBuildings: {
        "e16-alley-634-640": "roof-dcd48157",
        "e16-alley-630-632": "roof-dcd48157",
      },
      registeredAddresses: {
        "roof-dcd48157": ["625–627 East 17th Avenue", "625 E 17th Ave"],
        "e16-alley-634-640": ["634–640 East 16th Alley", "638 E 16th Aly"],
        "e16-alley-630-632": ["630–632 East 16th Alley", "630 E 16th Aly"],
        "roof-4dff8a97": [
          "631 East 19th Avenue · East Building",
          "631 E 19th Ave",
        ],
      },
    },
    "hilyard-south-exterior": {
      descriptor: config?.hilyard_south_exterior_site,
      directory: "hilyard-south-exterior-review",
      groundNode: "hilyard-south-approaches",
      routeToApproaches: true,
      ids: ["roof-f92cf968", "roof-10b438f6", "roof-769d99e6", "roof-57ecbd31"],
      sourceBatchIds: [
        "roof-f92cf968",
        "roof-10b438f6",
        "roof-769d99e6",
        "roof-57ecbd31",
      ],
      registeredAddresses: {
        "roof-f92cf968": ["Parkside Place", "1448 Hilyard St"],
        "roof-10b438f6": ["1131 East 20th Avenue", "1131 East 20th Avenue"],
        "roof-769d99e6": ["1039 East 21st Avenue", "1039 East 21st Avenue"],
        "roof-57ecbd31": ["1145 East 21st Avenue", "1145 East 21st Avenue"],
      },
    },
    "alder-harris-exterior": {
      descriptor: config?.alder_harris_exterior_site,
      directory: "alder-harris-exterior-review",
      groundNode: "alder-harris-approaches",
      routeToApproaches: true,
      ids: [
        "roof-71f4af04",
        "roof-0587b8ad",
        "roof-80aadee0",
        "roof-73a1a032",
        "roof-1a3a0846",
        "roof-c7815e30",
      ],
      sourceBatchIds: [
        "roof-71f4af04",
        "roof-0587b8ad",
        "roof-80aadee0",
        "roof-73a1a032",
        "roof-1a3a0846",
        "roof-c7815e30",
      ],
      registeredAddresses: {
        "roof-71f4af04": ["Lorax Manner", "1648 Alder St"],
        "roof-0587b8ad": ["Campbell Club", "1670 Alder St"],
        "roof-80aadee0": ["Woodside Manor", "1810 Harris St"],
        "roof-73a1a032": ["1065–1079 East 19th Avenue", "1065–1079 E 19th Ave"],
        "roof-1a3a0846": ["750 East 18th Avenue", "750 E 18th Ave"],
        "roof-c7815e30": ["746 East 19th Avenue", "746 E 19th Ave"],
      },
    },
    "east-nineteenth-exterior": {
      descriptor: config?.east_nineteenth_exterior_site,
      directory: "east-nineteenth-exterior-review",
      groundNode: "east-nineteenth-approaches",
      routeToApproaches: true,
      ids: ["roof-600a0bef", "roof-a8318b83", "roof-028770d6"],
      sourceBatchIds: ["roof-600a0bef", "roof-a8318b83", "roof-028770d6"],
      registeredAddresses: {
        "roof-600a0bef": ["Sigma Chi Chapter House", "1440 E 19th Ave"],
        "roof-a8318b83": [
          "1456 East 19th Avenue / 1458 East 19th Avenue",
          "1456 and 1458 E 19th Ave",
        ],
        "roof-028770d6": ["1355 East 19th Avenue", "1355 E 19th Ave"],
      },
    },
    "parkside-exterior": {
      descriptor: config?.parkside_exterior_site,
      directory: "parkside-exterior-review",
      groundNode: "parkside-driveway",
      ids: ["roof-6f59699a"],
      sourceBatchIds: ["roof-6f59699a"],
      registeredAddresses: {
        "roof-6f59699a": ["2300 Parkside Lane", "2300 Parkside Ln"],
      },
    },
    "millrace-research-exterior": {
      descriptor: config?.millrace_research_exterior_site,
      directory: "millrace-research-exterior-review",
      groundNode: "millrace-research-approach",
      routeToApproaches: true,
      ids: ["roof-8bd064b7"],
      sourceBatchIds: ["roof-8bd064b7"],
      registeredAddresses: {
        "roof-8bd064b7": [
          "1800 Millrace Drive / 1850 Millrace Drive",
          "1800 and 1850 Millrace Dr",
        ],
      },
    },
    "western-exterior": {
      descriptor: config?.western_exterior_site,
      directory: "western-exterior-review",
      groundNode: "western-exterior-approaches",
      ids: ["roof-fd954de8", "roof-7c73e16e", "roof-990dddda", "roof-be421cdc"],
      sourceBatchIds: [
        "roof-fd954de8",
        "roof-7c73e16e",
        "roof-990dddda",
        "roof-be421cdc",
      ],
      registeredAddresses: {
        "roof-fd954de8": [
          "Marlatt Apartments · Courtyard Building",
          "749–773 E 17th Ave",
        ],
        "roof-7c73e16e": ["Marlatt Apartments · West Wing", "749 E 17th Ave"],
        "roof-990dddda": ["Marlatt Apartments · East Wing", "761 E 17th Ave"],
        "roof-be421cdc": ["EWEB Willamette Substation", "777 Annie Mims Ln"],
      },
    },
    "east-station-exterior": {
      descriptor: config?.east_station_site,
      directory: "east-station-exterior-review",
      groundNode: "east-station-frontages",
      ids: ["roof-4cf339e8", "roof-ce1d33a1", "roof-38958a7f"],
      sourceBatchIds: ["roof-4cf339e8", "roof-ce1d33a1", "roof-38958a7f"],
      registeredNames: {
        "roof-4cf339e8": "UO Police Department East Station",
        "roof-ce1d33a1": "UOPD East Station Annex A",
        "roof-38958a7f": "UOPD East Station Annex B",
      },
    },
    "bushnell-east-exterior": {
      descriptor: config?.bushnell_east_site,
      directory: "bushnell-east-exterior-review",
      groundNode: "bushnell-east-approaches",
      ids: ["roof-b1c16a4e", "roof-e3dcdde4"],
      sourceBatchIds: ["roof-b1c16a4e", "roof-e3dcdde4"],
      registeredAddresses: {
        "roof-b1c16a4e": [
          "Kellenberger Library · Lottie Price Music Building & Ross Evans Chapel",
          "1188 Kincaid St",
        ],
        "roof-e3dcdde4": ["Burke-Griffeth Hall", "875 E 12th Ave"],
      },
    },
    "goodrich-quad-exterior": {
      descriptor: config?.goodrich_quad_site,
      directory: "goodrich-quad-exterior-review",
      groundNode: "goodrich-quad-approaches",
      ids: ["roof-fd7ba44a", "bushnell-facilities-1125", "roof-ca96d4a8"],
      sourceBatchIds: ["roof-fd7ba44a", "roof-ca96d4a8"],
      newBuildingIds: ["bushnell-facilities-1125"],
      registeredAddresses: {
        "roof-fd7ba44a": ["Goodrich Hall", "828 E 11th Ave"],
        "bushnell-facilities-1125": [
          "Bushnell Facilities & Maintenance",
          "1125 Alder St",
        ],
        "roof-ca96d4a8": ["1145 Alder Building", "1145 Alder St"],
      },
    },
    "alder-bushnell-exterior": {
      descriptor: config?.alder_bushnell_site,
      directory: "alder-bushnell-exterior-review",
      groundNode: "alder-bushnell-approaches",
      ids: ["alder-suites-950", "roof-e45bcd54", "roof-b98e8e3e"],
      sourceBatchIds: ["roof-e45bcd54", "roof-b98e8e3e"],
      newBuildingIds: ["alder-suites-950"],
      registeredAddresses: {
        "alder-suites-950": ["Alder Suites", "950 Alder St"],
        "roof-e45bcd54": ["Morse Center", "1075 Alder St"],
        "roof-b98e8e3e": ["Pomajevich Hall", "1090 Alder St"],
      },
    },
    "walnut-alder-broadway-exterior": {
      descriptor: config?.walnut_alder_broadway_site,
      directory: "walnut-alder-broadway-exterior-review",
      groundNode: "walnut-alder-broadway-approaches",
      ids: ["roof-b3b290df", "roof-8fea5de9", "roof-31cf5cf8"],
      sourceBatchIds: ["roof-b3b290df", "roof-8fea5de9", "roof-31cf5cf8"],
      registeredAddresses: {
        "roof-b3b290df": ["Transportation Services", "1401 Walnut St"],
        "roof-8fea5de9": ["968 Alder Apartments", "968 Alder St"],
        "roof-31cf5cf8": [
          "Former Motel 66 Entrance · July 2024",
          "755 E Broadway",
        ],
      },
    },
    "hilyard-fifteenth-exterior": {
      descriptor: config?.hilyard_1515_exterior_site,
      directory: "hilyard-fifteenth-exterior-review",
      groundNode: "hilyard-1515-approaches",
      ids: ["roof-9bdc0828", "east-15th-740", "hilyard-1547-1549"],
      sourceBatchIds: ["roof-9bdc0828"],
      splitBuildings: {
        "east-15th-740": "roof-9bdc0828",
        "hilyard-1547-1549": "roof-9bdc0828",
      },
      registeredAddresses: {
        "roof-9bdc0828": ["1515 Hilyard Apartments", "1515 Hilyard St"],
        "east-15th-740": ["Treetop Apartments · 740 E 15th", "740 E 15th Ave"],
        "hilyard-1547-1549": [
          "1547–1549 Hilyard Duplex",
          "1547–1549 Hilyard St",
        ],
      },
    },
    "hilyard-apartments-exterior": {
      descriptor: config?.hilyard_apartments_exterior_site,
      directory: "hilyard-apartments-exterior-review",
      groundNode: "hilyard-apartments-approach",
      ids: ["hilyard-apartments-973"],
      newBuildingIds: ["hilyard-apartments-973"],
      registeredAddresses: {
        "hilyard-apartments-973": [
          "Hilyard Apartments · 973 Hilyard",
          "973 Hilyard St",
        ],
      },
    },
    "treated-roof-exterior": {
      descriptor: config?.treated_roof_exterior_site,
      directory: "treated-roof-exterior-review",
      groundNode: "treated-roof-approaches",
      ids: Object.keys(treatedRoofAddresses),
      sourceBatchIds: Object.keys(treatedRoofAddresses),
      registeredAddresses: treatedRoofAddresses,
    },
    "fairmount-residential-exterior": {
      descriptor: config?.fairmount_residential_exterior_site,
      directory: "fairmount-residential-exterior-review",
      groundNode: "fairmount-residential-approaches",
      ids: Object.keys(fairmountResidentialAddresses),
      sourceBatchIds: Object.keys(fairmountResidentialAddresses),
      registeredAddresses: fairmountResidentialAddresses,
    },
    "broadway-orchard-exterior": {
      descriptor: config?.broadway_orchard_exterior_site,
      directory: "broadway-orchard-exterior-review",
      groundNode: "broadway-orchard-approaches",
      ids: Object.keys(broadwayOrchardAddresses),
      sourceBatchIds: Object.keys(broadwayOrchardAddresses),
      registeredAddresses: broadwayOrchardAddresses,
    },
    "franklin-complex-exterior": {
      descriptor: config?.franklin_complex_exterior_site,
      directory: "franklin-complex-exterior-review",
      groundNode: "franklin-complex-approaches",
      ids: Object.keys(franklinComplexAddresses),
      sourceBatchIds: Object.keys(franklinComplexAddresses),
      registeredAddresses: franklinComplexAddresses,
    },
    "franklin-boulevard-exterior": {
      descriptor: config?.franklin_boulevard_exterior_site,
      directory: "franklin-boulevard-exterior-review",
      groundNode: "franklin-boulevard-approaches",
      ids: Object.keys(franklinBoulevardAddresses),
      sourceBatchIds: Object.keys(franklinBoulevardAddresses),
      registeredAddresses: franklinBoulevardAddresses,
    },
    "bardell-avenue-exterior": {
      descriptor: config?.bardell_avenue_exterior_site,
      directory: "bardell-avenue-exterior-review",
      groundNode: "bardell-avenue-approaches",
      ids: Object.keys(bardellAvenueAddresses),
      sourceBatchIds: Object.keys(bardellAvenueAddresses),
      registeredAddresses: bardellAvenueAddresses,
    },
    "villard-street-exterior": {
      descriptor: config?.villard_street_exterior_site,
      directory: "villard-street-exterior-review",
      groundNode: "villard-street-approaches",
      ids: Object.keys(villardStreetAddresses),
      sourceBatchIds: Object.keys(villardStreetAddresses),
      registeredAddresses: villardStreetAddresses,
    },
    "garden-avenue-exterior": {
      descriptor: config?.garden_avenue_exterior_site,
      directory: "garden-avenue-exterior-review",
      groundNode: "garden-avenue-approaches",
      ids: Object.keys(gardenAvenueAddresses),
      sourceBatchIds: Object.keys(gardenAvenueAddresses),
      registeredAddresses: gardenAvenueAddresses,
    },
    "fairmount-boulevard-exterior": {
      descriptor: config?.fairmount_boulevard_exterior_site,
      directory: "fairmount-boulevard-exterior-review",
      groundNode: "fairmount-boulevard-approaches",
      ids: Object.keys(fairmountAddresses),
      sourceBatchIds: Object.keys(fairmountAddresses),
      registeredAddresses: fairmountAddresses,
    },
    heritage: {
      descriptor: config?.heritage_core_site,
      directory: "heritage-core-review",
      ids: ["roof-9017feee", "roof-399c648e"],
      groundNode: "heritage-core-approaches",
      replacedDetails: [
        "university-hall-detail.json",
        "villard-east-detail.json",
      ],
    },
  };
  const enabledReviews = new Set([
    "knight",
    "emu",
    "hedco",
    "music",
    "athletic",
    "museum",
    "gerlinger",
    "womens",
    "memorial",
    "fenton",
    "allen",
    "science",
    "straub",
    "kalapuya",
    "longhouse",
    "scholars",
    "moss",
    "olum",
    "graduates",
    "knight-law",
    "bean-unthank",
    "cedar-yasui",
    "carson-llc",
    "oregon-jaqua",
    "lillis-complex",
    "friendly-collier-mckenzie",
    "plc-lokey-tykeson",
    "northeast-science",
    "knight-campus",
    "northsite-millrace",
    "public-building-exterior",
    "hayward-exterior",
    "campus-frontage",
    "facilities-exterior",
    "office-exterior",
    "residential-exterior",
    "campus-neighbor-exterior",
    "chapter-house-exterior",
    "villard-garden-exterior",
    "alder-millrace-exterior",
    "east-campus-housing",
    "hilyard-west-exterior",
    "university-district-exterior",
    "university-district-clinic",
    "former-hospital-site",
    "zirc-exterior",
    "hilyard-central-exterior",
    "e-fifteenth-pair-exterior",
    "walnut-alder-broadway-exterior",
    "alder-bushnell-exterior",
    "goodrich-quad-exterior",
    "bushnell-east-exterior",
    "east-station-exterior",
    "western-exterior",
    "millrace-fairmount-exterior",
    "fairmount-kincaid-exterior",
    "southeast-fairmount-exterior",
    "northwest-infill-exterior",
    "millrace-research-exterior",
    "parkside-exterior",
    "east-nineteenth-exterior",
    "alder-harris-exterior",
    "hilyard-south-exterior",
    "west-boundary-exterior",
    "alton-franklin-exterior",
    "east-nineteenth-court-exterior",
    "onyx-house-exterior",
    "south-university-exterior",
    "onyx-university-split-exterior",
    "south-campus-frontages",
    "potter-university-exterior",
    "harris-potter-exterior",
    "fairmount-summit-hamble",
    "orchard-villard-hillside",
    "fairmount-moss-slope",
    "columbia-moss-frontages",
    "agate-emerald-frontages",
    "emerald-onyx-frontages",
    "onyx-university-frontages",
    "southern-boundary-exterior",
    "rive-eugene-exterior",
    "alder-thirteenth-exterior",
    "hilyard-fifteenth-exterior",
    "hilyard-apartments-exterior",
    "treated-roof-exterior",
    "fairmount-residential-exterior",
    "broadway-orchard-exterior",
    "franklin-complex-exterior",
    "franklin-boulevard-exterior",
    "bardell-avenue-exterior",
    "villard-street-exterior",
    "garden-avenue-exterior",
    "fairmount-boulevard-exterior",
    "heritage",
  ]);
  if (Object.hasOwn(reviewOptions, reviewMode)) enabledReviews.add(reviewMode);
  for (const key of enabledReviews) {
    if (reviewMode === `${key}-baseline`) enabledReviews.delete(key);
  }
  let completedReviews = 0;
  const [cascadeReview, loadedReviews] = await Promise.all([
    cascadeLoad,
    Promise.all(
      [...enabledReviews]
        .map(async (key) => {
          const options = reviewOptions[key];
          const candidates = [options];
          if (key === "heritage" && reviewMode !== "miller-baseline") {
            candidates.unshift({
              descriptor: config?.heritage_miller_site,
              directory: "heritage-miller-review",
              ids: [...options.ids, "roof-944fcd46"],
              groundNode: "heritage-miller-approaches",
              replacedDetails: [
                ...options.replacedDetails,
                "miller-west-detail.json",
              ],
            });
          }
          for (const candidate of candidates) {
            if (!candidate.descriptor) continue;
            try {
              return await loadBuildingSiteReview(
                base,
                manifest,
                config,
                candidate,
              );
            } catch (error) {
              console.warn(
                `Exterior review ${candidate.directory} unavailable; using the prior site.`,
                error,
              );
            }
          }
          return null;
        })
        .map((review) =>
          review.finally(() => {
            loadingProgress.value =
              16 + (46 * ++completedReviews) / enabledReviews.size;
          }),
        ),
    ),
  ]);
  const buildingReviews = loadedReviews.filter(Boolean);
  async function compose(exteriorReview) {
    const sourceScene = exteriorReview
      ? exteriorReview.loadSource(modelUrl, manifest.model.sha256, base)
      : new GLTFLoader().loadAsync(modelUrl);
    // Finish the assembly before a fallback can reuse the loaded site nodes.
    const results = await Promise.allSettled([
      exteriorReview?.field ?? loadJson(base + manifest.heightfield_url),
      config &&
        loadPresentation(base, name, ids, {
          config,
          exteriorReview,
          cascadeReview,
          buildingReviews,
          sourceScene,
          manifest,
          skipFoundationL2: reviewMode === "landcover-baseline",
          skipContextRoofs: reviewMode === "roof-baseline",
          skipPilotClearance: reviewMode === "tree-baseline",
          skipPilotTrees: reviewMode === "tree-model-baseline",
          skipContextTrees: reviewMode === "context-tree-model-baseline",
          skipUnderstory: reviewMode === "understory-model-baseline",
          skipPilotFurnishings: reviewMode === "furniture-baseline",
          skipPilotHardscape: reviewMode === "hardscape-baseline",
        }),
      sourceScene,
    ]);
    for (const result of results)
      if (result.status === "rejected") throw result.reason;
    const [heightfield, art, gltf] = results.map(({ value }) => value);
    exteriorReview?.fitGrade(gltf.scene);
    const field = applyFoundationGrade(
      gltf.scene,
      heightfield,
      art?.foundationGrade,
    );
    if (art && reviewMode !== "paving-corridors-baseline")
      art.refinedPavingCorridors = await installPavingCorridors(
        base,
        gltf.scene,
        manifest,
        art,
        exteriorReview,
      );
    return { heightfield: field, art, root: gltf.scene, exteriorReview };
  }
  if (config?.ford_arena_site && reviewMode !== "ford-arena-baseline") {
    try {
      const exteriorReview = await loadFordArenaReview(
        base,
        manifest,
        config.ford_arena_site,
      );
      return await compose(exteriorReview);
    } catch (error) {
      console.warn(
        "Ford/Arena site unavailable; using the prior scene.",
        error,
      );
    }
  }
  return compose(null);
}

try {
  const base = import.meta.env.BASE_URL + "scene/";
  loadingProgress.value = 6;
  profile = await loadJson(import.meta.env.BASE_URL + "viewer-profile.json");
  manifest = await loadJson(base + "manifest.json");
  viewerSettings = await loadJson(base + "viewer-settings.json");
  if (manifest.schema_version !== 1)
    throw new Error("Unsupported scene manifest version.");
  if (profile.building_identity_url) {
    try {
      const identityData = await loadJson(
        sceneAssetUrl(import.meta.env.BASE_URL, profile.building_identity_url),
      );
      applyBuildingIdentities(manifest, identityData);
    } catch (error) {
      console.warn("Building identity annotations unavailable:", error);
    }
  }
  loadingProgress.value = 16;
  const campusScene = await loadCampusScene(base, manifest, viewerSettings);
  loadingProgress.value = 76;
  const { exteriorReview } = campusScene;
  field = campusScene.heightfield;
  if (field.heights_m.length !== field.nx * field.ny)
    throw new Error("The terrain heightfield is incomplete.");
  applyProfile(profile, manifest, field);
  if (profile.building_info_url) {
    try {
      const info = await loadJson(
        sceneAssetUrl(import.meta.env.BASE_URL, profile.building_info_url),
      );
      for (const review of campusScene.art?.buildingReviews ?? []) {
        for (const [previousId, id] of Object.entries(review.identityMoves)) {
          if (
            info?.version === 1 &&
            info.records &&
            Object.hasOwn(info.records, previousId)
          ) {
            info.records[id] = info.records[previousId];
            delete info.records[previousId];
          }
        }
      }
      buildingCard.setInfo(info);
    } catch (error) {
      console.warn("Building information unavailable:", error);
    }
  }
  sound = createSound(
    profile.audio,
    import.meta.env.BASE_URL,
    $("#sound-toggle"),
  );
  createFeedback(profile.feedback, {
    iteration: profile.iteration || "development",
    getView: () => view,
    getPosition: () =>
      `E ${player.x.toFixed(1)} / N ${(-player.z).toFixed(1)} / H ${player.y.toFixed(1)} m (local ENU)`,
    pause: () => {
      keys.clear();
      drag = null;
      touchControls.reset();
      walkMotion.reset();
      motion = { ...motion, bobX: 0, bobY: 0, roll: 0, walking: false };
    },
    resume: () => viewport.focus({ preventScroll: true }),
  });
  if (profile.wildlife?.asset_url)
    squirrelFactory = await loadWildlifeFactory(
      sceneAssetUrl(import.meta.env.BASE_URL, profile.wildlife.asset_url),
      profile.wildlife.yaw_correction,
      profile.wildlife.refined_asset_url
        ? {
            refinedUrl: sceneAssetUrl(
              import.meta.env.BASE_URL,
              profile.wildlife.refined_asset_url,
            ),
            sha256: profile.wildlife.refined_asset_sha256,
          }
        : undefined,
    );
  analytics = createAnalytics(profile.analytics);
  if (analytics.enabled) {
    const notice = document.createElement("p");
    notice.textContent =
      "Aggregate page visits and basic interaction events are counted with GoatCounter. Search text and character coordinates are not sent. Do Not Track and Global Privacy Control are respected.";
    $("#about-panel").append(notice);
  }
  half = manifest.aoi_size_m / 2;
  const baseRecords = exteriorReview?.buildingRecords ?? manifest.buildings;
  const cascadeReview = campusScene.art?.cascadeReview;
  const buildingReviews = campusScene.art?.buildingReviews ?? [];
  const retiredCorridors = new Set(
    buildingReviews
      .map(({ retiredCorridor }) => retiredCorridor)
      .filter(Boolean),
  );
  const activeCorridors = (manifest.corridors?.features ?? []).filter(
    ({ id }) => !retiredCorridors.has(id),
  );
  const siteRecords = buildingReviews.reduce(
    (records, review) => review.records(records),
    cascadeReview?.buildingRecords(baseRecords) ?? baseRecords,
  );
  const absorbedBuildingIds = new Set(
    buildingReviews.flatMap((review) => review.absorbedIds),
  );
  const contextRoofs = campusScene.art?.contextRoofHeights;
  const contextBuildings = campusScene.art?.contextBuildingRecords;
  buildings = contextRoofs
    ? siteRecords.map((record) => {
        const peak = contextRoofs.get(record.id);
        if (peak === undefined) return record;
        const updated = { ...record, ...contextBuildings?.get(record.id) };
        return {
          ...updated,
          roof_z_m: peak,
          height_m: peak - updated.base_z_m,
        };
      })
    : siteRecords;
  for (const record of buildings) buildingRecords.set(record.id, record);
  presentation = campusScene.art;
  outdoorObstacleBoxes = buildingReviews
    .flatMap((review) => review.closedSiteBoxes)
    .concat(
      presentation?.furnishingBoxes ?? [],
      presentation?.hardscape?.boxes ?? [],
    );
  const extraCollisionBoxes = attachCollisionBoxes(
    buildings,
    presentation?.collisionSupplements || [],
  ).concat(outdoorObstacleBoxes);
  model = campusScene.root;
  model.updateMatrixWorld(true);
  const contextGeometries = [],
    remove = [];
  model.traverse((object) => {
    if (!object.isMesh) return;
    object.material = object.material.clone();
    object.receiveShadow = true;
    if (object.userData.asset_kind === "terrain") {
      terrainMesh = object;
      object.material.color.setHex(0x92989c);
    }
    if (object.userData.asset_kind === "building") {
      const id = object.userData.asset_id || object.name;
      if (presentation?.config.replaces_building_ids.includes(id)) {
        remove.push(object);
        return;
      }
      meshesById.set(id, object);
      collisionMeshes.push(object);
      object.castShadow = true;
      const record = buildings.find((building) => building.id === id);
      if (!record?.name) {
        let geometry = object.geometry.clone().applyMatrix4(object.matrixWorld);
        if (geometry.index) geometry = geometry.toNonIndexed();
        for (const attribute of Object.keys(geometry.attributes))
          if (!["position", "normal"].includes(attribute))
            geometry.deleteAttribute(attribute);
        contextGeometries.push(geometry);
        remove.push(object);
      }
    }
    if (object.userData.asset_kind === "corridor") {
      object.material.color.set(
        object.material.vertexColors ? 0xffffff : 0x5e6765,
      );
      if (object.material.vertexColors) object.material.metalness = 0;
      object.material.roughness = 0.98;
      applySurfaceGrain(object.material, 0.08);
      object.material.polygonOffset = true;
      object.material.polygonOffsetFactor = -1;
      object.material.polygonOffsetUnits = -1;
      object.receiveShadow = true;
    }
  });
  // Keep editable assets in Blender; batch unnamed runtime context to reduce draw calls.
  for (const object of remove) object.removeFromParent();
  if (contextGeometries.length) {
    const geometry = mergeGeometries(contextGeometries, false);
    if (!geometry) throw new Error("Context geometry could not be batched.");
    const material = new THREE.MeshStandardMaterial({
      color: 0xe9e8e0,
      roughness: 0.94,
    });
    const batch = new THREE.Mesh(geometry, material);
    batch.name = "Batched unnamed context";
    batch.castShadow = true;
    batch.receiveShadow = true;
    model.add(batch);
    for (const part of contextGeometries) part.dispose();
  }
  if (!terrainMesh) throw new Error("The GLB does not contain terrain.");
  if (presentation) {
    model.add(presentation.root);
    // Keep the source mesh for geographic checks, but draw only one full ground base.
    if (presentation.hasFoundation) terrainMesh.visible = false;
    for (const [id, group] of presentation.groups) meshesById.set(id, group);
    collisionMeshes.push(...presentation.collisionMeshes);
    const light = presentation.config.lighting;
    if (light) {
      scene.background.set(light.background);
      scene.fog.color.set(light.background);
      const hemisphere = scene.children.find(
        (child) => child.isHemisphereLight,
      );
      hemisphere.color.set(light.sky);
      hemisphere.groundColor.set(light.ground);
      hemisphere.intensity = light.ambient_intensity;
      sun.color.set(light.sun);
      sun.intensity = light.sun_intensity;
      sun.target.position.fromArray(light.target);
      scene.add(sun.target);
      sun.position
        .copy(sun.target.position)
        .add(new THREE.Vector3(-220, 420, -180));
      Object.assign(sun.shadow.camera, {
        left: -470,
        right: 470,
        top: 470,
        bottom: -470,
        near: 1,
        far: 1500,
      });
      sun.shadow.camera.updateProjectionMatrix();
      sun.shadow.normalBias = 0.25;
      sun.shadow.bias = -0.0004;
    }
    $("#toon-row").hidden = false;
    $("#toon-setting").addEventListener("change", (event) => {
      setEmissive(selected, 0);
      buildingHighlight.hover(null);
      presentation.setToon(event.target.checked);
      buildingHighlight.refresh();
      renderer.shadowMap.needsUpdate = true;
    });
  }
  scene.background.set(0x9ac7e6);
  scene.fog.color.set(0xc7dfec);
  applySurfaceGrain(terrainMesh.material, 0.08);
  scene.add(model);
  if (presentation?.contextFog) {
    // Opt in only after profiling the target device: cached fields add memory.
    if (viewerSettings.cache_static_haze === true)
      presentation.bakeStaticHaze();
    model.traverse((object) => {
      if (object.isMesh)
        for (const material of [object.material].flat())
          presentation.contextFog.apply(material);
      if (
        viewerSettings.cache_static_haze === true &&
        object.isMesh &&
        object.visible
      )
        presentation.contextFog.bakeMesh(object);
    });
    $("#context-fog-row").hidden = false;
    $("#context-fog-setting").addEventListener("change", (e) =>
      presentation.contextFog.setEnabled(e.target.checked),
    );
  }
  loadingProgress.value = 85;
  if (profile.character?.asset_url) {
    studentFactory = await loadStudentFactory(
      sceneAssetUrl(import.meta.env.BASE_URL, profile.character.asset_url),
      profile.character,
    );
    scene.remove(character.root);
    character = studentFactory();
    scene.add(character.root);
    const personPath = [
      [-42, -46],
      [-42, -34],
    ];
    const pathClear =
      Array.from({ length: 25 }, (_, i) => personPath[0][1] + i * 0.5).every(
        (z) => !isBlocked(-42, z, buildings, half),
      ) && !segmentHitsBoxes([-42, 46], [-42, 34], extraCollisionBoxes, 0.5);
    if (pathClear)
      fixedNpc = createFixedNpc({
        scene,
        viewport,
        camera,
        studentFactory,
        decorate: styleDanCarrere,
        ground: (x, z) => sampleGround(field, x, z),
        occluders: collisionMeshes,
        config: {
          name: "Dan Carrere",
          appearance: danCarrereAppearance,
          plantFeet: true,
          linkLabel: "University profile",
          role: "Associate Teaching Professor · Computer Science",
          url: "https://cas.uoregon.edu/directory/school-of-computer-and-data-sciences/all/dcarrere",
          line: "you just graduated",
          path: personPath,
          speed: 0.7,
          pauseSeconds: 2,
        },
      });
    else console.warn("Fixed NPC path unavailable: collision check failed.");
  }
  if (viewerSettings.navigation_url) {
    const graph =
      presentation?.refinedPavingCorridors?.navigation ??
      buildingReviews.find(({ navigation }) => navigation)?.navigation ??
      (await loadJson(sceneAssetUrl(base, viewerSettings.navigation_url)));
    const clearSegment = (a, b) => {
      if (segmentHitsBoxes(a, b, extraCollisionBoxes, 0.5)) return false;
      const steps = Math.max(1, Math.ceil(distance(a, b) / 2));
      for (let i = 0; i <= steps; i++) {
        const x = a[0] + ((b[0] - a[0]) * i) / steps,
          n = a[1] + ((b[1] - a[1]) * i) / steps;
        if (isBlocked(x, -n, buildings, half, 0.5)) return false;
      }
      return true;
    };
    const surfaces = [];
    let drapedOffset = 0;
    model.traverse((o) => {
      if (o.isMesh && o.userData.asset_kind === "landscape-surface") {
        const offset = o.userData.heightfield_offset_m;
        if (Number.isFinite(offset) && offset >= 0 && offset <= 0.3)
          drapedOffset = Math.max(drapedOffset, offset);
        else surfaces.push(o);
      }
    });
    model.updateMatrixWorld(true);
    const surfaceRay = new THREE.Raycaster(),
      heightCache = new Map();
    const ground = (x, z) => {
      const key = Math.round(x * 2) + "," + Math.round(z * 2);
      if (heightCache.has(key)) return heightCache.get(key);
      const y = sampleGround(field, x, z) + drapedOffset;
      surfaceRay.set(
        new THREE.Vector3(x, y + 20, z),
        new THREE.Vector3(0, -1, 0),
      );
      const hit = surfaceRay.intersectObjects(surfaces, false)[0];
      const height = Math.max(y, hit?.point.y ?? y);
      heightCache.set(key, height);
      return height;
    };
    const router = createRouter(
      graph,
      clearSegment,
      (a, b) => !segmentHitsBoxes(a, b, extraCollisionBoxes, 0.5),
    );
    outdoorRouter = router;
    const siteApproachIds = new Set(
      buildingReviews.flatMap((review) => review.routeApproachIds),
    );
    navigation = createNavigation({
      scene,
      router,
      ground,
      getView: () => view,
      getPlayer: () => player,
      focusSearch: () => {
        $("#building-search-input").focus();
        $("#building-search-input").select();
      },
      canPin: (p) => clearSegment(p, p),
      getBuildingApproach: ({ id }) => {
        if (!siteApproachIds.has(id)) return null;
        const entry = entrances?.entries.find(
          (item) => item.id === id && item.walkable,
        );
        return entry ? [entry.approach[0], -entry.approach[1]] : null;
      },
      fitRoute: (points) => {
        if (view !== "aerial") return;
        cancelCameraTransition();
        const bounds = new THREE.Box3().setFromPoints(
            points.map(
              (p) => new THREE.Vector3(p[0], ground(p[0], -p[1]), -p[1]),
            ),
          ),
          target = bounds.getCenter(new THREE.Vector3()),
          size = bounds.getSize(new THREE.Vector3());
        const span = Math.max(65, size.x, size.z) / Math.min(1, camera.aspect);
        orbit.target.copy(target);
        camera.position
          .copy(target)
          .add(new THREE.Vector3(span * 0.6, span * 1.2, span));
        orbit.update();
      },
    });
    $("#directions-open").hidden = false;
    if (viewerSettings.activity_url) {
      const activity = await loadJson(
        sceneAssetUrl(base, viewerSettings.activity_url),
      );
      life = createCampusLife({
        scene,
        router,
        activity: updateQuadActivity(
          activity,
          presentation?.refinedPavingCorridors?.quadActivity,
        ),
        studentFactory: studentFactory || createCharacter,
        squirrelFactory,
        getPlayer: () => player,
        ground,
        clearSegment,
      });
      $("#immersion-settings").hidden = false;
      $("#activity-density").addEventListener("input", (e) => {
        life.setDensity(e.target.value);
        const name = DENSITY_NAMES[life.state().densityLevel];
        $("#activity-density-value").textContent = name;
        e.target.setAttribute("aria-valuetext", name);
      });
    }
  }
  zombies = createZombieSchool({
    scene,
    field,
    buildings,
    half,
    onCaught: () => death.show(),
    getPlayer: () => player,
    router: outdoorRouter,
    clearSegment: (a, b) => {
      if (segmentHitsBoxes(a, b, extraCollisionBoxes, 0.6)) return false;
      const count = Math.max(
        1,
        Math.ceil(Math.hypot(a[0] - b[0], a[1] - b[1]) / 2),
      );
      for (let i = 0; i <= count; i++)
        if (
          isBlocked(
            a[0] + ((b[0] - a[0]) * i) / count,
            -a[1] - ((b[1] - a[1]) * i) / count,
            buildings,
            half,
            0.6,
          )
        )
          return false;
      return true;
    },
  });
  betaRegistry = createBetaRegistry($("#beta-functions"));
  let savedDensity = 2;
  function syncDensityUI() {
    if (!life) return;
    const state = life.state();
    $("#activity-density").value = String(state.densityLevel);
    $("#activity-density").setAttribute("aria-valuetext", state.density);
    $("#activity-density-value").textContent = state.density;
  }
  betaRegistry.register({
    id: "zombie-school",
    title: "ZOMBIE SCHOOL!!!",
    description:
      "Clean map + slow wandering chibi monsters. They chase within 30 m and lose interest beyond 60 m. Contact ends the round.",
    start() {
      savedDensity = life?.state().densityLevel ?? 2;
      life?.setDensity(0);
      syncDensityUI();
      $("#activity-density").disabled = true;
      zombies.start();
      $("#beta-badge").hidden = false;
    },
    stop() {
      zombies.stop();
      life?.setDensity(savedDensity);
      syncDensityUI();
      $("#activity-density").disabled = false;
      $("#beta-badge").hidden = true;
    },
  });
  entrances = createEntrances({
    scene,
    buildings,
    half,
    field,
    meshesById,
    surfaceHeight: presentation?.hardscape?.height,
    overrides: {
      ...viewerSettings.entrances,
      ...exteriorReview?.entrances,
      ...cascadeReview?.entrances,
      ...Object.assign(
        {},
        ...buildingReviews.map((review) => review.entrances),
      ),
    },
    onEnter: enterBuilding,
  });
  labels.populate(buildings);
  buildingSearch.populate(buildings);
  resetPlayer();
  setView("aerial");
  if (new URL(location.href).searchParams.get("return") === "1") {
    const saved = readReturn();
    if (
      saved &&
      (buildingRecords.has(saved.buildingId) ||
        absorbedBuildingIds.has(saved.buildingId))
    ) {
      const [x, , z] = saved.player;
      if (!isBlocked(x, z, buildings, half) && !isOutdoorObstacle(x, z)) {
        player.set(x, standingGround(x, z), z);
        character.root.position.copy(player);
      }
      yaw = saved.yaw;
      character.root.rotation.y = Number.isFinite(saved.heroYaw)
        ? saved.heroYaw
        : yaw + Math.PI;
      followDistance = THREE.MathUtils.clamp(saved.followDistance, 2.5, 30);
      setView(saved.view);
      pitch = THREE.MathUtils.clamp(saved.pitch, -0.7, 0.9);
      if (saved.view !== "aerial") updateCamera(0, true);
      else if (
        [saved.cameraPosition, saved.orbitTarget].every(
          (a) => Array.isArray(a) && a.length === 3 && a.every(Number.isFinite),
        )
      ) {
        camera.position.fromArray(saved.cameraPosition);
        orbit.target.fromArray(saved.orbitTarget);
        orbit.update();
      }
      life?.setDensity(saved.density ?? 2);
      syncDensityUI();
      $("#motion-setting").value = String(
        THREE.MathUtils.clamp(saved.motionLevel ?? 1, 0, 3),
      );
      $("#motion-setting").dispatchEvent(new Event("input"));
      for (const [id, checked] of Object.entries(saved.settings || {}))
        if (
          [
            "show-labels",
            "shadows-setting",
            "toon-setting",
            "context-fog-setting",
            "wireframe-setting",
          ].includes(id)
        ) {
          $("#" + id).checked = !!checked;
          $("#" + id).dispatchEvent(new Event("change"));
        }
      if (saved.soundEnabled === false && sound.state().enabled)
        $("#sound-toggle").click();
    }
    try {
      sessionStorage.removeItem(RETURN_KEY);
    } catch {}
    const url = new URL(location.href);
    url.searchParams.delete("return");
    history.replaceState(null, "", url.href);
  }
  drawMap = createMinimap($("#minimap"), buildings, half, activeCorridors);
  const skirt = new THREE.Mesh(
    new THREE.BoxGeometry(half * 2, 6, half * 2),
    new THREE.MeshStandardMaterial({ color: 0x9da3a5, roughness: 1 }),
  );
  skirt.position.y = manifest.quality.terrain_range_local_m[0] - 3.2;
  skirt.receiveShadow = true;
  scene.add(skirt);
  renderer.shadowMap.needsUpdate = true;
  loadingProgress.value = 96;
  const depth = createOverviewDepth(camera, model);
  const frozenStaticNodes = freezeStaticTransforms(model);
  let betaLastUpdate = 0;
  renderer.setAnimationLoop((now) => {
    const frameSeconds = Math.max(0, (now - lastTime) / 1000 || 0);
    const dt = Math.min(frameSeconds, 0.08);
    const movementDt = movementFrameSeconds(frameSeconds, !document.hidden);
    lastTime = now;
    elapsed += dt;
    if (!modalOpen()) updatePlayer(dt, movementDt);
    if (!death.dead) updateCamera(dt);
    entrances.update(player, view, modalOpen());
    depth.update(view);
    sky.update(
      camera,
      death.dead ? elapsed - dt : elapsed,
      reducedMotion.matches || death.dead,
    );
    navigation?.update(elapsed);
    fixedNpc?.update(modalOpen() ? 0 : dt, player);
    if (!modalOpen()) {
      life?.update(dt);
      zombies?.update(dt);
    }
    if (zombies?.active && now - betaLastUpdate > 250) {
      betaLastUpdate = now;
      $("#beta-badge").textContent =
        `ZOMBIE SCHOOL!!! · ${zombies.state().chasing} chasing`;
    }
    renderer.render(scene, camera);
    if (!loading.hidden) {
      loadingProgress.value = 100;
      loading.hidden = true;
    }
    labels.update(now, view);
    buildingCard.update();
    if (
      hoverPending &&
      hoverPointer &&
      !drag &&
      !modalOpen() &&
      now - lastHover > 80
    ) {
      lastHover = now;
      hoverPending = false;
      const box = renderer.domElement.getBoundingClientRect();
      raycaster.setFromCamera(
        new THREE.Vector2(
          ((hoverPointer.clientX - box.left) / box.width) * 2 - 1,
          (-(hoverPointer.clientY - box.top) / box.height) * 2 + 1,
        ),
        camera,
      );
      const hit = raycaster.intersectObjects(collisionMeshes, false)[0];
      const personHit =
        fixedNpc && raycaster.intersectObject(fixedNpc.root, true)[0];
      const personHovered =
        !!personHit && (!hit || personHit.distance < hit.distance);
      fixedNpc?.hover(personHovered);
      const id = personHovered
        ? null
        : resolveBuildingHit(hit, buildingRecords);
      buildingHighlight.hover(id);
      renderer.domElement.style.cursor = id || personHovered ? "pointer" : "";
    }
    developer.update(now);
    frames++;
    if (now - lastFps > 1000) {
      fps = Math.round((frames * 1000) / (now - lastFps));
      frames = 0;
      lastFps = now;
    }
    drawMap(
      player,
      yaw,
      selectedMapTarget,
      navigation?.points,
      fixedNpc?.root.position,
    );
    const heading = new THREE.Vector3();
    camera.getWorldDirection(heading);
    $(".compass i").style.transform =
      "rotate(" + Math.atan2(heading.x, -heading.z) + "rad)";
    const positionText =
      "E " +
      player.x.toFixed(1) +
      " / N " +
      (-player.z).toFixed(1) +
      " / H " +
      player.y.toFixed(1) +
      " m";
    if ($("#position").textContent !== positionText)
      $("#position").textContent = positionText;
  });
  const reviewFoundation = exteriorReview
    ? presentation.root
        .getObjectsByProperty("isMesh", true)
        .find((mesh) => mesh.userData.surface_layer === "foundation")
    : null;
  window.__campus = {
    getState: () => ({
      ready: true,
      entranceCount: entrances.entries.length,
      nearbyEntrance: entrances.nearby,
      hoveredBuilding: buildingHighlight.hovered,
      touchSpeed:
        Math.hypot(touchControls.axes.forward, touchControls.axes.right) *
        RUN_SPEED,
      riggedHero: !!character.rigged,
      developerMode: developer.enabled,
      dead: death.dead,
      sky: sky.state(),
      motionLevel: Number($("#motion-setting").value),
      inspectedNpc: developer.selected,
      life: life?.state() || null,
      beta: betaRegistry?.state(),
      zombies: zombies?.state(),
      audio: sound.state(),
      walkMotion: { ...motion },
      heroGait: character.gaitState?.() || null,
      navigation: navigation?.state() || null,
      view,
      followDistance,
      player: player.toArray(),
      camera: camera.position.toArray(),
      cameraNear: camera.near,
      frozenStaticNodes,
      cameraDirection: camera.getWorldDirection(new THREE.Vector3()).toArray(),
      characterDirection: character.root
        .getWorldDirection(new THREE.Vector3())
        .toArray(),
      selectedBuilding: selectedId,
      orbitTarget: orbit.target.toArray(),
      cameraTransition: !!cameraTransition,
      fps,
      buildings: buildings.length,
      namedBuildings: labels.count,
      roadSegments: activeCorridors.length,
      roadSurfaces: model.children.filter(
        (object) => object.userData.asset_kind === "corridor",
      ).length,
      visibleLabels: labels.visibleCount,
      aoiSize: manifest.aoi_size_m,
      grounded: vertical.grounded,
      verticalVelocity: vertical.velocity,
      blocked: isBlocked(player.x, player.z, buildings, half),
      ground: standingGround(player.x, player.z),
      drawCalls: renderer.info.render.calls,
      triangles: renderer.info.render.triangles,
      presentation: presentation
        ? {
            id: presentation.config.id,
            buildings: presentation.groups.size,
            toon: $("#toon-setting").checked,
            backgroundHaze: presentation.contextFog?.enabled || false,
            hazeCache: presentation.contextFog?.state(),
            landcover: Boolean(presentation.config.landcover_url),
            landcoverLevel: presentation.foundationGrade ? 2 : 1,
            refinedPavingCorridors:
              presentation.refinedPavingCorridors?.summary,
            batchedBuildings: presentation.batchedIds.size,
            ...presentation.config.stats,
            ...((presentation.omittedPilotTreeClearance ||
              presentation.siteTreeRemovals) && {
              trees:
                presentation.config.stats.trees +
                presentation.omittedPilotTreeClearance -
                presentation.siteTreeRemovals,
            }),
            refinedContextRoofs: contextRoofs?.size ?? 0,
            registeredPilotTrees: presentation.registeredPilotTrees,
            refinedPilotTrees: presentation.refinedPilotTrees,
            refinedContextTrees: presentation.refinedContextTrees,
            refinedUnderstory: presentation.refinedUnderstory,
            pilotFurnishings: presentation.furnishingBoxes.length,
            hardscapeRailBoxes: presentation.hardscape?.boxes.length ?? 0,
          }
        : null,
    }),
    fixedNpcInfo: () => fixedNpc?.state() || null,
    fixedNpcScreenPosition: () => {
      if (!fixedNpc) return null;
      const p = fixedNpc.root.position
        .clone()
        .add(new THREE.Vector3(0, 1.1, 0))
        .project(camera);
      return {
        x: ((p.x + 1) * viewport.clientWidth) / 2,
        y: ((1 - p.y) * viewport.clientHeight) / 2,
        visible: p.z > -1 && p.z < 1 && Math.abs(p.x) < 1 && Math.abs(p.y) < 1,
      };
    },
    collisionCheck: (x, z) =>
      isBlocked(x, z, buildings, half) || isOutdoorObstacle(x, z),
    entranceInfo: () => entrances.entries.map((e) => ({ ...e })),
    lifeColliders: () => life?.colliders() || [],
    npcInfo: (id) => life?.inspect(id) || zombies?.inspect(id),
    npcScreenPosition: (id) => {
      const root = [
        ...(life?.pickables() || []),
        ...(zombies?.pickables() || []),
      ].find((root) => root.userData.npcId === id);
      if (!root) return null;
      const point = new THREE.Box3()
        .setFromObject(root)
        .getCenter(new THREE.Vector3())
        .project(camera);
      return {
        x: ((point.x + 1) * viewport.clientWidth) / 2,
        y: ((1 - point.y) * viewport.clientHeight) / 2,
        visible:
          point.z > -1 &&
          point.z < 1 &&
          Math.abs(point.x) < 1 &&
          Math.abs(point.y) < 1,
      };
    },
    setView,
    reset: resetPlayer,
    labelInfo: (id) => labels.projectedLabel(id),
    namedBuildings: () =>
      buildings
        .filter((building) => building.name)
        .map(({ id, name, name_match }) => ({ id, name, name_match })),
    terrainCheck: (x, z) => {
      const ray = new THREE.Raycaster(
        new THREE.Vector3(x, 300, z),
        new THREE.Vector3(0, -1, 0),
      );
      const hit = ray.intersectObject(terrainMesh, true)[0];
      return {
        mesh: hit?.point.y,
        sampled: sampleGround(field, x, z),
        ...(presentation?.hardscape && {
          hardscape: presentation.hardscape.height(x, z),
          standing: standingGround(x, z),
        }),
        ...(reviewFoundation && {
          foundation: ray.intersectObject(reviewFoundation, true)[0]?.point.y,
          frontage: ray.intersectObject(exteriorReview.frontage, false)[0]
            ?.point.y,
        }),
        ...(cascadeReview && {
          courtyard: ray.intersectObject(cascadeReview.courtyard, false)[0]
            ?.point.y,
          bridge: ray.intersectObject(cascadeReview.link, false)[0]?.point.y,
        }),
        ...Object.fromEntries(
          buildingReviews
            .filter((review) => review.ground)
            .map(({ ground }) => [
              ground.userData.surface_layer,
              ray.intersectObject(ground, false)[0]?.point.y,
            ]),
        ),
      };
    },
  };
} catch (error) {
  console.error(error);
  loading.hidden = true;
  $("#error").hidden = false;
  $("#error p").textContent =
    error.message + " Rebuild the scene assets before trying again.";
}
