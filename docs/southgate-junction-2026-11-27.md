# Southgate and East 18th Avenue intersection

Four Lane County orthophotos from 2017, 2021, 2023 and 2025 place the two paired crossings over East 18th Avenue on either side of University Street. Recent images show the two bicycle guide lines, the westbound bicycle symbol and the stop bar in the south mouth. The July 2024 ground view documents the northwest curb return, signal pole and blue University Street nameplate. The model uses original geometry derived from the registered positions. [Lane County orthophotos](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [July 2024 street view](https://www.google.com/maps/@?api=1&map_action=pano&pano=8b0dWBYfCf41sRRjaVvaNw&heading=266.07).

| Feature | Modeled coverage |
| --- | --- |
| Pedestrian crossings | Four white boundary lines, with a continuous pedestrian band between each pair. The west band meets the Rankin sidewalk route. The east band connects the Southgate approach to the southeast corner. |
| Road markings | Two dashed bicycle guide lines, one westbound bicycle approach symbol and arrow, and the stop bar on the south mouth. |
| Paving | Four concrete curb transitions, two south sidewalk returns and the short asphalt return at the mouth of University Street south of East 18th Avenue. |
| Fixture | The northwest signal pole, blue `UNIVERSITY ST` blade and pedestrian signal housing share a registered collision footprint. The mounting dimensions are estimates. |

The new crossing geometry uses the existing Southgate terrain and the earlier Rankin sidewalk. The corner ramps follow the visible concrete limits. Rounded corners, grade and signal hardware are representative where the imagery provides partial coverage. [Editable survey](../data/metadata/southgate-junction.json) · [Southgate pavement exporter](../scripts/build-hayward-square-track.py) · [Rankin routes and fixture exporter](../scripts/build-rankin-frontage.py).

The Rankin graph now has 65 edges. Both production browser profiles match 611 exterior IDs and 388 resources. All seven sampled routes stay within the 0.13 m paving tolerance. Four crossing routes stay between the modeled boundaries and clear the pole envelope by at least 0.617 m. The four ramp probes match the visible pavement height. Sixty-five served files match the build. Both site exports and the walking coverage reproduce byte for byte. The University Street and Hayward midblock control exports also match their installed bytes. The revision was first verified in the research worktree.

The public release preview matches all 610 exterior IDs, 457 entrances and 386 tracked resources on desktop and phone. All 63 sampled files match the build by SHA-256.
