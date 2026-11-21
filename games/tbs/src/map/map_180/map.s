	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map180
Field_Map180:
	map_header 0, 0, 100, 90, 3, 1, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 90, 16, 16, 0, 0, 0xff, 0xff
	map_layer 100, 0, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map180, .LField_Map180_METATILES
	map_offset Field_Map180, .LField_Map180_SHAPES
	map_offset Field_Map180, .LField_Map180_GRID
	map_offset Field_Map180, .LField_Map180_ANIMATION
	map_offset Field_Map180, .LField_Map180_BLEND
	map_offset Field_Map180, .LField_Map180_MARKERS
.LField_Map180_METATILES:
	.incbin "games/tbs/src/map/map_180/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map180_SHAPES:
	.incbin "games/tbs/src/map/map_180/shapes.table.lz"
	.balign 4, 0
.LField_Map180_GRID:
	.incbin "games/tbs/src/map/map_180/map.grid.lz"
	.balign 4, 0
.LField_Map180_ANIMATION:
	.incbin "games/tbs/src/map/map_086/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map180_BLEND:
	.incbin "games/tbs/src/map/map_086/blend.script.lz"
	.balign 4, 0
.LField_Map180_MARKERS:
	treasure_spots_end
	.balign 4, 0
