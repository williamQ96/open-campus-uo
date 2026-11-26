# Canterbury Court and Millrace 3 exterior review

The November 23 local default installed two compound exteriors alongside fifteen earlier roof corrections. Both originally retained their scene IDs and L1 ratings. View the [current local preview](http://127.0.0.1:5197/) or [the source roof geometry in development mode](http://127.0.0.1:5191/?exterior-review=roof-baseline).

## Canterbury Court

The courtyard building at 750 East 14th Avenue corresponds to `roof-53501ed1`. The residential listing associates the address with the name, and the property operator identifies the courtyard property as Canterbury. The state footprint feature 1949484 has an interior ring, and the 2024 orthophoto shows the same opening and opposing roof projections into it. The previous mesh and collision covered the full 287.57 m² court. The revised roof uses two north–south wings and stepped cross sections. A narrow path and lawn follow the visible ground pattern. The wall finish and exact paving boundaries are approximate. The courtyard is modeled as enclosed at ground level while its actual entrances and any covered passages await evidence. [Property operator](https://caprieugene.com/virtual-tours/), [address listing](https://www.apartments.com/canterbury-eugene-or/m9nrd1h/), [Oregon footprint inventory](https://www.oregon.gov/dogami/pubs/pages/dds/p-sbfo-1.1.aspx), [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

## Millrace 3

UO identifies building 097 at 1301 Franklin Boulevard. The registered block, campus-map position, and repeated studio dormers in UO's photograph identify the former `roof-8826f960` as Millrace 3. The reconstructed 664.59 m² footprint follows the rectilinear roof and wall registration, using the 2024 image and state feature 1840949. The two roof slopes, a 10.94 m local ridge, five dormers per slope, skylights and vertical siding distinguish the new model. The photographed courtyard-facing glazing groups are approximated. The north and end wall opening schedules, current roof finish after later work and exact entrances remain open. The UO photo from the building's history and the 2024 image inform visible parts of the mesh. [UO building inventory](https://cpfm.uoregon.edu/sites/default/files/uo_building_inventory_published.pdf), [UO historical exterior photograph and description](https://artdesign.uoregon.edu/1980s-millrace-and-northsite-complex-active-hub), [2024 orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

## Verification

| Exterior | Shared interior roof cells | Previous median absolute height difference | Revised median absolute height difference |
| --- | ---: | ---: | ---: |
| Canterbury Court | 886 | 0.749 m | 0.192 m |
| Millrace 3 | 419 | 1.369 m | 0.102 m |

The comparison uses 1 m first-return cells inside both the former and revised roof outlines, away from edges. This is an agreement check against the same historical lidar used to establish the profiles. The reported heights use the scene's local coordinate frame. [NOAA 2013–2015 lidar metadata](https://www.fisheries.noaa.gov/inport/item/57407).

The browser compared the two building records and their estimated entrance approaches, sampled the open Canterbury court and neighboring walls, and checked both forms by picking roof triangles under their original IDs. Newly occupied areas add no intersections with the 7,705 centerline edges at 0.42 m clearance. The source and replacement retain 86,032 identical triangles in the eight affected batches. Matched views showed no new draw calls. A corrupt package falls back to the prior meshes, names and collision. Exact door thresholds, access outside the viewer and contemporary roof elevations remain unverified.

The editable [compound parameters](../data/metadata/compound-context-roofs.json) and [generator](../scripts/compound_context_roofs.py) feed the existing pinned runtime roof package. Run `python scripts/build-context-roof-refinements.py <audit.json>` to regenerate it. Registered references, photo and aerial hashes, mesh audits and browser images are under `D:/github/opencampus-interior-research-20261116/exterior-l2/compound-roofs-20261123/`. No source photographs or maps are embedded in the runtime.

## Millrace 3 exterior review, 2026-11-24

The five south studio windows now extend below the roof eave in the proportions shown by the school's historic photograph. The south wall gains horizontal base cladding and the timber entrance frame and short paved apron. The aerial shows a small light feature at the frame's approximate location. The reference supports the feature's form and rough placement. Its current fabric and the window, frame and threshold dimensions remain approximate. The contemporary north wall and roof fittings still need direct observation. [UO Millrace III photo](https://artdesign.uoregon.edu/1980s-millrace-and-northsite-complex-active-hub) and [2024 Oregon orthophoto](https://imagery.oregonexplorer.info/arcgis/rest/services/OSIP_2024/OSIP_2024_SL/ImageServer).

The registered massing, repeated dormers and documented studio elevation support L2 in the comparison with Knight Library. The footprint and estimated approach remain as established in the prior package. The two modeled posts are visual details. Their footprint is at least 57.41 m from the nearest of 7,705 route edges. All other 30 roof patch records are byte-equivalent after serialization, including Canterbury Court. Production desktop and mobile select Millrace 3 under its original ID. Invalid roof package bytes restore its prior geometry while Cascade and Johnson still load. Comparison files are in `D:/github/opencampus-interior-research-20261116/exterior-l2/johnson-millrace-20261124/`.
