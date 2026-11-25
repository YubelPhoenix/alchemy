	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map194
Field_Map194:
	map_header 0, 0, 60, 70, 3, 2, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 60, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 120, 0, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map194, .LField_Map194_METATILES
	map_offset Field_Map194, .LField_Map194_SHAPES
	map_offset Field_Map194, .LField_Map194_GRID
	map_offset Field_Map194, .LField_Map194_ANIMATION
	map_offset Field_Map194
	map_offset Field_Map194, .LField_Map194_MARKERS
.LField_Map194_METATILES:
	.incbin "games/tbs/src/map/map_003/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map194_SHAPES:
	.incbin "games/tbs/src/map/map_003/shapes.table.lz"
	.balign 4, 0
.LField_Map194_GRID:
	.incbin "games/tbs/src/map/map_194/map.grid.lz"
	.balign 4, 0
.LField_Map194_ANIMATION:
	.incbin "games/tbs/src/map/map_003/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map194_MARKERS:
	treasure_spots_end
	.balign 4, 0

	.global Tileset_PaletteUmbralVigil
Tileset_PaletteUmbralVigil:
	.incbin "games/tbs/src/graphics/tileset/palettes/pal_umbral_vigil.gbapal.lz"
	.balign 4, 0
