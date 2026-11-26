# Gerlinger Hall and Gerlinger Annex exterior review

The local default preview uses the registered Gerlinger Hall (UO 011, `roof-9ac93ab7`) and Gerlinger Annex (UO 062, `roof-f0b575d6`). The models keep their separate search records and are joined by the concrete breezeway. The earlier source and detail layers remain available through the development baseline and load if the new package fails verification.

## Evidence and placement

- Campus polygons establish the two building footprints and connector alignment. The 2024 orthophoto shows the long Hall roof, two dormer rows, the Annex roof breaks and the separation of the front court from the field. Historical lidar supports the Hall ridge and the Annex roof terraces. The roof traces in the image are slightly displaced relative to the mapped wall outlines. [UO Campus Map](https://map.uoregon.edu/) · [OSIP 2024 RGB imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer)
- The Hall assessment documents the east façade's five-bay rhythm, south arched windows and stairs, north sash and entrances, and west fenestration. The renovation record confirms copper on the four stair-tower roofs. The east model retains the documented entry ramp, pale columned portal, burgundy awnings and balcony rails. The model adds the four copper caps and both dormer rows. [UO Hall assessment, PDF pp. 8–22](https://cpfm.uoregon.edu/sites/default/files/gerlinger_hall_historic_assessment_2016-01-20.pdf) · [UO 2016 exterior renovation](https://news.uoregon.edu/content/finishing-touches-being-applied-gerlinger-hall-exterior)
- The Annex survey confirms the flat-roof brick mass, concrete upper panels, lower glazing, front planting court and concrete connection to the Hall. The front is based on the north elevation identified by the survey. The Annex's concrete joints, raised bed and east-end approach are simplified, and the entrance placement is estimated. [UO Annex survey, PDF pp. 1 and 4](https://cpfm.uoregon.edu/gerlingerannex2025)

The new building footprints cover 2,197.56 m² and 2,234.70 m² respectively. Circulation below the modeled breezeway is clear between its approximate supports. Three local approach points serve the Hall's east and north entrances and the Annex's north frontage. The opening positions, connector underside and support locations, threshold heights, planter geometry, and patterns of louvers and masonry remain approximate. Existing procedural trees obscure parts of the façades in the default scene. The interior door interaction still loads the shared preview.

## Exterior L2 review

The Hall and Annex were reviewed individually against the project's Knight Library example. The Hall's long articulated roof, four towers, and three distinct public façades are visible in the comparison. The Annex's different roof levels, concrete-and-glass frontage and connection to the Hall are visible at site scale. Both exterior records reach L2 in the local inventory. The older overlay history remains documented. [Hall east façade](gerlinger-east-refinement.md) · [Annex correction](gerlinger-annex-correction.md)

| Main roof | Same-cell comparisons | Prior median absolute height difference | Revised median absolute height difference |
| --- | ---: | ---: | ---: |
| Hall | 161 | 2.289 m | 0.424 m |
| Annex | 319 | 2.756 m | 0.067 m |

The figures compare ray hits on both versions with the same 2013–2015 lidar first returns used to inform the reconstruction. The Hall now covers all 220 sampled positions in the central roof rectangle, compared with 161 previously. The model also passed a screen for additional clearance conflicts across all 7,705 route edges. Paired elevations and rooftop views include diagnostic captures with vegetation hidden and context captures with normal vegetation. Browser checks exercised both building identities, west-to-east clearance beneath the breezeway, stair and planter collision, the Hall east entrance round trip, and the pre-existing scene on corrupt package bytes.

Rebuild with `python scripts/build-gerlinger-site-review.py --audit <path-to-audit.json>`. The two-node building asset and paving are original CC BY 4.0 geometry. Source photographs and plans were consulted as references. Source captures, photo comparisons, ray measurements and render checks are retained in the research worktree under `exterior-l2/gerlinger-20261124/`. Work remains local.

[Editable site registration and reference digests](../data/metadata/gerlinger-site-review.json) · [Builder](../scripts/build-gerlinger-site-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/gerlinger-site-review/site.json)
