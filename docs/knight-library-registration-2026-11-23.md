# Knight Library exterior registration

The registered Knight Library exterior became the local default on 2026-11-24. Use `/?exterior-review=knight-baseline` in the Vite development viewer for the original exterior. The building retains its stable ID and L2 designation.

The 2024 orthophoto and both footprint datasets place the original north wing east of the corresponding source mesh. The old visible model also omits part of the 1966 massing and places the 1994 south wing too far into the gardens. UO and Lane County footprints overlap with an intersection over union of 95.49%. The revised wall outline follows the campus map, and the current imagery and the campus survey distinguish the original north portion from the 1950, 1966 and 1994 work. [UO historic resource survey, updated 2025](https://cpfm.uoregon.edu/sites/default/files/2025-01/knightlibrary_2025.pdf), [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer), [Oregon building footprints](https://services8.arcgis.com/8PAo5HGmvRMlF2eU/arcgis/rest/services/Building_Footprints/FeatureServer/0).

The model registers 7,208 original north-detail faces and the two previous detail layers to the central façade and entrance pavilions. The library retains the source artwork, including the recessed glazing, three balcony parapets and lanterns. The addition has separately modeled roof levels and 1994 south pavilions, a glazed lower façade, stone bands and a metal-clad upper face with clerestory glazing. The south window rhythm, metal seams, masonry and current access are approximate. [2013–2015 lidar collection](https://www.fisheries.noaa.gov/inport/item/57407), [south and southeast exterior photographs, PDF page 17](https://cpfm.uoregon.edu/sites/default/files/knight_library_prelim_hp_assessment.pdf#page=17), [UO Libraries expansion history](https://library.uoregon.edu/knight-library-history-renovation-and-expansion).

| Check | Before | Candidate |
| --- | ---: | ---: |
| Visible plan coverage of UO footprint | 71.52% | 99.998% |
| Visible model area outside UO footprint, including projections | 3,234.85 m² | 143.04 m² |
| Median roof height difference on 1,471 comparable historical first-return cells | 3.596 m | 0.117 m |
| Pilot trees with geometry intersecting the library | 10 | 3 |
| Tree part to building surface contacts | 17 | 3 |
| Render meshes for Knight Library | 11 | 1 |

The historical roof screen uses samples away from the edge and can include rooftop equipment or vegetation. The revised mesh covers all 2,157 sampled points. Its 90th-percentile absolute height difference on paired cells is 4.130 m. The 7,705 route edges show no new conflicts at the 0.42 m screen threshold. All 1,111 perimeter samples cover the modeled foundation. The first candidate screen found a new contact at the southwest tower. The local default planting now fits that ornamental cherry to UO record 3967 and the aerial, for six tree fits in total. The candidate then has three crown contacts in the east planting, where the nearest mapped campus stems are 17.55–25.58 m from the source trees. The four fits deferred in the previous round clear the candidate in a separate simulation and remain pending. [Previous planting registration](pilot-tree-registration-2026-11-23.md), [public tree inventory](https://fass-ig-web1.uoregon.edu/arcgis/rest/services/DistributedEdit/CampusTrees/FeatureServer).

The development review keeps both north entrances as estimated locations. Their interaction targets use the authored points because an automatic wall-ray snap had placed the west target on the stairs behind the approach. The west gate opens the generic local interior with a canvas click, and the east gate opens it by keyboard. Both restore the development review on return. Stair and landing elevations remain approximate. Corrupt site asset bytes retain the original exterior and entrance. The candidate removes superseded overlays after installation.

Default adoption rechecked the same entrances, return, tree fits and outline alongside Erb Memorial Union. The legacy exterior and nearby planting remain available for comparison, and the two site models fall back independently. [Companion EMU placement check](emu-green-exterior-2026-11-23.md#default-adoption-and-exterior-review-2026-11-24).

## Reproduction

Run `python scripts/build-knight-library-exterior.py --audit <path>` from the project root. The builder pins the source scene, terrain and original facade recipes. [Editable placement and geometry input](../data/metadata/knight-library-exterior.json), [preview descriptor](../apps/web-preview/public/scene/knight-library-review/site.json). The georeferenced imagery, lidar comparison, geometry reports and rendered before/after views are in the local research folder `exterior-l2/knight-registration-20261123`.
