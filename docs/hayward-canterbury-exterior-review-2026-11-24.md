# Hayward Field and Canterbury Court exterior review

## Hayward Field

The editor replaces the rectangular west-stand placeholder with the public exterior of the rebuilt stadium. The outline follows the 2024 orthophoto and the outdoor campus map. The model has a continuous U-shaped roof, 76 curved timber ribs, stepped seating, nine track lanes, an open infield, the Powell Plaza approach and a tapered tower. The height of the tower is 57.51 m above the modeled grade, based on the UO press kit. The roof perimeter was traced in plan, and its height profile and connection to the stands use completed-project photos. The regional elevation mosaic still gives the pre-rebuild stands. [UO project press kit, PDF pages 6 and 10–11](https://goducks.com/documents/download/2021/3/31/HF_UOPressKit_03302021.pdf) · [Venue design and plaza](https://hayward.uoregon.edu/about) · [Structural engineer's exterior views](https://www.mka.com/projects/university-of-oregon-hayward-stadium/).

The integrated exterior retains `context-oc-hayward`. The 2024 orthophoto places the redundant northwest `roof-64589bec` and east `roof-f7af1b95` meshes inside the rebuilt stadium. About 87.6% of the northwest source footprint and 81.9% of the east source footprint overlap the UO 280 mapped exterior. Each old ID stays in the ledger with its prior grade and a link to Hayward. Columbia Hall remains selectable under `uo-036`. The reopened stadium center and north plaza stay clear of ground collision, with support and tower footprints on their own polygons.

Source batch `context-campus-2-1` loses 600 triangles from `[9892, 10492)`. The twenty generated trees inside the playing area, stands and paved site are removed only if the new exterior installs successfully. The retained vertex attributes, batch triangle order and retained tree indices compare exactly. The graphics describe the public exterior. Roof height, fabric appearance, stand row intervals, facade mesh, access thresholds and tower details are approximate. No source imagery, signage or artwork is embedded.

## Canterbury Court

The existing courtyard and stepped roof remain in the original context batch. Pale stucco, two rows of framed windows, simple entry panels and a short railed ramp model the published exterior type. The public listing photo shows the two-story wall and a yellow-railed ramp. Its exact orientation was inferred from the 2024 image, and the model retains the existing estimated north approach and enclosed 287.57 m² open-air court. Courtyard window intervals and exterior door positions are schematic. [Exterior listing](https://www.apartments.com/canterbury-court-eugene-or/m9nrd1h/) · [Property source](https://caprieugene.com/virtual-tours/) · [Existing roof registration](compound-context-exteriors-2026-11-23.md#canterbury-court).

Only Canterbury's authored geometry changes in the 31-member context-roof package. The other 30 records compare exactly. The original `roof-53501ed1` remains available to the viewer, with the same court collision and approach.

## Verification

Nine paired views, a 7,710-edge route screen, two walkable modeled stadium entrances, canopy and tower rays, and eight runtime collision probes were checked. Local production desktop and mobile kept both building names and the Columbia identity. Invalid stadium bytes, a changed terrain hash, a bad east-stand batch anchor and a bad last tree anchor each restore the previous stadium records, trees and collision. Repeated exports match the local production package. The revised scene has 515 selectable buildings, including 437 in source batches, and 139 road segments.

The [Hayward specification](../data/metadata/hayward-exterior-review.json), [builder](../scripts/build-hayward-exterior-review.py) and [Canterbury specification](../data/metadata/compound-context-roofs.json) are editable. The terrain-covered field and the main entrance are scene geometry and do not supply an interior model. Local development and verification only.
