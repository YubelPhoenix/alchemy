# Aster — 6-building concept translation v1 (NOT a playable field map)

**Approved visual target:** the generated hillside-village illustration with two northern homes, an inn and shop facing the central well, two southern homes, western waterfall and bridge, eastern lily pond, layered woodland and active garden/service plots.

**This file is a translation specification, not a map build.** The source AI illustration is visual art direction only. The original 64×64 GBA Map180 field, scene actors, events, dialogue, portals and user saves remain untouched by this branch. A matching annotated reference, 64×64 placement diagram, original-sprite comparison sheet and full machine-readable placement manifest were prepared as conversation artifacts, not inserted into the ROM.

## Approximate placement on existing 64×64 metatile coordinates

The concept is projected into x 0–63, y ~11–53; these are preliminary editable *design* coordinates and do not replace actual native tiles or registered event script positions.

| Site | Role / story contract | Approx. center | Original sprites in supplied scenery.zip |
| --- | --- | --- | --- |
| A | NW house; appears ordinary, later sealed | (18,18) | `buildings/Vale/Vale_Isaacs_House.gif` |
| B | NE house; duplicate-home mystery | (45,17) | `buildings/Vault/Vault_Building3.gif` |
| C | Inn and guest/service yard | (15,30) | `buildings/Vale/Vale_Inn.gif` |
| D | Shop, outdoor trade stall and stock | (49,30) | `buildings/Vale/Vale_WepArm_Shop.gif` |
| E | Occupied SW family home and firewood work yard | (17,43) | `buildings/Vault/Vault_Building1.gif` |
| F | Occupied SE family home and kitchen garden | (41,43) | `buildings/Vale/Vale_Jennas_House.gif` |
| G | Dry well / civic commons | (32,34) | `outdoor/sm/well.gif` |
| H | Market stall attached to shop | (41,29) | `outdoor/lg/Wood_Counter.gif` |
| I | Western river crossing | (7,36) | `buildings/Vale/Vale_Bridge.gif` (candidate; collision/width require matching terrain) |
| J | Southern field entry and exit | (32,52) | `outdoor/lg/Vale_Gate.gif` |
| K | North-center stair/level connection | (33,20) | requires actual compatible cliff + stair transition metatiles |
| L | Western waterfall | (5,22) | requires native animated water and cliff set |
| M | Eastern lily pond | (58,31) | `plants/lilypad1.gif` over actual matching water/bank tiles |
| N | Northern memorial — eighth story event | (29,19) | `outdoor/sm/grave1.gif` (visual candidate only) |

## Preserve Aster's exact story structure

Eight proposed exterior event functions: sealed A, duplicate B, inn C, shop D, inhabited west E, inhabited east F, well G and memorial N. Do not delete or rewrite the existing seven NPC roles, Other Isaac encounter, dialogue chronology, scene stages, or reciprocal southern overworld link. No ruined-state replacement map. No Psynergy Stone.

## Required spatial design

- Main north–south access connects southern gate (32,52), central commons (32,34), and north stairs (~33,20). Inn/shop frontage branches west/east from the commons. Upper house paths follow two separate rises. Southern household paths approach each front door from the south.
- Forests, cliff terraces and household boundaries are *landscape geometry*, not random tree sprites. The generated concept's waterfall/river on the west and pond on the east are major elements, not decorative water patches.
- Each home has a practical fenced garden/work yard and water access. Inn has barrels/service access; shop has stocked outdoor market frontage. Keep walkable approaches at least ~2 metatiles, main route ~3 where practical.
- Use exact user-provided original scenery GIFs as the exterior *sprite vocabulary*. Do NOT assume those cutouts are already registered in Aster's Golden Sun set_02 charblock, palette, or metatile definition.
- The scenery ZIP does not provide complete waterbank/cliff/road terrain autotiles; locate compatible source map data before trying gameplay integration.

## Integration gates

1. Select compatible terrain and confirm full source metatile/palette/layer support.
2. Rebuild landform, waterfalls, riverbanks, forest edges and roads in actual Golden Sun tiles — not a procedural collage and not the generated image pasted as a background.
3. Place six functional exterior structures and complete walkable property parcels, then register all event, actor and door positions together in `aster.c` / Map180.
4. Add interiors and working shop/inn interactions, test collision/sprite priority at waterfall banks and bridge, paths, both stairs, every doorway, and save/reload.
5. Compare the actual emulated 16px render with the generated concept and original Ashfall town maps. Reject even technically valid tilemaps when foliage, water, rooftops or paths visibly clip.

No live Map180 changes are authorized or represented by this design-only branch.
