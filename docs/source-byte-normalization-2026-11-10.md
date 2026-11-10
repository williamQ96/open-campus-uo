# Source byte normalization, 2026-11-10

The Windows checkout used `core.autocrlf=true`. This transformed canonical Git LF runtime/generator source into CRLF working bytes without changing the JavaScript logic. Earlier exact-byte export regressions correctly rejected those changed working bytes. The project now explicitly preserves LF for these source types in `.gitattributes`; source-pinned JSON, GLBs and evidence retain their own exact-byte rules. No Git global configuration was changed.

The new Knight, Gerlinger and Tykeson export receipts generated before normalization truthfully record the CRLF generator/exporter bytes present at generation time. Those immutable receipts and GLBs were not rewritten. The table below gives the mechanically equivalent LF source hashes now used by Git and future checkouts. This is a byte-format mapping, not a claim that arbitrary code changes are equivalent. Existing geometric/material roundtrip assertions remain exact. A later re-export may embed different source-byte metadata and therefore have a different binary digest even where geometry is identical.

| Source | Prior CRLF SHA-256 | Canonical LF SHA-256 |
| --- | --- | --- |
| `src/exterior-detail.js` | `671133697d3a2f293de95944307b7e40e4c7ccd9889be2266f2017f51034e58c` | `c0181be4a2256830571390bfb8497335d368e9d4e3aed9b9da625b5044fa1e40` |
| `src/fern-geometry.js` | `8fdfe298ef46917a6734bb538ba09c300ee03689b724f901321c7d0445564aab` | `b98702f061a8b6a9214a223d6e9f1d0db146135b544336fc89113079219a11b8` |
| `scripts/export-exterior-detail.mjs` | `ef4c37949636e311def958d0699dbe94d00cd4cb6ca42da8295df3b2cc88d0b0` | `9ab1d371f74afdf25ef7806ac8fb48c901dcab10a3a3eba708ae5b45e46863d5` |
| `scripts/export-tykeson-exterior.mjs` | `cec125d5f017564b92108238dd5a10ff70273d39fa130abce6cbe27b6679ffd8` | `ce61859467a8939cf6118ed018f6ba9e57cf74a9accef32961a0b6b3c85318d6` |
| `src/bike-rack-geometry.js` | `7dc0a51af992b6ea6d3304fc78369c83d9a18ed80d53fbd4d7b9827c827656d6` | `6f5e3863ca122e1fc365734611a2aae7a4567e547e098921130621216ce3fe88` |
| `src/sky.js` | `d8e6302d18b56c0cd59cdae6b451a40573d5cad838031b4041a7d52beb281890` | `a839539864ce132cc4931b34bfcc27fa516038ce4f096a2494a6fe11825de003` |
| `src/npc-templates.js` | `7b31f66734ee0309e07c870ff295c308743abf5e97e1aa6fb17552b2e348145b` | `85fc7fe0db2cc78a940ea2444e7b00e5130cd725a402bb4b01a4df135480dda5` |

The bike-rack and original cloud/fern GLBs embed the canonical LF hashes, matching Git HEAD. Their previous failure was a local checkout provenance mismatch, not a reason to modify historical assets or weaken the hash assertions. Frozen checks run after normalization distinguish those baseline issues from actual runtime regressions.

Three historical exporters (`export-collier-exterior.mjs`, `export-fenton-exterior.mjs`, `export-susan-exterior.mjs`) were already committed with literal CRLF bytes. They are explicitly `-text` exceptions and were restored byte-for-byte from the unchanged Git objects, rather than normalized or relabeled.
