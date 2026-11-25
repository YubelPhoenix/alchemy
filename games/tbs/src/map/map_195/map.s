	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map195
Field_Map195:
	map_header 0, 0, 58, 60, 3, 2, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 58, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 116, 0, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map195, .LField_Map195_METATILES
	map_offset Field_Map195, .LField_Map195_SHAPES
	map_offset Field_Map195, .LField_Map195_GRID
	map_offset Field_Map195, .LField_Map195_ANIMATION
	map_offset Field_Map195, .LField_Map195_BLEND
	map_offset Field_Map195, .LField_Map195_MARKERS
.LField_Map195_METATILES:
	.incbin "games/tbs/src/map/map_037/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map195_SHAPES:
	.incbin "games/tbs/src/map/map_037/shapes.table.lz"
	.balign 4, 0
.LField_Map195_GRID:
	.incbin "games/tbs/src/map/map_195/map.grid.lz"
	.balign 4, 0
.LField_Map195_ANIMATION:
	.incbin "games/tbs/src/map/map_037/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map195_BLEND:
	.incbin "games/tbs/src/map/map_020/blend.script.lz"
	.balign 4, 0
.LField_Map195_MARKERS:
	treasure_spots_end
	.balign 4, 0

	.global Tileset_PaletteUmbralGrove
Tileset_PaletteUmbralGrove:
	.incbin "games/tbs/src/graphics/tileset/palettes/pal_umbral_grove.gbapal.lz"
	.balign 4, 0
