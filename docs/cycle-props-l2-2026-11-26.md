# Generic bicycle, kick scooter and riders at L2

The local outdoor group PROP-03 comprises a hybrid bicycle, a standing kick scooter and their procedural riders. The new bicycle uses a double-triangle frame, paired stays and fork, wire spokes, brake discs, saddle, chain, opposed cranks and flat grips. The rider sits forward with a foot on each pedal. The scooter uses a low deck, covered hubs, curved fenders, integrated fork, stem collar, controls, headlamp and rear light. Its rider stands with staggered feet on the deck. Both poses share the actual grip coordinates with their controls.

[Editable procedural source](../apps/web-preview/src/props.js) · [Runtime collision and placement](../apps/web-preview/src/life.js) · [Six-kind GLB](../apps/web-preview/public/props/campus-props.glb)

## Dimensional evidence

| Model | Length × grip width (m) | Wheelbase (m) | Wheel diameter (m) | Reference |
| --- | ---: | ---: | ---: | --- |
| Hybrid bicycle | 1.751 × 0.600 | 1.057 | 0.694 | Trek FX 2 size M lists a 105.7 cm wheelbase, 28.5 cm bottom bracket height and 700 × 35 tires. |
| Electric kick scooter | 1.238 × 0.582 | 0.928 | 0.254 | Segway's manual lists 1.210 × 0.570 × 1.264 m and 10-inch tires for a representative standing scooter. The generic model includes its own fender overhang and controls. |

The manufacturer dimensions guide the proportions. The geometry and materials are original. The university describes campus bicycle and scooter parking. The chosen models, riders and activity paths are authored for the scene. [Trek specifications](https://www.trekbikes.com/us/en_US/bikes/hybrid-bikes/active-fitness-bikes/fx/fx-2/a/548019/) · [Segway specification manual](https://support.segway.com/product_files/20230714054332_Ninebot%20KickScooter%20Max%20G2%20Product%20Manual.pdf) · [UO Transportation Services](https://transportation.uoregon.edu/bike).

The mesh uses a single material and one draw call per visible rider and vehicle pair. The bicycle has 3,236 triangles and the scooter 1,748. The four tire centers reach the local ground plane. The default rider and vehicle heights are 1.750 m and 1.944 m. Runtime capsules follow the resized footprint and use each rider's height. Feet remain on the supports across the tested height variants. The model uses static crank, wheel and rider poses on the authored routes. Scene grade can still leave gaps at the wheels since route placement uses one height for the entire model.

## Verification

- Eight paired front, profile, rear and head-on renders checked silhouette and rider attachment. All six exported position, normal and color arrays match their current procedural meshes. The four road-vehicle meshes match the preceding export byte for byte at the attribute level. The six export node transforms match the preceding export.
- Desktop and phone production previews loaded the new export and used two bicycles and two scooters at the default density. Both verified movement, assigned pedestrian paths and the model-derived collision sizes. All four density modes produced 0, 7, 29 and 74 colliders.
- Formatting, 195 unit tests, four targeted browser checks, the production build, asset ledger structure, source manifest and viewer hash checks passed. This scope used the export and navigation browser cases. The older full-scene draw-call check has a separately documented baseline issue.
- The prior export remains available at [release 11bac65](https://github.com/williamQ96/open-campus-uo/blob/11bac6514dc0d8c1bc2ede3f7439d664440aea83/apps/web-preview/public/props/campus-props.glb). The revised GLB has SHA-256 `3b427b6612681ea8a93bec416dd54ea166b2b1043b535cdc13c2134e3dbfe2b4`. This refinement is local and uncommitted.
