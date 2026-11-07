	.include "games/tbs/src/map/map.inc"
	.section .rodata
	@ Aster, prototype exterior; reuse Vault's original metatiles and shapes.
	.global Field_Map180
Field_Map180:
	map_header 0, 0, 64, 64, 3, 0, 0, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map180, .LAsterMetatiles
	map_offset Field_Map180, .LAsterShapes
	map_offset Field_Map180, .LAsterGrid
	map_offset Field_Map180
	map_offset Field_Map180
	map_offset Field_Map180, .LAsterMarkers
.LAsterMetatiles:
	.incbin "games/tbs/src/map/map_019/metatiles.delta1.lz"
	.balign 4, 0
.LAsterShapes:
	.incbin "games/tbs/src/map/map_001/shapes.table.lz"
	.balign 4, 0
.LAsterGrid:
	.incbin "games/tbs/src/map/map_180/map.grid.lz"
	.balign 4, 0
.LAsterMarkers:
	treasure_spots_end
	.balign 4, 0
