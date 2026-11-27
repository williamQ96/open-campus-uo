# Bardell, Buckingham and Walnut Path exterior review

The local scene rebuilds 18 residential exteriors near the northeastern boundary. It also replaces the old building mesh over Canoe Canal with the Walnut Path footbridge, its ramps, and a trail connection. All 18 residences keep their scene IDs. The old bridge building ID `roof-d1a66ce1` remains in the inventory as a historical mapping for ENV-05.

## Residential reconstruction

The working crosswalk uses 19 City footprints, County parcel ties, Lane County aerials from 2017, 2021 and 2025, 38 street bearings from 30 panoramas, and the 2013–15 and DOGAMI surface grids. The 2017 surface partly covers 3320 Bardell, so the other two surface grids constrain its roof. The specification records the individual hips, gables, porch positions and garage openings, and keeps geometry and materials editable. Obscured façades, door sizes and some roof transitions are estimates. Street and aerial imagery served as reference. The GLB contains original geometry and material colors. [Residential specification](../data/metadata/bardell-buckingham-review.json) · [Reproducible exporter](../scripts/build-bardell-buckingham-review.py).

- **3370 Bardell** joins City outlines 149972 and 149973 across the 2.69 m gap visible beneath a continuous connection in the aerials. The rebuilt roof covers the join, with an open rear yard. A ray in that yard misses the model.
- **3335 Buckingham** has three separate garage leaves, a recessed entrance, and separate low garage and main roof levels. The paired roof probes hit at 3.505 and 4.706 m relative to the scene origin.
- **592 Merewether** keeps the roof beyond east 1000 m and extends the visible ground under it. A ray at east 1001.657 m hits the roof. The estimated east-facing frontage exceeds the walkable boundary. The other seven modeled entrances have walkable approaches.

The two surface grids provide 10,522 eligible rays across 36 building and grid combinations. Every ray hit the rebuilt geometry. The audit pairs 7,362 with pre-rebuild hits. Twenty-six median absolute residuals decrease and ten increase. The table reports the increases so they can be followed up on site.

| Residence | Surface | Previous (m) | Rebuilt (m) |
| --- | --- | ---: | ---: |
| 3320 Bardell | 2013–15 | 1.2496 | 1.6370 |
| 3325 Bardell | 2013–15 | 1.1000 | 1.3778 |
| 3325 Bardell | DOGAMI | 1.1644 | 1.1653 |
| 3348 Bardell | 2013–15 | 0.9450 | 1.1629 |
| 3348 Bardell | DOGAMI | 0.9144 | 1.0463 |
| 3334 Buckingham | 2013–15 | 1.0476 | 1.2198 |
| 3342 Buckingham | DOGAMI | 1.1270 | 1.3945 |
| 3354 Buckingham | 2013–15 | 0.2301 | 0.5557 |
| 3365 Buckingham | DOGAMI | 0.7341 | 1.1924 |
| 592 Merewether | 2013–15 | 1.1133 | 1.1303 |

Twenty-two matched views cover the 18 houses and four roof, garage or terrain details. The index audit keeps all seven neighboring source ranges intact while replacing 4,891 source triangles. Checks against 7,710 original route edges found at least 11.2878 m of clearance from the new occupied footprints.

## Walnut Path crossing

The older mesh falls over the bridge in all three Lane County aerial years. The City bike route lines 762 and 985 correspond to the crossing and the south trail. The new route uses the existing path node at east 801.782 m, north 559.924 m. The routed trail extends from that connection across the deck to the north end of the modeled approach. [City bike route data](https://services3.arcgis.com/F7NiRLGNbA2hh7gE/arcgis/rest/services/EugBikeways/FeatureServer/0) · [City park map](https://www.eugene-or.gov/DocumentCenter/View/4748/Alton-Baker-Park-Map?bidId=).

The deck is approximately 36.48 m long and 7.42 m wide. Its -0.625 m top follows median lidar heights of -0.609 m, -0.642 m and -0.621 m over 218 samples each. Tapered 12 m ramps tie to the existing terrain. The canal surface and bottom retain the existing terrain elevations. The rail placement and ramp profiles are modeled estimates. The navigation addition is 242.718 m long with 48 new edges. Sixteen collision sections follow the rails. [Bridge specification](../data/metadata/walnut-path-bridge-review.json) · [Reproducible exporter](../scripts/build-walnut-path-bridge-review.py).

## Local viewer

Both repeat builds matched the staged bytes and the packaged descriptors and meshes. The bridge supplies a walkable surface to the viewer, with twelve sampled ramp or deck points above the underlying terrain and an additional clear approach point on the terrain. Each of the sixteen rail-section centres blocks movement and the deck centreline remains clear. At one deck probe the sampled terrain is -5.514 m and the standing height is -0.625 m. The residential and bridge packages have independent validation and fallback.

Desktop and phone browser runs verify 18 named selections and 28 clear gate probes per device. A damaged residential mesh restores the 18 legacy buildings and keeps the bridge. A damaged bridge mesh or displaced pinned route anchor restores the obsolete crossing and its legacy entrance. The active router reaches the north landing in both directions in 33 points over 235.57 m, and all 48 new edges clear the current scene. With the bridge review disabled, the original router has no connection to the north landing.

The inventory has 548 L2 building exteriors, 54 active L1 building exteriors, 38 historical mappings, and 15 L2 outdoor groups. The local viewer has 602 selectable buildings, 55 remaining source batch members, two context roof treatments and 470 entrance records. This checkpoint is local. The publicly deployed release remains at `c3dc42c`.
