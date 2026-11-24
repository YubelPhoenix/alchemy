	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map184
Field_Map184:
	map_header 0, 0, 32, 36, 3, 1, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 32, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 36, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map184, .LField_Map184_METATILES
	map_offset Field_Map184, .LField_Map184_SHAPES
	map_offset Field_Map184, .LField_Map184_GRID
	map_offset Field_Map184, .LField_Map184_ANIMATION
	map_offset Field_Map184, .LField_Map184_BLEND
	map_offset Field_Map184, .LField_Map184_MARKERS
.LField_Map184_METATILES:
	.incbin "games/tbs/src/map/map_184/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map184_SHAPES:
	.incbin "games/tbs/src/map/map_184/shapes.table.lz"
	.balign 4, 0
.LField_Map184_GRID:
	.incbin "games/tbs/src/map/map_184/map.grid.lz"
	.balign 4, 0
.LField_Map184_ANIMATION:
	.incbin "games/tbs/src/map/map_054/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map184_BLEND:
	.incbin "games/tbs/src/map/map_054/blend.script.lz"
	.balign 4, 0
.LField_Map184_MARKERS:
	treasure_spots_end
	.balign 4, 0
