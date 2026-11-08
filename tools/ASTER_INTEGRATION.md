# Aster — convergence town integration contract

**Status: experimental, NOT release-ready.** This branch is separate from the Ashfall story branch. Source files and stage events exist, but there is **no ordinary overworld contact into Aster** and there is **no successful compiled ROM or emulator acceptance test recorded**. Do not merge based on static checks alone.

## Implemented on this branch

- **Map**: `tools/aster_layout.py` deterministically generates `games/tbs/src/map/map_180/map.txt`; 64 × 64 proposed cells, with exit at (32,63). Three 64 × 64 map layers are placed in the underlying 128 × 128 packed grid, and six cottages copy original Vale (Map003) metatiles across their ground, middle and overhead layers. The open terrain uses Vale's native three-layer grass arrangement (0xba/0x15/0x15). The blueprint reserves continuous connected streets; three original Vale dirt-ground patches now indicate crossroads, but do not yet form convincing full roads. **The art direction is Golden Sun only; the Paradox mockup was rejected.**
- **Map linkage**: `Field_Map180` is registered as the appended `gMaps` row **186 (0xba)** and `SceneId_Aster` references it, with overlay **0x3d3**. Map resource and object records exist.
- **Town actors**: seven NPC slots in `games/tbs/src/scene/aster.c`: elder (26,33), innkeeper (49,21), greeter (23,34), boy (35,39), resident (45,34), Other Isaac proxy (36,13), mirror woman (41,34). The Other Isaac proxy is currently a generic young-man sprite, **not finished custom art**.
- **Interactive landmarks**: well (32,34), memorial (32,13), sealed house (5,3), inn (45,3), two residential homes, shop and duplicate house. The eight approach tiles use Aster-only behaviors `0xe1`–`0xe8`; all exterior facades remain solid. The five new building thresholds show contextual dialogue but **do not lead to interiors**.
- **Dialogue**: `tools/aster_dialogue.tsv` contains 28 staged source records. All 28 plus four extra event stingers are **actually appended** to `games/tbs/text/en.po` (IDs 10727–10758); the earlier four Aster pilot lines remain (10723–10726). The `po` file is what compiles, not the TSV alone. **32 of 36 messages are now referenced by scene code.** The remaining four are the arrival/fracture/revelation gate and departure lines, intentionally held until a safe reciprocal overworld transition exists. The audit fails if any other compiled Aster message becomes unwired.
- **State machine**: scene-local flags `FLAG_SCENE_TEMP_00` through `0D`. Arrival → Fracture after the well, memorial, and greeter have been encountered (order independent). Fracture → Revelation through Other Isaac at the northern path. No permanent story flags or rewards are changed. Dialogues and landmark effects have one-time guards.
- **Visual studies**: `tools/aster_square_memorial.png` and `tools/aster_square_dirt.png` informed the stone memorial and earth patches now in Map180. `tools/aster_ruin_visual_study.png` is a **non-playable overgrowth study only**; its pasted-on tree clusters were rejected as a finished ruined town. The normal and ruined states do not yet have a game-state switch or distinct registered maps.
- **Return route**: Aster's gate currently sends the party to **`WORLD_MAP_FROM_VAULT_SOUTH`** for experimental evacuation. This is **not a reciprocal Aster return** and must be replaced before release.

## Open engine problems (do not claim solved)

1. **Real appearance and collision**: six cottages now copy native Vale map-layer tiles and all three 64x64 layers are registered. A genuine Golden Sun source-derived offline preview is available at `tools/aster_visual_review.png`; the formal failure list is `tools/ASTER_VISUAL_QA.md`. No compiled ROM has been rendered or walked in an emulator, so sprite priority, thresholds and collision remain unverified. The source-only preview passes basic Golden Sun style and now shows a Vale stone memorial. The dry well remains visually missing; paths are only small disconnected dirt patches, greenery repeats too much, and building damage is not implemented. The uploaded *Paradox* art is **not used** in the source or approved concept. No additional foreign art should be added.
2. **Overworld placement and return**: choose an actually unused reachable area of the world map away from Suhalla Gate. Audit collision and encounter data, reserve a new contact actor and exit IDs without shifting vanilla actors, and define a paired `WORLD_MAP_FROM_ASTER` arrival. Do not guess coordinates or repurpose Vault.
3. **Original custom art**: the duplicate Isaac and any Ash Jenna apparition need planned official or user-created assets, not placeholder NPC stand-ins.
4. **Stage persistence**: scene-temp flags reset on normal re-entry. That is intentional for this prototype; design and verify a durable story-state policy before production if the town must remember the player's first visit.
5. **Map event placement**: north Other Isaac, eight interaction tiles and south gate must be manually checked after the ROM builds. Pay particular attention to the 64x64 camera/layer windows, copied metatile collision, and stepping on `0xe1–0xe8`.
6. **Text rendering**: lines may fit 27 characters but still overflow due to glyph widths, control codes, font kerning or speaker banners. Playtest every page, including two-page original innkeeper dialogue.
7. **Save compatibility**: entering and leaving must preserve party, Djinn, chapter progress, menus, save/reload and world-map position.

## Repeatable automated checks

- `python3 tools/aster_layout.py --check` — tracked grid matches generator.
- `python3 tools/check_aster.py` — map markers, connected walkable areas, all 28 source/compiled dialogue entries, PO page limits, actor/scene/source references and overlay imports.
- GitHub Actions: `.github/workflows/aster-prototype.yml`. Only a short **source audit** runs automatically on this experimental branch. A modified-English ROM compile can be requested via **Run workflow**; it is deliberately manual to avoid repeated expensive toolchain builds. A passing source audit does **not** imply a passing ROM or gameplay.

## Acceptance walkthrough (manual after successful ROM build)

1. Launch Aster through a verified development scene selector or the eventual overworld contact; check a new and pre-existing save. Do not enable a globally intrusive debug cheat in a release.
2. Verify all seven NPCs draw on reachable cells and do not block the plaza, memorial, or exit.
3. Visit the well, memorial and greeter in all six orders; ensure fracture triggers exactly once and the player's controls always return.
4. Speak to every NPC in arrival, fracture and revelation; test normal Talk and Mind Read, single and repeated conversations. Confirm no vanilla NPC text leaks in.
5. Approach the sealed door and all five new house/inn/shop thresholds from the street. Ensure none accidentally transfers into a missing interior, and repeat after fracture. Roofs and facades must remain impassable.
6. Talk to the northern Other Isaac before and after fracture. After revelation, revisit memorial and exit; observe the intended changes in dialogue and no glyph corruption.
7. Test opening Start, A, Psynergy and party menus; save, reload, Retreat and re-enter. Confirm existing Ashfall story flags and vanilla town dialogue are unchanged.
8. Verify a proper two-way overworld entrance: return to the same reachable contact, not Vault. Confirm no encounter softlocks, black screen, or freeze.
9. Build from a clean checkout and inspect the actions log and emulator results. Merge only after checks 1–8 pass.

## Narrative rules

Aster must look like a Golden Sun settlement from its first frame. Its **contradictory geography and history**, not a foreign visual style, eventually provide evidence of a physical fragment of Ash Jenna's version of Weyard overlapping Isaac's world. The arrival dialogue does not reveal that yet; see `tools/ASTER_WORLD_DESIGN.md`. Aster is a settlement caught between Isaac's world and Ash Jenna's. The horror comes from incompatible memories and repeated conversations becoming contradictory; never corrupt text bytes or simulate a broken cartridge. The manifestation called Other Isaac is a deliberately ambiguous echo, **not** a claim about Golden Sun canon. Isaac remains a mostly silent protagonist. Every scripted text page is limited to **27 characters per line, three lines per page**, with manual width verification required.

The town should feel initially inhabited, then impossible, then like the memory of people who know Jenna's other fate. Never use external-game tiles or another RPG's visual style to signal convergence; only distort familiar native Golden Sun scenery. Endings and lore revelations must support the Ash Jenna storyline rather than replace it.
