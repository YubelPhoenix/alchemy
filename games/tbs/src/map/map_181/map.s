	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map181
Field_Map181:
	map_header 0, 0, 34, 32, 3, 1, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 34, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 32, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map181, .LField_Map181_METATILES
	map_offset Field_Map181, .LField_Map181_SHAPES
	map_offset Field_Map181, .LField_Map181_GRID
	map_offset Field_Map181, .LField_Map181_ANIMATION
	map_offset Field_Map181, .LField_Map181_BLEND
	map_offset Field_Map181, .LField_Map181_MARKERS
.LField_Map181_METATILES:
	.incbin "games/tbs/src/map/map_181/metatiles.delta1.lz"
	.balign 4, 0
.LField_Map181_SHAPES:
	.incbin "games/tbs/src/map/map_181/shapes.table.lz"
	.balign 4, 0
.LField_Map181_GRID:
	.incbin "games/tbs/src/map/map_181/map.grid.lz"
	.balign 4, 0
.LField_Map181_ANIMATION:
	.incbin "games/tbs/src/map/map_054/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map181_BLEND:
	.incbin "games/tbs/src/map/map_054/blend.script.lz"
	.balign 4, 0
.LField_Map181_MARKERS:
	treasure_spots_end
	.balign 4, 0
	.global Tileset_PaletteUmbralMerc
Tileset_PaletteUmbralMerc:
	.incbin "games/tbs/src/graphics/tileset/palettes/pal_umbral_merc.gbapal.lz"
	.balign 4, 0
