# Shared entrance portal review

PROP-04 uses an original paired storefront assembly as the reusable marker at generic campus approaches. It retains the green leaves and gold surround. The visible assembly now has separate recessed infills, stiles, top and kick rails, a transom and a threshold. Each leaf has a projecting pull on the front and a push bar on the rear. The 54 mm stiles, 57 mm top rails and 98 mm bottom rails use published narrow-stile dimensions. The 1.95 × 2.88 × 0.24 m envelope remains the viewer's illustrative marker size. The opaque infills read as glazing while hiding the solid backdrop of the campus buildings. [Commercial dimensions and hardware](https://www.kawneer.com/products/doors-and-entrances/190-350-500-standard-entrances/).

The default scene draws this model at 323 generic approaches. The other 288 entrance records point to building-authored gates and use the invisible interaction surface. The 611 entrance records, including their approach points and walkability flags, match the previous runtime at the tested scene configuration. The visible center seam has a 16 mm gap. An invisible pick surface spans it for mouse and touch. Physical door locations, appearance and access remain subject to site-specific verification.

## Geometry and runtime checks

The trim and leaves render as two instanced meshes. An export check reimported both parts and matched their 576 positions, normals and colors, triangle indices, material roughness and local transforms. Geometry tests ray-traced both pulls and bars, the sill, transom, recessed glazing and open center seam. The browser checks covered center-seam selection, authored door selection, wall occlusion, keyboard entry, mouse and touch entry, and return to the outdoor position.

The first-person comparison at scene entry roof-78e56866 used the same camera position, heading, viewport and disabled activity in both renders. It measured 49 draws before and after. Scene triangles rose from 771,888 to 845,532, equal to 323 markers × 228 added triangles. This is a camera-specific draw and triangle count. Device frame time remains unmeasured.

Formatting, 195 unit tests, six focused browser tests, the production build, 340 archived files and 272 viewer pins passed. Desktop and phone production previews both entered the shared classroom through the generic marker and returned to the same approach. This batch is local and uncommitted.

## Editable model and export

The geometry generator lives in the viewer and the standalone GLB contains the same two meshes at the model origin. The standalone model omits the campus position and the interaction proxy. Run the exporter from the viewer directory with its local Vite server on port 5173 and provide a new output GLB path. The exporter verifies the source hash and geometry roundtrip before it writes. The original model is CC BY 4.0. Reference pages stay external. [Generator](../apps/web-preview/src/entrances.js) · [Exporter](../apps/web-preview/scripts/export-entrance.mjs) · [GLB](../assets/exterior-refinement/entrance-portal-l2-2026-11-26.glb) · [Earlier version and evidence](entrance-performance-2026-11-04.md).
