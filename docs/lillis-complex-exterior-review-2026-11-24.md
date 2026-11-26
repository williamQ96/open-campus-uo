# Lillis Business Complex and Computing Center exterior review

Five registered exterior models replace the old blockouts under their existing IDs. Each is reviewed at L2 against the [Knight Library comparison](knight-library-registration-2026-11-23.md). University outlines were translated 2.68 m west and 0.40 m north to register with the aerial. The Computing Center outline was trimmed alongside Lillis to maintain the separation documented by the university. [University map](https://map.uoregon.edu/) · [Lillis ground-floor plan](https://business.uoregon.edu/sites/default/files/media/lillis-map-level-1.pdf) · [Computing Center resource survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/computingcenter_2025.pdf) · [2024 OSIP aerial](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

| Model | Scene ID | Wall envelope | Main exterior elements |
| --- | --- | ---: | --- |
| Chiles Business Center | `roof-1afe792e` | 450.386 m² | South entry pavilion, tall divided arch window, banded brick walls, distinct west-end roof |
| Anstett Hall | `roof-0a498bf7` | 574.954 m² | Raised west court entrance, terra-cotta portal and triple arches, raised basement, divided sash, layered flat roof |
| Peterson Hall | `roof-75e776d0` | 563.983 m² | East court staircase and portal opposite Anstett, raised basement, divided sash, raised east roof wing |
| Lillis Hall | `roof-86754ad7` | 3,369.213 m² | Glazed photovoltaic south wall, arched atrium roof, curved north rotunda, lower terraces and auditorium, five modeled roof array groups |
| Computing Center | `context-b0039` | 1,040.850 m² | Two-story brick and concrete mass, tall divided windows, equipment deck and recessed north entrance |

The old Peterson mesh crossed Chiles, Peterson and part of Lillis. Its replacement occupies Peterson's registered campus outline. The prior Chiles-labeled mesh was at Computing Center, with 86.11% of the mesh inside that building's university outline. The canonical Chiles ID now sits on Chiles, while the two overlapping Computing Center blockouts are represented by one corrected exterior under the Computing Center ID. Lillis's east wing supersedes unnamed `roof-7fee2881`, whose area fell 96.18% inside the Lillis footprint. Its 302 triangles are removed from one source batch under pinned anchors. Its table entry retains the earlier ID and points to Lillis. [Lillis complex buildings](https://business.uoregon.edu/about/lillis-complex) · [Computing Center survey and site plan](https://cpfm.uoregon.edu/sites/default/files/2025-01/computingcenter_2025.pdf#page=4).

The plaza includes stair approaches, planters, lamps, walkways and three trees registered from the university inventory, including the documented yellow buckeye. Each historic hall uses its own courtyard-facing main entrance. Nine entrances are modeled across the five buildings. The Chiles south projection follows the elevation and historic photograph. The Lillis solar strips and north rotunda follow the case study and aerial. Glazing, mullion spacing, individual rooftop fittings, stair dimensions and some courtyard edges remain approximate. [Anstett survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/anstetthall_2025.pdf#page=4) · [Peterson survey](https://cpfm.uoregon.edu/sites/default/files/2025-01/petersonhall_2025.pdf#page=4) · [Chiles repair elevations](https://bid.oregonstate.edu/opportunity/viewFile/1334/UO%20CHILES%20ROOF_DRAWINGS.pdf?1345156445=) · [Chiles archive photograph](https://expo.uoregon.edu/spotlight/history-uo-architecture/feature/chiles-business-center) · [Lillis case study](https://pages.uoregon.edu/arempel/_documents/Lillis_final_small_file.pdf#page=4).

| Model | Eligible samples | Paired hits | Previous median absolute difference | L2 median absolute difference |
| --- | ---: | ---: | ---: | ---: |
| Chiles | 368 | 0 | — | 0.032 m on all eligible samples |
| Anstett | 474 | 458 | 1.834 m | 0.178 m |
| Peterson | 477 | 411 | 0.679 m | 0.148 m |
| Lillis | 3,007 | 1,306 | 1.667 m | 0.156 m |
| Computing Center | 907 | 323 | 0.551 m | 0.028 m |

The roof samples come from the 2017 surface used to guide the models, with a 0.96 m inset and building-specific height ranges. The replacement covers all 5,233 eligible points. Chiles has no paired samples because its old mesh had a different location. [2017 campus surface](campus-surface-2017-2026-11-24.md).

Reviewed nineteen paired views. The neighboring batch keeps the same position, normal and color buffers, and its index sequence differs by exactly the pinned 302-triangle range. The 7,710 active route edges passed the modeled clearance screen. Desktop and mobile production verified selection of all five buildings, nine walkable model entries and thirteen collision probes. Corrupt model bytes, an invalid terrain hash or a shifted batch anchor restored the entire prior group. Default selection has 524 buildings including 451 batch members.

The [editable specification](../data/metadata/lillis-complex-site-review.json) and [builder](../scripts/build-lillis-complex-site-review.py) generate the assets. Run `python scripts/build-lillis-complex-site-review.py --audit <audit.json>` from the project root. The research worktree under `exterior-l2/east-campus-20261124/` holds the georeferenced overlay, source crosswalk, before-and-after images, and smoke results.
