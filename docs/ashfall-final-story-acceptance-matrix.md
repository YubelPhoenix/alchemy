# Ashfall final story acceptance matrix

> Status as of 3 November 2026. See the **current pre-play audit** at [Ashfall Pre-play Audit](ashfall-preplay-audit-2026-11-03.md), including the world-map A-button freeze and the dormant palette-cache cleanup. Static source/dialogue inspection is **not** a substitute for playing the patched ROM. An item marked PENDING is not accepted, even if compilation succeeds.

## The narrative contract

1. The first Golden Sun adventure is the spine: Vale and Sol Sanctum; Mercury/Imil; Kolima; Fuchin/Xian; Altin; Lamakan; Kalay/Tolbi/Colosso; Venus; Lalivero; Babi's ship; and the original post-clear Jenna/Kraden reveal. Optional encounters do not displace the rescue mission, the Elemental Stars or the later beacons.
2. **Ash Jenna** is the evil, ruthless, unrepentant alternate Jenna from the user's sprite animation. Her story of a destroyed world is her **claim**, and her accusation against the Wise One is not verified by Isaac. She is never the original Jenna, never morally exonerated, and never quietly redeemed. Isaac may agree to investigate, but this is not assent to killing.
3. **Original Jenna** is missing for Isaac, but is shown alive with Kraden in the original ending. Felix and Sheba's survival becomes known to Jenna/Kraden only in the final Alex reveal; Isaac's party must not speak as if it witnessed their rescue.
4. Mia remains an Imil healer and responsible party member. Her Manticore anger is about what she felt, not an event in which she killed an innocent person. Kegare's impersonation, Heart's mistaken identification of Isaac as Matthew and Ash Jenna's vendetta are independent.
5. Golden Sun's real Psynergy Stones and already-established magical phenomena stay; discarded Bloom/sleeper/awakened cosmology, phantom Ivan voices, caravan subplot and unsupported mythology do not return.
6. Villagers and companions must be more than a chorus of ominous one-liners: preserve practical concern, humor, family ties, disagreement, ordinary work and a range of emotional responses.

## Event-to-speaker audit

These maps were checked against the corresponding scripted **source** functions, not inferred from message names. A change to a row with an established speaker must preserve that speaker's point of view.

| Scene and source | Exact speaker assignment / message order | Branch invariants |
| --- | --- | --- |
| Mercury, `MercuryLighthouseAerie_MiaInterrupts` | N59 Mia; N60 Isaac; N61 Mia; N62 Isaac; N63 Mia; N64 Saturos | The uneasy cooperation must still lead to the existing duel aftermath, not an invented new battle. |
| Mercury, `MercuryLighthouseAerie_MiaYields` | N65 Mia; N66 Mia; N67 Isaac; N68 Mia; N69 Mia; Saturos speaks N70 in `SaturosResumes` | Menardi leaves with hostages; Mia pursues her alone; remaining party confronts Saturos and later reunites. |
| Altin, `AltinPeak_TalkToTrappedMiner` | N140 miner (Yes/No); N141 miner on Yes, N142 miner on No; N143 Mia; N144 Garet; N145 Mia; N158 Ivan; N146 Isaac; N147 miner; N169 miner; N170 Ivan; N171 Garet; N172 miner (Yes/No); N173 miner on Yes, N174 Mia on No | The miner's second question is NOT the first rescue question. Flag `FLAG_DARK_MINERS_FREED` only after help and `FLAG_DARK_MINER_STAYED` only after Yes to staying. |
| Lamakan, `LamakanDesert_ManticoreAftermath` | N149 Mia; N150 Garet; N151 Mia; N152 Mia; N153 Isaac; N159 Ivan | The monster may target anyone in battle; do not claim it attacked one specific ally. The aftermath precedes Ash Jenna's automatic reveal. |
| Lamakan, `LamakanDesert_MeetAshJenna` before the boss | N106 Ash Jenna; N107 Isaac; N108 Ash Jenna; N109 Ash Jenna; N110 Isaac | This brief first meeting is optional; finale must still work if missed. |
| Lamakan, `LamakanDesert_AshJennaFinale` | Optional opening N224 Ash Jenna/N225 Isaac, otherwise N195 Ash Jenna/N196 Isaac; N197 Ash Jenna; N198 Garet; N199 Ash Jenna; N200 Ivan; N201 Mia; **N203 Garet** only if the miner stay flag is set; N208 Isaac choice prompt; Yes: N209 Isaac, N210 Ash Jenna, N211 Ivan, N212 Ash Jenna; No: N213 Isaac, N214 Ash Jenna, N215 Ivan, N216 Mia; N221 Ash Jenna | N203 was previously accidentally sarcastic in Ash Jenna's voice despite being spoken by Garet. Fixed to acknowledge Isaac's decision to stay with the frightened miner. The choices are preserved in distinct flags. |
| Tolbi, `Tolbi_MeetAshJenna` | N74 Ash Jenna; N75 Isaac; N240 Ash Jenna if accepted or N241 if refused; N76 Ash Jenna; N77 Garet; N78 Ash Jenna; N79 Mia; N80 Ash Jenna; N81 Mia; N82 Ash Jenna; N83 Isaac; N154 Ivan; N115 Isaac; N116 Mia; N117 Isaac; N118 Mia | After N240/N241, **reset message ID to N76** before the consecutive N76–N83 sequence. The follow-up with Mia should work after either branch. |
| Tolbi, `Tolbi_TalkToKegare` | N102 Kegare; N103 Isaac; N104 Kegare; N226 Mia; N227 Kegare; N228 Mia; N105 Isaac | Kegare is optional and independent of Ash Jenna; test both encounter orders and a lost battle/retry. |
| Kolima, `Kolima_TalkToHeart` and `Kolima_HeartAftermath` | N123 Heart; N124 Isaac; N125 Heart; N126 Heart; N127 Heart; N128 Isaac. On victory: N129 Heart; N130 Isaac; N131 Heart; N132 Heart | Heart's last line now refuses forgiveness rather than promising a second appearance absent from the playable TBS route. Defeat must not mark the optional battle as won. |
| Lalivero, `Lalivero_TalkToAshJenna` | N300 Ash Jenna; N301 Isaac; N302 Ash Jenna; N303 Isaac; N304 Ash Jenna; N305 Isaac; N306 Ash Jenna; N307 Isaac; N308 Ash Jenna; N309 Isaac; N310 Ash Jenna; Yes N311 Isaac / No N312 Isaac; N313 Ash Jenna; N314 Isaac; N315 Ash Jenna; N316 Isaac; N317 Ash Jenna; N318 Isaac | Coda requires Tolbi conversation and completed Venus lighthouse. The alternate Jenna remains actively hostile. No blocker to Iodem's Black Orb or the ship; once-only completion flag `FLAG_DARK_ASH_JENNA_LALIVERO`. |
| Lemurian ship, `LemurianShip` departure cutscene | Garet's going-home question; Ivan/Mia's Babi/Lemuria follow-up; Mia's rough-sea question | Each of the three Yes/No prompts must display its correct reply and resume the next message cursor, independent of the answer. |
| Original ending, `WorldMap_ShowEndingEvent` | Jenna and Kraden speak on the drifting island; Alex appears and leads them to Felix and Sheba | Keep the original camera, scene, messages, and revelation. No evil Ash Jenna cameo. |

## Playthrough checklist (all PENDING)

- **PENDING — Opening and route chronology:** New game through Vale, Sol Sanctum, Mercury, Imil, Kolima, Fuchin, Xian, Altin, Lamakan, Kalay, Colosso, Venus, post-Venus Lalivero, ship, true ending. Verify no missed mandatory progression event, premature scene or unearned knowledge.
- **PENDING — Mercury alternatives:** Examine each entry, a retry/loss branch, solo Mia–Menardi fight, party reconstruction and subsequent Saturos fall, and the flags that persist after exiting.
- **PENDING — Altin humanitarian branch:** Rescue Yes and No, second miner stay Yes and No, item reward once, no reward on decline, and the optional N203 callback in Lamakan only after staying. Confirm no duplicated Power Bread on map re-entry.
- **PENDING — Lamakan Manticore:** Fight and lose/retry, then inspect the automatic Mia aftermath and Ash Jenna reveal, both with and without the earlier optional desert meeting. Inspect the heat gauge before/after lengthy cutscenes.
- **PENDING — Ash Jenna choices:** Accept and refuse at Lamakan; examine both Tolbi callbacks; preserve the correct N76 continuation; then verify N311 vs N312 in Lalivero. Test skipped Tolbi and revisiting Lalivero before and after the coda.
- **PENDING — Independent optional fights:** Fight Heart at Kolima, lose/retry, win/aftermath and confirm one-time disappearance; fight Kegare in Tolbi before and after Ash Jenna and check the same win/defeat behavior. No fake connection between enemies.
- **PENDING — Venus climax and postclear:** Verify Felix, Sheba, Jenna and Kraden's locations through every transition, both answer branches at Venus, Isaac party's limited knowledge of the fall, the original ship departure, and the final island revelation.
- **PENDING — Audio, visuals, readability:** Confirm speaker portraits match the line's speaker, including the evil alternate sprite coloration and Heart's custom mugshot; all dialog fits at actual game speed; no mistimed text while an actor is hidden or absent.

## Release rubric

**Narrative readiness is not measured by raw dialogue volume.** A release-quality pass must verify: consistent causality, accurate source speakers, no false environmental facts, no invented lore or exposition beyond what the character knows, earned choice callbacks, distinct voices and tonal contrast, and an ending that respects Golden Sun while leaving appropriate uncertainty for the next installment. Build/IPS success checks syntax and ROM viability; **full branch playtesting** is required before claiming 10/10.

## Visual-identity and automated safety-contract addendum

The three Ash Jenna **field** appearances must use the original Jenna character sprite, with the alternate actor's grey tint and unique ID. Kegare must visibly mimic Mia using the existing Mia character sprite, also as an independent NPC actor, while the true Mia stays in the party. These are **base-game sprite substitutions**, *not* the final custom sprite art from the creator's animation. Do not claim an exact visual recreation until the animation's actual art has been imported and checked.

`tools/dark_story/check_story_contract.py` now enforces important source-level invariants on each dialogue/ROM build, including these identities, choice callbacks and battles that can be retried after defeat. This automated check must pass, but all **PENDING** playthrough tests above remain pending. Explicitly inspect whether showing two Mia appearances (real Mia versus Kegare) causes any palette, portrait, actor-collision, sprite-cache or animation conflict in Tolbi. Check the three Ash Jenna appearances for correct Jenna frames and grey coloring at real hardware resolution; their current sprite is provisional.


### Mercury combat-balance pre-play check (still PENDING)

The mandatory Isaac and Mia solo-duel code calls `Unit_LevelUpTo` for Isaac at **14** and Mia at **24**, and no post-victory normalization is present in the scene. The Mia–Menardi fight uses a dedicated level-24/600-HP enemy. Mia's special weapon may be skipped if her inventory is full. **Save before the confrontation; leave Mia an open item slot; verify levels/gear before and after the party reunion and gauge whether later battles remain engaging.** This is a documented balance risk, not a source-verified game crash or a reason to invent a new route.

