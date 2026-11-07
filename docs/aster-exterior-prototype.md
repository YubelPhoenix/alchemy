# Aster exterior prototype — integration notes

**Experimental and untested in game.** Do not merge yet.

The first new exterior is `map_180`, configured at `gMaps[186]` with
Vault's existing palette and tiles. `ResourceId_AsterMap` = 978 and
`ResourceId_Map001` = 296, so its gMaps resource offset is 682.
A dedicated scene/overlay is registered as `SceneId_Aster` with resource
`0x3d3`, area `0x47`, map index `0xba`. Two previously unused resource
directory slots are consumed, avoiding renumbering vanilla resources.

The 32x32 prototype has blocked building footprints, a walkable plaza and
north approach, a well, memorial, two test NPCs, and south gate behavior 1.
Building / monument / road tiles are placeholders. NPC dialogue triggers,
interiors, Mind Read, convergence effects, music and actual world-map contact
**are not yet implemented**.

Access is only via debug scene selection or temporary test scene jump.
The south exit deliberately returns to Vault's safe existing world-map entry
`WORLD_MAP_FROM_VAULT_SOUTH`, *not* a new unverified map coordinate.

Rebuild/check the asset via:
`python3 tools/aster_layout.py --check`

Next QA: build in CI or locally, load the scene, test drawn tiles,
collisions, NPCs, exit, save/load. If those pass, verify free world-map
terrain before adding entry and reciprocal return. Preserve 27-character
dialogue lines and never use invalid text control codes for corruption.
