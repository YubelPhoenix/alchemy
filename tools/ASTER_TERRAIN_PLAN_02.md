# Aster terrain plan 02 — implementation handoff

**Design branch only.** The approved six-building, well-centered, terraced Golden Sun village illustration remains the sole visual target. This planning pass does **not** claim a new finished map, a palette-safe spritesheet, or changes to the live gameplay Map180 or Aster scene.

## First source-level discoveries

- The live `games/tbs/src/map/map_180/map.s` uses Vale `map_003` metatiles/shapes but its 4th (animation) map offset is empty.
- Vale `map_003/map.s` defines `tileset_anims.script.lz` for matching `set_02`. **Draft PR #11** adds that pointer experimentally, and remains unmerged until full ROM compilation and an emulator tile/animation test.
- Vault `map_018` loads `set_15`; Xian `map_048` loads `set_38`. Their graphics cannot simply be pasted into Vale's `set_02` metatile bank. Use the supplied original sprites as design references until import/palette registration is resolved.
- Native scenery assets verified locally: `Vale_Bridge.gif` is **128×64 pixels** (8×4 metatiles); `well.gif` is **32×30 pixels**. Visible footprint and collision footprint are separate contracts.

## Author-defined road and terrain geometry

A local 64×64 mask study (`aster_terrain_layers_v2.json`) explicitly provides:
- A western waterfall/river (243 water cells), with one bridge and separate 8×4 art reservation versus 7×2 walkable strip.
- A separate irregular 90-cell eastern pond and 128 edge/bank cells to receive proper native shore transitions.
- A continuous 78-cell retaining cliff with a 12-cell central stair passage toward the upper homes.
- A central well-plaza detour and 354 walkable road/plaza cells joining the southern gate, six doors, northern memorial and bridge.

The **abstract road graph connects all 11 required anchors**. It rejects geometry through houses, cliff faces, pond water, or the central well. This is NOT GBA collision verification.

The local handoff archive includes the reference-annotated concept, tile-coordinate schematic, editable JSON, exact QA report, and build script. Do **not** use the source-study shapes as final visible game tiles; they have no terrain palette assignments yet.

## Next actual map-engine task

Develop a single cohesive **cliff → stair → path → river bank → bridge** sample using a compatible registered Golden Sun tileset, with no copied card-like terrain patches. In the emulator, verify source animation, sprite priority, slopes, bank/water collision and authentic path corners before extending the sample to the full town. Only then update Map180, story triggers, seven NPCs and portals in one reviewed change.

**Ruined Aster remains postponed.** There is no second destroyed map under development.
