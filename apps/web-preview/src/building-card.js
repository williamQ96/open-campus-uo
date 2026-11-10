// SPDX-License-Identifier: Apache-2.0
import * as THREE from "three";

export function createBuildingCard(viewport, camera, { onEnter, onClose }) {
  const card = document.createElement("section");
  card.className = "building-card";
  card.hidden = true;
  card.setAttribute("aria-labelledby", "building-card-name");
  const heading = document.createElement("h2");
  heading.id = "building-card-name";
  const close = document.createElement("button");
  close.className = "building-card-close";
  close.textContent = "×";
  close.setAttribute("aria-label", "Close building card");
  const info = document.createElement("p");
  info.className = "building-card-summary";
  const occupants = document.createElement("p");
  occupants.className = "building-card-occupants";
  const source = document.createElement("a");
  source.className = "building-card-source";
  source.target = "_blank";
  source.rel = "noopener noreferrer";
  const enter = document.createElement("button");
  enter.className = "building-card-enter";
  enter.textContent = "Enter";
  card.append(heading, close, info, occupants, source, enter);
  viewport.append(card);
  for (const type of ["pointerdown", "pointerup", "wheel"])
    card.addEventListener(type, (event) => event.stopPropagation());
  let keyboardOrigin = null,
    returnFocus = null,
    pendingRestore = null;
  viewport.addEventListener(
    "pointerdown",
    () => {
      keyboardOrigin = null;
    },
    true,
  );
  viewport.addEventListener(
    "keydown",
    (event) => {
      if (
        event.key === " " &&
        card.contains(event.target) &&
        event.target.closest?.("button")
      ) {
        event.stopPropagation();
        return;
      }
      const label = event.target.closest?.(".building-label");
      if (label && ["Enter", " "].includes(event.key)) {
        keyboardOrigin = label;
        // Keep the native button activation; do not let movement swallow Space.
        event.stopPropagation();
      }
    },
    true,
  );
  close.onclick = onClose;
  enter.onclick = () => record && onEnter(record);
  let record = null,
    anchor = new THREE.Vector3(),
    lastPosition = "";
  let dataset = null;
  function renderInfo() {
    const details =
      dataset?.version === 1 ? dataset.records?.[record?.id] : null;
    const url = details?.source?.url;
    let validUrl = false;
    try {
      validUrl = new URL(url).protocol === "https:";
    } catch {
      /* Unknown source. */
    }
    const verified =
      typeof details?.purpose === "string" &&
      validUrl &&
      typeof details.source.label === "string" &&
      /^\d{4}-\d{2}-\d{2}$/.test(details.source.checked_on);
    info.textContent = verified
      ? details.purpose
      : "Information not yet verified.";
    const names =
      verified && Array.isArray(details.occupants)
        ? details.occupants.filter(
            (name) => typeof name === "string" && name.trim(),
          )
        : [];
    occupants.textContent = names.length
      ? `Known occupants: ${names.join(", ")}`
      : "";
    occupants.hidden = !names.length;
    source.hidden = !verified;
    if (verified) {
      source.href = url;
      source.textContent = `${details.source.label} · checked ${details.source.checked_on}`;
    } else source.removeAttribute("href");
  }
  function updatePosition() {
    if (pendingRestore) {
      const target = pendingRestore;
      pendingRestore = null;
      if (
        document.activeElement === viewport &&
        target.isConnected &&
        !target.hidden &&
        target.getClientRects().length
      )
        target.focus({ preventScroll: true });
    }
    if (!record) return;
    const point = anchor.clone().project(camera);
    card.hidden = point.z <= -1 || point.z >= 1;
    if (card.hidden) return;
    const width = viewport.clientWidth,
      height = viewport.clientHeight,
      w = card.offsetWidth,
      h = card.offsetHeight;
    const top = height < 500 ? 88 : width <= 600 ? 154 : 174,
      bottom = width <= 600 || height < 500 ? 110 : 24;
    const x = THREE.MathUtils.clamp(
      ((point.x + 1) * width) / 2 + 18,
      12,
      Math.max(12, width - w - 12),
    );
    const maxY = Math.max(12, height - bottom - h);
    const y = THREE.MathUtils.clamp(
      ((1 - point.y) * height) / 2 - h / 2,
      Math.min(top, maxY),
      maxY,
    );
    const position = `translate(${Math.round(x)}px, ${Math.round(y)}px)`;
    if (position !== lastPosition) {
      card.style.transform = position;
      lastPosition = position;
    }
  }
  return {
    setInfo(value) {
      dataset = value;
      if (record) renderInfo();
    },
    show(building, position) {
      const keyboard =
        keyboardOrigin?.dataset.buildingId === building.id
          ? keyboardOrigin
          : null;
      keyboardOrigin = null;
      if (record?.id !== building.id) returnFocus = keyboard;
      pendingRestore = null;
      record = building;
      card.dataset.buildingId = building.id;
      heading.textContent = building.name || "Unidentified structure";
      renderInfo();
      anchor.copy(position);
      card.hidden = false;
      lastPosition = "";
      updatePosition();
      if (keyboard && !card.hidden) close.focus({ preventScroll: true });
    },
    hide() {
      if (card.contains(document.activeElement)) {
        pendingRestore = returnFocus;
        viewport.focus({ preventScroll: true });
      }
      returnFocus = null;
      record = null;
      card.hidden = true;
    },
    update: updatePosition,
  };
}
