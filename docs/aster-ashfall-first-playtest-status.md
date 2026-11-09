# Ashfall + Aster — first playable test integration

**Branch:** `experiment/ashfall-aster-first-playtest`

**Source base:** Ashfall `dark-story-rewrite` commit
`62dd7b5331a7e23a12df0090e9e823a3aed8f425`.
This is a source-only experimental branch. It has **not** been compiled,
run in an emulator, playtested, or merged to `dark-story-rewrite` or `main`.

## Integrated source

- The native 64x64 Aster map (Map180) and original Vale tile/palette/
  animation references, including its 18-cell west-bridge test.
- Aster scene 201 with seven NPCs, four indexed scenery sprites, a standard
  Golden Sun signpost beside the south lane, eight staged map interactions,
  and 36 authored dialogue contexts. The Sanctum and houses still have
  exterior thresholds but **no working interior maps**.
- Indexed `SPR_505`–`SPR_509` PNG assets, their metadata, sprite
  registrations, and scene/map/resource/object table entries.
- Aster's source `en.po` is exactly the inherited vanilla Ashfall
  catalogue plus 36 Aster message rows; do not compile the inherited
  `dark_story_rewrite.py` directly against it.
- Claude's newer combat code is left untouched. The read-only checker
  pins the current `boss_ai.c` Git blob to
  `c1c6b07bf3c04c0fa01390e24a3d41f034df3b6b`.

## Experimental TWO-WAY world connection (not approved terrain)

- World icon: `SPRITE_WORLD_MAP_ASTER` at X=5696, Z=1504.
- Reused previously unused signpost slot 39, actual actor ID 47.
  **No other world-map actor IDs are shifted.**
- Actor proximity/contact triggers experimental exit kind 115, routing
  to Aster's default south entrance.
- Aster's southern exit returns to reserved WorldMap entrance 98,
  X=5696, Z=1536, facing south.
- The icon, approach terrain, world position, camera and return ground
  are **not verified walkable**. If the position is obstructed, move the
  icon/entrance together after checking in an emulator. Do not merge this
  contact to stable Ashfall yet.

## No-cost read-only checks

In an existing checkout of this exact branch (no hosted Actions):

```bash
python3 -B tools/check_aster_ashfall_integration.py
python3 -B tools/prepare_aster_ashfall_dialogue.py --check
```

The checker verifies map/sprite/dialogue registration, that the
experimental reciprocal route still uses its reserved slots, and that
the pinned tactical boss AI has not been overwritten. It invokes the
native map, bridge, foliage, sprite and scene source QA helpers.
It now also invokes the independent read-only overworld contract test,
which compares the full world actor table with the approved Ashfall base,
confirms exactly one replacement at unused slot 39, checks static icon
clearance (Vault is about 168 world pixels away), and validates the paired
world/Aster entrance and exit. **This is not a terrain walkability test.**

**New source-isolation gate (November 8):**
`tools/check_aster_branch_isolation.py` is included in the read-only
preflight. It requires a clean checkout of this exact branch with
Ashfall baseline commit `62dd7b5331a7e23a12df0090e9e823a3aed8f425`
available in the local Git history. It checks the exact set of Aster-only
added files and the size/status of approved changes to eleven inherited
Ashfall files. A new file outside the approved list, or extra edits to
world-map/story/sprite/resource registrations, stops the gate before any
compile. To expand the scope later, first review the new baseline diff and
explicitly update the audit list; never bypass it to force a build.
The isolated branch's reviewed file inventory permits Aster-only additions
and 11 deliberate registration/catalogue changes, but no battle or
workflow modifications. Validate the current inventory before every build.

Passing does **not** prove successful compilation or game behavior.

## Required order for ANY later experimental build

In a disposable checkout **only**:

1. Run the above read-only source gate.
2. Set `ASTER_DISPOSABLE_BUILD=1` and run
   `python3 -B tools/prepare_aster_ashfall_dialogue.py --apply`.
   This moves the old alchemy-null marker behind Aster messages,
   applies the current dark-story rewrite, checks message ordering,
   and applies Aster's approved line-polish. **Do not overwrite
   `en.po` with a file from another branch**.
3. Generate Ashfall's artwork with the CURRENT Ashfall source,
   using the current pinned compiler and existing asset scripts.
4. Compile a modified English ROM and a clean canonical upstream
   baseline; create an IPS using the complete ROM-to-ROM diff.
   Never stack this test IPS on an existing Ashfall-patched ROM.
5. Discard experimental saves after testing; existing `.sav` files
   store absolute ROM pointers that may have moved.

A build must never start merely because this branch receives a source
commit. No GitHub Actions, paid runner, Codespaces or new artifact
uploads are authorized by this document. Check GitHub billing and
artifact safety gate **before any future manually authorized IPS build**.

## Aster exterior dialogue pass (source-only, November 8)

- Corrected **five automatic threshold interactions** (inn, west house,
  east house, shop, duplicate house): they now show a line **once per
  stage**, not every time Isaac walks over a door tile. An event runs on
  the first crossing but not on later crossings of the same threshold.
- Ten distinct scene-local flags track the arrival/fracture readings;
  the duplicate house also has a separate revelation-stage flag.
  This leaves room for the town's changed dialogue when the player
  uncovers another history. `Scene_Arrive` clears these flags on
  ordinary re-entry; no permanent flags, items, Djinn or save layouts
  were changed.
- The existing `check_aster_v14.py` source preflight now checks that
  all five threshold functions use the one-shot helper and that the
  eleven new flags remain in separate scene-temp slots 0x20E..0x218.
  This is source contract checking, not actual input/controller QA.
- **November 8 follow-up:** the three gate-sign messages now have an
  optional TALK interaction on a native Golden Sun signpost at (30,60),
  just west of the south lane. It is appended AFTER the original seven
  NPCs and four scenery actors: no existing talk/mind-read IDs shift.
  The final revelation farewell is now an optional second conversation
  with the original greeter. This does **not** become an automatic
  departure cutscene: the south exit trigger and its original map cell
  are unchanged.
- Source-only reachability was rechecked with the sign treated as an
  occupied tile. The (32,61) player entry, (32,62) south exit marker,
  all eight original story marker tiles, and an adjacent sign talk
  approach remain accessible in the native map graph. The checker
  enforces these points and the stage-message references. Sprite
  appearance, actual talk/exit input and runtime collision still
  require a local emulator playtest.
- **Story persistence is provisional:** the town's fracture/revelation
  flags also use scene-temporary storage, so the encounter resets upon
  a normal re-entry. We are deliberately **not** assigning permanent
  Ashfall save flags before save compatibility and story progression
  are tested. This is not a final-release narrative state system.

## Emulator acceptance gates

- World: enter Aster from Vault-side terrain, exit to its own icon,
  move away and re-enter. Confirm no impassable ground or auto-loop.
- Town: verify native tiles, woodland/river/bridge/waterfall, sprite
  priorities, seven NPC talks and mind reads, eight marker events,
  signpost TALK in all three stages, the greeter's optional farewell,
  south exit, and story fracture in different discovery orders.
- Save/menu: use disposable new saves; verify party, Djinn, items,
  camera, saves/reloads, and town/world transitions remain intact.
- Story: early Flint/Vault/Hammet progression, mid-game transitions,
  late-game Ash Jenna, Kegare, Heart, Sarah and their tactical AI.
- Interiors/settlement: no house or Sanctum interiors yet; this is a
  blocking final-release issue, not a reason to hide first-test status.

**Status:** integrated source and route prototype only; NOT playable
until a full IPS compile and emulator verification are completed.
