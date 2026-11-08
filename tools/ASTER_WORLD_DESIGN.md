# Aster — the town that does not belong

**Story design proposal, not established Golden Sun canon.** Aster exists in the
experimental Ashfall storyline. It is not an original location from The Broken
Seal; the unusual construction is a deliberate story clue, not a mistake.

## The eventual explanation (keep this out of arrival dialogue)

Aster was built in **Ash Jenna's reality**. During convergence, a piece of
that world's occupied geography overlaps Weyard. The buildings come with the
inhabitants and their contradictory histories. This is **not** simply a mirage,
a town built by Weyard's people, or everyone having the same hallucination.

The architecture is different because it really was built by people in a
different world, using different materials and traditions. Buildings are
recognizable as homes, but their roof shapes, woodwork, room layouts and
street patterns match nowhere Isaac has visited. The settlement is also
dislocated in *time*: witnesses disagree on who founded it or when.

The seam is unstable. One home appears twice. A visitor can remember two
incompatible childhoods. Some residents remember both Jennas; others remember
one. Neither world can smoothly erase the other, and neither group understands
what happened at first. Ash Jenna knows more than the townspeople, but should
not provide immediate exposition.

## What the player learns, and when

1. **Arrival — unfamiliar but inhabited.** The building style is odd but not
   treated as proof of anything. People discuss ordinary work. The well is dry,
   the memorial has missing names, and the elder insists Aster has always
   existed. Isaac cannot check the world's memory against his own yet.
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

## Visual direction, and important asset boundary

The supplied `Monster Girl Quest: Paradox` archive is an excellent *private
visual reference* for Aster's different architecture. Especially useful are
`Outside_A2/A3/A4/B/C` and `Inside_A2/A4/B/C`, plus decayed variants.

**Do not copy these commercial assets into the public GitHub repository or a
public ROM release without permission or another legitimate redistribution
right.** The current experimental game grid copies **original Golden Sun
Vault facades** as temporary geometry. A separate private review image can
show the prospective Paradox visual treatment, but it is not in the ROM.
The production town should use permission-cleared or original matching art,
converted into the engine's 4bpp palettes and 16x16 metatile system.

## Acceptance gates

- CI source checks for 64x64 layout, 128x128 three-layer storage, eight event
  tiles, and seven actors are necessary but insufficient.
- ROM compile, emulator rendering, actual collision, working thresholds, and
  two-way world-map entry remain unproven and must be tested.
- Interiors, sign variation, permanent story stage, and Ash Jenna appearance
  are future work; no description should imply they are already functional.
- Keep the 27-character dialogue line limit and three lines per page.
