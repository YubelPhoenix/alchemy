	.include "games/tbs/src/map/map.inc"
	.section .rodata
	@ Aster, 64x64 exterior. All three layers use genuine Vale (Map003)
	@ metatiles, shape table, and matching Golden Sun set_02 palette.
	@ 128x128 grid holds layers at (0,0), (64,0), (0,64) cells.
	@ External Paradox spritesheets are NOT embedded or redistributed.
	.global Field_Map180
Field_Map180:
	map_header 0, 0, 128, 128, 3, 2, 1, 0, 2, 2, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 128, 0, 16, 16, 0, 0, 0xff, 0xff
	map_layer 0, 128, 16, 16, 0, 0, 0xff, 0xff
	map_offset Field_Map180, .LAsterMetatiles
	map_offset Field_Map180, .LAsterShapes
	map_offset Field_Map180, .LAsterGrid
	@ This shares Vale set_02, so its original tile animation script
	@ is the matching source for water and other animated metatiles.
	@ Experimental support only: verify visual behavior in emulator.
	map_offset Field_Map180, .LAsterAnimation
	map_offset Field_Map180
	map_offset Field_Map180, .LAsterMarkers
.LAsterMetatiles:
	.incbin "games/tbs/src/map/map_003/metatiles.delta1.lz"
	.balign 4, 0
.LAsterShapes:
	.incbin "games/tbs/src/map/map_003/shapes.table.lz"
	.balign 4, 0
.LAsterGrid:
	.incbin "games/tbs/src/map/map_180/map.grid.lz"
	.balign 4, 0
.LAsterAnimation:
	.incbin "games/tbs/src/map/map_003/tileset_anims.script.lz"
	.balign 4, 0
.LAsterMarkers:
	treasure_spots_end
	.balign 4, 0
