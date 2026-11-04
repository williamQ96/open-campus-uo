# Villard Hall east facade

The source-pinned procedural replacement retains `roof-399c648e`, the original campus GLB, and the approximate campus footprint. It interprets the east facade using [Daderot's 2017 CC0 photograph](https://commons.wikimedia.org/wiki/File:Villard_Hall_-_University_of_Oregon_-_Eugene,_Oregon_-_DSC09617.jpg) and the [UO 2017 assessment, east elevation](https://cpfm.uoregon.edu/sites/default/files/171103_uo_villard_hall_robinson_assessment_final_reduced.pdf) (page 34, PDF page 40). The original CC0 photograph is archived with metadata and hash; the UO document is linked, not redistributed. No photo texture is used.

The simplified mass, tower roofs, windows, columns, entry porch, rail and ornamental details are interpretations, not a dimensional reconstruction. Eight shrubs represent a garden shown in the photograph; placement and species are illustrative. Non-east elevations are placeholders; current conditions, dimensions, collision clearance and accessibility are unverified. Building remains level 1. Interior is untouched.

The east scene was reviewed before and after; regression checks cover selection, rendering modes and the campus landmark scene. [Before](images/villard-east-before.png) / [after](images/villard-east-after.png).

## Arch follow-up

The six east ground-floor windows now use continuous arched profiles rather than overlapping boxes and circles. Geometry remains a simplified interpretation of the existing photo and UO elevation; see [scene review](images/villard-arches-after.png).

## Roof follow-up

Three tapered roof volumes replace gabled stand-ins using the existing photo and labeled elevation. Shape and dimensions are approximate; the roof is not a measured reconstruction. [Scene review](images/villard-tapered-roof.png).

## Multi-elevation follow-up, 2026-11-04

The [UO 2017 Villard Hall assessment](https://cpfm.uoregon.edu/sites/default/files/171103_uo_villard_hall_robinson_assessment_final_reduced.pdf), PDF pages 40–41 (printed pages 34–35), documents north, east, south and west historical elevations. Later proposal drawings are not treated as constructed conditions. The document is consulted, not redistributed or used as a texture.

The source-pinned reversible exterior now has schematic north and south openings, bands, north entry steps and four approximate corner roof forms. Existing east details and landscaping remain. These are stylized approximations: dimensions, current doors and windows, western facade, precise mansard geometry and grading require further survey. The level remains 1; this is not a claim of Knight-equivalent completion. [North before](images/villard-north-v2-before.png), [north after](images/villard-north-v2-after.png), [south](images/villard-south-v2.png), [east and roof](images/villard-east-v2.png).

Three conservative ENU collision rectangles cover the replacement body, north steps and existing east portico while retaining the original footprint. The steps and portico are obstacles, not verified walkable or accessible entrances. No existing navigation graph edges intersect these rectangles with a 0.5 m margin. The nearest surveyed graph node is approximately 62 m from the building center, so precise entrance routing and accessibility remain unverified; a building-approximate graph route was tested. Nine sampled north approach positions showed no other building or vegetation ray hits; this is not a comprehensive clearance survey.

The previous layer is preserved at `assets/exterior-refinement/villard-before-multiface-2026-11-04.json`. The underlying campus GLB, original geographic footprint, existing vegetation and interiors are unchanged.
