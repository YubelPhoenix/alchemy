# Ashfall rear-facing battle sprite tracker

Baseline: 71a1b7626ce3886d4731c000b2de17feb1a1b8f0. This branch is an isolated experiment, not a release build.

| Boss | Sprite | Asset / implementation | Build | Emulator |
| --- | ---: | --- | --- | --- |
| Ash Jenna | 477 | Audit only | Pending | Pending |
| Heart | 484 | Rear idle frames 1 and 11 prepared; source selector added | Pending | Pending |
| Kegare | 487 | Audit only | Pending | Pending |
| Sarah | 488 | Audit only | Pending | Pending |
| ??? | 489 | Audit only; sequential animation frames need separate mapping | Pending | Pending |
| Vengeful Wraith | 491 | Audit only | Pending | Pending |
| Menardi Atropos | 492 | Audit only; orientation-specific aura needed | Pending | Pending |

Heart: the author supplied HeartPosing.png and HeartChoke.png. Only HeartPosing is selected for this experiment. The casting candidate has a more frontal torso and a substantially wider silhouette at game resolution; do not install it as a rear cast. The source is stored in assets/heart/rear/HeartPosing.png. The original frame positions 0,2,4,6,8,10 and unused action duplicates 3,5,7,9 are unchanged. Both rear idle positions share one drawing (rear breathing is static). The selected frames use the existing native front/back table for the rear sectors only; all other frames and sprites retain the old Kind 44 behavior. The asset builder regenerates the rear artwork so the official workflow does not overwrite it.

Static validation: exact baseline PNG Git blob 96d0097d5ade5f51e59341d4a699a745c843c58b; replacement PNG blob 99c55053f7118392ca1b67c66dcf2d68ba5e9bfc. The source artwork blob matches the supplied file. A local pixel comparison confirmed only frames 1 and 11 changed; 224-color palette and 64x768 sheet preserved. The zero-run packer calculation including directory is 13,993 bytes (original 13,946; one 16 KiB slot is 16,384). The direction selector model passed 9408 combinations of sprite ID, cache slot, layer, camera, flip flag, base frame and angular sector. This is not execution of the actual game renderer or a ROM build. The full asset builder and toolchain have not been run locally.

Acceptance checks: both Heart encounters; normal command camera, rotation past both rear sector boundaries and return, idle-to-dash/lunge/cast/damage/defeat transitions, hit flash, status overlays and normal front idle breathing; mixed Rift battle with ???; ordinary enemies and Saturos/Menardi; frame cache capacity and no visual glitches. Rear action poses retain front artwork and can cause visible orientation discontinuities; do not claim full rear support. No builds triggered by this experiment branch. Do not merge until the ROM is built and tested.
