# Aster V14 reproducible integration and no-charge local preflight

Aster V14 is an isolated experimental branch. This update makes the staged
native Map180 **reproducible** and routes the repository's existing source
checks to the proper V14 layout instead of the retired town layout.

## What now works

- `python3 tools/aster_v14_native_map.py --check` reconstructs the
  exact staged 128x128 native three-layer map from
  `tools/aster_v14_native_snapshot.json`. The Git blob hash must match.
- `python3 tools/aster_layout.py --check` recognizes V14 and checks
  the new snapshot. Running the obsolete generator in write mode **refuses
  to overwrite V14**.
- `python3 tools/check_aster_v14.py` (which now also calls `tools/check_aster_native_foliage.py`) verifies the snapshot, nine
  markers, seven scene actors, house/reserved-site solidity, source-grid
  reachability, and just the southern edge being open.
- `python3 tools/check_aster.py` also routes its map contract to the
  V14 layout while continuing to inspect dialogue, scene imports, Aster
  resource rows, and compiled-source IDs.
- `python3 tools/aster_v14_preflight.py` runs these checks and
  verifies the original debug-entry shortcut remains inactive, without
  triggering remote builds.

## Source-only problems that remain

The original map had 786 solid-grass cells with no upper visual metatile.
Those were NOT all defective: 251 belong to the map perimeter, 210 fall
within original native house footprints, and 56 are the reserved Sanctum
and additional-home footprints. Only 269 were unclassified interior cells.

This woodland pass adds **12 original Golden Sun Vale 4x5 native tree
silhouettes**, retaining normal map behavior beneath 66 completely transparent
foliage cells, and requiring solid ground beneath 174 visible tree cells.
The current unclassified interior total is **235**, not zero.
This is a source-grid improvement only, not an emulator approval.

The north and outskirts are better framed by genuine native sprites, but
waterbanks, cliff faces, 235 remaining unclassified cells and the two reserved
buildings still need visual-and-collision review using a real Golden Sun
render or emulator. Some of those cells may already be accounted for by
nearby overhanging native sprite art.

The six original native facades are present, but Sanctum and the
additional house are only solid reserved plots. The dry well and memorial
still need finished registered native art. V13's imported preview sprites
do not become GBA metatiles simply by appearing in a PNG.

The current southern exit still returns the party through
`WORLD_MAP_FROM_VAULT_SOUTH`. This is an experimental safety return,
not a reciprocal Aster world-map entrance. A genuine world contact
requires auditing `games/tbs/src/scene/world_map.c`, including
`CONTACT_LAST_ACTOR = 65`, its `STEP_TRIGGER_AREA_BASE = 100`
contact behaviors, scene exit table, actor template order, world-map
collision and area placement. **Do not append an actor/exit casually**.

There has been no full ROM compile or emulator walkthrough of this V14
branch. The local preflight checks only source consistency; they do not
prove animation priorities, renderer compatibility, correct world-map
travel, or stable save/load behavior.

## Cost precautions

This branch has no configured Actions `push` workflow selector.
Do not use the web UI's Run workflow option. Use local checks and
optional local builds only. The user's GitHub account-level $0 budgets,
included-usage discounts and actual charges must be checked in GitHub's
private billing pages; none can be guaranteed from repository metadata.
