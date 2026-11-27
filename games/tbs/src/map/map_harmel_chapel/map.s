	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.balign 4
	.global Field_HarmelChapel
Field_HarmelChapel:
	map_header 0, 0, 32, 36, 3, 2, 1, 1, 1, 1, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 255, 255
	map_layer 32, 0, 16, 16, 0, 0, 255, 255
	map_layer 64, 0, 16, 16, 0, 0, 255, 255
	map_offset Field_HarmelChapel, .LField_HarmelChapel_METATILES
	map_offset Field_HarmelChapel, .LField_HarmelChapel_SHAPES
	map_offset Field_HarmelChapel, .LField_HarmelChapel_GRID
	map_offset Field_HarmelChapel
	map_offset Field_HarmelChapel
	map_offset Field_HarmelChapel, .LField_HarmelChapel_MARKERS
.LField_HarmelChapel_METATILES:
	.incbin "games/tbs/src/map/map_harmel_chapel/metatiles.delta1.lz"
	.balign 4, 0
.LField_HarmelChapel_SHAPES:
	.incbin "games/tbs/src/map/map_harmel_chapel/shapes.table.lz"
	.balign 4, 0
.LField_HarmelChapel_GRID:
	.incbin "games/tbs/src/map/map_harmel_chapel/map.grid.lz"
	.balign 4, 0
.LField_HarmelChapel_MARKERS:
	treasure_spots_end
	.balign 4, 0
	.global Tileset_HarmelChapelPalette
Tileset_HarmelChapelPalette:
	.incbin "games/tbs/src/map/map_harmel_chapel/palette.gbapal.lz"
	.balign 4, 0
	.global Tileset_HarmelChapelTilesA
Tileset_HarmelChapelTilesA:
	.incbin "games/tbs/src/map/map_harmel_chapel/tiles_a.4bpp.mtf"
	.balign 4, 0
	.global Tileset_HarmelChapelTilesB
Tileset_HarmelChapelTilesB:
	.incbin "games/tbs/src/map/map_harmel_chapel/tiles_b.4bpp.mtf"
	.balign 4, 0
	.global Tileset_HarmelChapelTilesC
Tileset_HarmelChapelTilesC:
	.incbin "games/tbs/src/map/map_harmel_chapel/tiles_c.4bpp.mtf"
	.balign 4, 0
	.global Tileset_HarmelChapelTilesD
Tileset_HarmelChapelTilesD:
	.incbin "games/tbs/src/map/map_harmel_chapel/tiles_d.4bpp.mtf"
	.balign 4, 0
