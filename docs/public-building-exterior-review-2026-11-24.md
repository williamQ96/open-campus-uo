# Clinical Services, natural history museum, Outdoor Program Barn and Agate Hall exterior review

The local default scene uses registered exteriors for four existing IDs. Campus wall outlines and Oregon's 2024 orthophoto locate the envelopes. Roof forms use the 2013–15 Oregon Lidar Consortium or the 2017 USACE first-return grid, depending on coverage.

| Campus asset | Scene ID | Rebuilt exterior |
| --- | --- | --- |
| B0029 Clinical Services Building | `roof-c1ff8b83` | Western membrane roof, raised center and sloping east wings. Concrete, brick-colored bands and exposed rafter ends. |
| B0049 Museum of Natural and Cultural History | `roof-e11ec58d` | Pitched timber fronts, low membrane roof fields, center roof band and a west entry porch with open sides. |
| B0052 Outdoor Program Barn | `roof-a997a75f` | Rotated wall outline, rising roof band, standing-seam slopes, east bay and an array modeled over the aerial footprint. |
| B0147 Agate Hall | `roof-b068940e` | Long hipped roof, six auditorium skylights, lower south annex and west stucco entrance with arches and green awnings. |

Clinical Services follows the university's 2006 survey for the asymmetrical roof profile, rough concrete and visible rafter ends. The museum uses the existing-site drawing on PDF page 14 and the museum's courtyard photo. Timber forms are original modeled geometry. The Barn's dated rental photo documents an open equipment bay, and the campus solar inventory confirms the rooftop installation. Its panel count, roof details and gate positions remain estimates. Agate Hall follows the campus survey site outline and the 2016 photograph of the west entrance. The neighboring Agate House is outside the Agate Hall model. [Clinical survey, PDF page 4](https://cpfm.uoregon.edu/sites/default/files/clinicalservice05_30_07.pdf#page=4) · [Museum existing-site diagram](https://cpfm.uoregon.edu/sites/default/files/mnch3reassessreport5-18-12rev1_2.pdf#page=14) · [Museum entry photo](https://natural-history.uoregon.edu/) · [Barn solar inventory](https://cpfm.uoregon.edu/solar-projects) · [Barn rental photo](https://news.uoregon.edu/content/thanks-op-rent-kayaks-and-bikes-and-snowboards-free) · [Agate Hall survey](https://cpfm.uoregon.edu/agatehall2025) · [Agate entrance photo](https://news.uoregon.edu/content/american-english-institute-makes-move-renovated-agate-hall).

The project compared the roof and frontage views against the Knight Library exterior example. Exact window spacing, entry thresholds, landscaping, rooftop equipment and unseen sides still need field verification. The dated source photos guided the modeled geometry and remain external references. The new geometry contains no source textures, signs or artwork.

## Model and runtime checks

| Asset | Roof source | Samples hit | Median absolute vertical residual |
| --- | --- | ---: | ---: |
| Clinical Services | 2013–15 | 1,779 | 0.524 m |
| Natural history museum | 2017 | 1,716 | 0.230 m |
| Outdoor Program Barn | 2013–15 | 324 | 0.130 m |
| Agate Hall | 2017 | 2,114 | 0.244 m |

These residuals use the historical surfaces that informed the model. The ray check takes valid returns at least 0.84 m inside each registered wall outline. It hits all 5,933 samples, plus the six modeled Agate skylight centers. Reviewed 22 clear and landscape-context views across 11 cameras. Checked 7,710 route edges, six walkable modeled approaches and ten collision points, including clear passage below the museum porch and solid collision at its posts.

The Agate range `[300, 1262)` removes 962 source triangles from `context-campus-2-0`. The three source anchors match, and the kept indices and all original position, normal and color arrays compare exactly. Successful adoption supersedes the Barn, museum and Agate facade overlays for these four IDs. The existing Clinical roof patch and museum wall tint continue to describe fallback source geometry. Damaged model bytes, a mismatched terrain pin and a bad Agate source anchor each restore the previous four records, approaches and collision results. The production scene retains 517 selectable buildings, with 438 from source batches, and 139 road segments.

The [editable specification](../data/metadata/public-building-exterior-review.json) and [builder](../scripts/build-public-building-exterior-review.py) reproduce the installed package. The research directory holds the registration sources, roof sections, local browser checks and exports. Local development and verification only.
