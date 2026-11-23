	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map182
Field_Map182:
	@ Camera bounds fit the maze itself (40 x 35 cells).
	map_header 0, 0, 80, 70, 3, 2, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 80, 16, 16, 0, 0, 0xff, 0xff
	map_layer 104, 0, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map182, .LField_Map182_METATILES
	map_offset Field_Map182, .LField_Map182_SHAPES
	map_offset Field_Map182, .LField_Map182_GRID
	map_offset Field_Map182, .LField_Map182_ANIMATION
	map_offset Field_Map182, .LField_Map182_BLEND
	map_offset Field_Map182, .LField_Map182_MARKERS
.LField_Map182_METATILES:
	.incbin "games/tbs/src/map/map_182/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map182_SHAPES:
	.incbin "games/tbs/src/map/map_182/shapes.table.lz"
	.balign 4, 0
.LField_Map182_GRID:
	.incbin "games/tbs/src/map/map_182/map.grid.lz"
	.balign 4, 0
.LField_Map182_ANIMATION:
	.incbin "games/tbs/src/map/map_012/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map182_BLEND:
	.incbin "games/tbs/src/map/map_012/blend.script.lz"
	.balign 4, 0
.LField_Map182_MARKERS:
	treasure_spots_end
	.balign 4, 0
