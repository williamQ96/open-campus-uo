# HEDCO south drop-off and Lot 19 crossings

The south walk from Kendall Plaza reaches the HEDCO drop-off and the parking area north of Clinical Services. Four Lane County orthophotos from 2017, 2021, 2023 and 2025 establish the drive outline, the elongated turnaround island, the two zebra crossings and two striped parking access aisles. The 2014 courtyard study records the south route toward the drop-off and music school. The clinic parking map identifies the patient parking as Lot 19. [Lane County orthophotos](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Courtyard study, printed p. 99](https://scholarsbank.uoregon.edu/server/api/core/bitstreams/a054136d-556e-4939-a611-daed2b31686a/content#page=107) · [Clinic parking map](https://hedcoclinic.uoregon.edu/sites/default/files/2025-12/Parking%20Map%20-%20New%20with%20CSB.pdf).

| Feature | Modeled coverage |
| --- | --- |
| Drive and parking | 1,858.69 m² of asphalt, including the east turnaround, marked parking rows and five direction arrows. |
| Footpaths | 295.29 m² of new concrete along the north frontage, the central access walk and the south sidewalk. Two zebra crossings connect the two sides with modeled curb transitions. |
| Planting | Four curb islands totaling 296.21 m², with 30 representative low shrubs. |
| Navigation | 26 new edges connect the end of Kendall's west walk to the two crossings, the internal parking access walk and the sidewalk north of Clinical Services. |

The concrete and asphalt use the project's filtered terrain with representative curb and ramp rises. Paint thickness, plant species and shadowed parking details are estimates. The south sidewalk route ends on the north side of Clinical Services. The clinic map separately identifies the public clinic entrance on East 18th Avenue. [Editable site record](../data/metadata/clinical-dropoff-landscape.json) · [Exporter](../scripts/build-clinical-dropoff-landscape.py).

The design preserves the published Kendall approach. The new package and its navigation depend on the pinned Kendall package. Free-pin connectors use the modeled sidewalks and marked crossings. The wider drive and parking bays remain outside that pedestrian coverage.

Desktop and phone production previews each matched all 611 local exterior IDs to their scene geometry, loaded 382 resources and registered all 26 waypoints. The Kendall approach reaches the central crossing and the south walk in 65.81 m. The route via the west crossing measures 77.87 m. Four sampled routes stay within 0.13 m of the modeled pedestrian surfaces and cross asphalt only at the marked crossings. The closest island clearance across the samples is 0.921 m. The four island collisions, six ground probes and four browser cases pass. Independent exports preserve the existing Kendall model byte for byte. The drop-off mesh, descriptor and coverage reproduce, and 59 preview responses match the production build. The 610-exterior release includes this landscape package.
