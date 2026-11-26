# Ashfall dialogue correction review — 2026-11-25

Parent: 4fcacb2d9271d0c07779dc2cc3c25fd8e9d56e8b (stabilization/20261125).
Upstream English message source: pascalpixel/alchemy blob 080419430482c5947ad785ba04ab80157113a071.

This isolated review branch is intentionally outside the push-triggered ROM build branch list. No workflow file was altered, no workflow dispatched or cancelled, and no merge to stabilization or main is authorized by this change.

## Correction register

| Overlay | Message IDs | Reason |
| --- | --- | --- |
| phase2_sanctum.tsv | 04051 | Restore first-visit question semantics. |
| phase69_lalivero_town_sequences.tsv | 10389–10404 | Restore the entire original Iodem conversation block, speakers, Yes/No response, Black Orb narration and explanation. |
| phase66_babi_audience_part1.tsv | 08920 | Restore Iodem's perspective. |
| phase67_babi_audience_part2.tsv | 08944, 08957, 08965, 08966, 08984 | Restore Stone of Sages, Ivan's deduction, draught time estimate and ongoing lighthouse construction. |
| phase58_true_ending.tsv | 10534 | Restore Kraden's question to Alex. |
| phase10_goma_mccoy_mia.tsv | 05528–05530 | Restore Mercury Clan restriction and Mia's trust in Isaac. |
| phase75_lama_hama_reveal_story_overhaul.tsv | 06489, 06496, 06566, 06589 | Restore geographical context, direct address and Psynergy transfer lore. |
| phase92_karagol_docks_trade_kraken_aftermath.tsv | 07957 | Restore seasickness question. |
| phase95_karagol_ship_deck_remaining.tsv | 08041 | Restore island exploration question. |
| phase112_ship_rooms_oarsman_replacement_kraken.tsv | 07800, 07809 | Restore confirmation questions. |
| phase29_altin.tsv | 06335 | Restore conversational question. |
| phase53_babi_lighthouse.tsv | 09999, 10000 | Restore stone-door constraint and confirmation question. |
| phase68_suhalla_iode_sequence.tsv | 09737 | Restore guard account. |
| phase50_babi_scholars.tsv | 08222 | Restore the sealing of Alchemy as Kraden's research question. |
| phase60_venus_lighthouse.tsv | 09858 | Restore original puzzle inscription. |
| phase35_lamakan_jenna.tsv | N106 | Punctuation only. |
| phase72_fuchin_xian_regional_overhaul.tsv | 06081 | Add upstream fallback overlay for altered base question. |
| phase104_alpine_hsu_rescue_desert_travelers.tsv | 06606 | Add upstream fallback overlay for altered base line; no assumption about rescue choice. |

42 existing replacement rows changed, including one punctuation-only change; two new replacement rows restore upstream text over modified base messages. Total 44 IDs in 18 TSV files. No event scripts, maps, game mechanics, workflow definitions, or approved mystery dialogue were changed.

## Deferred decisions and validation

- Sarah optional encounter order, permanent placement of ???, and the name of Mia's weapon require author decisions; no changes here.
- Retired blank message slots remain reserved. Tret's voices and watcher foreshadowing remain pending interpretation.
- The prior 124-file structural scan and selected event/source checks are not a completed full contextual campaign audit. Original event branches, actual rendered maps, compiled ROM, and emulator playthrough remain unverified.
- Do not merge or trigger a build until explicitly authorized.
