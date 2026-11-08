# Aster — actual Golden Sun source-art visual review

**Review result: connected native roads, nonmagical garden, original street plan; NOT approved for release.**
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

- **Town plan is original, not Vale's.** Six buildings now belong to
  the northern remembrance lane, offset residential quarter and southern
  market with the real inn-sign roof. NPC positions are checked against
  the scene source. The clearing still needs denser, varied scenery.
  The first different-tree test generated cropped trunks and rectangular
  blue patches; it was **rejected without touching Map180**. The six
  existing complete native tree stamps remain repetitive placeholders.
- **Cliff remnants removed.** The new house rendering copies native roofs
  and walls only, keeping Vale grass beneath. This eliminates the previously
  clipped cliffs; the doors still need an actual in-game facing test.
- **Psynergy Stone explicitly removed.** The user rejected Vale's crystal
  landmark; it no longer exists in Aster's game map. The northern memorial
  is now a **low wood-fence remembrance garden with wildflowers**, source
  `tools/aster_memorial_garden.png`, and a protected event at (32,14).
  It is nonmagical, but a future legible wooden name plaque is still needed
  so the changing inscriptions are visually motivated. The **dry well at
  (32,34) remains visually absent**: the water-filled Vale spring was
  correctly rejected because it contradicts the opening dialogue.
- **Door routes structurally corrected.** Each of six house approaches is now
  one walkable cell south of its roof crop with a continuous spur to the
  primary roads. The source audit checks these geometric relationships.
  Actual character positioning and engine collision remain unverified.
- **No house interiors.** They remain blocked structures with dialogue
  at nearby event tiles, not real rooms.
- **Connected dirt lanes now present.** All six door approaches connect
  into the original Aster street pattern through native Golden Sun dirt tiles.
  The generator uses Vale's matching grass-to-earth shoulder family,
  including an irregular variant; this is real Map180 source, not just a
  Photoshop overlay. The road edges remain visually repetitive and sharp
  around intersections, so further texture improvement is needed before
  final visual approval. Gameplay collision and metatile priorities have
  not yet been checked in an emulator.
- **No normal two-way entrance.** The scene still lacks a world-map contact;
  its experimental exit returns to Vault. This is not correct release
  navigation.
- **No ROM/emulator verification.** Source render does not verify actual
  engine priorities, scrolling, gameplay events, save stability, menu
  rendering or byte-for-byte build.

## Next build acceptance

1. Refine the newly connected native dirt lanes: soften the repeated
   scalloped edge, correct crossings, and test character movement and visual
   priorities in the emulator.
2. Replace cliff fragments with complete terrain transitions.
3. Build a true *dry* well using compatible Golden Sun tiles. Add a wooden
   name register to the approved nonmagical remembrance garden. **Do not
   reintroduce a Psynergy Stone, crystal shrine, or Vale's old layout.**
4. Replace repeated tree clusters with varied, complete native Vale vegetation, fences and domestic touches while preserving NPC reachability.
5. Rerun the source renderer, inspect at 1x/native pixel scale and revise.
6. Compile experimental ROM and capture a **real emulator screenshot**.
7. Audit all scripted text with the 27-character limit and playtest interactions
   in the ROM. Do not merge on appearance alone.

## Story constraint

Aster's alternate geography should remain recognizably Golden Sun.
The eventual Ash Jenna-world revelation comes from memory and physical
contradictions, not from importing another game's tileset. The original
*Monster Girl Quest: Paradox* mockup was rejected.

## Ruined state design requirement (NOT built)

Aster's ruined version must use the *same* 64x64 streets and six structural
addresses. Keep the well (32,34), memorial (32,13) and south gate (32,63) in
place; the player must be able to identify the same settlement. Treat the
southern gate and minimum west-to-east path as accessible even in ruin. Proposed
physical changes are a collapsed sealed house, abandoned inn, blocked northern
street, and duplicate home partly overgrown—**none is implemented yet**.
Do not create a separate ruined PNG by applying a color filter; use changed
Golden Sun metatiles only, with coherent debris/collision and authored event
logic once the normal state is visually approved.

## First ruined-Aster render: visual study ONLY

Preview: [Aster overgrowth study](aster_ruin_visual_study.png).
The experiment layers six existing Vale tree clusters onto the **same six**
building addresses. The memorial, invisible well, gate, eight event locations
and original planned roads stay at their exact positions. It has no separate
ROM map, collision map or stage trigger.

**Result: rejected as finished ruined-state art.** Large square vegetation
stamps clearly cover rooftops; no masonry has fallen, no structures have
collapsed, and there is no coherent debris. It is useful only to establish
that the broken version must preserve Aster's legibility and silhouette.
Further ruin art must be constructed intentionally using native or
permission-cleared Golden Sun-style assets, with updated walkable routes and
story-specific doorway behavior. Its test overlays are now calculated from
the current building coordinates, not the obsolete symmetrical layout. Do not merge this study into normal Aster.


## Paired ruined map source — not playable yet

Generator: tools/aster_ruin_variant.py
Map data: tools/aster_ruined_map.txt
Golden Sun tile preview: tools/aster_ruined_variant.png
Source parity audit: tools/check_aster_ruin.py

A second 64x64 source state now preserves the same six buildings, south gate,
seven NPC slots, dry-well location, ordinary non-Psynergy memorial, and all
eight scene triggers. Fourteen roof cells in four structures are deliberately
altered, together with two damaged garden-fence cells. The house footprints
remain impassable, and the generated grid passes a difference-by-difference
source audit.

**Structural test: PASS. Art verdict: NOT APPROVED.** In the preview, holes
look like beige flat roof patches, not believable destroyed or burned thatch.
No second registered scene, state switch or playable ruined map exists.
This study establishes matching world geometry rather than completed horror
scenery; it is not an emulator screenshot.

The native-only dry-well candidates (tools/aster_dry_well_*.png) were inspected
and rejected: the candidate stone ring displays invalid cliff/void graphics,
while cropped chimney masonry looks like part of a house rather than a well.
The playable normal town still has an invisible dry-well placeholder.
Do not substitute a water-filled fountain, a Psynergy Stone or foreign tiles.

One earlier comparison used Map009 as if it shared Vale's set_02 palette.
**Correction:** Map009 actually uses Golden Sun set_08. Its art cannot be
copied into Aster's set_02 metatile table without a deliberate palette and
tile-index conversion. The offline comparison renderer is now corrected to
reference its own set_08 assets, avoiding false evidence of compatibility.

Next gates: a recognizable dry stone well with correct collision; authentic
ruined-roof silhouettes and debris rather than rectangular patches; coherent
landscaping; proper paired world-map entry; ROM compile, emulator inspection
and event testing. Do not merge on source checks alone.
