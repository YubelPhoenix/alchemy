# Ashfall narrative stabilization — audit register

Baseline 9c635b3bea86b9ba3456f3f2a8b95cd3ade00072. This report is a partial contextual audit, not a completed playthrough or release certificate. The current-canon document supersedes conflicting historical notes; it does not authorize new plot facts. No build or workflow modification is part of this pass.

## Evidence and scope

- Original English catalogue blob 1cbd1ebc0e0af07dced60cba63d2d877021eb4c5: recovered and parsed 10,739 numbered entries. Prior overlay scan covered 124 TSV files at 953d7f7, before the 28 Vault removals. The current targeted comparisons examined the affected NPC overlays against original text, including Vale/Vault/Bilibin, early dungeons, Imil/Mercury, Altin/Lamakan, Fuchin/Lama, Kalay/Lunpa, and the southern campaign. Full line-by-line contextual comparison is not complete.
- Repository tree has 273 C/assembly scene files. Only the relevant source scripts and targeted trigger paths were inspected; not all 273 have been independently audited.
- Protected phase118_mystery_leader.tsv matches original approved revision a88d3ad byte-for-byte (blob 1b4e886fa1178952b3bd1a463a7fbc0890728f77).
- No local checkout or emulator available; no rendered-map or ROM runtime validation. The container cannot resolve github.com. Connector can read text blobs, but static inspection cannot establish rendered environments.
- Prior removal: Altin custom miner actor, event, reward, and trigger; 27 reserved custom messages cleared; 28 Vault overrides removed. Current source checks in altin_peak.c, lamakan_desert.c and tolbi.c show no live calls to the cleared miner/Mia follow-ups. Reserved flags and message slots stay for compatibility.

## Confirmed obsolete replacements removed in this pass

| ID | File | Live source | Reason |
| --- | --- | --- | --- |
| 04642 | phase2_vault.tsv | vault.c:1475 | Restore original town introduction (heart of Angara) instead of ash everywhere. |
| 04733 | phase5_vault_a.tsv | log_rooms_a.c:4033 | Restore original missing family heirloom thought; remove invented mother's ashes. |
| 07181 | phase15_vale_revisit.tsv | cottage_rooms_a.c:1320 | Restore original dangerous roads/weapons trade; remove unsupported ash-driven monster causation. |
| 05982 | phase21_bilibin_riverbank.tsv | mccoy_palace.c:1815 | Restore hired warriors/McCoy's response; remove gray-sky accusation. |
| 05983 | phase21_bilibin_riverbank.tsv | mccoy_palace.c:1817 | Restore thought about warriors' reward; remove ash claim. |
| 05985 | phase21_bilibin_riverbank.tsv | mccoy_palace.c:1821 | Restore question about choosing a warrior's life; remove world-dying assertion. |

Only overlays are removed, so original IDs, control tokens and triggers remain. No new replacement prose is authored.

## Original narrative review: findings awaiting approval

- Sol Sanctum 04051: original asks whether this is the first visit. Replacement asks "You've never been inside, have you?" while sol_sanctum_entrance.c:853-856 retains original Yes/No semantics. Recommend restoring the positive question, but no change in this pass.
- Venus Lighthouse 10272: earlier audit incorrectly treated the Elemental Stars plural as an Ashfall-origin contradiction. The original says "The Elemental Stars? We have them!" Preserve the original plot exchange; withdraw the earlier issue.
- Vault 04907-04910: older Djinn/strange creature exchange adds "Watching the ash fall" and insinuates the creature is something other than a beast. Direct trigger was not located in the checked files. Candidate for restoring original subject/wording; do not classify as live without checking sequential/script references.
- Sol Sanctum 04333 and the three watcher appearances: current added line "Something is watching us" may be intentional foreshadowing. Do not remove the watchers or related dialogue before the author confirms.
- Mia's hired-thieves encounter near Imil: N29-N31 explicitly describes a red-haired girl hiring them. This may be Ash Jenna foreshadowing. Preserve; do not invent a new explanation.
- Vale 04381 "Mt. Aleph is awake" can be figurative personification, not evidence of an Awakened faction. Do not treat keyword matches as lore.
- Lamakan N106: first sentence has no terminal punctuation before the next question; ordinary proofreading candidate, not a story rewrite.
- Sarah N340-N349 assumes earlier meetings. Current optional encounters have no required defeat sequence. Treat as a release-path decision if prior encounters can actually be skipped; no forced sequence or altered lore without author approval.
- ??? in Vale: the encounter is intentionally temporary for testing, and the original approved exchange presumes prior sightings/attempts. Do not rewrite or force boss order now. On eventual relocation, review the Rift lines that name Vale or depend on prior duel victory and the final encounter order.
- Ash Jenna's existing appearances and medicine incident remain. Do not infer "stays in Vale" means delete her earlier narrative appearances; permanent boss location is protected, other scene decisions remain for author confirmation if needed.
- Wraith: phase_karis.tsv preserves final "Dad..." and the party's reactions. The throne callback is conditional on FLAG_DARK_RIFT_KARIS_BEATEN. Preserve.
- Rift: 192 N-series overlay rows; 129 directly referenced across umbral_rift.c and world_map.c; 63 lack direct references in those two files. This does not establish global unreachability, particularly for sequential calls or non-field labels. Many are drafts of still-canonical exchanges rather than abandoned plotlines. Do not bulk-clear them. Wraith enemy name is a label, not a field dialogue call.
- Rift throne: N541 is gated by completed Lamakan revelation; N614 by Wraith victory; prior Vale warning and Heart recognition are conditional. Preserve Apollo Lens/Ace/Spade exchange and current character intent rather than removing it for stylistic brevity. The ultimate object of ???'s search remains for the author, not the audit.
- Rift geometry: verify each actual rendered room, entrance, exits, silhouette position and light/anchor placement before accepting descriptive dialogue. Source comments alone are not geometry evidence.

## Acceptance matrix

| Area | Current evidence | Remaining gate |
| --- | --- | --- |
| Vale storm and opening | Earlier targeted dialogue/source inspection; catalogue available | Full event and NPC/Mind Read review |
| Sol Sanctum | Original question comparison; watcher source inspected | All sequential choices, actor/event context, geometry |
| Vault/Goma | Confirmed obsolete overlays restored; Goma Whirlwind fix previously committed | Remaining live/sequential NPC routes and revisits |
| Bilibin/Tret | Three live obsolete McCoy thoughts restored; curse flag logic inspected earlier | All curse and rescue variants |
| Imil/Mercury | Dialogue tables/key encounter scripts inspected earlier | Healer, duel, chase and reunion sequencing/runtime |
| Fuchin/Xian/Altin/Lama | Regional overlays inspected; miner removed | Force/Reveal guidance, optional Hsu paths, map context |
| Lamakan | Linear Ash Jenna dialogue and calls inspected; retired callbacks absent | Both optional first-sighting paths and fight aftermath |
| Kalay/Lunpa | Selected overlay review and Sarah continuity issue | Palace, rescue and alternative branches |
| Karagol/Tolbi/Colosso | Prior overlay scan; Ash Jenna linear encounter inspected | All ship choices, tournament and NPC visit states |
| Suhalla | Guard report and Ash Jenna dialogue inspected | Before/after optional gate duel, medicine context |
| Babi/Venus/Lalivero | Selected regional overlays, original Stars exchange and Ash Jenna coda | Remaining sequential and post-Venus states |
| Ship/ending | Prior selected source review; preserve original ending | Complete branch and ending replay |
| Custom bosses | Current character tables and selected source checked | Encounter defeat/retry, final intended placement, battle text |
| Umbral Rift | Dialogue-to-source cross-reference and room event order inspected | Actual rendered map inspection; runtime, optional path and seal |
| Build | Not requested or run | Author authorization and compilation |
| Release | NOT ACCEPTED | Remaining contextual and runtime gates |

Do not equate zero formatting errors, a source change, or an automated keyword scan with narrative acceptance.


## Follow-up: Imil recovery and central/eastern regional review

Baseline f80498e54c68dd0ec28bb6ef7f204d95d743f1cd. Compared the post-Mercury Imil overlay against original catalogue blob 1cbd1ebc0e0af07dced60cba63d2d877021eb4c5, and checked live post-beacon triggers in imil.c:2127–2195. Removed nine obsolete or unnecessary post-recovery overlays (05690, 05691, 05696, 05704, 05705, 05713, 05718, 05719, 05721). Original text restores the Water of Hermes, the villagers' recovery, Mia's departure without worry, and gratitude toward the party. The original 05713 already mentions Mia's reservations about lighting the beacon; it does not introduce an unspecified cost to the village. Compatible 05720, 05745, 05747 remain. No custom battle or event altered.

Inspected the current Mercury Aerie custom dialogue N37–N58 and the Mia/Menardi confrontation, victory/retry and reunion source (mercury_lighthouse_aerie.c:1200–1345). The visible party and speaker order match the custom dialogue sequence. Preserve the custom duel and reunion; no rewrite authorized. Runtime and map checks remain outstanding.

Targeted original-vs-overlay keyword comparison also covered Goma/McCoy, Imil, Kolima/Tret, Hsu rescue, Xian, Fuchin/Lama, Kalay tour and palace/Hammet/Layana, including the relevant phase10–12, 86–89, 94, 96–100, 103–104 files. This is not full contextual acceptance. Tret 05332 ("Those voices... were mine?") is a candidate for review against the retired voice mythology, not a confirmed leftover: it may refer to his own curse. Kolima's original sentient trees and curse remain canon. Xian's Hsu rescue and Kalay's ordinary merchant/tour dialogue are not discarded storylines. No edits to those scenes.

Remaining: full source-trigger and sequential-message audit, original-game choice verification, final encounter placement and rendered maps. No build requested or triggered by this source-only cleanup.


## Follow-up: southern Weyard, Babi, Lalivero, and original ending

Baseline fb9dd374c8d75c336bb1a182b4f163402d3ec190. Source-only review; no authorization to rewrite main-story conversations or change builds. Compared the original English catalogue to selected replacements across 27 southern/central overlays (phase90–93, 95, 110–113; phase102, 106–109, 64–67; phase105, 68–70, 56–60). These are targeted text comparisons, not complete per-message contextual acceptance. The missing Karagol ship, Kraken, injured/replacement oarsmen, island landfall, refugees from Lalivero, Babi's illness, and the search for Lemuria all exist in the original narrative and must not be removed as abandoned Ashfall lore. No confirmed retired plotline surfaced in the inspected southern samples. Preserve the current Ash Jenna scenes.

### Confirmed speaker/sequence regressions — awaiting author review

Babi's post-Colosso audience (babi_palace.c:1405 onward, BabiPalace_MeetBabiAfterColosso; phase66/67):
- 08920 is Iodem's line, original "We intended to thank you and your companions for saving Babi, Isaac." Replacement "We owe you and your companions for bringing me back, Isaac." It incorrectly makes Iodem the person rescued. Restore original.
- 08957 is Ivan's continuation of his deduction about Babi's draught and wealth, original "And become wealthy enough to rule Tolbi." Replacement "With that time, I built my fortune and came to rule." It makes Ivan speak as Babi. Restore original.
- 08944 drops the Stone of Sages' gold-transmutation property; 08965–08966 drop the explicit time estimate for the dwindling draught. Recommend original information.
- 08983 already said "I have built Babi Lighthouse" in the original, so that alone is not an Ashfall defect. 08984's original present-progressive question ("you're building") was changed to completed past tense ("You built"); restoring 08984 alone preserves the original distinction that construction is ongoing.

Lalivero (lalivero.c:543–719, Lalivero_IodemGivesBlackOrb; phase69):
- 10389 (Iodem): "We came back from Venus without [Jenna]. We couldn't find her." Iodem is addressing the party, not reporting himself as one of its members. Original is second person.
- 10390 (Garet): "And the lower passage was flooded, you say? You couldn't search it?" Garet witnessed the flooding. Original is first person and explains why they could not exit.
- 10391 (Iodem): "But we looked out to sea. There was a bank of mist that wouldn't move." The original has Iodem reminding the party of their promise to Babi.
- 10397 is Garet's Yes/No prompt: original "Then I guess we have no choice but to go..." The replacement "You gave Babi your word. I came to ask you to keep it." speaks as Iodem and no longer invites the same choice.
- 10398 (Iodem, Yes branch): original accepts the answer and arranges departure. Replacement "But Jenna is missing! Are we meant to sail without her?" incorrectly objects as a party member and hardcodes Jenna.
- 10399 (Iodem, No branch): replacement is nearly duplicated by the immediately following message.
- 10400 (Ivan): original "But...we have to find [Jenna] first..." Replacement "I would never ask you to abandon [Jenna]. Please, hear me out." Ivan speaks as Iodem.
- 10402 is the speakerless narration immediately after Actor_SetPosition(ACTOR_BLACK_ORB,...): original "Iodem takes out the Black Orb." Replacement "There's a way to cross these waters. Look closely." moves spoken dialogue into narration.
- 10403 (Mia): original "Oh, isn't that..." Replacement "Iodem draws a black orb from his robes." moves narration into Mia's dialogue.
- 10404 (Iodem): original "You will need it to sail Babi's ship." Replacement "The Black Orb! Does that control Babi's ship?" makes the person presenting it ask the question.
- Recommendation: restore the entire affected sequential block 10389–10404 from the original catalogue instead of patching individual sentences without their context. Keep all IDs, speaker calls, choices, and Black Orb item presentation intact. No changes made pending author review.

### Final voyage and ending

- lemurian_ship.c:349–476 preserves three original Yes/No questions and their respective Garet/Mia branches. Current phase57 dialogue retains the main objectives of finding Jenna and fulfilling the promise to Babi. Some responses change tone; do not treat as retired lore. Preserve gameplay branches and the original scene.
- world_map.c:2566–2670 preserves the drifting-island exchange, Alex's appearance and Felix/Sheba recovery. phase58 10534 changed Kraden's question "What is this? Alex, what happened?" to a third statement that Felix and Sheba are alive, after 10532 and 10533 already announce survival. This removes the question that creates the original ending's uncertainty and hardcodes the names; recommend restoring original 10534. No custom ending added.
- Suhalla 09737 changes "carrying the barrels exhausted us" to "The water ran out"; factual alteration of the soldiers' account, not a confirmed retired storyline. Recommend original if author wants faithful restoration.
- No new gameplay, character history, or map change. Full rendered-map and runtime verification, original event-by-event review of remaining NPC states, and release acceptance are still outstanding.

