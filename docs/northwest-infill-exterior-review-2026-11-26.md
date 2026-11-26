# Four western campus and riverfront exteriors at L2

The default scene uses four individual exterior models under their original scene IDs. Municipal addresses and building outlines establish their location and extent. The 2024 orthophoto and three historical surface datasets inform the roof geometry. [City building footprints](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [Oregon 2024 imagery](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Editable register](../data/metadata/northwest-infill-exterior-review.json)

| Building | Scene ID | Rebuilt exterior |
| --- | --- | --- |
| Phi Kappa Psi Chapter House, 729 E 11th Ave | `roof-8007cb2f` | L-shaped stepped hip, three dormers and the south triple arcade with an estimated approach. [Chapter association front view, page 4](https://static1.squarespace.com/static/631fbb77b73893428e0a0a1f/t/66fd946eb1af6e276184d1e2/1727894642560/Duck%2BTales%2B-%2BFall%2B2021.pdf) |
| 642 East 8th Avenue | `roof-3961d925` | Long shallow gable, blue-gray lower metal siding, darker lap siding and the recessed timber corner entrance. [City case Z 24-2](https://www.eugene-or.gov/AgendaCenter/ViewFile/Agenda/_06262024-1256) · [2025 renovation listing](https://www.loopnet.com/Listing/642-E-8th-Ave-Eugene-OR/34657758/) |
| 1414 Alder Street, also indexed as 790 E 14th Ave | `roof-d830368a` | Alder-side parking recess, steel exterior stair and gallery. The north facade retains the observed canopy form. The restaurant operator announced its campus location closure in June 2026. [Campus location reference](https://traveloregon.com/things-to-do/eat-drink/restaurants/pegasus-smokehouse-pizza-university/) · [Operator update](https://www.pegasuspizza.net/) |
| Eugene Steam Plant, 701 Annie Mims Ln | `roof-ec27d788` | Two main roof levels, tall steel-grid windows, concrete piers, a projecting window bay and several blocked lower openings. The model represents the existing pre-redevelopment plant. [City project history](https://www.eugene-or.gov/3875/Downtown-Riverfront-Steam-Plant) · [Existing elevation sheets](https://www.eugene-or.gov/DocumentCenter/View/39806) |

Roof and facade details retain estimated dimensions. The south chapter-house approach is the only modeled entrance in this package. The steam plant extends across the west boundary of the 2 km terrain square. Its full modeled envelope follows the city outline.

## Verification

- All 8,625 roof checks against three historical surfaces intercepted the rebuilt roofs. On 7,710 shared samples, the four buildings each had a lower median absolute height error on every surface. Twelve comparisons improved. Historical surface cells can include vegetation and edge returns.
- Seven camera pairs were reviewed. The model removes 1,430 selected triangles from three context batches. Index sequences and attribute hashes for the 92 peer records in those batches were preserved in the isolated comparison. Screened the replacement walls, supports and approach against 7,710 route edges. Minimum clearance was 6.160 m.
- Desktop and phone production each loaded the staged mesh and descriptor by byte match, kept all 524 selectable buildings and verified four solid and four clear collision probes. The route from 968 Alder terminates at the chapter-house approach after 68 points. Failure to verify the site asset restores the earlier four members.
- This package is local and uncommitted. Use `python scripts/build-northwest-infill-exterior-review.py --stage PATH --audit PATH` for a separate export and `/?exterior-review=northwest-infill-exterior-baseline` in development for the preceding context view.
