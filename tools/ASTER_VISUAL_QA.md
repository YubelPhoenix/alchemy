# Aster — actual Golden Sun source-art visual review

**Review result: nonmagical remembrance garden, original street layout; visual design NOT APPROVED.**
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

- **Town plan is original, not Vale's.** Six buildings now belong to three
  purposeful districts: northern remembrance lane, offset residential
  quarter, and southern market with the actual inn-sign roof. The innkeeper
  moved to (46,55), and the NPC source audit verifies all seven positions.
  The 64x64 clearing still needs much denser, varied scenery. Six native
  tree stamps look too repetitive and natural roads are not yet completed.
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
- **Roads mostly remain invisible.** Six doorway approaches, three east-west
  links and the central north-south route remain walkable in the blueprint.
  Three small, genuine Vale dirt patches now indicate frequent crossing
  points without creating the earlier chimney-graphics artifacts. The three
  patches repeat too obviously and do not yet visually join the roads; they
  need a cohesive, purpose-built native Golden Sun dirt path treatment.
- **No normal two-way entrance.** The scene still lacks a world-map contact;
  its experimental exit returns to Vault. This is not correct release
  navigation.
- **No ROM/emulator verification.** Source render does not verify actual
  engine priorities, scrolling, gameplay events, save stability, menu
  rendering or byte-for-byte build.

## Next build acceptance

1. Develop coherent, edge-matched native Vale dirt/stone paths along the
   planned connections; scattered identical dirt patches are not sufficient.
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
