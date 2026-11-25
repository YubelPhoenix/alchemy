	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.global Field_Map193
Field_Map193:
	map_header 0, 0, 128, 128, 3, 1, 2, 1, 1, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 128, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 128, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map193, .LField_Map193_METATILES
	map_offset Field_Map193, .LField_Map193_SHAPES
	map_offset Field_Map193, .LField_Map193_GRID
	map_offset Field_Map193, .LField_Map193_ANIMATION
	map_offset Field_Map193, .LField_Map193_BLEND
	map_offset Field_Map193, .LField_Map193_MARKERS
.LField_Map193_METATILES:
	.incbin "games/tbs/src/map/map_123/metatiles.delta2.lz"
	.balign 4, 0
.LField_Map193_SHAPES:
	.incbin "games/tbs/src/map/map_123/shapes.table.lz"
	.balign 4, 0
.LField_Map193_GRID:
	.incbin "games/tbs/src/map/map_193/map.grid.lz"
	.balign 4, 0
.LField_Map193_ANIMATION:
	.incbin "games/tbs/src/map/map_123/tileset_anims.script.lz"
	.balign 4, 0
.LField_Map193_BLEND:
	.incbin "games/tbs/src/map/map_020/blend.script.lz"
	.balign 4, 0
.LField_Map193_MARKERS:
	treasure_spots_end
	.balign 4, 0

	.global Tileset_PaletteUmbralPalace
Tileset_PaletteUmbralPalace:
	.incbin "games/tbs/src/graphics/tileset/palettes/pal_umbral_palace.gbapal.lz"
	.balign 4, 0
