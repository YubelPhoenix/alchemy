	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map192
Field_Map192:
	map_header 0, 0, 32, 26, 3, 1, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 32, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 26, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map192, .LField_Map192_METATILES
	map_offset Field_Map192, .LField_Map192_SHAPES
	map_offset Field_Map192, .LField_Map192_GRID
	map_offset Field_Map192, .LField_Map192_ANIMATION
	map_offset Field_Map192, .LField_Map192_BLEND
	map_offset Field_Map192, .LField_Map192_MARKERS
.LField_Map192_METATILES:
	.incbin "games/tbs/src/map/map_192/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map192_SHAPES:
	.incbin "games/tbs/src/map/map_192/shapes.table.lz"
	.balign 4, 0
.LField_Map192_GRID:
	.incbin "games/tbs/src/map/map_192/map.grid.lz"
	.balign 4, 0
.LField_Map192_ANIMATION:
	.incbin "games/tbs/src/map/map_054/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map192_BLEND:
	.incbin "games/tbs/src/map/map_054/blend.script.lz"
	.balign 4, 0
.LField_Map192_MARKERS:
	@ The chest in the left alcove (subject 100, the Ritual Room's chest trigger).
	treasure_spot 3, 3, 100
	treasure_spots_end
	.balign 4, 0
@ Golden Sun: Ashfall: the lighthouse tileset's third sheet with the Ritual
@ Room's pentagram in free tiles (graphics/tileset/umbral_ritual/tiles_c.png).
	.global Tileset_UmbralRitualTilesC
Tileset_UmbralRitualTilesC:
	.incbin "games/tbs/src/graphics/tileset/umbral_ritual/tiles_c.4bpp.mtf"
	.balign 4, 0
