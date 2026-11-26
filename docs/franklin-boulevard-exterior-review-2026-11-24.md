# Franklin Boulevard exterior review

Reviewed on 2026-11-24 for Open Campus: UO. Six commercial exteriors now appear in the local default scene under their original IDs and Eugene addresses.

| Address | Scene ID | Exterior reviewed |
| --- | --- | --- |
| 1675 Franklin Blvd | `roof-5e02b3d2` | Low asymmetric ridge, dark storefront and covered entrance landing. The façade follows the operator photo uploaded in November 2025. |
| 1809 Franklin Blvd | `roof-fd64edbd` | Lower west roof, green sloped fascia, yellow striped covers and south storefront glazing. |
| 1895 Franklin Blvd | `roof-1587e3e1` | Flat roof with a raised side projection, equipment, brown parapet, glazed frontage and drive-through window. The finishes represent the 2024 Starbucks frontage. |
| 1917 Franklin Blvd | `roof-b1290409` | Elevated photovoltaic array, pale main roof and a south service frontage with glazed garage bays. |
| 1933 Franklin Blvd | `roof-0dc3fa8a` | Broad hips around a recessed roof well, rooftop equipment and an open south gallery with yellow piers. |
| 2091 Franklin Blvd | `roof-4b8868e0` | Shop, covered forecourt and two registered canopy columns. Both lanes beside the columns stay open for movement. |

The municipal points fall inside both the source scene and Oregon state outlines. The 2024 orthophoto registers the roof outlines, equipment, openings to parking and adjacent masses. Roof heights come from the 2013–15 and 2017 surfaces. The editable registration holds the feature IDs, georeferenced export URLs, roof sections, approach positions, finish colors and dated facade references. [Registration](../data/metadata/franklin-boulevard-exterior-review.json) · [Eugene address points](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/ArcGIS/rest/services/EugAddress/FeatureServer/0) · [Oregon statewide footprints](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx) · [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer) · [2017 elevation review](campus-surface-2017-2026-11-24.md).

The 1675 operator photo has an unknown capture date. The west strip at 1809 has consistent low returns, and the forecourt panorama shows the green fascia and yellow covers. The 1895 broker listing and street view supply the storefront and parapet. The 1917 and 1933 street views resolve the tilted PV row and hipped roof. The north roof at 2091 covers the enclosed shop, with the connected south arm supported by columns. The export uses original geometry and flat material colors. Door widths, obscured openings, support dimensions and entry thresholds are approximate. [1675 façade](https://darkmattercanna.com/wp-content/uploads/2025/11/DM_EUG_front-of-building-300x200.jpg) · [1809 façade](https://www.google.com/maps/@?api=1&map_action=pano&pano=CIHM0ogKEICAgIDCipzDXA&heading=0) · [1895 broker listing](https://www.showcase.com/1895-franklin-blvd-eugene-or-97403/33056440/) · [1917 façade](https://www.google.com/maps/@?api=1&map_action=pano&pano=dlW6HvPsegarXu9J68e3AQ&heading=0) · [1933 façade](https://www.google.com/maps/@?api=1&map_action=pano&pano=m4fyFmsrN2C0suXilNHodA&heading=0) · [2091 canopy](https://www.google.com/maps/@?api=1&map_action=pano&pano=VC78f4XLAXx5sNCDLjI54w&heading=0).

The shared 1920–1960 roof and Womack Hall at 850 Franklin were reviewed separately in the [following batch](franklin-complex-exterior-review-2026-11-24.md). The separate review covers the shared structure's shop entrances and roof steps, and Womack Hall's roof wings and façade after the residence-hall conversion. [Market of Choice](https://marketofchoice.com/locations-franklin/) · [Womack Hall](https://bushnell.edu/student-life/residence-life/).

## Verification

| Building | Shared roof cells | 2013–15 median absolute error, source → L2 | 2017 median absolute error, source → L2 |
| --- | ---: | ---: | ---: |
| 1675 | 290 | 0.860 → 0.695 m | 0.779 → 0.195 m |
| 1809 | 133 | 0.617 → 0.473 m | 1.063 → 0.378 m |
| 1895 | 240 | 0.992 → 0.146 m | 0.862 → 0.030 m |
| 1917 | 113 | 1.046 → 0.131 m | 1.088 → 0.103 m |
| 1933 | 492 | 0.919 → 0.692 m | 0.803 → 0.145 m |
| 2091 | 287 | 0.787 → 0.082 m | 0.813 → 0.050 m |

Both published elevation periods cover all 1,700 audit cells. Of those, 1,555 are shared by the source and replacement. The 2017 median error in newly covered cells of 1809's west strip is 0.838 m. At 1917, the 2017 90th-percentile error across the shared cells is 1.001 m, including returns where the historic grid and individual modeled PV modules differ.

- Twelve paired street and roof views cover the six sites. The isolated overlay removes 1,422 triangles from four batches and preserves the source vertex attributes and indices of all 72 remaining members in those batches.
- The static check covers 7,710 route edges. The nearest existing route is 1.996 m from the new collision outlines.
- Desktop and mobile production checks verified the six addresses, walkable entries, published thresholds and both fuel-canopy passages. The original model ranges returned when an anchor shifted, the terrain hash differed or a correctly hashed GLB could not be parsed. All 29 selected Playwright tests passed, and the three Franklin cases also passed in a focused rerun.
- The default preview has 519 selectable buildings, with 368 source-batch members and 13 separate context roof treatments. The outdoor ledger has 153 L2 buildings, 366 independent L1 buildings, 13 L1 outdoor asset groups and 21 historical mappings. [Outdoor ledger](asset-refinement-inventory.md).

[Builder](../scripts/build-franklin-boulevard-exterior-review.py) · [Runtime descriptor](../apps/web-preview/public/scene/franklin-boulevard-exterior-review/site.json).

```powershell
python scripts/build-franklin-boulevard-exterior-review.py --audit D:/path/to/franklin-boulevard-audit.json
```

With `--stage <directory>` the builder exports an isolated copy. The stage and adopted files match byte for byte. The research worktree stores the render pairs and roof metrics under `exterior-l2/east-campus-20261124/franklin-boulevard-stage/`. Changes remain local pending publication.
