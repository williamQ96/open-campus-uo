# Bicycle prop refinement

2026-11-03 · Local, unpublished · inventory PROP-03 remains level 1.

The original generic bicycle and rider now have open low-poly tires, rims and spokes, a seat post, crank and pedals. Placement and activity routes are unchanged. Dimensions and rider posture remain approximate. Scooter refinement remains open. The exported prop collection and runtime procedural source were regenerated; the newly imported `assets/props/campus-props-bike-refinement.blend` is an editable candidate. The prior Blender file is preserved.

[Near-view review](images/bicycle-refinement-review.png). The candidate was checked in a local browser with a standalone neutral scene; this is not an in-campus acceptance view. The web production build passed and the five prop types had finite vertex coordinates. The updated bicycle has 3,960 non-indexed vertices.

Context reference: [UO Transportation Services — Bike Parking](https://transportation.uoregon.edu/bike) confirms bikes and scooters are used on campus. It does not substantiate a particular vehicle design or placement; no imagery or geometry from that page was copied or redistributed. Original geometry is contributed under CC BY 4.0.

The shared viewer lock still records its original `src/props.js` hash. This downstream content change intentionally leaves the lock untouched; reconcile it during any future managed viewer upgrade. The remaining inventory rows have not been reclassified or individually verified in this pass.

A subsequent [campus-context review and prop batch](environment-batch-2026-11-03.md) supersedes the earlier standalone-only verification.

**Rider follow-up:** Foot-to-pedal/deck and hand-to-handle connections were adjusted for sampled rider heights; poses remain static. See [review](environment-refinement-2026-11-03.md#rider-contact).
