# Ashfall + Aster — first playable test integration

**Branch:** `experiment/ashfall-aster-first-playtest`

**Source base:** Ashfall `dark-story-rewrite` commit
`62dd7b5331a7e23a12df0090e9e823a3aed8f425`.
This is a source-only experimental branch. It has **not** been compiled,
run in an emulator, playtested, or merged to `dark-story-rewrite` or `main`.

## Integrated source

- The native 64x64 Aster map (Map180) and original Vale tile/palette/
  animation references, including its 18-cell west-bridge test.
- Aster scene 201 with seven NPCs, four scenery sprites, eight staged
  interactions, and 36 authored dialogue contexts. The Sanctum and houses
  have exterior thresholds but **no working interior maps**.
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
The latest remote comparison confirms 44 changed paths: 33 Aster additions
and 11 deliberate registration/catalogue changes. None are battle or
workflow paths. No hosted Actions run was started by these audit commits.

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

## Emulator acceptance gates

- World: enter Aster from Vault-side terrain, exit to its own icon,
  move away and re-enter. Confirm no impassable ground or auto-loop.
- Town: verify native tiles, woodland/river/bridge/waterfall, sprite
  priorities, seven NPC talks and mind reads, eight marker events,
  south exit, and story fracture in different discovery orders.
- Save/menu: use disposable new saves; verify party, Djinn, items,
  camera, saves/reloads, and town/world transitions remain intact.
- Story: early Flint/Vault/Hammet progression, mid-game transitions,
  late-game Ash Jenna, Kegare, Heart, Sarah and their tactical AI.
- Interiors/settlement: no house or Sanctum interiors yet; this is a
  blocking final-release issue, not a reason to hide first-test status.

**Status:** integrated source and route prototype only; NOT playable
until a full IPS compile and emulator verification are completed.
