# Aster — actual Golden Sun source-art visual review

**Review result: connected native roads, nonmagical garden, original street plan; NOT approved for release.**
Source renderer: `tools/aster_visual_preview.py`.
Generated visual: [Aster native screenshot-like map image](aster_visual_review.png).
Comparison baseline: [Original Vale rendered from the same sources](aster_vale_reference.png).

These are **offline tile renders**, not emulator captures. A previous full
experimental ROM compilation succeeded, but the revised roads have not been
walked or viewed in an emulator. They use the genuine Golden Sun: The Broken Seal palette, 8×8 tiles,
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

## Present visual quality (2026-11-07 updated source render)

**Pass:** coherent Golden Sun palette, grass and six recognizable houses.
The repeated home is intentionally a clue to Aster's convergence story.

**Fail — must fix before considering the level attractive or playable:**

- **Town plan is original, not Vale's.** Six buildings now belong to
  the northern remembrance lane, offset residential quarter and southern
  market with the real inn-sign roof. NPC positions are checked against
  the scene source. The 12 tree groups now use two complete native Vale
  red/blue silhouettes, with ordinary Aster grass underneath instead of
  rectangular copied terrain. The scene still has large empty lawns and
  needs domestic props and more natural variation.
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
- **New restrained native flower plots.** Four two-by-two Golden Sun Vale
  meadow crops now sit beside the occupied western/eastern homes, shop and inn.
  Initial three-by-three imports had obvious blue leftovers and were rejected
  after rendering. The corrected crops are intact and visually subtle; they
  cannot by themselves solve Aster's empty-lawn problem. The northern sealed
  and duplicate homes deliberately remain unplanted. The source-level audit
  checks each original three-layer crop and all existing entrance triggers.
- **No house interiors.** They remain blocked structures with dialogue
  at nearby event tiles, not real rooms.
- **Connected, three-cell native dirt lanes are now in the map.** Every
  doorway spur joins a visible east-west lane. Roads use Vale's authentic
  left shoulder, solid-soil center and right shoulder. Repeating broken
  dirt junctions and three five-by-five source crops with stray blue pixels
  were removed. The new preview has cleaner crossings and wider paths,
  although the roads still look too long and straight for a lived-in town.
  Engine collision, tile priority and NPC movement remain untested.
- **No normal two-way entrance.** The scene still lacks a world-map contact;
  its experimental exit returns to Vault. This is not correct release
  navigation.
- **Emulator verification is still missing.** A full experimental ROM
  compiled before this visual pass; neither that build nor the revised
  streets have a verified emulator screenshot, collision test, save test
  or event-playthrough result.

## 2026-11-07 additional woodland review — NOT incorporated

- [Sparse native-tree test](aster_perimeter_sparse.png) (six outer clusters)
  and [dense test](aster_perimeter_dense.png) (those clusters plus two
  northern backyards) were rendered from the actual Vale Map003 set_02
  metatiles and original palette. These tests preceded the new
  native canopy crop pass. **Both original expansion tests were rejected.**
  Copied 4x5 source backgrounds form conspicuous rectangular green/dark
  cards at the perimeter; more repetitions make that defect worse.
- [First foliage crop atlas](aster_foliage_candidate_atlas.png) separates
  native ground from upper-layer graphics. Several seemingly useful
  treetops actually include cliff or house fragments. A second
  [refinement atlas](aster_foliage_refinement_atlas.png) tests narrower
  original source crops. Do not place an unreviewed crop just because it
  uses original Golden Sun data.
- Neither woodland test changed the playable Map180, its paired ruined
  grid, collision flags, actors, memorial or entry thresholds. Continue
  toward intact silhouettes and organic-looking village outskirts
  rather than a tiled perimeter of copied trees.

## 2026-11-07 varied native woodland pass — in experimental map

- [Ten-tree preview](aster_woodland_sparse.png) and
  [fourteen-tree preview](aster_woodland_full.png) replaced the old
  card-like foliage stamps with separately isolated Golden Sun Vale blue
  and autumn-red *upper-layer* trees, preserving native bright grass
  behind their silhouettes. These source-only trials showed a clear
  improvement; the accepted map uses **twelve staggered tree groups**.
- Implemented in `tools/aster_layout.py` and Map180 with six restored
  house-adjacent tree sites plus six new outer trees. The source audit
  locks down their coordinates, exact native upper layers, solid tree
  movement behavior, all eight story triggers and all seven NPC positions.
  The separately generated ruined source has the same twelve placements.
- A detached blue/cliff fragment at (3,4) inside source crop Vale
  (4,13) was replaced by Vale's native transparent metatile 0x15
  for all six autumn-red trees. This does not redraw or invent pixels.
- **Visual verdict: improved, still not ready for release.** The foliage
  no longer appears as pasted rectangular blocks, but 64x64 Aster still
  needs an actually visible dry well, sensible small-town domestic
  details, successful movement/collision checks, interior scenes,
  reciprocal overworld travel and convincing ruin artwork.
- Historical perimeter and first-variation experiments are archived as
  references, not rerun as build steps.

## Next build acceptance

1. The wider native paths now have coherent intersections. Break up long,
   unnaturally straight runs, then test walking, tile priorities and
   threshold access in an emulator.
2. Remove leftover tiny stray scenery pixels and add coherent vegetation
   and domestic details without hiding doors or NPCs.
3. Build a true *dry* well using compatible Golden Sun tiles. Add a wooden
   name register to the approved nonmagical remembrance garden. **Do not
   reintroduce a Psynergy Stone, crystal shrine, or Vale's old layout.**
4. Improve native yard props, short fences and nonrepetitive vegetation while preserving NPC reachability; the accepted twelve-tree crop pass is only the first landscaping improvement.
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
