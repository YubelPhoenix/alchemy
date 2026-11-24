@ Golden Sun: Ashfall: the Umbral Rift's battle backdrops, recolored in the
@ Rift's obsidian and violet: Venus Lighthouse's hall for its monsters, and the
@ storm over the grid floor (heart_floor.png) for the Throne Hall.
	.section .rodata
	.balign 4
	.global Battle_UmbralRiftBackdrop
Battle_UmbralRiftBackdrop:
	.incbin "games/tbs/src/graphics/battle_bg/umbral_rift.gbapal"
	.incbin "games/tbs/src/graphics/battle_bg/umbral_rift.bitmap.d7"
	.balign 4
	.global Battle_UmbralThroneBackdrop
Battle_UmbralThroneBackdrop:
	.incbin "games/tbs/src/graphics/battle_bg/umbral_throne.gbapal"
	.incbin "games/tbs/src/graphics/battle_bg/umbral_throne.bitmap.d7"
