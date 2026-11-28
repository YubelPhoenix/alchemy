# Ashfall rear-facing sprite tracker

Baseline: 71a1b7626ce3886d4731c000b2de17feb1a1b8f0. Source integration candidate; ROM build and emulator verification remain pending.

| Boss | Sprite | Rear positions | Packed bytes (baseline / revised) | Source | ROM / emulator |
| --- | ---: | --- | --- | --- | --- |
| Heart | 484 | 1, 11 (idle) | 13,946 / 14,087 | Integrated | Pending |
| Ash Jenna | 477 | 5 (slash) | 16,048 / 15,912 | Integrated | Pending |
| Kegare | 487 | 5 (slash) | 13,850 / 13,737 | Integrated | Pending |
| Vengeful Wraith | 491 | 7 (cast) | 14,100 / 14,387 | Integrated | Pending |
| Menardi Atropos | 492 | 11 (cast) | 15,390 / 15,347 | Integrated, exterior aura adaptation | Pending |
| Sarah | 488 | none | unchanged | Excluded by author | Regression only |
| ??? | 489 | none | unchanged | Deferred by author | Regression only |

All prepared frames are conversions of author-supplied artwork, not generated assets. Heart uses the approved refined frame, not the earlier prototype. Ash Jenna and Kegare have image-only anchor corrections of +18 and +8 source pixels before mirroring. Native direction table selects rear poses only where supplied. Unsupported poses retain the old Kind 44 behavior; pose transitions may still show an orientation discontinuity. No animation scripts or battle mechanics were changed. Heart rear breathing is static.

The five baseline sheets were decoded and every nonreplacement frame was compared exactly. All source palette indices and dimensions are retained. PNG round-trip checks passed. Conservative packed-size check counts offset directory, zero runs, literals and terminators; all below 16 KiB. Host C89 test of selector and anchor helper passed 1,179,648 input combinations; this is not an execution of the game renderer. Build-time art generators reapply the indexed rear frames and check the palette, frame layout and memory budget. No full ROM build or full builder execution performed yet.

Atropos uses the original ten-phase cast aura table for the new rear cast only on transparent pixels; front-facing aura, idle hair, fabric, crimson eyes and all strike/dissolve logic remain untouched. Rear cloth/hair are static and the exterior glow may need visual adjustment. Actual rear aura and transitions require emulator testing.

Acceptance: all selected encounters, rear/front camera sectors including command view, returning to normal view, attack and cast transition timing, shadow/feet/weapon placement, damage flash, status overlays, defeat, Atropos exterior aura, mixed Rift encounters, Sarah and ??? untouched, original Menardi/Saturos and regular enemies. Build only after static review; no claim of release readiness.

Pre-merge CI audit: the artwork validator now recognizes only the explicit approved rear pairs and checks their exact indexed pixels against the supplied-art conversions. All other duplicate-pair checks remain in effect. Build triggers also cover rear assets and the shared overlay helper. Full CI execution is pending.
