# Overview startup, controls and building scope

The browser first draws a 191 KB overview with terrain, roads and footprints for 611 exterior IDs. It reuses the same camera and controls for the full scene. Detailed site requests start after the first overview frame and use the current frustum to choose the next queued work. Each started request settles and offscreen work continues until the queue drains. A failed site retains the existing geometry or a solid outline from the overview if the detailed package was its only source. Navigation and walking become available with the full runtime.

## Building directory

Use [building-scope.json](../apps/web-preview/data/building-scope.json) as the single editable scope list. The 38 IDs under `backgroundOnly` keep their exterior meshes and physical collisions. They are skipped by labels, search, picking, cards and entrances. Exclude these IDs when selecting future L2 exterior or interior refinement work. Remove an ID from that object to restore its prior eligibility. Historical modeled assets stay in the inventory for provenance.

The `pending` object records boundary and classification conflicts. The first pass preserves Flock13 and 1365 Villard pending an unambiguous outline. Rainier Building, Alder Building and the University Business Operations Center have explicit UO records and remain selectable. The modeled Womack Hall and Morse Center match Bushnell's directory. The North Building at 677 E 12th Avenue matches the independent University District office listing. [UO facilities inventory](https://cpfm.uoregon.edu/sites/default/files/2026-02/facilities_fact_sheet_2025.pdf) · [UO Business Affairs directory](https://ba.uoregon.edu/staff-directory-and-map) · [Bushnell campus map](https://my.bushnell.edu/m/d/m/c0cc99ee-f9d3-4bdf-8f64-39779bdaa513/CampusMap/Index) · [University District building identification](university-district-clinic-review-2026-11-26.md)

## Ground color and Overview controls

The marked lawn areas use revised foundation vertex colors based on the dated aerials. The archived source uses brightness and vegetation inferred from NAIP RGB, which colored some shadowed vegetation as dark stone. The corrected polygons cover confirmed grass near Collier House, Old Campus Quad and the Memorial Quad east lawn. They leave the parking parcel at the west arrow, the surveyed road layers and live shadows in place. [Source ground method](phase13-environment-comfort.md)

Overview uses the viewport for OrbitControls, which lets right-button drags and wheels reach the camera across floating labels. The primary button still activates a label or rotates the view from the canvas. Right-button release only finishes the gesture.

Regenerate the lightweight scene with `python scripts/build-campus-overview.py`. The build reads the existing scene registry and detailed site bounds. Its output is deterministic.

## Browser verification

Under the same cold-cache Chrome settings (three runs per build, 35 ms latency, 40 Mbps downstream and SwiftShader), median time to the first campus frame fell from 130.50 s to 0.50 s. The first measured response to a right-button drag moved from 133.96 s to 0.58 s. The initial progressive build reached full detail after a median of 116.46 s.

After starting the detail requests, the test panned and rotated the camera away, then let all 152 review jobs settle while returning deliberate 404s for the Old Campus Quad and Education Annex detail meshes. The scene retained all 611 building IDs, including the separately verified solid fallback at Education Annex. It preserved the camera and enabled walking and navigation after the swap. The building audit counted 609 individual meshes and two IDs in shared geometry. The Maverick Hotel roof still blocked walking, and a click on its rendered roof left the card closed.

When the entire detail manifest returns 503, the retry control remains available and the low-detail campus still accepts camera gestures. The Education Annex fallback retains its solid footprint without an inferred entrance or its missing detailed ramp and rail.

The camera regression started at three zoom levels and required both right-button pans, wheel zoom and left-button rotation to move the camera as expected. The second pan started on a visible label. Building-card, search and narrow-screen browser checks also passed.

Matched camera captures show restored color at all three sampled lawns. Four road, paving and parking control crops were pixel-identical. Toggling the Shadows setting changed 54,083 pixels above the same RGB threshold in both builds.

## University District parking follow-up

The screenshot's rightmost arrow lands on existing asphalt west of campus. The adjacent green rectangle was an inferred lawn overlay. Both dated aerials show parking stalls across its footprint and a narrow planted verge along the south edge. [Lane County 2023 aerial](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer/2) · [Lane County 2025 aerial](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer/57)

The correction removes 181 complete overlay triangles within the verified paved interior, using east bounds of −744 to −645 m and north bounds of −109 to −60 m in the scene coordinate system. It requires the matching expanded scene and an available L2 foundation. The parking lot continues to use the existing foundation, terrain heights and walking data.

In a matched 1,107 × 595 Chrome render, the lawn at the center of the rectangle gave way to the L2 foundation mesh. All 7,533 changed pixels were within the lot. Five samples of the existing asphalt, planted verge, road and paving were pixel-identical. Toggling live shadows yielded the same 54,083-pixel mask in both builds.

## Remaining ground-color patches from the annotated screenshot

The three campus arrows mark remaining gray patches around Collier House, Old Campus Quad and the east side of Memorial Quad. With the Shadows setting off, the patches still show on the L2 foundation. The fourth arrow lands on paved parking, which is visible in both aerials. [Lane County 2023 aerial](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer/2) · [Lane County 2025 aerial](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer/57)

Ten lawn and planted-ground polygons extend the existing color correction. The outlines follow the two aerials at the path forks, around the Memorial Quad walks and along the Collier parking edge. Color still interpolates across the existing 5 m foundation grid, so small residual patches and blended edges remain near paths and trees.

At the registered 1,107 × 595 camera pose, 8,950 pixels changed. Eight 7 × 7 control crops over paved surfaces and the parking verge matched exactly. The shadow-toggle masks matched at a threshold of nine RGB levels, covering 52,793 pixels. At eight levels, one boundary pixel crossed the threshold from eight to nine.

## Additional verified lawn edges

The annotated 1,107 × 595 view was checked with browser shadows off. Five more boundaries follow planted ground visible in both aerials. They cover the strip beside the Collier House parking bays, three pieces of Old Campus Quad lawn by the Allen and Friendly walks and Fenton Hall, and the Memorial Quad lawn by the museum frontage. The correction uses the existing 5 m foundation vertex grid. Surface boundaries between grid vertices still blend across their edges. [Lane County 2023 aerial](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer/2) · [Lane County 2025 aerial](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer/57)

The matched production Chrome builds changed 3,955 pixels with shadows enabled and 3,956 with shadows disabled. Eight sampled paved and verge regions matched exactly, including the circled University District parking lot. The shadow toggle produced identical masks at both tested RGB thresholds, with 54,084 pixels above eight levels and 52,793 above nine levels.
