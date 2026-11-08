# Aster V14 → Ashfall selective integration plan

**Audit date:** 2026-11-08. **Status:** source compatibility review only; no
merge, ROM build, emulator test, or workflow run is authorized by this file.

## Branch boundaries

- Aster source: `experiment/aster-v14-native-map-staging`.
- Current story/boss build: `dark-story-rewrite`.
- `main` is NOT the destination for a blind Aster merge.
- **Do not merge V14 wholesale.** The current Aster branch lacks the
  `games/tbs/src/battle/battle/boss_ai.c` module present in
  `dark-story-rewrite`; its `round.c`, `enemy_ai.c`, and `enemies.c`
  differ from current Ashfall. The V14 IPS is a **full test-ROM diff against
  the clean game**, not an Aster-only overlay.

## Confirmed free slots in dark-story-rewrite (recheck at integration time)

| Resource | Current Ashfall | Staged Aster |
|---|---|---|
| Scene | 201 original scenes, no Aster | Appended scene 201 |
| Native map | 186 rows, no Aster | Appended Map180 at index 186 (`0xba`) |
| Overlay | No `0x3d3` scene | Aster scene overlay `0x3d3` |
| Sprite slots | `SPR_505`–`SPR_509` entries empty | Icon, well, memorial, Sanctum, added home |
| Scene symbols | No `SceneId_Aster` | `SceneId_Aster` declared |

Checks above inspect committed source; they are **not** a proof of ROM
linking, available runtime memory, or renderer behavior.

## Controlled transfer scope (after V14 emulator acceptance)

Transfer Aster-specific source and integrate the registration deltas into
the NEWER Ashfall files, manually reconciling against the destination:

1. Map: `games/tbs/src/map/map_180/map.s` and `map.txt`; use the immutable
   `tools/aster_v14_native_snapshot.json` to prove exact map identity.
   Preserve the native Vale metatile, shape, palette and animation references.
2. Scene: `games/tbs/src/scene/aster.c`, `scene/entry/aster.s`,
   `scene/import/aster.s`; any scene-table import and linker dependencies.
3. Sprite assets and animations: `spr_505`–`spr_509` source PNG/TSV,
   with **selective** additions to `sprite_ids.h`,
   `graphics/sprite/sprites.tsv` and `graphics/sprite/layout.tsv`.
4. Scene/map/object wiring: append the Aster declaration/entry into
   `include/scene_ids.h`, `src/field/scenes.s`,
   `src/field/maps.c`, `src/system/resource/directory.s`, and
   `games/tbs/objects.tsv` without replacing existing lines or indices.
5. Dialogue: author from `tools/aster_dialogue.tsv`, verify every relevant
   `MsgAster*` ID and the 27-character/3-line layout constraint, and append
   only Aster messages to the current Ashfall `games/tbs/text/en.po`.
   **Never copy the older full V14 catalogue over newer Ashfall messages.**
6. Overworld: the current V14 exit goes to Vault as a temporary fallback.
   The reversible `tools/aster_world_route_probe.py` is a test technique,
   NOT a production route. After actual terrain/emulator QA, implement a
   permanent reciprocal pair using currently unused IDs without shifting
   existing actors, exits, entrances or story events.

## Explicitly preserve from the newer Ashfall branch

- `games/tbs/src/battle/battle/boss_ai.c`, round/targeting and enemy AI.
- Enemy stats, battle effects and Claude's later balancing changes.
- Story rewrites, branch-policy safeguards and Sarah/Heart/Ash Jenna assets.
- The working baseline's save/version strategy. Test on disposable saves.

## No-charge gate and acceptance order

1. Keep every experiment on `experiment/aster-v14-native-map-staging`.
   Never push to `main` or `dark-story-rewrite` during Aster source QA.
2. Use read-only/source checks locally on a separate checkout:
   `python3 tools/aster_v14_preflight.py`.
3. If the native encoder is installed, run
   `bash tools/aster_v14_local_smoke.sh --map-only` locally.
4. Only with the necessary local toolchain and a verified **clean owned**
   English Golden Sun ROM, use `tools/aster_v14_build_ips.sh`; its output
   is a complete V14 experimental test patch, **never stack it on Ashfall**.
5. Emulator QA must cover original-style tiles/animation, bridge and water,
   NPC priorities, all eight triggers, every entry/exit, menu/party/Djinn
   behavior, and new/return visits before a selective integration.
6. **After** Aster passes, prepare a separate integration branch based on
   the current `dark-story-rewrite` HEAD. Recheck all slot reservations,
   transfer the specific Aster additions, and compile/test locally before
   proposing an eventual merge.

This document authorizes no GitHub Actions, Codespaces, paid runner,
paid service or automatic build. Do not claim playable integration until an
emulator session confirms it.
