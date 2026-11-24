	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map190
Field_Map190:
	map_header 0, 0, 34, 54, 3, 1, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 34, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 54, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map190, .LField_Map190_METATILES
	map_offset Field_Map190, .LField_Map190_SHAPES
	map_offset Field_Map190, .LField_Map190_GRID
	map_offset Field_Map190, .LField_Map190_ANIMATION
	map_offset Field_Map190, .LField_Map190_BLEND
	map_offset Field_Map190, .LField_Map190_MARKERS
.LField_Map190_METATILES:
	.incbin "games/tbs/src/map/map_190/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map190_SHAPES:
	.incbin "games/tbs/src/map/map_190/shapes.table.lz"
	.balign 4, 0
.LField_Map190_GRID:
	.incbin "games/tbs/src/map/map_190/map.grid.lz"
	.balign 4, 0
.LField_Map190_ANIMATION:
	.incbin "games/tbs/src/map/map_163/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map190_BLEND:
	.incbin "games/tbs/src/map/map_054/blend.script.lz"
	.balign 4, 0
.LField_Map190_MARKERS:
	treasure_spots_end
	.balign 4, 0
	.global Tileset_PaletteUmbralVenus
Tileset_PaletteUmbralVenus:
	.incbin "games/tbs/src/graphics/tileset/palettes/pal_umbral_venus.gbapal.lz"
	.balign 4, 0
