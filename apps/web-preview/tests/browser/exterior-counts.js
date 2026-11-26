export const DEFAULT_BATCHED_BUILDINGS = 169;
export const DEFAULT_SELECTABLE_BUILDINGS = 555;
export const DEFAULT_ENTRANCES = 559;
const DEFAULT_CONTEXT_ROOF_TREATMENTS = 2;

// Earlier review baselines restore only their own source buildings and roof treatments.
export function exteriorCounts({ buildings = 0, batched = 0, roofs = 0 } = {}) {
  return [
    DEFAULT_SELECTABLE_BUILDINGS + buildings,
    DEFAULT_BATCHED_BUILDINGS + batched,
    DEFAULT_CONTEXT_ROOF_TREATMENTS + roofs,
  ];
}
