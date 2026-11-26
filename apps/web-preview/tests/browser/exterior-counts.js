export const DEFAULT_BATCHED_BUILDINGS = 340;
const DEFAULT_SELECTABLE_BUILDINGS = 519;
const DEFAULT_CONTEXT_ROOF_TREATMENTS = 7;

// Earlier review baselines restore only their own source buildings and roof treatments.
export function exteriorCounts({ buildings = 0, batched = 0, roofs = 0 } = {}) {
  return [
    DEFAULT_SELECTABLE_BUILDINGS + buildings,
    DEFAULT_BATCHED_BUILDINGS + batched,
    DEFAULT_CONTEXT_ROOF_TREATMENTS + roofs,
  ];
}
