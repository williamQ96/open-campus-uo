// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { createFixedNpcPath } from "./fixed-npc-path.js";
import { createPersonOcclusion } from "./fixed-npc-occlusion.js";

// The visual features are a stylized representation, not a photographic likeness.
export function createFixedNpc({
  scene,
  viewport,
  camera,
  studentFactory,
  ground,
  occluders = [],
  config,
}) {
  const actor = studentFactory(
    config.appearance ? { ...config.appearance, speedMps: config.speed } : null,
  );
  const owned = [];
  actor.root.name = `Fixed NPC: ${config.name}`;
  if (config.plaid) {
    const swatch = document.createElement("canvas");
    swatch.width = swatch.height = 128;
    const ctx = swatch.getContext("2d");
    ctx.fillStyle = "#55433c";
    ctx.fillRect(0, 0, 128, 128);
    ctx.fillStyle = "#8e7061";
    ctx.fillRect(0, 0, 128, 30);
    ctx.fillRect(0, 0, 30, 128);
    ctx.fillStyle = "#c1a38c";
    ctx.fillRect(0, 12, 128, 4);
    ctx.fillRect(12, 0, 4, 128);
    const plaidTexture = new THREE.CanvasTexture(swatch);
    plaidTexture.colorSpace = THREE.SRGBColorSpace;
    plaidTexture.flipY = false;
    plaidTexture.wrapS = plaidTexture.wrapT = THREE.RepeatWrapping;
    plaidTexture.repeat.set(18, 18);
    owned.push(plaidTexture);
    actor.root.traverse((o) => {
      if (
        o.isMesh &&
        (o.material?.name?.includes("Gold collar") ||
          o.material?.name?.includes("Forest green"))
      ) {
        o.material.color.set("#ffffff");
        o.material.map = plaidTexture;
        o.material.needsUpdate = true;
      }
    });
  }
  const path = createFixedNpcPath({
    points: config.path,
    speed: config.speed,
    pauseSeconds: config.pauseSeconds,
  });
  const groupOnBone = (boneName, offset, parts) => {
    actor.root.updateMatrixWorld(true);
    const bone = actor.root.getObjectByName(boneName);
    if (!bone) return;
    const meshes = [];
    for (const { geometry, color, position, rotation } of parts) {
      const m = new THREE.Mesh(geometry);
      m.position.set(...position);
      if (rotation) m.rotation.set(...rotation);
      m.updateMatrix();
      let g = geometry.clone().applyMatrix4(m.matrix);
      geometry.dispose();
      if (g.index) g = g.toNonIndexed();
      g.deleteAttribute("uv");
      const c = new THREE.Color(color),
        colors = new Float32Array(g.attributes.position.count * 3);
      for (let i = 0; i < colors.length; i += 3) {
        colors[i] = c.r;
        colors[i + 1] = c.g;
        colors[i + 2] = c.b;
      }
      g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      meshes.push(g);
    }
    const merged = mergeGeometries(meshes, false);
    meshes.forEach((g) => g.dispose());
    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.9,
    });
    owned.push(merged, mat);
    const mesh = new THREE.Mesh(merged, mat),
      anchor = new THREE.Group();
    anchor.add(mesh);
    const pos = bone.getWorldPosition(new THREE.Vector3());
    anchor.position.copy(pos.add(new THREE.Vector3(...offset)));
    actor.root.add(anchor);
    actor.root.updateMatrixWorld(true);
    bone.attach(anchor);
  };
  if (config.hatAndBeard)
    groupOnBone(
      "Head",
      [0, 0, 0],
      [
        {
          geometry: new THREE.CylinderGeometry(0.27, 0.29, 0.085, 16),
          color: "#4b4942",
          position: [0, 0.41, 0],
        },
        {
          geometry: new THREE.CylinderGeometry(0.205, 0.22, 0.16, 16),
          color: "#5e5a50",
          position: [0, 0.5, 0],
        },
        {
          geometry: new THREE.SphereGeometry(0.17, 12, 8).scale(1, 0.62, 0.35),
          color: "#756960",
          position: [0, 0.04, 0.2],
        },
        {
          geometry: new THREE.SphereGeometry(0.022, 6, 4),
          color: "#252827",
          position: [-0.075, 0.245, 0.17],
        },
        {
          geometry: new THREE.SphereGeometry(0.022, 6, 4),
          color: "#252827",
          position: [0.075, 0.245, 0.17],
        },
      ],
    );
  scene.add(actor.root);
  const label = document.createElement("button");
  label.type = "button";
  label.className = "fixed-person-label";
  label.textContent = config.name;
  label.setAttribute("aria-label", `View ${config.name} profile`);
  viewport.append(label);
  const bubble = document.createElement("div");
  bubble.className = "fixed-person-bubble";
  bubble.textContent = config.line || "";
  bubble.hidden = true;
  viewport.append(bubble);
  const dialog = document.createElement("dialog");
  dialog.className = "fixed-person-card";
  dialog.setAttribute("aria-label", config.name);
  const title = document.createElement("h2");
  title.textContent = config.name;
  const info = document.createElement("p");
  info.textContent = config.role;
  const link = document.createElement("a");
  if (config.url) {
    link.href = config.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = config.linkLabel || "Profile";
  }
  const close = document.createElement("button");
  close.type = "button";
  close.className = "fixed-person-card-close";
  close.textContent = "x";
  close.setAttribute("aria-label", "Close");
  dialog.append(title, info);
  if (config.url) dialog.append(link);
  dialog.append(close);
  viewport.append(dialog);
  for (const type of ["pointerdown", "pointerup", "wheel"])
    dialog.addEventListener(type, (event) => event.stopPropagation());
  let returnFocus = null;
  function closeCard() {
    if (!dialog.open) return;
    dialog.close();
    const target = returnFocus === label && !label.hidden ? label : viewport;
    target.focus({ preventScroll: true });
    returnFocus = null;
  }
  function openCard() {
    if (dialog.open) return;
    returnFocus = document.activeElement;
    dialog.show();
    // Position synchronously before the next paint, including on slow frames.
    positionCard();
    close.focus({ preventScroll: true });
  }
  close.addEventListener("click", closeCard);
  function onKeyDown(event) {
    if (
      event.key === " " &&
      (event.target === label || event.target === close)
    ) {
      // Preserve native button activation without triggering campus jump input.
      event.stopPropagation();
      return;
    }
    if (
      event.key === "Escape" &&
      dialog.open &&
      !document.querySelector("dialog:modal")
    ) {
      event.preventDefault();
      event.stopPropagation();
      closeCard();
    }
  }
  document.addEventListener("keydown", onKeyDown);
  const materials = [];
  actor.root.traverse((o) => {
    if (o.isMesh)
      for (const m of [o.material].flat())
        if (m?.emissive) materials.push([m, m.emissive.clone()]);
  });
  let hovered = false,
    modelHovered = false,
    labelPointerHovered = false;
  const syncHover = () => {
    hovered =
      modelHovered || labelPointerHovered || document.activeElement === label;
    for (const [m, old] of materials)
      m.emissive.copy(old).addScalar(hovered ? 0.12 : 0);
  };
  const hover = (on) => {
    modelHovered = on;
    syncHover();
  };
  label.addEventListener("pointerenter", () => {
    labelPointerHovered = true;
    syncHover();
  });
  label.addEventListener("pointerleave", () => {
    labelPointerHovered = false;
    syncHover();
  });
  label.addEventListener("focus", syncHover);
  label.addEventListener("blur", syncHover);
  label.addEventListener("click", openCard);
  let elapsed = 0,
    state = path.state();
  const projected = new THREE.Vector3();
  const cardMiddle = new THREE.Vector3(),
    cardEdge = new THREE.Vector3(),
    cardRight = new THREE.Vector3(),
    cardFeet = new THREE.Vector3();
  function positionCard() {
    projected
      .copy(actor.root.position)
      .add(new THREE.Vector3(0, 2.02, 0))
      .project(camera);
    const width = viewport.clientWidth,
      height = viewport.clientHeight,
      w = dialog.offsetWidth,
      h = dialog.offsetHeight,
      anchorX = ((projected.x + 1) * width) / 2,
      anchorY = ((1 - projected.y) * height) / 2;
    cardMiddle.copy(actor.root.position);
    cardMiddle.y += 1;
    cardRight.setFromMatrixColumn(camera.matrixWorld, 0).normalize();
    cardEdge.copy(cardMiddle).addScaledVector(cardRight, 0.5).project(camera);
    cardMiddle.project(camera);
    cardFeet.copy(actor.root.position).project(camera);
    const radius = Math.max(
        20,
        (Math.abs(cardEdge.x - cardMiddle.x) * width) / 2,
      ),
      right = anchorX + radius + 12,
      left = anchorX - radius - 12 - w,
      fitsRight = right + w <= width - 12,
      fitsLeft = left >= 12;
    const preferredX = fitsRight ? right : fitsLeft ? left : anchorX - w / 2;
    const x = THREE.MathUtils.clamp(
      preferredX,
      12,
      Math.max(12, width - w - 12),
    );
    const top = height < 500 ? 88 : width <= 600 ? 154 : 174,
      bottom = width <= 600 || height < 500 ? 110 : 24,
      maxY = Math.max(12, height - bottom - h);
    const y = THREE.MathUtils.clamp(
      fitsRight || fitsLeft
        ? anchorY + 12
        : ((1 - cardFeet.y) * height) / 2 + 8,
      Math.min(top, maxY),
      maxY,
    );
    dialog.style.transform = `translate(${Math.round(x)}px, ${Math.round(y)}px)`;
  }
  const isOccluded = createPersonOcclusion(camera, occluders);
  let occluded = false,
    lastOcclusion = -Infinity,
    occlusionChecks = 0,
    occlusionTotalMs = 0,
    occlusionMaxMs = 0;
  return {
    root: actor.root,
    isOpen: () => dialog.open,
    hover,
    open: openCard,
    update(dt, player) {
      elapsed += dt;
      state = path.update(hovered || dialog.open ? 0 : dt);
      const [x, z] = state.position;
      actor.root.position.set(x, ground(x, z), z);
      actor.root.rotation.y = state.heading;
      actor.animate(elapsed, state.moving && !hovered && !dialog.open, {
        speed: config.speed,
      });
      projected
        .copy(actor.root.position)
        .add(new THREE.Vector3(0, 2.02, 0))
        .project(camera);
      const inView =
        projected.z > -1 &&
        projected.z < 1 &&
        Math.abs(projected.x) < 1 &&
        Math.abs(projected.y) < 1 &&
        camera.position.distanceTo(actor.root.position) < 150;
      if (!inView) lastOcclusion = -Infinity;
      else if (performance.now() - lastOcclusion >= 120) {
        lastOcclusion = performance.now();
        occluded = isOccluded(actor.root.position);
        const duration = performance.now() - lastOcclusion;
        occlusionChecks++;
        occlusionTotalMs += duration;
        occlusionMaxMs = Math.max(occlusionMaxMs, duration);
      }
      const visible = inView && !occluded;
      if (!visible && dialog.open) closeCard();
      if (!visible && document.activeElement === label && !dialog.open)
        viewport.focus({ preventScroll: true });
      if (!visible) {
        modelHovered = labelPointerHovered = false;
        syncHover();
      }
      for (const el of [label, bubble]) {
        el.style.left = `${((projected.x + 1) * viewport.clientWidth) / 2}px`;
        el.style.top = `${((1 - projected.y) * viewport.clientHeight) / 2}px`;
      }
      label.hidden = !visible;
      bubble.hidden =
        !config.line || !visible || player.distanceTo(actor.root.position) > 4;
      if (dialog.open) positionCard();
    },
    state: () => ({
      ...state,
      position3: actor.root.position.toArray(),
      cardOpen: dialog.open,
      occluded,
      occlusionChecks,
      occlusionTotalMs,
      occlusionMaxMs,
      hovered,
      gait: actor.gaitState?.() || null,
    }),
    dispose() {
      modelHovered = labelPointerHovered = false;
      if (
        document.activeElement === label ||
        dialog.contains(document.activeElement)
      )
        viewport.focus({ preventScroll: true });
      syncHover();
      document.removeEventListener("keydown", onKeyDown);
      actor.dispose();
      owned.forEach((x) => x.dispose());
      label.remove();
      bubble.remove();
      dialog.remove();
    },
  };
}
