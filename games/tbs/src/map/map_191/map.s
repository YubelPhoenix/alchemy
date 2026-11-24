	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map191
Field_Map191:
	map_header 0, 0, 44, 48, 3, 1, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 44, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 48, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map191, .LField_Map191_METATILES
	map_offset Field_Map191, .LField_Map191_SHAPES
	map_offset Field_Map191, .LField_Map191_GRID
	map_offset Field_Map191, .LField_Map191_ANIMATION
	map_offset Field_Map191, .LField_Map191_BLEND
	map_offset Field_Map191, .LField_Map191_MARKERS
.LField_Map191_METATILES:
	.incbin "games/tbs/src/map/map_191/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map191_SHAPES:
	.incbin "games/tbs/src/map/map_191/shapes.table.lz"
	.balign 4, 0
.LField_Map191_GRID:
	.incbin "games/tbs/src/map/map_191/map.grid.lz"
	.balign 4, 0
.LField_Map191_ANIMATION:
	.incbin "games/tbs/src/map/map_054/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map191_BLEND:
	.incbin "games/tbs/src/map/map_054/blend.script.lz"
	.balign 4, 0
.LField_Map191_MARKERS:
	treasure_spots_end
	.balign 4, 0
	.global Tileset_PaletteUmbralCross
Tileset_PaletteUmbralCross:
	.incbin "games/tbs/src/graphics/tileset/palettes/pal_umbral_cross.gbapal.lz"
	.balign 4, 0
