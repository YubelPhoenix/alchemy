# Aster — the town that does not belong

**Story design proposal, not established Golden Sun canon.** Aster exists in the
experimental Ashfall storyline. It is not an original location from The Broken
Seal. **Art direction is locked to original Golden Sun: The Broken Seal.**
Aster should first read as an ordinary Weyard village, not a guest location
from another RPG.

## The eventual explanation (keep this out of arrival dialogue)

Aster was built in **Ash Jenna's version of Weyard**. During convergence,
a piece of that world's occupied geography overlaps Isaac's Weyard. The
buildings come with the inhabitants and their contradictory histories. This
is **not** simply a mirage, and it is not meant to look like it came from
another unrelated RPG.

**Both worlds use Golden Sun's visual language.** Their buildings and
streets look like the villages Isaac already knows: thatched roofs, wooden
walls, grass, dirt paths, wells and modest interiors. Their differences are
historical, not an unrelated architectural culture. A home can be a precise
duplicate of another home, the graveyard remembers the wrong dead, and a
street can end at a house that residents insist has always been somewhere
else. Aster is dislocated in *time*: witnesses disagree on who founded it
or when.

The seam is unstable. One home appears twice. A visitor can remember two
incompatible childhoods. Some residents remember both Jennas; others remember
one. Neither world can smoothly erase the other, and neither group understands
what happened at first. Ash Jenna knows more than the townspeople, but should
not provide immediate exposition.

## What the player learns, and when

1. **Arrival — familiar and inhabited.** Everything looks like a Golden Sun
   village. People discuss ordinary work. The well is dry, the memorial has
   missing names, and the elder insists Aster has always existed. Isaac
   cannot check the town's memory against his own yet.
2. **Fracture — physical contradiction.** The east and west homes are
   architectural duplicates. The sealed home has sounds with no source. A
   resident claims Jenna visited yesterday. A sign changes its wording; the
   text must change *intentionally through dialogue*, not by corrupting ROM
   bytes or making a fake crash.
3. **Revelation — another lived history.** The ambiguous Other Isaac echo and
   an account of Ash Jenna make it possible to infer that the town is a place
   from her world. The memorial is not recording deaths; it is losing track of
   which history counts as a return. Do not claim Other Isaac is canon.
4. **Later Ash Jenna encounter — explanation earned.** An explicit confirmation
   can happen later, after the Suhalla/greater-Ashfall story supplies the
   mechanism of convergence. Until then, Aster remains a disturbing mystery.

## Exterior blocking pass: 64x64 Golden Sun map cells

| Structure | Location | Story purpose | Current gameplay |
| --- | --- | --- | --- |
| Sealed house | northwest (3,3) | An occupied home no one remembers entering | Threshold message only |
| Inn | northeast (43,3) | Empty rooms; contradictory headcount | Threshold message only |
| West home | west (3,24) | Human-scale ordinary domestic life | Threshold message only |
| East home | east (50,24) | Familiarity becomes duplication | Threshold message only |
| Shop | southwest (3,44) | Ordinary trade; later a wrong inventory | Threshold message only |
| Duplicate home | southeast (50,44) | Copies the west home's facade | Threshold message only |
| Memorial | central north (32,13) | Names/history changing | Step-on scripted event |
| Well | central south (32,34) | Dry/full disagreement | Step-on scripted event |
| South gate | (32,63) | Controlled test exit; no legitimate paired world-map entry yet | Temporary Vault-return exit |

Seven NPC slots are positioned on connected walkable paths. Exterior walls and
door cells are intentionally blocked until separate interior maps are built.
The eight doorstep/landmark approaches have distinct scene-local behaviors
0xe1 through 0xe8.

## Visual direction — GOLDEN SUN ART ONLY

Do not reuse the supplied *Monster Girl Quest: Paradox* tiles, including in
future mockups. The previous cross-game concept is **rejected**. Its palette,
roof silhouettes, perspective and scale do not fit Ashfall.

Reference villages: **Vault** for grass, thatched roofs, winding roads and
village scale; **Bilibin** for a crowded central plaza and memorial; **Imil**
for a subdued, isolated mood. These are reference locations, not permission
to mix incompatible tileset palettes. The prototype currently uses the
actual Vault (Map019) metatile table and its matching palette.

The source layout places six familiar houses around grass, narrow native
approach paths, and the well/memorial. Fracture should change things that
are **already native to the game**: duplicate doorways, mismatched window
locations, inaccessible rooms, shifting names, wrong reflections and
repeated people. No garbled ROM text, broken-menu effect, imported building
style or new pixel-art aesthetic is required.

Until the game is built and inspected in an emulator, the facades and
street cells are **provisional native-tile arrangements**, not an approved
pixel-perfect village or a playable level.

## Acceptance gates

- CI source checks for 64x64 layout, 128x128 three-layer storage, native
  Vault source tiles, eight event tiles, and seven actors are necessary but
  insufficient.
- ROM compile, emulator rendering, actual collision, working thresholds, and
  two-way world-map entry remain unproven and must be tested.
- Interiors, sign variation, permanent story stage, and Ash Jenna appearance
  are future work; no description should imply they are already functional.
- Keep the 27-character dialogue line limit and three lines per page.
