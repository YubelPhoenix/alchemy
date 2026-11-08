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

## Aster's own geography (experimental 64x64 cells)

The town must **not** be a carbon copy of Vale. Vale supplies compatible
Golden Sun pixel-art materials, but the *settlement plan is original*:
a quiet northern remembrance lane, two offset residential streets, and
a small commercial quarter by the south gate. Aster's roads have short,
unequal branches rather than Vale's original winding house placements.

| Structure | Aster top-left cell | Function and physical relationship |
| --- | --- | --- |
| Sealed house | (7,4) | Northwest of the remembrance lane; no interior yet |
| Duplicate house | (48,5) | Far northeast; eerily repeats the western home's facade |
| Western home | (8,26) | A home facing the western residential lane |
| Eastern home | (49,27) | Offset from its western counterpart, not mirror-symmetrical |
| Shop | (6,45) | Southwest of the busy south entrance |
| Inn | (42,44) | Southeast market quarter, using the original Golden Sun inn-sign roof |
| Remembrance garden | around (32,13) | Plain wood-and-flower memorial; accessible dialogue at (32,14) |
| Dry well, incomplete art | (32,34) | Gathering place and convergence clue; interaction at (32,35) |
| South gate | (32,63) | Experimental exit only; no reciprocal world map arrival yet |

The normal map includes six recognizable buildings and their individual
connected front-door approaches. Eight scene behaviors `0xe1–0xe8` remain
wired. Seven NPC positions are verified against the scene source.
The south market, remembrance lane and residents' quarters should have
different practical purposes and different scenery densities.

**Visual prohibition:** No Psynergy Stone, altar, glowing crystal, or other
Vale mystical landmark belongs in Aster's memorial. The player specifically
rejected it. An **ordinary fenced remembrance garden** has replaced the
crystal: wildflowers, weathered wood and blank or missing names. Its event
messages, rather than magical effects, establish the dread.

## Visual direction — GOLDEN SUN ART ONLY

Do not reuse the supplied *Monster Girl Quest: Paradox* tiles, including in
future mockups. The previous cross-game concept is **rejected**. Its palette,
roof silhouettes, perspective and scale do not fit Ashfall.

Reference villages: **Vale** for thatched homes and bright grass, **Bilibin**
for a crowded central plaza and memorial, and **Imil** for an isolated mood.
The experimental map uses Vale's **actual** Map003 metatiles, shapes, palette
and three 16KB tile character blocks. Mixed-palette village tile imports
are prohibited; future decoration must come from the same compatible set.

The source layout places familiar Golden Sun house art in **new Aster streets and
neighborhoods**, with a nonmagical remembrance garden, plain grass and
a planned dry well. Matching Golden Sun art is necessary, but rearranging
Vale's village unchanged is specifically forbidden. Fracture should change things that
are **already native to the game**: duplicate doorways, mismatched window
locations, inaccessible rooms, shifting names, wrong reflections and
repeated people. No garbled ROM text, broken-menu effect, imported building
style or new pixel-art aesthetic is required.

Until the game is built and inspected in an emulator, the facades and
street cells are **provisional native-tile arrangements**, not an approved
pixel-perfect village or a playable level.

## Acceptance gates

- CI source checks for 64x64 layout, 128x128 three-layer storage, native
  Vale source tiles, eight event tiles, and seven actors are necessary but
  insufficient.
- ROM compile, emulator rendering, actual collision, working thresholds, and
  two-way world-map entry remain unproven and must be tested.
- Interiors, sign variation, permanent story stage, and Ash Jenna appearance
  are future work; no description should imply they are already functional.
- Keep the 27-character dialogue line limit and three lines per page.
