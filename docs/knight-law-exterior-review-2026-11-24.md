# Knight Law Center exterior review

The local preview uses a registered exterior for William W. Knight Law Center, UO 050, under the existing scene ID `roof-f52041e8`. The rebuilt envelope covers 4,460.08 m² and follows the first-floor plan around the open east courtyard. It includes the Agate Street arch, projecting west gables, two differently oriented east wings, the recessed north roof, the curved glazed roof of the interior street, and the low glazed gallery with brick piers. The original classroom fallback remains in use for entry. [University map](https://map.uoregon.edu/) · [University architecture archive and courtyard photograph](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/william-w-knight-law-center) · [Architect's west elevation photograph, PDF p. 16](https://pages.uoregon.edu/ftepfer/projects/PacificDominoLabs2015-17/ArchSelectProcess/QualificationsSubmitted/YGHPacificHall.pdf#page=16).

The campus map was shifted 2.50 m west and 0.20 m north to align the wall outline with the 2024 aerial. The 2017 surface set the main roof levels and informed the dormer and clerestory tiers. At joined hips and gables, overlapping roof solids follow independent pitches. Window spacing on partially visible elevations, roof fittings, threshold elevations, and paving edges use approximate dimensions. The GLB contains original geometry and colors. [2024 aerial service](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 surface evidence](campus-surface-2017-2026-11-24.md) · [Earlier west façade study](knight-law-refinement.md).

| Roof comparison | Before | After |
| --- | ---: | ---: |
| Coverage of 3,653 eligible raster cells | 2,834 | 3,653 |
| Median absolute height difference on 2,834 matched cells | 2.104 m | 0.488 m |
| South angled wing on 418 matched cells | 2.969 m | 0.193 m |
| Lower courtyard gallery on 256 matched cells | 7.684 m | 0.048 m |

The matching cells use the same raster that informed the roof geometry. Samples within 0.88 m of the exterior plan or within 0.64 m of a region edge were excluded, along with nonfinite values and heights outside 8–24.7 m. Twelve paired views cover the roofs, west arch, north and south elevations, and east courtyard in toon, shaded, and landscape contexts. The replacement preserved the tested neighbor batch's geometry attributes and indices. Three registered approaches are walkable in the preview and all 7,710 active route edges clear the footprint. Desktop and mobile production checks exercised naming, selection, courtyard collision, and fallback on an invalid GLB or incorrect source anchor.

The exterior was reviewed at L2 against the [Knight Library exemplar](knight-library-registration-2026-11-23.md). The [editable layout](../data/metadata/knight-law-site-review.json) and [generator](../scripts/build-knight-law-site-review.py) reproduce the registered package. From the project root, run `python scripts/build-knight-law-site-review.py --audit <audit.json>`. The research worktree's `exterior-l2/east-campus-20261124/` contains the registered outlines, annotated sources, paired renders, roof residuals, and production checks.
