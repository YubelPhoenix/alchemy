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
