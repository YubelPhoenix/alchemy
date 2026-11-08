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

## Implemented in the November 8 native art/dialogue pass

**Water animation:** `games/tbs/src/map/map_180/map.s` now references
Vale's own `map_003/tileset_anims.script.lz`, restoring the original
set_02 animated-water/waterfall channels rather than leaving the map
animation pointer at zero. Actual movement in the GBA renderer still
requires emulator testing.

**Western crossing:** 18 pre-existing, walkable bridge cells
(`x=3..11, y=35..36`) now use original Vale bridge deck and overhead
metatiles from `Map003` (`x=9..17, y=38..39`). All 18 cells were
previously passable and remain so. No new west map exit or event was
created. The complete bridge baseline and source coordinates are in
`tools/aster_native_boundary_manifest.json`. New read-only
`tools/check_aster_native_bridge.py` verifies the full native
source-to-destination mapping. This **does not** certify art alignment,
rail priority, or the visible shoreline.

**Registered native scenery actors:** Four new 224-colour indexed
sprites were added only in unused 506–509 slots. The original seven
talking NPCs remain in their original actor order and locations, with
the scenery actors appended after them:
- `SPR_506`: 32×32 dry well at `(32,34)`, near event `e1`.
- `SPR_507`: 32×64 engraved memorial at `(29,19)`, near `e2`.
- `SPR_508`: 64×64 compact Sanctum façade at `(42,33)`.
- `SPR_509`: 64×64 compact second house façade at `(13,57)`.

Their sprites, animation TSVs, registry entries, and scene placements
are verified by the new `tools/check_aster_native_decor.py`. None
overwrites Camelot's original sprites or the earlier Aster overworld
icon 505. **The last two are overlay façades on solid collision-reserved
plots, not finished walkable interiors.** We cannot certify their size
or draw-order without a ROM test.

**Dialogue:** `tools/aster_polish_dialogue.py` contains ten reviewed,
27-character-limit edits to the innkeeper, elder, village memories,
fracture and Ash echo. The `--check` mode is read-only; the
`--apply` mode updates the disposable build's local English PO
and dialogue TSV only. The tracked `games/tbs/text/en.po` was left
unchanged because a push to that path could trigger the dialogue
GitHub Actions workflow. No new message IDs or lasting story flags
were added. All 36 original Aster message IDs remain protected.

**Checks and reproducibility:** After the bridge commit, the exact
native map Git blob is
`a03c527bb290a4b1dc0aff268c022aa6f317cb3a`.
The RLE map snapshot and native boundary manifest both carry the
matching hash. Source review verified all nine event markers, the
original seven NPC coordinates, unchanged native ground collision,
and all 18 bridge tiles.

## Still incomplete — do not claim release readiness

- **Terrain:** Original Vale water and deck animation data are linked,
  but complete riverbanks, cliff faces, waterfall visuals and the
  visible west-bank junction are **not** in-emulator certified.
  The 235 unclassified invisible-solid cells from the previous foliage
  census still need visual inspection; some may be intentional.
- **Buildings:** The original six house facades remain. The Sanctum
  and additional house now have compact sprite artwork but their
  reserved 4×7 footprints remain solid and **no interiors or door
  transitions are implemented**. Inn/shop thresholds still display
  dialogue rather than functioning as full store/inn interiors.
- **Landmarks:** The well/memorial have registered sprite artwork and
  existing stage-sensitive events, but final art priority/collision
  and animation need an emulator check.
- **Dialogue/events:** Ten refinements are staged for the local
  ROM/IPS builder. Three original Mind Read triggers exist; the other
  four NPCs still need standalone Mind Read text and correct build
  message IDs before this part is genuinely complete.
- **World map:** An optional two-way test-only Aster icon/exit probe
  exists. Production Aster's overworld actor and walkable geographic
  location near Vault are deliberately not registered permanently.
- **Build:** No V14 ROM compile, IPS proof, emulator screen/video,
  save/load, or main Ashfall merge has been performed. Source checks
  cannot substitute for those tests.

This work remains on `experiment/aster-v14-native-map-staging`.
Never substitute a preview GIF for native map data, and do not modify
the main Ashfall branch without a tested IPS.
 
## Cost precautions

This branch has no configured Actions `push` workflow selector.
Do not use the web UI's Run workflow option. Use local checks and
optional local builds only. The user's GitHub account-level $0 budgets,
included-usage discounts and actual charges must be checked in GitHub's
private billing pages; none can be guaranteed from repository metadata.
