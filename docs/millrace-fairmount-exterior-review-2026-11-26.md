# Millrace and Fairmount exterior review

Four buildings retain their existing scene IDs and use original L2 exteriors. City footprints 170790, 170824, 170504 and 150060 register the geometry, while the 2024 Oregon orthophoto and dated street views establish the visible roof and facade arrangements. Openings on screened elevations and trim dimensions remain approximate. [City footprint layer](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [Editable model register](../data/metadata/millrace-fairmount-exterior-review.json).

- **Alpha Tau Omega Chapter House, 1000 Alder St.** The chapter directory and the dated view identify the building. Two shallow roof forms recover the tall brick house and low south wing. The east side has a pale panel, raised lettering and a recessed entry with a sidelight. The measured roof grid records different heights at the two wings. [Chapter directory](https://uoifc.squarespace.com/alpha-tau-omega) · [June 2024 east view](https://www.google.com/maps/@?api=1&map_action=pano&pano=7-1SeDYtv7ICmgfk3nfkXw&heading=264.24).
- **1956 E 15th Avenue.** Municipal address points and the 2024 north view identify the main house. The rear house at 1515 Orchard Alley has a separate building polygon. The rebuilt street house has intersecting gables, a north porch projection, a chimney and blue west window frames. [2015 listing](https://www.redfin.com/OR/Eugene/1956-E-15th-Ave-97403/home/26197095) · [July 2024 north view](https://www.google.com/maps/@?api=1&map_action=pano&pano=_USKaGROeIu1Mk-YlFM6qw&heading=180.78).
- **1871 E 19th Avenue.** The revised bungalow has a high rear roof over two levels, a lower street volume, a west cross gable and green shingle siding. The west view establishes the change in height and trim. The lower entrance remains a modeled approximation. [2021 listing](https://www.homes.com/property/1871-e-19th-ave-eugene-or/qf0mn72e5w6pp/) · [August 2022 street view](https://www.google.com/maps/@?api=1&map_action=pano&pano=jJ6C5teLi8tEP3meLItOlA&heading=2.64).
- **Walnut Alley Garage Building.** Three west gables, overhead doors with glazed upper panels and separate apron slabs match the alley view and roof profiles. The geographic label and empty entrance list reflect the available evidence. [July 2019 alley view](https://www.google.com/maps/@?api=1&map_action=pano&pano=L3Dhfhi8gHhnOW0FihgKJg&heading=107.71).

## Verification

Every one of the 3,705 sampled historical roof cells intersects an adopted roof. Shared-cell medians compare the previous and revised geometry over the same cells. The bungalow's DOGAMI median increases, while its two NOAA medians fall. The historical grids include vegetation near the roof edges. [NOAA elevation archive](https://noaa-nos-coastal-lidar-pds.s3.amazonaws.com/laz/index.html) · [DOGAMI elevation mosaic](https://gis.dogami.oregon.gov/arcgis/rest/services/lidar/DIGITAL_SURFACE_MODEL_MOSAIC/ImageServer).

| Grid | Chapter house | 1956 E 15th | 1871 E 19th | Walnut Alley |
| --- | ---: | ---: | ---: | ---: |
| NOAA 2013–2015 | 1.162 → 0.091 m | 0.696 → 0.358 m | 1.212 → 0.855 m | 1.019 → 0.619 m |
| NOAA 2017 | 1.153 → 0.074 m | 0.691 → 0.181 m | 0.533 → 0.220 m | 1.026 → 0.144 m |
| DOGAMI Lane County | 1.173 → 0.075 m | 0.702 → 0.325 m | 0.419 → 0.523 m | 0.872 → 0.395 m |

Seven paired renders cover the principal facades and roof forms. Removing 1,106 source triangles preserves the remaining indices, vertex attributes and 112 peer IDs across three batches. The regional audit checks 7,709 route edges after the modeled solid bay removes one TIGER-derived terminal edge. Its final node lies inside the observed south wing. The remaining route closest to this package clears it by 1.0118 m.

Desktop and phone production previews verify 522 selectable buildings, 305 source batch members, four searches, 11 collision probes and three walkable estimated approaches. Routing from 968 Alder uses 33 points and ends at the chapter's modeled east approach. The garage remains searchable with an empty entrance list. One damaged source anchor restores the full preceding set and its entry state.

To reproduce, run `python scripts/build-millrace-fairmount-exterior-review.py --stage OUTPUT --audit AUDIT.json` from the repository root. The GLB, descriptor and browser build are local and uncommitted. [Builder](../scripts/build-millrace-fairmount-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/millrace-fairmount-exterior-review/site.json).
