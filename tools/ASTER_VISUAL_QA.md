# Aster — actual Golden Sun source-art visual review

**Review result: IMPROVED, NOT APPROVED.**
Source renderer: `tools/aster_visual_preview.py`.
Generated visual: [Aster native screenshot-like map image](aster_visual_review.png).
Comparison baseline: [Original Vale rendered from the same sources](aster_vale_reference.png).

These are **offline tile renders**, not emulator captures or a successful ROM
compile. They use the genuine Golden Sun: The Broken Seal palette, 8×8 tiles,
per-layer character blocks, metatile tables and three layer windows.

## Technical errors found and corrected

1. The first Aster preview had violet unpainted ground and disconnected stone
   blocks. The original Vault Map019 snippets were not complete homes.
2. The first review script also failed to correctly render untouched Vale
   because it ignored 0xFFF first-use metatile placeholders and the GBA
   layer-specific tile character bases. We corrected both and verified that
   the original Vale render now resembles a real Golden Sun town.
3. Aster is now linked to Vale Map003's **own** metatiles, shapes, palette and
   tileset; the six cottages use original cropped Vale sections. No Paradox
   artwork was used.
4. Replacing grass with an arbitrary one-layer foliage metatile produced a
   carpet of identical leaf patterns. We corrected the field background
   by copying Vale's actual **three-layer repeat** (metatile 0xba for ground,
   0x15 in both middle and overhead).
5. Source audits check that Aster has no unresolved 0xFFF placeholders, uses
   matching Vale resources, and retains all eight accessible scene event
   triggers and seven NPC placements.

## Present visual quality (2026-11-07 source render)

**Pass:** coherent Golden Sun palette, grass and six recognizable houses.
The repeated home is intentionally a clue to Aster's convergence story.

**Fail — must fix before considering the level attractive or playable:**

- **Overlarge empty clearing.** Most of the 64x64 grid is uninterrupted grass.
  Add native Golden Sun trees, shrubs, fences, rocks, flower patches, small
  outbuildings and paths to give it a village's lived-in density.
- **Hard crop edges on cliffs.** Some houses carry partial Vale cliff pieces,
  which stop abruptly. Either integrate matching cliff edge metatiles
  organically or recrop houses without these background cliffs.
- **Landmarks invisible.** Well at (32,34) and memorial at (32,13) currently
  use grassy placeholder graphics with collision/event behavior; they are
  not yet drawn as a real well or memorial. Their story text alone is not
  adequate visual worldbuilding.
- **Door/actor placement unverified.** Threshold events stand near a home
  area, not rigorously matched to the newly copied door pixels. NPC and
  collision locations remain source-scanned, not emulator-walked.
- **No house interiors.** They remain blocked structures with dialogue
  at nearby event tiles, not real rooms.
- **Roads not visually differentiated.** The map retains intended connected
  road corridors in its source blueprint, but they currently use the same
  visible native grass graphics.
- **No normal two-way entrance.** The scene still lacks a world-map contact;
  its experimental exit returns to Vault. This is not correct release
  navigation.
- **No ROM/emulator verification.** Source render does not verify actual
  engine priorities, scrolling, gameplay events, save stability, menu
  rendering or byte-for-byte build.

## Next build acceptance

1. Add native Vale dirt/stone paths along the existing blueprint streets.
2. Replace cliff fragments with complete terrain transitions.
3. Create and place actual well and memorial scenery using Golden Sun art.
4. Add trees, fences and domestic touches while preserving NPC reachability.
5. Rerun the source renderer, inspect at 1x/native pixel scale and revise.
6. Compile experimental ROM and capture a **real emulator screenshot**.
7. Audit all scripted text with the 27-character limit and playtest interactions
   in the ROM. Do not merge on appearance alone.

## Story constraint

Aster's alternate geography should remain recognizably Golden Sun.
The eventual Ash Jenna-world revelation comes from memory and physical
contradictions, not from importing another game's tileset. The original
*Monster Girl Quest: Paradox* mockup was rejected.
