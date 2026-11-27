// SPDX-License-Identifier: Apache-2.0
import { distance } from "./routing.js";

function insideRing(east, north, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [e0, n0] = ring[j];
    const [e1, n1] = ring[i];
    if (
      n0 > north !== n1 > north &&
      east < e0 + ((e1 - e0) * (north - n0)) / (n1 - n0)
    )
      inside = !inside;
  }
  return inside;
}

export function createPavedRouteAccess(polygons) {
  const surfaces = polygons.map(([outline, ...holes]) => {
    const east = outline.map((point) => point[0]);
    const north = outline.map((point) => point[1]);
    return {
      bounds: [
        Math.min(...east),
        Math.min(...north),
        Math.max(...east),
        Math.max(...north),
      ],
      outline,
      holes,
    };
  });
  const paved = (east, north) =>
    surfaces.some(
      ({ bounds: [west, south, edge, top], outline, holes }) =>
        east >= west &&
        east <= edge &&
        north >= south &&
        north <= top &&
        insideRing(east, north, outline) &&
        !holes.some((ring) => insideRing(east, north, ring)),
    );

  return (point, node) => {
    // Free pins off the surveyed paving retain approximate access. A point
    // already on it uses the registered network to leave the paved area.
    if (!paved(...point)) return true;
    const steps = Math.ceil(distance(point, node) / 0.2);
    for (let i = 1; i <= steps; i++) {
      const t = i / steps;
      if (
        !paved(
          point[0] + (node[0] - point[0]) * t,
          point[1] + (node[1] - point[1]) * t,
        )
      )
        return false;
    }
    return true;
  };
}
