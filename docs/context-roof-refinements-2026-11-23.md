# Context roof refinement review

The local campus preview uses thirty-one revised context roofs. They retain individual scene IDs and remain L1. The first eleven are documented below, followed by four simple pitched forms, [two compound exteriors](compound-context-exteriors-2026-11-23.md), and [fourteen flat or stepped roofs](context-flat-roofs-2026-11-23.md). Open [the revised scene](http://127.0.0.1:5173/) or [the prior roofs in the development viewer](http://127.0.0.1:5173/?exterior-review=roof-baseline).

## How the roofs were selected

- Screened the 534 existing building IDs. Of these, 59 context meshes have sufficiently regular outlines for a simple roof trial and one strong reciprocal state footprint match. Presence and shape were compared with the newer imagery by ID. The state geometries may predate the imagery. [Campus footprint screen](exterior-refinement-plan.md#campus-footprint-comparison-2026-11-23), [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx).
- Fit two orientations of gable and hip models against 1 m cells from historic first returns, with spatial blocks withheld during each fit. Both the source and fitted roof surfaces were compared at the held-out cell centers. The same held-out set helped select the form and orientation. Sixteen models passed the fit screen. [NOAA 2013–2015 Lane County collection](https://www.fisheries.noaa.gov/inport/item/57407), [campus point-cloud screen](exterior-refinement-plan.md#historical-point-cloud-height-screen-2026-11-23).
- Compared all sixteen roofs with separate 2024 Oregon orthophoto crops. Eleven have a sufficiently clear single gable or hip silhouette. Five have uncertain outlines, equipment, or separate roof sections and were deferred. The test concerns roof form and dates. Current thresholds, surveyed dimensions, heights after 2015 and building names remain to be verified. [Oregon 2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

## Installed roofs

Errors are the median absolute heights in metres at held-out historical cells. The previous reference is the authored roof planes in the existing appearance plan. The comparison describes agreement with historical heights.

| Scene ID | Form | Held-out cells | Previous difference | Revised difference |
| --- | --- | ---: | ---: | ---: |
| `roof-3c2b8bdc` | Gable | 38 | 0.870 | 0.040 |
| `roof-4855fc7e` | Gable | 39 | 1.104 | 0.061 |
| `roof-be421cdc` | Gable | 39 | 0.866 | 0.105 |
| `roof-f447a8a6` | Hip | 84 | 1.176 | 0.104 |
| `roof-4286ad30` | Gable | 55 | 1.629 | 0.085 |
| `roof-4fa203d9` | Hip | 28 | 0.919 | 0.072 |
| `roof-cea1e466` | Gable | 80 | 1.301 | 0.141 |
| `roof-eab27ea2` | Hip | 52 | 1.231 | 0.146 |
| `roof-fd954de8` | Hip | 29 | 1.123 | 0.133 |
| `roof-57dfe898` | Hip | 43 | 1.323 | 0.156 |
| `roof-4c8ea72b` | Gable | 71 | 0.709 | 0.167 |

The evaluated cohort covers 2,232 roof cells, including 558 held-out cells. The median of the eleven per-building median differences is 1.123 m before and 0.105 m after. The color and surface edge registration are approximate. Generic facade openings remain pending verification. The existing facades scale vertically between their footing and the fitted eave. Roof and upper-wall geometry uses the existing building footprint and original stylized material treatment.

## Scene and rebuild checks

The viewer validates the recipe and source art hash and stages the six batch changes together. Source triangles outside the eleven model spans retain their vertex positions, normals, colors and order. This includes the provisional Alder overlay, which was already merged into one affected batch. The revised heights reach the hover and selection models through the existing records. Horizontal collision continues to follow the recorded footprints. An integrity failure keeps the original batches available.

Checked all eleven roofs at three vertical rays per building, six unaffected indexed or non-indexed streams containing 73,715 retained triangles, and eleven pairs of Chromium detail views. No draw calls were added in the matched views. The mesh batch total changed from 75,307 to 75,025 triangles. The local evidence includes an additional paired PBR render.

Edit [the fitted roof parameters](../data/metadata/context-roof-refinements.json) and run `python scripts/build-context-roof-refinements.py <audit.json>` to regenerate [the viewer recipe](../apps/web-preview/public/scene/context-roof-refinements.json). The input points and aerial originals stay in the external evidence archive. No aerial imagery is embedded in the runtime recipe.

The reproducible source screen, source hashes, visual decisions, audit and rendered pairs are under `D:/github/opencampus-interior-research-20261116/exterior-l2/roof-batch-20261123/`. Run `fit-screen.py` and `acquire-review.py` there to repeat the numerical and visual screens. Run `render.mjs` with the development viewer running to reproduce the comparison.


## Expanded review

The second pass screened 112 context records outside the original sixteen fitted candidates. Each had one substantial intersection and a reciprocal footprint match with at least 70% overlap in each direction. The existing outline had to cover at least 70% of its minimum rotated rectangle. Simple gables and hips competed on spatially separated candidate-selection cells. A third set of 2 m blocks was withheld from fitting and model selection, then used to accept or reject the chosen form. Twelve passed the historical elevation screen. Review of individual 2024 orthophoto crops supported one gable and three hips. Eight were deferred for obscured roof ends, uncertain outlines, attached roof tiers, cross-gables or a courtyard. [Oregon 2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer), [NOAA Lane County lidar](https://www.fisheries.noaa.gov/inport/item/57407).

| Scene ID | Form | Verification cells | Previous median error | Revised median error |
| --- | --- | ---: | ---: | ---: |
| `roof-7dcf2f03` | Gable | 43 | 1.625 m | 0.081 m |
| `roof-fb6ac47a` | Hip | 31 | 0.959 m | 0.181 m |
| `roof-f1651047` | Hip | 39 | 0.859 m | 0.189 m |
| `roof-76af1329` | Hip | 26 | 1.331 m | 0.155 m |

Across the four buildings, the median of the per-building errors fell from 1.145 m to 0.168 m on 139 separately held-out historical cells. The local default uses all fifteen corrections in seven existing mesh batches. Browser checks resolve each model's original ID at three roof points, match 82,084 untouched triangles byte for byte against the source art, and verify collision at all fifteen centers. The four new paired views and one PBR pair add no draw calls. The full seven-batch triangle count fell from 84,314 to 83,956. The missing-package fallback preserves the original art and the Ford/Arena gates.

All four corrections reuse the existing footprints. Their appearance and historic heights apply to the main roofs. Precise present-day heights, building identities, smaller roof sections, and facade openings are still open. The four remain L1. One deferred case, `roof-53501ed1`, has a clearly visible open courtyard and stepped perimeter roof in the 2024 image. Its single-hip height fit was rejected and [a separate courtyard reconstruction](compound-context-exteriors-2026-11-23.md) was adopted later.

Rebuild all fifteen with the same repository generator and pinned parameters linked above. Expansion evidence is under `D:/github/opencampus-interior-research-20261116/exterior-l2/roof-batch-expanded-20261123/`. The directory contains the split fit screen, reference requests and hashes, the individual visual decisions, the Chromium side-by-side images and the geometry audit. The runtime package contains geometry parameters and mesh replacement data.
