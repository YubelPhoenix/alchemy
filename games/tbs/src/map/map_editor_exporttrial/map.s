	.include "games/tbs/src/map/map.inc"
	.section .rodata
	.balign 4
	.global Field_EditorExportTrial
Field_EditorExportTrial:
	map_header 0, 0, 80, 42, 3, 2, 1, 1, 1, 3, 0, 0
	map_layer 0, 0, 16, 16, 0, 0, 255, 255
	map_layer 0, 80, 16, 16, 0, 0, 255, 255
	map_layer 160, 0, 16, 16, 0, 0, 255, 255
	map_offset Field_EditorExportTrial, .LField_EditorExportTrial_METATILES
	map_offset Field_EditorExportTrial, .LField_EditorExportTrial_SHAPES
	map_offset Field_EditorExportTrial, .LField_EditorExportTrial_GRID
	map_offset Field_EditorExportTrial
	map_offset Field_EditorExportTrial
	map_offset Field_EditorExportTrial, .LField_EditorExportTrial_MARKERS
.LField_EditorExportTrial_METATILES:
	.incbin "games/tbs/src/map/map_editor_exporttrial/metatiles.delta1.lz"
	.balign 4, 0
.LField_EditorExportTrial_SHAPES:
	.incbin "games/tbs/src/map/map_editor_exporttrial/shapes.table.lz"
	.balign 4, 0
.LField_EditorExportTrial_GRID:
	.incbin "games/tbs/src/map/map_editor_exporttrial/map.grid.lz"
	.balign 4, 0
.LField_EditorExportTrial_MARKERS:
	treasure_spots_end
	.balign 4, 0
	.global Tileset_EditorExportTrialPalette
Tileset_EditorExportTrialPalette:
	.incbin "games/tbs/src/map/map_editor_exporttrial/palette.gbapal.lz"
	.balign 4, 0
	.global Tileset_EditorExportTrialTilesA
Tileset_EditorExportTrialTilesA:
	.incbin "games/tbs/src/map/map_editor_exporttrial/tiles_a.4bpp.mtf"
	.balign 4, 0
	.global Tileset_EditorExportTrialTilesB
Tileset_EditorExportTrialTilesB:
	.incbin "games/tbs/src/map/map_editor_exporttrial/tiles_b.4bpp.mtf"
	.balign 4, 0
	.global Tileset_EditorExportTrialTilesC
Tileset_EditorExportTrialTilesC:
	.incbin "games/tbs/src/map/map_editor_exporttrial/tiles_c.4bpp.mtf"
	.balign 4, 0
	.global Tileset_EditorExportTrialTilesD
Tileset_EditorExportTrialTilesD:
	.incbin "games/tbs/src/map/map_editor_exporttrial/tiles_d.4bpp.mtf"
	.balign 4, 0
