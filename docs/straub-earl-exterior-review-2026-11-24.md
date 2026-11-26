# Straub and Earl Hall exterior review

The local default has two independently selectable exteriors. Straub retains `roof-5ded2bf0` and Earl retains `roof-f01c8434`. The earlier Earl south end and southeast wing meshes `roof-303d99fd` and `roof-aedc356a` are absorbed into the Earl model and retained in the ledger as historical mappings. The two grounds meet at the west wall of Earl along the classroom expansion. The outdoor approaches terminate at their modeled doors. [Campus map](https://map.uoregon.edu/) · [Scene identity crosswalk](earl-boundary-audit.md#registered-footprint-follow-up-2026-11-24).

| Exterior | Ground footprint | Rebuilt features |
| --- | ---: | --- |
| Straub | 2,877.97 m² | West gable and perpendicular returns, gabled portico with three stone arches, stucco attic band, dormers, two levels of classroom roof, and the sloped auditorium roof. |
| Earl | 2,191.27 m² | Separate McClure, Morton, Sheldon, Stafford and Young roof levels, the lower connecting spine, open courts between the wings, and upper window bands with painted ribbed panels. |

The architect's post-project photographs establish Straub's west portico and glazed approach from the north. The schematic sections and the newer roof data align the shared classroom wing over part of Earl. The 2026 housing photo guides the ribbed panels, glazing and brick base on the pictured courtyard frontage. The university reported window and cladding replacements in 2025–26 and reroofing on Young and Stafford in 2026. Roof finishes and the window details of floors or elevations outside the photo coverage remain approximate. [Straub cultural survey](https://cpfm.uoregon.edu/straubhall2025) · [Opsis project photographs](https://opsisarch.com/project/university-of-oregon-straub-hall-building/) · [Completed project](https://rowellbrokaw.com/blog/2015/6/30/recent-photos-of-the-new-uo-straub-hall) · [Earl housing photo](https://housing.uoregon.edu/earl) · [2026 Earl work](https://news.uoregon.edu/content/get-update-construction-activity-around-university-0).

## Roof evidence

The older Lane County grid includes low surfaces in the area of the classroom expansion. Across 160 cells on the lower north lecture block, median surface height rose from 4.263 m in the old grid to 13.008 m in the later survey. The adjacent raised roof has a median of 17.068 m across 200 cells in the later survey. A source-locked DOGAMI export of the 2017 USACE highest-hit raster supplies these post-expansion observations. The export uses a 1 m grid in the project's CRS. Highest surfaces include equipment and some vegetation. [2017 campus surface record](campus-surface-2017-2026-11-24.md).

| Exterior | Eligible cells | Cells hit by both meshes | Prior median absolute height difference | New median absolute height difference |
| --- | ---: | ---: | ---: | ---: |
| Straub | 2,509 | 2,144 | 1.772 m | 0.078 m |
| Earl | 1,813 | 1,585 | 1.232 m | 0.072 m |

## Verification and scope

Compared 11 before-and-after views including the west portico, north glazing, south landing and Earl's northeast and east courts. Both exteriors reach L2 after individual review against Knight Library for recognizable massing, major roof and façade features, distinct materials and scene integration. Recent reroofing finishes, the exact threshold elevations, wall and roof equipment dimensions, and some rear openings remain approximate. The modal doors lead to the shared interior preview. [Knight Library comparison](knight-library-registration-2026-11-23.md) · [Straub basement source record](interior-preflight-straub-hall-2026-11-16.md).

Screened all 7,705 route edges at 0.42 m with zero new conflicts. Runtime probes check the two concave approaches, neighboring walls and the shared classroom mass. Three guarded index ranges in a shared context batch compose with the Women's Memorial Quad review. The before-and-after index and vertex attribute comparison confirms that the two unrelated members keep the same buffers and IDs. A failed hash restores the previous two exteriors, overlay and retired sections together.

The editable sources are [the scene layout](../data/metadata/straub-earl-site-review.json) and [the builder](../scripts/build-straub-earl-site-review.py). Run `python scripts/build-straub-earl-site-review.py --audit <audit.json>` from the repository root. Research evidence, source photographs and comparative renders are in `exterior-l2/straub-earl-20261124/`. The delivered 17.3 MB model contains original geometry.
