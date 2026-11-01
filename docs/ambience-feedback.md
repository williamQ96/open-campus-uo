# Campus ambience and feedback — iteration 11

**English** | [简体中文](zh-CN/ambience-feedback.md)

This batch extends the existing three views, split-screen walking controls, search, minimap and fixed-origin directions. Publication status is recorded in [the development log](../DEVELOPMENT_LOG.md).

## Density and collision

Settings → **Campus activity density** replaces the former two switches with one keyboard/touch-accessible four-position slider. Each fresh load starts at **Mid**. No leaves the hero playable and removes every ambient actor, parked prop and associated collision volume.

| Level | Walkers | Bicycles | Scooters | Road cars | Squirrels | Parked props |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No | 0 | 0 | 0 | 0 | 0 | 0 |
| Low | 2 | 0 | 0 | 1 | 2 | 2 |
| Mid | 8 | 2 | 2 | 4 | 8 | 5 |
| High | 20 | 5 | 5 | 10 | 20 | 14 |

These are population targets. Invalid routes, obstructed placements or the player occupying a proposed position can reduce actual counts. New actors avoid existing bodies and the player. Cars use side offsets on clear road portions; walking/riding and squirrel paths are authored estimates. Squirrels pause periodically. These are illustrative activity patterns, not wildlife observations or live traffic. [`configs/campus-life.json`](../configs/campus-life.json) owns local parking and squirrel paths; `prepare-explorer-life.py` preserves them during regeneration.

Upright horizontal capsules with vertical height intervals approximate each actor and vehicle. The player uses substeps and wall sliding; NPCs yield to the player, props and other NPCs. No pushing, rigid-body dynamics, riding on vehicles, collision-aware indoor access or traffic signals are simulated. Congestion can pause an actor. Verify route clearances after geometry changes.

## Sound and walking motion

The sound button beside Directions controls **music and footsteps together**. Sound defaults on. The browser may require a first click, touch or key press before playback; the button tooltip explains that state. A quiet local CC0 MP3 loops, with no third-party media service at runtime. Muting pauses playback and footsteps. Hidden tabs pause audio.

Footsteps follow **actual horizontal ground distance**, not key presses: they stop when idle, blocked, airborne, in Overview or when a dialog is open. Follow and First person both use them. First person adds at most about 1.8 cm vertical sway and 0.14° roll, without changing player coordinates, collision or navigation. Settings can disable sway; the operating system's reduced-motion preference also suppresses it. Follow does not bob its camera.

The [asset archive and credits](../data/asset-sources/campus-life/README.md) include CC0 music, the CC0 squirrel source, adapted Blender/GLB and an original synthesized footstep. About also credits these assets. Code and generic behavior flow upstream; these downloaded assets, colors and paths stay here.

## Feedback to this project

The feedback icon opens a form with optional title, required description and optional coordinates. Coordinates are blank until explicitly typed or **Use current position** is pressed. A blank title becomes `Feedback #<UTC timestamp> · iteration 11`; this is a draft identifier, not a predicted GitHub issue number.

**Continue on GitHub** opens a prefilled issue in `williamQ96/open-campus-uo`. The reporter signs in and confirms creation on GitHub. The campus page cannot claim success or know the created issue number. Draft fields remain available while the page is open, and a link works if a popup is blocked. No account token or anonymous-write backend is embedded. Very long drafts offer a copy-and-paste fallback rather than truncating feedback. Draft text and coordinates are not sent to analytics; after continuing, GitHub receives the information included in the draft URL. Feedback is public if confirmed in this public repository.

Project corrections and iteration history remain downstream. Reusable methods and validation patterns go into the upstream methodology log. The recommended development loop is early playable whitebox → source-guided moderate-fidelity modeling with documented inference → community feedback or developer-led refinement → another playable iteration. See the [upstream method](https://github.com/williamQ96/open-geospatial-to-3d-reconstruction-pipeline/blob/main/docs/iterative-community-modeling.md).
