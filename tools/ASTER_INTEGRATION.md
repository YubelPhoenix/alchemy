# Aster — convergence town integration contract

Status: **experimental / not playable**. Do not merge into the story branch until a ROM build AND in-game entry/exit/event audit pass.

## Existing resources
- `tools/aster_layout.py` deterministically generates `games/tbs/src/map/map_180/map.txt`.
- 32×32 cell proposal, south gate at (15,31), well (16,16), memorial (16,10).
- Layout uses provisional metatile values. They require verification against the chosen tileset, collision and actual engine scene data.
- `map_180` must not be described as an available map ID until table reservations, scene dispatch, existing references and resource loading have been audited.

## Location and entrance
Place a new optional world-map entrance in a verified unused accessible area, not at Suhalla Gate. Its exact coordinates stay unresolved until the world map's collision, entrance and encounter tables are checked. The south gate returns to the **same overworld location**, preserving formation, progression flags and save compatibility. Never repurpose an existing required entrance.

## State machine
- ARRIVAL: innocuous, almost normal. NPCs use `arrival` entries.
- FRACTURE: unlock upon interacting with the well, memorial and one resident (order independent). Reuse the **same** NPCs with `fracture` entries; no unreadable text or random bytes.
- REVELATION: unlock after speaking to the northern Other Isaac. The northern appearance is a scene event and should not impersonate a real party member object. Reuse `revelation` dialogue. Exit remains possible at all times.
- Events must be idempotent: repeat talks should neither repeat rewards nor endlessly trigger cutscenes.
- All stages require an explicit flag allocation audit; no arbitrary flag numbers.

## Horror, continuity and characters
Aster is the overlapping memory of two worlds. Ash Jenna shares Jenna's past and knowledge of Vale; the town offers fragments of people who remember incompatible outcomes. The Other Isaac is a deliberately ambiguous manifestation, not a canon claim that a second Isaac already exists in Golden Sun. Retain Isaac's mute protagonist presentation where practical; avoid lengthy new dialogue for him. Environmental unease should come from changed meaning, positions and duplicate NPC events, **never** malformed glyphs or text corruption.

## Engine implementation checklist
1. Verify `map_180` is free across scene/map/overlay/resource tables and references; avoid overwriting vanilla.
2. Determine real tileset/metatile IDs and movement/collision values by inspecting an existing town exterior, then replace provisional numbers.
3. Add appropriate scene script, object list and overlay/resource wiring using engine-native conventions; do not leave a map-text-only shell.
4. Add precisely one reversible overworld entrance and one escape/return transition. Verify save and reload on both sides.
5. Reserve stage flags and wire dialogue IDs in the actual text tables; no dialogue TSV is automatically compiled.
6. Verify all speaker/context mappings and run text width validation; **27 characters maximum per line, 3 lines maximum per page**.
7. Build a test ROM and test NPC positions, no softlocks, NPC/event repeat interaction, save compatibility and original game progression.
8. Only then consider merging or describing the town as playable.

## Dialogue staging
`tools/aster_dialogue.tsv` is a *narrative source of truth*, not a compiled game-text resource. Columns: stage, key, speaker, line1, line2, line3. Each row has at most three lines of no more than 27 characters. Identical keys may change between stages on purpose.
