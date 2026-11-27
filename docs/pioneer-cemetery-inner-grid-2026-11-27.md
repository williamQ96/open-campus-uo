# Pioneer Cemetery screened interior grave plots

The registration covers three areas within the cemetery. The first is the northern interior east of the existing grass trace, the second is between Walton and Cherry avenues east of Kelley Drive, and the third is north of Dorris Avenue. The 2023 and 2025 county images show the clearest plot outlines in different areas. The 2017 and 2021 images provide alternate sun angles and visibility under the trees. The National Register plat provides the historic grid. New geometry follows visible features and open segments on the contemporary imagery. [National Register nomination and plat](https://npgallery.nps.gov/GetAsset/8377666e-d980-4494-bce2-3993f6f19669#page=36) · [Lane County orthophotos](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Association tour map](https://eugenepioneercemetery.org/self-guided-tour/).

| Feature | Local model |
| --- | --- |
| Plot boundaries | Fifteen open traces with a combined length of 233.25 m. The standard 0.21 m curb section and weathered color are approximate. |
| Grave markers | Forty anonymous stone forms with estimated heights of 0.25–0.98 m. Nine taller forms register collision. The archival grid supports orientation and context. |
| Grass traces | Three exposed strips totaling 60.94 m and 76.87 m². Two extend the northern grass alignment on either side of an obscured section. A third follows an open section between Walton and Cherry. |
| Planting | Two low shrubs use footprints apparent on the dated imagery. Species and heights are representative. |

The candidate screen removes duplicates, points within surviving curbs and features without sufficient visibility. The west end of one Walton–Cherry curb stops before a retained tree stem. The exporter checks the new details against the terrain, plot bounds and registered trunks. The grass traces retain open ends where crowns obscure the alignment. The named gravel roads carry the cemetery routes. Buried curb continuity, species, exact profiles and individual memorial identification need ground evidence. [Editable measurements](../data/metadata/pioneer-cemetery-inner-grid.json) · [Exporter](../scripts/build-pioneer-cemetery-inner-grid.py).

The detail package attaches to the pinned cemetery scene. It installs the three meshes and nine collision envelopes together. The cemetery exporter still reproduces the existing base asset and descriptor byte for byte.

Desktop and phone production previews each verified all 611 local exterior IDs, 384 resources, three clear grass-strip probes and nine marker collisions. Seven control routes reproduce the preceding scene's route geometry and stay at least 18.656 m from the new collidable markers. The closest new curb, strip or marker footprint is 0.266 m from a modeled tree base. The build, 199 unit tests, six browser checks, two repeat exports, 61 served-file hashes and 507 archive records pass. The 610-exterior release includes this landscape detail.
