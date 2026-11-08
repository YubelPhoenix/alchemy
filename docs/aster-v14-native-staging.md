# Aster V14 native Map180 staging — NOT RELEASE READY

This isolated branch starts from experiment/aster-convergence-town. It is NOT merged with main or Ashfall.

## Implemented in actual native source

- Replaced Map180's old 64x64 positions with approved V9/V12 terrain reservations in the native 128x128 three-layer text format.
- Preserved original Vale metatile references; resolved all 1331 original Vale 0xfff placeholders using original ordering, validated against metatiles.tsv.
- Six full native Vale building facades were transplanted. Seven actors in scene/aster.c were relocated to matching map coordinates.
- Moved the eight e1..e8 interaction markers and south exit 1 to (32,62); all unique and reached by flood fill from (32,61).
- Added source-native path soil, selected native open-water cells, and full four-by-five native Vale trees where collision clearance permitted, including northern candidates suggested by V13.
- Retained V12's terrain-class fixes. Restricted the only reachable map edge to (32,63). West bridge remains unwired.

## This is NOT finished

- The V13 GIF scenery is a visual prototype; not all original V13 plants are GBA metatiles, so the native map may look different.
- Shore and cliff shaping is incomplete. The original Vale water/waterfall animation script now links into Map180; the native 9x2 west bridge decking is stamped with unchanged collision, but both still require emulator art review.
- The Sanctum and additional house have separate indexed native-format compact façade sprites (508/509) attached as scene actors, but their plots remain collision-reserved and have no walkable interiors or checkpoint service.
- Dry well (506) and memorial (507) have new registered indexed source art and existing story triggers. Sprite rendering, overlap and collision remain unverified in-game.
- The reciprocal WORLD_MAP_FROM_ASTER transition has not been added. Aster's exit still points to WORLD_MAP_FROM_VAULT_SOUTH and is NOT production-safe.
- tools/aster_layout.py now refuses to overwrite the V14 native map; tools/check_aster.py dispatches to the dedicated V14 map contract. Do not run any obsolete map generator in write mode.
- No V14 ROM or emulator test has been run. Use the local-only Aster IPS builder and reversible overworld probe in a disposable checkout, after compiler setup; never test with a real Ashfall save.

## Safety

No Actions workflow on this repository selects pushes to experiment/aster-v14-native-map-staging. No workflow was manually dispatched. Changes were made by GitHub contents API without executing builds. Verify private billing independently.

## Validated pre-commit

- Exactly 9 markers at expected coordinates.
- All 7 NPC anchors relocated in the matching scene source.
- 6 complete native roofs, no overlap with roads or NPC/events.
- Southern edge (32,63) alone reachable; other borders blocked.
- All event markers and actor sites connected to (32,61).
- Original source SHA checks and Vale metatile count matched.

## Recovery checkpoint — 2026-11-08 (read-only GitHub source audit)

This checkpoint was verified against the committed **V14 staging branch** using
read-only GitHub file requests and independent in-memory checks. It is not an
Alchemy compiler, game-engine, or emulator acceptance result.

- **Map snapshot integrity:** `tools/aster_v14_native_snapshot.json`
  reconstructs exactly the committed `map_180/map.txt`; its Git blob SHA and
  the native-boundary manifest both match
  `a03c527bb290a4b1dc0aff268c022aa6f317cb3a`.
- **Native grid:** 128×128 packed source cells (16,384 total); 284 distinct
  packed tile tokens. Nine distinct triggers (eight events and one south exit)
  appear at the V14 coordinates and are reached from spawn at (32,61).
- **Collision and access:** 2,252 non-solid reachable ground cells; only the
  (32,63) south-edge cell is reachable on the boundary. All seven NPC anchors
  match the scene source. When seven NPC locations are additionally treated
  as blocking tiles, 2,245 cells remain reachable, all nine triggers remain
  accessible, and every NPC has at least three reachable neighboring tiles.
  This models source flags only; it does not reproduce engine collision.
- **Scenery integrity:** the registered `spr_505.png` Aster icon is present.
  The committed native indexed `spr_506.png` (well), `spr_507.png`
  (memorial), `spr_508.png` (Sanctum) and `spr_509.png` (additional house)
  match the immutable Git blob hashes in `check_aster_native_decor.py`.
  In-emulator sprite priority/rendering has not been verified.
- **Water animation:** Aster references Vale's
  `map_003/tileset_anims.script.lz`, the same built asset the original Vale
  `map.s` references. The underlying `map_003/tileset_anims.tsv` source is
  present. The `.lz` is a generated artifact, not a tracked source file;
  no successful native build has been verified.
- **Reversible world-map route:** source anchors and unused test registration
  are still available. No world-route probe was applied. The committed Aster
  south exit still points to Vault's temporary world-map return; it must not
  be considered a production-safe reciprocal exit.

### Next acceptance steps (not completed)

1. On a **disposable local checkout** of this exact staging branch, run
   `python3 tools/aster_v14_preflight.py` or
   `bash tools/aster_v14_local_smoke.sh --check-only`.
2. Once the host graphics encoder is available, run
   `bash tools/aster_v14_local_smoke.sh --map-only` and inspect any errors.
3. Only after compiler/dependency setup, and only with a verified clean owned
   English TBS ROM, use the guarded local IPS builder documented in
   `tools/aster_v14_build_ips.sh`. Test on a **separate ROM copy and save**.
4. In an emulator, verify sprite priority and animation, waterfall, cliff and
   bridge art, NPC interaction, event progression, collisions, entrance/exit,
   and overworld walkability before considering any integration.
5. Compare against `dark-story-rewrite` selectively. **Do not blindly merge**
   V14 into that branch or `main`, which has diverged and contains independent
   dialogue/boss changes.

**Cost boundary:** This checkpoint used no GitHub Actions, Codespaces, hosted
runners or remote ROM builds. No emulator, compiler or native map-encoder pass
is claimed. Keep V14 branch isolated and do not manually dispatch workflows.
