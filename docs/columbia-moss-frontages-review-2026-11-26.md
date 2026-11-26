# Fourteen exteriors around Columbia, Moss and Agate

| Scene ID | City outline | Modeled exterior |
| --- | ---: | --- |
| `roof-99c1fdae` | 170559 | McMenamins East 19th Café at 1485 East 19th. Raised mahogany-toned deck, open rail, street-facing glazing and a plain sign panel. |
| `east18-alley-1472` | 170560 | 1472 East 18th Alley. Independent two-storey building with white siding and a shallow entry projection. |
| `east19-1473` | 170561 | Studio One Café at 1473 East 19th. Low façade, stained timber and an estimated approach from the street. |
| `roof-bf2551ce` | 170478 | Prince Puckler's and Sweet Life Petite. Two recessed storefronts, shared pitched canopy and two estimated approaches. |
| `emerald-apartments-north` | 170565 | North building at 1877 Emerald. Horizontal window bands, shallow roof and repeated west frontage. |
| `roof-825d1e23` | 170566 | South building at 1877 Emerald. Brick wall bands, shallow roof and exterior stairs. |
| `east19-1445` | 170637 | 1445 East 19th. Independent building with south brick face, east gallery and full-length balcony. |
| `roof-2d8c25c4` | 214548 | 1980 Columbia. High south wing, cedar-colored shingles, arched balcony window and two dormers above the recessed double garage. |
| `roof-c0961aa0` | 171173 | 1935 Columbia. West gable, garage and stepped terrain apron. |
| `roof-424f6339` | 170490 | 1895 Columbia. Intersecting main roofs, lower east wing and a shaded street elevation. |
| `roof-f262cbec` | 171166 | 1969 Columbia. Street-side projecting bay and staggered roof on the slope. |
| `columbia-2003` | 170625 | 2003 Columbia. Previously missing standalone building with segmented roof, stepped siding and a garage bay. |
| `roof-c03b3a5d` | 170627 | 2367 Fairmount. Bright side wing, covered south porch and an estimated street approach. |
| `roof-7cc5046c` | 171175 | 1964 Moss. Covered east frontage, driveway and an estimated approach. |

The 1485 and 1473 East 19th roof outlines are 1.238 m apart. The alley building at 1472 and Studio One are 1.946 m apart. The City boundaries of 1472 and 1485 touch with no measured overlap, and the model keeps both shells independently selectable. The two Emerald Apartment roofs are 3.306 m apart. Their gaps to 1445 East 19th are 1.507 and 1.696 m. The Agate retail outline includes 1605, 1607 and 1609, with one roof over three municipal addresses. The two operator pages identify the modeled shops at 1605 and 1609. The middle door's use is unverified. The package uses original geometry and flat finishes. [City footprint service](https://gis.eugene-or.gov/arcgis/rest/services/PWM/COE_Basemap_Tiled_Pro/MapServer/3) · [McMenamins café](https://www.mcmenamins.com/east-19th-cafe/home/) · [Studio One Café](https://studio-one-cafe.com/) · [Prince Puckler's](https://www.princepucklers.com/drinks) · [Sweet Life Petite](https://www.sweetlifedesserts.com/faq) · [Emerald Apartments manager](https://vonkleinrentals.com/all-units/).

Both eastern street-view sightlines toward 1980 Columbia pass through the nearer City roof 170630. The agent's 2021 sold-listing photograph supplies the cedar-shingle elevation, green balcony, twin garage doors and gabled dormers. The south to southeast camera direction and garage setback come from comparison with the 2017, 2021 and 2025 aerials. The model uses estimated grades and screened side elevations. The street views at 1895 and 1969 Columbia and west side of 1964 Moss also leave parts of the façades uncertain. At 2003 Columbia the old `roof-c03b3a5d` intersects only 4.8199 m² of the City roof. The independently modeled 2003 and 2367 roofs are 3.762 m apart. [2021 agent listing](https://patmason.withwre.com/listings/my-sold-listings) · [Lane County aerial service](https://lcmaps.lanecounty.org/arcgis/rest/services/AirPhotos/AirPhotos/MapServer) · [Editable dimensions and evidence](../data/metadata/columbia-moss-frontages-review.json).

| Model | 2013–15 paired median error (m) | DOGAMI paired median error (m) |
| --- | ---: | ---: |
| McMenamins | 0.6982 → 0.1220 | 0.6932 → 0.1203 |
| 1472 East 18th Alley | 1.9382 → 0.2857 | 1.8027 → 0.7746 |
| Studio One | 0.6618 → 0.4658 | 0.4433 → 0.2831 |
| Prince Puckler's and Sweet Life Petite | 0.9052 → 0.3332 | 0.4907 → 0.0697 |
| Emerald North | 3.2502 → 0.0492 | 3.2053 → 0.0420 |
| Emerald South | 0.8402 → 0.0652 | 0.7943 → 0.0817 |
| 1445 East 19th | 0.9898 → 0.0273 | 1.0254 → 0.0390 |
| 1980 Columbia | 0.9902 → 0.8143 | 1.1056 → 0.5383 |
| 1935 Columbia | 0.8397 → 0.6132 | 0.9588 → 0.4120 |
| 1895 Columbia | 0.6488 → 0.5780 | 0.7463 → 0.4543 |
| 1969 Columbia | 0.9381 → 0.3940 | 0.8930 → 0.6905 |
| 2003 Columbia | 0.6798 → 0.4592 | 2.6199 → 2.5941 |
| 2367 Fairmount | 1.5353 → 0.8532 | 1.5013 → 0.4439 |
| 1964 Moss | 0.9596 → 0.6450 | 0.8388 → 0.5228 |

The new models intersect all 8,583 sampled roof cells, including 6,751 paired with source triangles. The 2017 grid contributes 77 cells at 1895 Columbia and lowers its median from 0.4762 m to 0.3964 m on 63 paired cells. Each 2003 Columbia survey provides only three pairs. The medians over all 301 new hits in each survey are 1.0694 m and 0.8569 m. The partial overlap limits how much the paired comparison says about the entire roof.

Twenty matched views and exact vertex attribute and index comparisons preserve 83 peers across two source batches. The adopted scene removes 3,080 source triangles. Two horizontal rays pass through the retail canopy openings to the recessed front. Horizontal and vertical rays in the 1445 East 19th gallery reach the rear wall and upper soffit. The exporter checks 7,710 route edges and a minimum clearance of 0.9478 m. [Exporter](../scripts/build-columbia-moss-frontages-review.py).

Desktop and phone select all fourteen buildings, show two results for Emerald Apartments and find the shared shop model under Sweet Life Petite. Both pass 27 collision probes and four clearance probes at each of the five estimated approaches. The existing building-based directions UI reaches one approach per destination. Routes from Knight Library to Studio One, the shared shop building, 2367 Fairmount and 1964 Moss contain 221, 233, 287 and 281 points. Invalid model bytes and an invalid final source anchor both restore the nine legacy entrances and their collision. The staged, repeated, installed, built and served bytes match. This package is local and uncommitted.
