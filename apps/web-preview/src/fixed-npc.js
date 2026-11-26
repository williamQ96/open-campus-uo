// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";
import { createFixedNpcPath } from "./fixed-npc-path.js";
import { createPersonOcclusion } from "./fixed-npc-occlusion.js";

// The visual features are a stylized representation, not a photographic likeness.
export function createFixedNpc({
  scene,
  viewport,
  camera,
  studentFactory,
  decorate,
  ground,
  occluders = [],
  config,
}) {
  const actor = studentFactory(
    config.appearance ? { ...config.appearance, speedMps: config.speed } : null,
    { plantFeet: config.plantFeet },
  );
  actor.root.name = `Fixed NPC: ${config.name}`;
  const disposeStyle = decorate?.(actor.root);
  const path = createFixedNpcPath({
    points: config.path,
    speed: config.speed,
    pauseSeconds: config.pauseSeconds,
  });
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
      const [previousX, previousZ] = state.position;
      state = path.update(hovered || dialog.open ? 0 : dt);
      const [x, z] = state.position;
      actor.root.position.set(x, ground(x, z), z);
      actor.root.rotation.y = state.heading;
      const distanceM = Math.hypot(x - previousX, z - previousZ);
      actor.animate(elapsed, distanceM > 0.0001, {
        speed: config.speed,
        distanceM,
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
      disposeStyle?.();
      label.remove();
      bubble.remove();
      dialog.remove();
    },
  };
}
