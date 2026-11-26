# Pilot furnishings at L2

The default scene replaces the pilot furniture layer with nine wood benches, eleven dark-green acorn lights and one three-hoop rack. PROP-01 covers these representative pilot furnishings. The asset records campus design cues and modeled positions. A current physical inventory, surveyed offsets, rack count and fixture photometry remain open.

## Shapes and placement

- Each bench is 1.524 m wide and about 0.97 m tall, with separate seat and back slats, shaped armrests, wood legs and adjustable anchor shoes. Seat height is about 0.43 m above the highest sampled support. The campus recommends a five-foot anchored Parkside bench. [UO exterior improvements](https://cpfm.uoregon.edu/sites/default/files/2026-05/_div_32_exterior_improvements_050426.pdf) · [Gardenside catalog](https://www.gardenside.com/Gardenside-2011-Catalog.pdf).
- The lamp has a 3.048 m post with a tapered shaft, fluting, stepped base, frosted acorn globe and metal finial. UO identifies this form and finish for representative campus lighting. [UO outdoor lighting plan](https://cpfm.uoregon.edu/sites/default/files/lighting_plan-2020.pdf) · [Earlier fixture diagram](https://cpfm.uoregon.edu/sites/default/files/lightingplan_update03_2012_0.pdf).
- The original 0.914 m tall rail-mounted rack reuses the archived three-hoop model. The architect's gallery shows bicycle parking on both sides of the pictured south entrance. The adopted southwest position uses current modeled paving and a representative three-hoop row. The exact facility registration remains open. [Tykeson Hall gallery](https://www.office-52.com/work/tykeson-hall-university-of-oregon/) · [Original rack](bike-rack-candidate-2026-11-04.md).
- Nine legacy anchors retain their horizontal positions and eleven move. The PLC courtyard bench moves five meters south of its legacy anchor. Two Johnson Lane lamp bases move four and five meters south, respectively, clearing the modeled road edge. The editable register includes the old and new ENU coordinates, foot samples, collision rectangles and nearest clearance measurements. [Placement register](../data/metadata/pilot-furnishings-l2.json).

## Verification

- Checked all 21 footprints against 7,710 route edges and road widths, the current modeled building footprints and authored entrance approaches. The measured minima are 1.451 m to a graph edge, 1.18 m to a modeled road surface, 1.68 m to a building footprint and 4.88 m to an authored approach envelope. Measurements describe the scene.
- Raycast 97 support samples in the live scene. The largest reference-to-rendered ground difference was 0.018 m. Center probes found no modeled road surface or low tree geometry at the fixture anchors. Replacement foundations extend into the sampled supports.
- Four matched camera pairs keep the baseline draw counts of 85, 83, 104 and 87. Furnishings use three material batches for wood, hardware and glass. Desktop and phone production smoke checks each loaded the 21 obstacle envelopes and the same 522 selectable buildings. Browser tests confirm open paths around the model and recovery to the archived furniture layers when replacement bytes fail verification.
- The historical clean-map performance check requires fewer than 180 draws. Five consecutive frames at the default spawn camera measured 203 draws in each furniture version.
- The reproducible export is pinned by SHA-256 and the source art, navigation graph, corridor patch, heightfield and archived rack are checked during export. The scene installs the new asset and its collision boxes together. The development comparison is available at `/?exterior-review=furniture-baseline`.

Run `python scripts/build-pilot-furnishings.py --out PATH` to export. Run `npm run test:browser -- pilot-furnishings.spec.js` from the web-preview app for the two viewports and invalid-asset fallback. The model and scene adoption are local and uncommitted.
