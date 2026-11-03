# Ashfall Story Rewrite — Continuity Ledger

Status: working audit document  
Branch: `dark-story-rewrite`  
Scope: narrative chronology, story-state dependencies, and rewrite coverage  
Last audited revision: `2ed6097dd245e14c3c68e77dc16d104ec9aa79dd`

This document separates the original game's progression from Ashfall's custom events. Phase filenames are organizational labels, **not** a reliable chronological sequence.

## Working rules

1. Follow scene scripts, event triggers, and story flags rather than phase numbers.
2. Track the party's location, party members, completed events, known information, and active branch flags before writing a scene.
3. Rewrite all player-facing dialogue consistently: main cast, townspeople, merchants, guards, children, travelers, optional NPCs, Mind Read text, signs, and state-dependent variants.
4. Preserve message IDs, control codes, placeholders, branch behavior, and event structure. Respect the project's established text-box constraints.
5. Do not make a character respond to information they have not learned.
6. A successful build is not sufficient validation. Test event order, branch outcomes, dialogue states, and the final ROM.
7. Do not flatten every voice into grim exposition. Character and NPC dialogue should vary naturally with age, role, fear, grief, temperament, and understanding.

## Original-game progression: verified anchors

The following is the baseline route established by the original scene scripts. Ashfall may add encounters and revisits, but those additions must be mapped onto this route rather than inferred from phase numbering.

| Order | Location / event | Continuity requirement |
|---|---|---|
| 1 | Vale and Sol Sanctum | Establish the original party, the incident, and the initial journey. |
| 2 | Bilibin, Kolima, Tret, and Imil | Preserve the consequences of Tret's transformation and the Mercury Lighthouse journey. |
| 3 | Mercury Lighthouse | Its completion enables later Ashfall encounters. |
| 4 | Mogall Forest, Xian, and Altin | These belong to the original westward journey before the Lamakan crossing and Tolbi. |
| 5 | Lamakan Desert and the Manticore | The original route crosses the desert before Kalay and Tolbi. Ashfall's post-Mercury material adds separate encounters here. |
| 6 | Kalay | More than one story state exists. The first Hammet Palace visit occurs before Ivan reports to Layana; later dialogue and access change. |
| 7 | Karagol Sea crossing | Leads the party from Kalay toward Tolbi. |
| 8 | Tolbi and Colosso | Babi is missing during the tournament period; the party's discovery of him in Altmiller Cave is part of this sequence. |
| 9 | Altmiller Cave and Babi's return | Babi is found while Tolbi searches for him during Colosso. `FLAG_BABI_SAVED` is a key progression flag. |
| 10 | Colosso aftermath and Babi's audience | `FLAG_COLOSSO_OVER` and `FLAG_BABI_SPOKE_AFTER_COLOSSO` distinguish later palace and world states. Babi sends Iodem with the party toward Gondowan Passage. |
| 11 | Gondowan Passage and Suhalla | Suhalla has dialogue states before and after Babi's audience. The desert crossing with Iodem occurs after the audience. |
| 12 | Babi Lighthouse and Lalivero | Lalivero is visited before and after Venus Lighthouse, with different NPC and access states. |
| 13 | Venus Lighthouse and Aerie | The Aerie contains the confrontation, first battle, beacon lighting and second battle, followed by Sheba's peril and fall sequence. |
| 14 | Return to Lalivero | The party returns after the Aerie; Iodem's farewell and the Black Orb / wharf progression are part of the route onward. |
| 15 | Lemurian ship and ending | The ship's departure sequence is the game's final scene path; the ending continues beyond the Aerie battles. |


### Vale state map verified against `games/tbs/src/scene/vale.c`

Vale dialogue must be audited by visit state, not by phase-file number. The scene source documents four distinct states: (1) the opening roof-repair sequence at `VALE_FROM_TITLE`, three years after the storm, followed by `VALE_FROM_ROOF_MENDED` and Dora sending Isaac, Garet, and Jenna up Mt. Aleph with Kraden; (2) the pre-departure visit, when Jenna stops Isaac from sneaking up Mt. Aleph and the guard warns him, with the puppies removed only after the party meets Saturos and Menardi; (3) the post-departure state under `FLAG_VALE_PARTY_LEFT`, when Dora refuses to open Isaac's house and villagers discuss tremors and Kraden's absence; and (4) the return after `FLAG_KALAY_REACHED`, when Garet has reunion dialogue with his family, can ask them to protect Vale, and Dora is ill inside the cottage. The existing Vale phases contain dialogue for several of these states, but the complete NPC / Mind Read / conditional coverage and each message's actual trigger still need to be checked before any Vale section is marked complete.




### Bilibin / Gang of Three dialogue coverage repair
A follow-up source-to-phase check now finds all 67 distinct `MsgBilibin...` identifiers referenced in `bilibin.c` represented across the relevant Bilibin, Kolima/Imil, and riverbank phase files. This closes the named-message omission list for the Bilibin overlay; generic sequential dialogue blocks and each conditional state still need separate verification.


A source-to-phase comparison of `bilibin.c` found nine named Bilibin messages missing from the relevant rewrite batches. Restored them in `phase8_bilibin_a.tsv` and `phase21_bilibin_riverbank.tsv`: the tree-man's Mind Read (`05040`), McCoy's Treasury and barricade signs (`05230`, `05234`), the bottom tree's Mind Read (`05233`), the Bilibin well examination (`10717`), and the Gang of Three / Jill riverbank sequence (`06005`, `06010`, `06015`, `06016`). The Jill rescue sequence also had two unrewritten generic message rows (`06007`, `06009`); those are now included so the event's full dialogue block is covered.

The source trigger for `06015` and `06016` is conditional on `FLAG_BILIBIN_JILL_RESCUED`, meaning Jill has been pulled from the river and is present with the other two children after the curse is lifted. The old text said she was "gone" and implied she had died. The new lines instead acknowledge how close they came to losing her, without contradicting the rescue flag or her presence in the scene. The other two boys now recognize Isaac as the one who pulled Jill from the river, and Jill's offer and reward text are restored in the sequence. No event flags, rewards, or scene logic were changed.

### Kolima post-curse Mind Read: voice recovery

`games/tbs/src/scene/kolima.c` binds `MsgKolimaForAWhileIThoughtId` to Mind Read on the young man who speaks after `FLAG_KOLIMA_CURSE_LIFTED`. The previous text said he had "waited [his] whole life" to speak, although he could speak before the curse and was only temporarily transformed into a tree. It also repeated the same point as his spoken dialogue. The Mind Read now reads: "For a while, I thought I'd never speak again. I keep testing my voice, just to be sure it's still mine." This keeps the aftermath personal without implying he was born unable to speak.

### Bilibin and Imil state map verified against scene scripts

Bilibin's town, Treasury, and Barricade are separate scenes, not interchangeable versions of one visit. In town, `FLAG_KOLIMA_CURSE_LIFTED` controls the tree-man at the entrance, the villagers' dialogue/thoughts, and the return of the former tree-man. A later state begins only after `FLAG_SATUROS_BEATEN_AT_MERCURY`: travelers from Imil have crossed the river, and the Gang of Three / Jill river rescue has its own conditional state. Dialogue that mentions Mia or the Imil travelers must be checked against this later state rather than assumed to be available on the first Bilibin visit.

Imil's scene source confirms a separate progression: before Saturos is beaten at Mercury Lighthouse, villagers are sick or waiting for Mia, the weapon and armor shops are closed, and Mia is first met healing the old man in the couple's house. After Saturos is beaten, the lighthouse is lit, the fountain flows, the villagers and sellers are cured, and Mia's farewell to Megan and Justin plays on the first subsequent visit to the Sanctum. Some NPC lines also change while Mia is in the party. The audit must preserve all of these states, including the custom Mia/thieves interlude, without letting cured-village dialogue appear early.

## Ashfall custom-event placement

These are custom additions or altered encounters. They must be treated as revisits or branches where their event conditions say so.

| Existing phase file(s) | Content / placement note |
|---|---|
| `phase28_tolbi.tsv` | Tolbi dialogue coverage. Verify each message against its actual pre-Colosso, Colosso, or post-Colosso state. |
| `phase29_altin.tsv`, `phase31_altin_bread.tsv` | Altin-related material. Do not assume these files represent the first visit merely because of their names. |
| `phase30_tolbi_ash_jenna.tsv` | Later Tolbi Ash Jenna encounter; its event condition places it after Colosso and after Mercury Lighthouse is lit. |
| `phase32_imil_tolbi_kindness.tsv`, `phase33_kegare.tsv` | Optional kindness route and Kegare encounter-access gates. Preserve the underlying decision flags and conditional availability. |
| `phase34_mogall_lamakan.tsv`, `phase35_lamakan_jenna.tsv` | Mogall and Lamakan custom material. Verify each encounter's trigger and ensure Ash Jenna's later appearance acknowledges the earlier meeting. |
| `phase37_mia_tolbi.tsv`, `phase38_heart.tsv` | Mia's post-Tolbi recovery scene and the separate Heart cameo dialogue. Keep Heart and Kegare distinct. |
| `phase40_altin_peak_miners.tsv`, `phase41_altin_peak_mood.tsv` | Altin Peak rescue and aftermath. Preserve the rescue choice and the miner's subsequent condition. |
| `phase42_manticore_mia.tsv` | Mia's post-Manticore episode. This must follow the Manticore encounter and be reflected in later party dialogue. |
| `phase43_ivan.tsv` | Ivan's observations during Ash Jenna's confrontation and the Altin mine rescue. No supernatural hearing is part of the current story. |
| `phase44_miner_aftermath.tsv` | Altin Peak miner's ordinary recovery after the mine collapse and the choice to stay with him. |
| `phase47_finale.tsv` | Lamakan finale and Ash Jenna's major revelation. This is not the overall Golden Sun ending; it directs the party onward to Kalay. |
| `phase49_babi_palace.tsv` | 89 non-empty Babi's Palace message entries rewritten across pre-Colosso, Colosso, and post-Colosso states, including residents, Sheba-related dialogue, Mind Read, examinations, and event prompts. |
| `phase50_babi_scholars.tsv` | 19 Babi scholars' room entries rewritten, covering Alchemy, the Venus Ruins, the lighthouse, and Kraden's absence. |
| `phase51_suhalla.tsv` | 30 Suhalla town messages rewritten across the pre- and post-audience states, including villagers' dialogue and Mind Read. |
| `phase52_suhalla_interiors.tsv` | 44 Suhalla interior messages rewritten, including merchants, travelers, wounded soldiers, Mind Read, and environmental examinations. |
| `phase53_babi_lighthouse.tsv` | 38 Babi Lighthouse messages rewritten, covering workers, injured guards, Faran's pursuit, Sheba's rescue, the sealed door, and the ruins clue. |
| `phase54_lalivero.tsv` | 51 Lalivero town-map messages rewritten, covering Sheba's absence, the soldiers, the aftermath of Venus Lighthouse, and the wharf. |
| `phase55_lalivero_interiors.tsv` | 99 interior messages rewritten, including Sheba's family, town residents, Mind Read, wounded soldiers, Iodem, and the ship. |
| `phase56_black_orb.tsv` | 3 world-map messages rewritten for the Black Orb / Babi's ship interaction and optional shipwreck inspection. |
| `phase57_lemurian_ship.tsv` | 16 messages rewritten for the departure from Gondowan and the voyage toward Lemuria. |
| `phase58_true_ending.tsv` | 13 non-empty messages rewritten for the post-game drifting-island scene with Jenna, Kraden, and Alex. |
| `phase59_tunnel_ruins.tsv` | 8 Tunnel Ruins statue messages rewritten, preserving the lady/statue riddle and the four directional pillar clues. |
| `phase60_venus_lighthouse.tsv` | 25 Venus Lighthouse messages rewritten, including scholars, guards, relief inscriptions, statue dialogue, and the route clue. |
| `phase61_aerie_first_battle.tsv` | 121 Aerie messages rewritten for the first confrontation, Sheba's captivity, the Shaman's Rod bargain, and the first battle. |
| `phase62_aerie_beacon_fusion.tsv` | 64 Aerie messages rewritten for Felix's decision, beacon activation, Saturos and Menardi's return, and the fusion battle. |
| `phase63_aerie_fall_aftermath.tsv` | 64 Aerie messages rewritten for the collapse, Sheba's fall, Felix's sacrifice, and the party's return. |
| `phase64_babi_palace_small_sequences.tsv` | 48 sequential Babi Palace messages for Colosso prompts, rest scenes, and post-audience exchanges. |
| `phase65_babi_palace_iode_search.tsv` | 36 sequential messages for Iodem's account of the search for Babi at Altmiller Cave. |
| `phase66_babi_audience_part1.tsv` | 41 sequential messages for the audience, Colosso's reward, and the first Lemuria revelations. |
| `phase67_babi_audience_part2.tsv` | 40 sequential messages for the Draught of Lemuria and Babi's request to find the lost city. |




### Vale return visit: Cottage Rooms B correction and coverage check
A broader scan across eight Vale-related scene files (`vale.c`, `vale_kradens_cottage.c`, `vale_plaza.c`, `vale_stormy_night.c`, `vale_eruption.c`, `cottage_rooms_a.c`, `cottage_rooms_b.c`, and `vale_cave.c`) initially appeared to find one missing early-game line: `MsgValeTheHealersAreSupposedToGuard` (message `07307`), a Mind Read thought on the strongman in Garet's family's house after Kalay. A global phase search then found it already present in `phase2_sanctum.tsv`, despite that file's misleading name. The attempted duplicate in `phase15_vale_revisit.tsv` was removed after the validator caught it. This is a useful example of why coverage must be checked across every phase file, not inferred from filenames. The four remaining unmatched named messages belong to the later Babi scholars' room, not early Vale.


The after-Kalay inn scene in `games/tbs/src/scene/cottage_rooms_b.c` identifies `MsgValeYouveGrownSoMuch` as the inn patron's observation that Isaac has grown so much he is nearly unrecognizable. The rewrite had changed this to "You've grown thin," which altered the meaning and introduced an unnecessary comment on Isaac's body. Message `07187` in `phase15_vale_revisit.tsv` has been restored to "You've grown so much. I almost didn't recognize you."

A source-to-phase name check found all 67 distinct `MsgVale...` identifiers referenced in `vale.c` among the four Vale phase files (`phase1_vale`, `phase2_vale`, `phase5_vale_departure`, `phase15_vale_revisit`). This is a useful named-message coverage check, not proof of complete dialogue coverage: generic `message` entries, cottage-room scenes, Mind Read variants, and sequential branches still need separate trigger-by-trigger verification. Three `MsgVale...` identifiers in `cottage_rooms_b.c` belong to the later Babi scholars' room and are not early Vale omissions. The source also documents legacy events that no trigger table reaches; these must not be mistaken for missing playable dialogue.

### Sol Sanctum first-visit correction

The first-entry sequence in `games/tbs/src/scene/sol_sanctum_entrance.c` explicitly asks whether this is the party's first time inside Sol Sanctum. Kraden's event then has him explain that he has heard of a hidden passage, reflect on how the Sanctum differs from what he imagined, and question the absence of sunlight in a place built to honor the sun. The former `04056` line claimed, "I've walked these halls for years," contradicting both the first-visit question and the scene's event sequence. It has been corrected to say that Kraden has studied the Sanctum's history for years but has never stood inside it until now. `04060` now refers to the contradiction bothering him for years, making clear that his prior knowledge came from study, not repeated visits. No scene logic was changed.
The same first-visit prompt has a conditional response: the scene comment documents Kraden's response to a "no" answer as "I doubt that..." The former `04053` began "Of course not," which read as agreement with a claim that the party had visited before. It has been revised to "I doubt that. Few people have ever been allowed inside," preserving the branch's intended meaning. The yes/no branches remain intact.


### Heart / Chalice cameo in Kolima

Heart is Chalice from *Golden Sun: Dark Dawn*, using her Japanese name as in the sprite animation. Her characterization is not that of a newly invented alternate-world antagonist. In the sprite-animation continuity, the Dark Dawn world is destroyed; Tuaparang escapes that destruction and continues observing events from the shadows while pursuing its own plans. Heart is a powerful Dark Adept whose earlier defeat by Matthew taught her not to leave her abilities unused. The Kolima encounter must preserve those facts without turning her into an exposition device or revealing Tuaparang's full plans.

`phase38_heart.tsv` has been revised accordingly: Heart recognizes Matthew's resemblance in Isaac, explains that she previously held back her full power, establishes that she came to observe this world, and challenges the party without holding back. After defeat, she recognizes Isaac is not Matthew, identifies herself as Heart and a member of Tuaparang, confirms that her people escaped their world's destruction, and leaves Tuaparang's purpose undisclosed. The Kolima scene comments were corrected to match this characterization. The existing battle/event flow and reward have not been changed. The apparently unrelated `ENCOUNTER_ZONE_SCRIPTED_MIA_MENARDI` name is a legacy shared zone: `games/tbs/src/overworld/encounter_zones.c` explicitly documents slot 3 as Heart's Kolima battle. Sprite presentation and in-game timing still require separate validation.

## Current rewrite batch summary

Phases 49–67 now contain **849 rewritten source-message entries**: Babi's Palace and scholars plus the sequential audience/search blocks (273), Suhalla and its interiors (74), Babi Lighthouse (38), Lalivero and its interiors (150), Black Orb interactions (3), Lemurian ship departure (16), post-game ending (13), Tunnel Ruins (8), Venus Lighthouse (25), and the Aerie (249). The 165 entries in phases 64–67 restore sequential Babi Palace dialogue; the expanded Aerie files now include the previously omitted exchange lines. These rows have passed the repository dialogue validator and the modified-edition build. **This is not yet complete scene coverage:** remaining NPC, Mind Read, examination, conditional, and sequential branches still require source-to-phase review before any location is marked complete. In-game progression checks also remain pending.

### Important custom-state observations

- Ash Jenna has at least two distinct encounters: the Lamakan revelation and the later Tolbi confrontation. Dialogue must acknowledge the earlier meeting.
- The post-Mercury custom events are gated by story conditions; their phase numbers do not mean they occur before the original Altin or Lamakan visits.
- The Lamakan confrontation recalls the miner recovery choice, but that choice does not determine Isaac's response to Ash Jenna's offer.
- The Tolbi Ash Jenna encounter is a later event, gated by Colosso being over and Mercury Lighthouse being lit.
- Kegare's appearance is conditional. Do not write her as a guaranteed encounter for every playthrough.

## State-dependent original scenes that must remain distinct

### Kalay

The first visit to Hammet Palace occurs before `FLAG_IVAN_REPORTED_TO_LAYANA`. Guards recognize Ivan and take the party to Lady Layana. Later dialogue differs. The Colosso tour group and the tunnel access also have separate conditions. After Hammet is returned from Lunpa, Layana opens the tunnel.


### Vault revisit: Colosso chronology correction
A named-message coverage scan across `vault.c`, `vault_revisit.c`, `stone_rooms.c`, `log_rooms_a.c`, `log_rooms_b.c`, and `vault_cave.c` found 233 distinct message identifiers, all represented in the six Vault phase files (`phase2_vault`, `phase5_vault_a/b/c`, `phase20_vault_leftovers`, and `phase6_gaps`). This verifies named-ID presence only; sequential `message` offsets, branch responses, Mind Read state changes, and post-Kalay revisits still require a trigger-by-trigger content audit.


The Vault return sequence is selected only after `FLAG_KALAY_REACHED` (`vault.c` routes the party into `vault_revisit.c`). Its houses use `log_rooms_b.c`, where the source comment for `MsgVaultThePrisonersSaidTheyWantedTo` explicitly says the prisoners wanted to break out before Colosso began. The rewrite had changed this to a "war in Tolbi" and described Colosso as a blood pit where people bet on survival. That invented a war and distorted the source event: Colosso is the tournament the prisoners wanted to attend. Message `07372` in `phase20_vault_leftovers.tsv` now says they begged to be let out before Colosso began because even thieves wanted to see the tournament. No scene flags or event logic were changed.

### Babi's Palace

The script documents separate pre-Colosso, Colosso, and post-Colosso dialogue states. Sheba's captivity, the soldiers' search, and the audience with Babi must not be collapsed into one state. `FLAG_COLOSSO_OVER` and `FLAG_BABI_SPOKE_AFTER_COLOSSO` are essential distinctions. The Babi's Palace batch currently rewrites 89 named palace messages, with a further 19 scholars' room entries in `phase50_babi_scholars.tsv`. A separate source audit of the later scholars' room in `cottage_rooms_b.c` found four additional unrewritten message groups: the `MsgValeFolksSeemKnow` question/answer sequence and three bookcase examination messages (`MsgValeTheresABookEntitledEncyclopediaOf`, `MsgValeTheresANotebookEntitledExperimentsIn`, and `MsgValeTheresANotebookEntitledStudyOf`). These belong to the Babi Palace scholars' visit, not early Vale, and must be added to the later scholars batch. A source-code pass has since identified large sequential blocks beginning at `MsgTolbiGetUp`, `MsgTolbiLikeSleep`, `MsgTolbiIodemIodem`, `MsgTolbiCallsName`, and `MsgTolbiWaitingCompanions`, plus smaller question/answer sequences. These additional lines are not yet covered; the 89+19 count is partial.

### Suhalla

Before `FLAG_BABI_SPOKE_AFTER_COLOSSO`, villagers discuss the sandstorms, Angaran distrust, and Sheba's hostage status. After the audience, their dialogue reflects soldiers caught in the storms on the way to Babi Lighthouse. The party crosses the desert with Iodem after Babi's audience. The town rewrite currently covers 30 named messages. Its interiors have a further 44 named messages across the pre- and post-audience states; `FLAG_IODEM_MET_WOUNDED_SOLDIERS` and `FLAG_BABI_LIGHTHOUSE_IODEM_ARRIVED` distinguish the wounded-soldier and Iodem-arrival dialogue. The 38-message Iodem sequence beginning at `MsgSuhallaIodem` in `timber_rooms_a.c` is additional and still needs coverage.

### Lalivero

The first visit occurs with Iodem; townspeople discuss Sheba's capture, injured soldiers explain where her captors went, and the wharf guard blocks access. After Venus Lighthouse, the party returns. Iodem's farewell and the Black Orb handover lead to the wharf opening. Preserve the relevant conditions, including `FLAG_VENUS_LIGHTHOUSE_PARTY_RETURNED`, `FLAG_IODEM_FAREWELL_SEEN`, `FLAG_SAW_SHIP_AT_IDEJIMA`, and `FLAG_LALIVERO_WHARF_OPEN`. The current draft covers 51 named town-map and 95 named interior messages, but four sequential event blocks beginning at `MsgLaliveroMoreTolbisSoldiersLayDefeated`, `MsgLaliveroWhereGoingIsaacIodemAsked`, `MsgLaliveroBabiToldMeShipAncients`, `MsgLaliveroThoughtShipWeSawAt`, and four interior sequences beginning at `MsgLaliveroImSorry`, `MsgLaliveroHowDidSearchForSheba`, `MsgLaliveroDoNotWorryAboutSheba`, and `MsgLaliveroTellOthers` still need to be audited and rewritten.

### Babi Lighthouse and Tunnel Ruins

Babi Lighthouse currently has 38 named messages covering its workers, guards, Faran's pursuit, Sheba's rescue, and sealed-door sequence. Two sequential event blocks beginning at `MsgBabiYoureSureTheyWentThrough` and `MsgBabiTheDoor` add approximately 59 more messages and still need coverage. Keep `FLAG_BABI_LIGHTHOUSE_DOOR_SHOWN`, `FLAG_BABI_LIGHTHOUSE_DOOR_OPEN`, `FLAG_BABI_LIGHTHOUSE_ASKED_TO_FOLLOW`, `FLAG_BABI_LIGHTHOUSE_BACK_FROM_STONE_DOOR`, and `FLAG_BEYOND_DOOR` distinct. Tunnel Ruins has 8 rewritten riddle and pillar messages; its `FLAG_TUNNEL_RUINS_STATUE_DOOR_OPEN`, `FLAG_VENUS_LIGHTHOUSE_FIRST_PATH`, `FLAG_VENUS_LIGHTHOUSE_SECOND_PATH`, pillar-placement, douse, and freeze flags must be tested against the puzzle sequence.

### Venus Lighthouse and Aerie

Venus Lighthouse has 25 rewritten messages across the approach and four floors, including scholars, guards, the relief inscription, the statue's message, and the route clue. Preserve its pillar, wall, gate, socket, switch, and `FLAG_VENUS_LIGHTHOUSE_LIT` states. The Aerie has 209 rewritten messages split across three phases: first confrontation and battle, beacon activation and fusion battle, and the collapse / Sheba fall aftermath. Keep `FLAG_AERIE_FIRST_BATTLE_BEGUN`, `FLAG_AERIE_SECOND_BATTLE_BEGUN`, `FLAG_VENUS_AERIE_FUSION_SLIDING`, `FLAG_VENUS_AERIE_FUSION_GROWING`, `FLAG_VENUS_AERIE_BEACON_ERUPTED`, `FLAG_VENUS_AERIE_PARTY_LIFTED`, and `FLAG_VENUS_LIGHTHOUSE_PARTY_RETURNED` distinct. The sequence is drafted, but build, battle-state, and in-game route validation remain pending.

### Ending

The world-map ending and Lemurian ship departure are separate from the Aerie event. The world-map script documents the ending after the cleared game is saved; the Lemurian ship departure sequence leads into the final scene path and return to the title. Drafts now cover 3 Black Orb / ship-world-map messages, 16 Lemurian ship departure messages, and 13 post-game ending messages. The sequence still requires build and in-game validation.

## Coverage status

The current rewrite directory contains phase files through `phase63_aerie_fall_aftermath.tsv`. Drafted dialogue coverage does **not** establish a successful build or complete in-game validation.

| Area | Audit status |
|---|---|
| Early game through Mercury Lighthouse | Existing phase files present; comprehensive NPC / Mind Read / branch coverage still needs verification. |
| Post-Mercury custom encounters | Existing phases present; event-order and callback audit in progress. |
| Kalay / Karagol / Tolbi / Altmiller / Colosso | Original progression verified in scene scripts; Ashfall message-by-message coverage remains to be checked. |
| Babi's Palace and scholars' rooms | Source-message rewrite drafted (89 + 19 entries); automated build and in-game state validation pending. |
| Babi's audience / Gondowan Passage | Partial. Named messages are drafted, but the long Iodem/Babi audience and other sequential message blocks remain. |
| Suhalla / desert / Babi Lighthouse | Partial. 30 Suhalla town, 44 named interior, and 38 named Babi Lighthouse messages are drafted; the 38-message Iodem sequence and 59-message Babi Lighthouse sequences remain. |
| Lalivero first/second visit and interiors | Partial. 51 named town and 95 named interior messages are drafted; 62 town-map and 59 interior sequential messages remain. |
| Black Orb / Lemurian ship / true ending | Drafts exist for 3 Black Orb, 16 ship, and 13 post-game ending messages; sequence and in-game validation pending. |
| Tunnel Ruins / Venus Lighthouse / Aerie | Drafts exist for 8 Tunnel Ruins, 25 Venus Lighthouse, and 209 Aerie messages; puzzle, battle, and post-fall state validation pending. |

## Known caution items

- `phase13_menardi_aerie.tsv` is currently only a tiny stub; inspect before treating it as meaningful coverage.
- Do not infer a missing scene from a missing phase file alone. First inspect the game's text tables, scene triggers, and the existing rewrite tooling to identify the actual source messages.
- Do not rename or reorder existing phase files merely to make their numbering look chronological. Document the actual chronology separately.
- Do not invent new story flags or alter event logic as a shortcut to narrative continuity.
- Before editing a dialogue batch, capture its source message ID, original text, scene, trigger condition, and any state variants. Then validate text length, control codes, and branch completeness.

## Next audit actions

1. Inventory the game's text data and determine how the current TSV phase files are applied. **Done.**
2. Build a source-message coverage index for every late-game scene listed above. Draft batches now cover Babi's Palace, scholars' rooms, Suhalla, Babi Lighthouse, Lalivero, the Black Orb, the Lemurian ship, the post-game ending, Tunnel Ruins, Venus Lighthouse, and the Aerie; validate them before marking coverage complete.
3. Audit custom branch flags and callbacks against their event scripts.
4. Rewrite the missing sequential event-message blocks first: Babi Palace / Iodem's audience, the Suhalla Iodem scene, Babi Lighthouse, and Lalivero / Iodem's departure. Then audit world-map transitions and optional NPCs before running the full validator, build, and in-game route checks.
5. Run the existing rewrite/build tooling and inspect the resulting ROM in-game across representative branches.
6. Extend this ledger as each area is verified; mark coverage complete only after source-message comparison and in-game validation.


### Vale stormy-night prologue: source-led event and branch audit

A direct read of `cottage_rooms_b.c` and `vale_stormy_night.c` confirms the playable order behind `phase1_vale.tsv`. The opening is not one uninterrupted cutscene: Dora wakes Isaac upstairs, the tunic interaction is its own choice, Kyle calls them downstairs, and the fire/smoke effect plays as they leave for the plaza. The storm map then advances through four separately flagged rockfalls. The shoving man, Garet's chest, and Garet joining Isaac are distinct interactions; Garet's chest choice does not prevent him from joining.

The river sequence has additional state and optional dialogue that must remain distinct. The elders' Boulder event leads the boys toward the plaza; the party then encounters Felix clinging in the river with Kyle, Dora, Jenna, and Jenna's parents. The first river event includes Kyle's repeated greeting state, while the rescue conversation contains two consecutive yes/no prompts. In `ValeStormyNight_DoraGoesForHelp`, the first prompt uses the consecutive entries beginning at `MsgValeGoLookNorth` (the `+4` and `+5` responses), and the second uses the three-entry block beginning at `MsgValeDontSupposeTwo`. The branches are not interchangeable: the event sends Jenna toward the plaza, sends Dora north for help, and either sends Isaac and Garet after Jenna or lets them head to the plaza. The later Kyle interaction also changes after `FLAG_VALE_STORM_KYLE_GREETED_ISAAC`; the repeat line is `MsgValeTwoDontEnough`.

After the party has gone to aid the elders, the Boulder-swept-downriver event reunites Isaac, Garet, Jenna, and the exhausted strongman with the riverbank group, then carries Felix, his parents, and Kyle away. The script's flag `FLAG_VALE_STORM_BOULDER_SWEPT_THEM_AWAY` gates later dialogue and the post-event state. These details are important when reviewing the phase's emotional beats: the party does not witness every part of the disaster in a single scene, and the dialogue must respect which characters are present and which events the player has actually seen.

This pass confirms the event order and the existence of the branch/state distinctions; it does **not** certify every message in `phase1_vale.tsv`. The full message-by-message pass still needs to match every sequential offset, talk trigger, Mind Read/examination entry, optional interaction, and post-flag variant to its exact speaker and runtime state. No scene logic was changed in this audit.


### Lamakan-to-Tolbi continuity failure audit

A source-backed audit records the pre-repair continuity failures. The normal post-Manticore return now runs Mia's emotional aftermath and then Ash Jenna's full revelation/finale before the party proceeds to Kalay. The discarded caravan sequence and its choice are not part of the current story. The shorter N106–N110 Lamakan watch exchange is an optional conversation on the Manticore pass, distinct from that automatic return sequence. The later Tolbi encounter follows the guaranteed Lamakan revelation and has now been rewritten as a continuation.

Kegare has two encounter-access routes: sheltering the harbor child, or completing all three Altin/Imil/Tolbi kindness payments. Those conditions are access gates only; they do not explain her origin or motive. Her dialogue now centers on deliberately mimicking Mia and intending to replace her, without falsely claiming Isaac rescued the child. The fishermen question has been removed, and the harbor child remains a separate Ashfall thread. Lamakan NPC text now matches the desert's source-defined sand/heat mechanics.

See `docs/ashfall-lamakan-tolbi-continuity-repair.md` for the verified event order, trigger behavior, and repair record. The initial audit did not change event logic; subsequent dialogue corrections are recorded below.


### Canonical correction: Kegare cameo super boss

The character previously named Ondra is **Kegare (穢れ)**, meaning impurity/defilement. Per the user's sprite-animation continuity, Kegare deliberately mimics Mia and ultimately intends to replace her. She is a cameo super boss from that wider continuity, in the same broad cameo category as Heart, not a native Golden Sun sea goddess or a benevolent entity created by kindness.

The earlier Tideglass Queen / shared-tide explanation is noncanonical and must be discarded. Child-rescue and three-kindness flags, if retained, are encounter-discovery/access conditions only; they do not explain Kegare's origin or motive. The harbor child is a separate story thread unless a coherent connection is established independently. Keep Kegare and Heart distinct. Her dialogue should emphasize unsettling imitation and replacement while keeping her full origin restrained enough that she remains a cameo rather than taking over Golden Sun's main plot. See `docs/ashfall-lamakan-tolbi-continuity-repair.md` for the superseding character definition and revision requirements.

### Cameo superboss balance requirements

Both Heart and Kegare are intended to be difficult but fair optional superbosses. Their current enemy definitions need a balance pass before their encounters are considered complete.

- **Kegare:** a powerful Water Adept who deliberately imitates Mia. Her battle kit must include the strongest appropriate Water-element Psynergy available to an enemy in this game's ability table, and she must have access to **Ply**. The exact offensive set should create varied pressure rather than rely on repeated high-damage actions. Her healing must prolong the fight without making progress feel futile. Her stats and level must be calibrated to the party's realistic progression at the Tolbi encounter, not simply inflated because she is a superboss.
- **Heart:** the current definition is overtuned for a Kolima cameo encounter: level 55, 9,999 HP, 999 PP, 520 attack, 190 defense, 200 agility, and two actions per turn. Reassess all of these together, including her ability set and action strategy. Preserve a distinctive, threatening fight, but make victory realistically achievable through preparation, sound party composition, and tactical play.
- **Shared fairness standard:** neither boss should require extreme overleveling, luck-based resets, exploits, or an effectively endless healing loop. Evaluate damage output, survivability, healing frequency, speed/action economy, elemental matchup, and the expected party level/equipment at the actual unlock point as one encounter. Do not copy the same difficulty profile onto both bosses: their identities and battle roles should remain distinct.
- **Validation:** do not call either fight balanced based on a code build alone. Record the expected progression point and test the encounter with plausible party levels and equipment. Confirm that the battle can be won consistently with a reasonable strategy while still punishing careless play.

### Simplified Mia arc: no sentient Tideglass Blade

The sentient Tideglass Blade storyline is retired. It introduced an unnecessary second mythology (a voice in the weapon, influence/possession of Mia, a transfer decision for Isaac, and a separate mercy condition) that distracted from the Ashfall conflict.

Canonical direction going forward:

- Mia's behavior after the Manticore is an emotional response to what the party has witnessed and the anger and strain she is carrying. She briefly speaks more harshly than she intends, recognizes it, and remains accountable for it. There is no second self, possession, weapon voice, or loss of memory.
- Ash Jenna is the antagonist who deliberately recognizes and exploits Mia's vulnerability. Her taunts are personal and cruel, but they do not reveal a supernatural connection between Mia and Jenna.
- Isaac and the party support Mia. The Tolbi follow-up is a short character scene about being unsettled and choosing not to let Ash Jenna define her; there is no weapon-transfer choice.
- The Tideglass Blade is not a sentient artifact and must not be the cause of Mia's behavior, a branching ending condition, or an explanatory link to Kegare.
- The finale's mercy count is based only on the miner-stayed and Mogall-door-opened choices. The discarded caravan sequence and retired blade decision are not counted.
- Existing ordinary weapon terminology in unrelated original-game dialogue is unaffected. This correction removes the custom sentient-weapon plot, not the game's ordinary swords or battle equipment.

### Current superboss balance pass

The first numerical rebalance is in place, pending encounter testing:

| Boss | Level | HP | PP | Attack | Defense | Agility | Actions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Heart | 38 | 3,600 | 240 | 300 | 130 | 140 | 1 |
| Kegare | 33 | 4,200 | 300 | 285 | 125 | 145 | 2 |

Kegare's current enemy ability set uses Ice Missile, Freeze Prism, Deluge, and Froth Spiral as her strongest varied Mercury-element attacks, supported by Water Blessing and Ice Blessing, plus Ply and Pure Ply. Her role is a Water Adept: pressure through powerful water/ice Psynergy and measured healing, not an endless recovery loop. Heart keeps her own ability identity but no longer has 9,999 HP, 999 PP, 520 attack, 190 defense, 200 agility, or two actions every turn.

These values are a first balance target, not a claim that the fights are fully validated. The encounter unlock points and realistic party levels/equipment must be used for testing. Adjust further if either fight proves unfair or trivial in play.



### Current continuity repair pass — November 2026

The post-Lamakan Tolbi encounter has been revised in `phase30_tolbi_ash_jenna.tsv`. Ash Jenna recognizes the party from Lamakan and continues her warning about the Wise One and the next lighthouse. The former sleeper/harbor thread is no longer part of the scene. Mia acknowledges her anger after the Manticore without accepting Ash Jenna's attempt to define her by it. The Tolbi event sequence and flags remain unchanged.

The contradictory mud / flood wording in `phase34_mogall_lamakan.tsv` has also been removed. The dialogue now describes the actual source-defined sand, heat, dust, and ash-thick air of Lamakan; no environmental or heat-hazard logic was changed.

Kegare's former Ondra source identifiers and dialogue filename have been renamed to Kegare. Her encounter-access conditions remain unchanged and are not presented as the source of her origin or motive. Her current moveset now contains the four highest-power appropriate Mercury Psynergy attacks in the table (Ice Missile, Freeze Prism, Deluge, Froth Spiral), both Water/Ice Blessings, Ply, and Pure Ply. Her two-action turn structure remains unchanged. Run 354 passed the full build-and-patch workflow on its tested commit. Subsequent Aerie sequential-dialogue additions are covered by run 358, which passed dialogue validation, modified-edition compilation, baseline verification, IPS generation, and test-patch upload. A code build alone does not constitute boss-balance testing or in-game progression verification.

### Current late-game source-to-phase audit — 2 November 2026

This section supersedes the older late-game coverage counts and the earlier next-action list above. The branch now contains dialogue batches through `phase70_lalivero_interior_sequences.tsv`. Phases 49–70 contain **1,087 unique replacement rows** in total: 756 across phases 49–63 and 331 across phases 64–70. The dialogue validator rejects duplicate IDs across the batch, so this is a count of distinct replacement entries, not a count of scene visits.

The Babi Palace and surrounding sequences have advanced beyond the earlier partial status:

- `babi_palace.c`: all 93 distinct named message references found in the scene are represented across phases 49 and 64–67. The four sequential Babi Palace batches now contain 175 rows (52, 42, 41 and 40).
- `cottage_rooms_b.c`: the later Babi scholars' room had six missing entries. Added the Kraden question and both responses (08889–08891), plus the three bookcase examinations (10679–10681), to `phase50_babi_scholars.tsv`. Phase 50 now contains 25 rows. These are player-facing dialogue and examination text; no scene logic or flags changed.
- `babi_lighthouse.c`: all 40 distinct `MsgBabi...` references are represented in phase 53. The sequential sealed-door event is also covered: every message ID from 09986 through 10070 is present (85 entries). `MsgFieldFlippedSwitch` is a shared system message, not a missing Babi-specific line.
- `suhalla.c`: all 30 distinct named message references are represented in phase 51. The 44 interior references in `timber_rooms_a.c` are represented in phase 52, and the separate 38-message Iodem / wounded-soldier sequence (09707–09744) is represented in phase 68.
- `lalivero.c`: all 51 distinct named message references are represented in phase 54; the 62-row town sequence is in phase 69. The 59-message interior sequence (10320–10378) is fully represented across phases 55 and 70, with no missing IDs in that range.
- `venus_lighthouse_aerie.c`: all eight distinct named message references are represented across phases 61–63. The Aerie draft remains subject to event-order, battle-state and in-game checks.

A source-to-phase scan also surfaced several shared messages used by more than one scene: `MsgInnWelcome`, `MsgSuhallaNowhereFound`, `MsgGomaNoUsePsynergy`, `MsgValeWoodenBoxEmpty`, `MsgVaultIsaacCheckedChest`, and `MsgGotPsynergyStone`. These must be checked against the complete phase index before being treated as omissions; shared system text should not be rewritten blindly. The same applies to shared field text such as `MsgFieldFlippedSwitch`.

The commit adding the six Babi scholars entries is `1719d5e345ad3e8ca314b48138c28f98616b8ab6`. Workflow run 396 has passed the dialogue-validation step; the pinned toolchain build and modified-edition compilation were still in progress at the time of this note. Do not call the patch build-verified until that run completes successfully.

### Next audit actions

1. Resolve the shared-message list above against all phase files. Rewrite only those shared lines that are genuinely missing and whose player-facing meaning warrants a replacement.
2. Continue source-to-phase review of optional NPC dialogue, Mind Read, examinations, conditional actor tables and post-flag variants for Tolbi through the Lemurian ship. Named-message presence alone does not prove that every branch or sequential offset is covered.
3. Audit the story flags and callbacks in phases 28–70 against the actual scene scripts. In particular, keep pre-/post-Colosso, pre-/post-audience, first-/second-visit Lalivero, Aerie battle/fall, and Black Orb/ship states distinct.
4. Run the dialogue validator and build after each edit batch. Then test the resulting IPS in-game across representative branches, the Venus Lighthouse puzzle, both Aerie battles, the Sheba aftermath, the Black Orb departure and the post-game ending. A successful compile is not proof of correct progression or balance.



### Suhalla Gate checkpoint dialogue coverage — 2 November 2026

A dedicated phase71_suhalla_gate_checkpoint.tsv now covers nine previously absent named dialogue references from games/tbs/src/scene/suhalla_gate.c: travel papers (09805), the Babi Lighthouse question (09806), the soldier obeying Babi's orders (09810), the Colosso spectator (09811), Iodem's confrontation (09812), the wounded soldier asking for help from the Lighthouse (09831), the injured Colosso victor (09832), the guard ashamed before Iodem (09833), and the surviving guard's account of the attack (09834).

The lines were rewritten against their original English text and the source event sequence. In particular, the post-audience scene is still Iodem questioning his wounded guards after the attack; it does not imply that the party has already reached Babi Lighthouse. The original game question about Felix and the subsequent Iodem dialogue remain in their source-defined sequence; no scene logic, flags, actor placements, or event ordering were changed.

The shared MsgGotPsynergyStone (02416) was deliberately not included: it is not a Suhalla Gate-specific line and must be resolved against the full phase index before any shared-text rewrite. The checkpoint's unnamed sequential message offsets also remain a separate branch-level audit item. This addition has not yet been validated by GitHub Actions or tested in-game; run the dialogue validator and full build before calling it technically verified.


## Focused characterization and continuity repairs

The following targeted revisions address issues found during the dialogue audit:

- Menardi's early duel no longer gives Saturos an unestablished childhood history. His reply now responds to the immediate danger posed by Isaac's party.
- Ash Jenna's Lamakan taunt now identifies the Mercury beacon as the one Isaac failed to stop and refers to the party pursuing the lighthouse sequence, rather than implying Isaac is lighting the beacons.
- Mia's post-Tolbi exchange now moves from recognizing Ash Jenna's deliberate attack to choosing how Mia will respond. Her divided-finale branch now states why she leaves: she cannot keep waiting for a solution that has not come, and chooses to act alone.
- Ivan no longer has supernatural hearing or a connection to a Bloom. His lines now reflect ordinary observation and urgency during the mine rescue.
- Heart's post-battle explanation retains the Tuaparang and lost-world revelation but stops short of explaining the faction's purpose or history.

The Lamakan confrontation now uses a single accept/refuse choice for Ash Jenna's offer. The miner's recovery choice is remembered only as a character callback. Mia remains with the party regardless of that earlier choice; the old Mogall-door mercy calculation and Divided departure are gone. The event message index advances between each speaker, so the consecutive branch message IDs are intentional.


## Canonical decision: remove the Bloom and its dependent storyline

The Bloom, awakened/sleeper mythology, and supernatural voice-hearing plot have been removed. They are not part of the current Ashfall story and must not be restored during later dialogue or scene work.

The Mogall camp/keeper sequence and its Alex encounter have been removed. Alex's custom Mogall and Altin Peak appearances were also removed because they existed to explain or reinforce the Bloom plot. The broken Mogall sign no longer carries the unexplained warning about lights being awake.

Altin Peak's trapped-miner encounter remains, but it is now a conventional mine-collapse rescue. The men are trapped by a failed support structure and rising water; there is no transformation, grey-eyed state, or supernatural aftermath. After the rescue, Isaac may stay with an injured miner while he recovers. This choice is remembered in the Lamakan confrontation but does not determine the party's ending.

Ash Jenna's motivation has been simplified. She is a Jenna from a world she says the Wise One destroyed, and she wants Isaac's help confronting him. The Lamakan scene presents this as her account and her offer, not as an objective explanation of a new supernatural system. The Tolbi encounter continues that conflict without sleepers, awakened people, harbor voices, or lighthouse doors.

Isaac now makes one clear choice: accept or refuse Ash Jenna's offer. Mia does not abruptly abandon the party because of the miner decision. The old Bloom branch, Mogall door mercy flag, supernatural Ivan dialogue, and divided-ending departure have been retired.


## Final editorial review — opening to ending (2 November 2026)

This is a narrative editorial assessment of the existing rewrite text, **not** certification that every scene, branch, and event trigger has been playtested. The source-defined chronology and state maps above remain authoritative.

### Story spine and editorial priorities

1. **Vale storm and departure (phase1, phase2, phase5):** The storm's urgency and the family stakes are effective. Protect the contrast between ordinary family warmth and sudden catastrophe. Several departure NPCs deliver similar warnings or hopes; vary their concrete concerns instead of repeating "come home" or "be careful." Preserve all alternate answers and revisit flags.
2. **Sol Sanctum (phase2_sanctum):** Kraden's curiosity and the party's caution are established, but puzzle exposition sometimes repeats what the player has just observed. Keep clues that guide gameplay; trim only redundant explanation after checking message triggers and control tokens. The first discovery should feel dangerous as well as wondrous.
3. **Bilibin / Kolima / Imil / Mercury:** The strongest throughline is harm to ordinary people followed by partial recovery. Ensure Mia's compassion and responsibility are shown in action rather than delivered as repeated moral statements. Keep cursed/cured and pre-/post-Mercury dialogue states distinct.
4. **Mogall / Xian / Altin / Lama / Lamakan:** The geographical order is established above. Avoid reintroducing the retired Bloom, supernatural hearing, or Mogall Alex scenes. The miners' recovery and Ash Jenna's warnings must not imply the same causal mechanism. Hama's Reveal scene should preserve the desert's mechanical instructions while allowing Ivan a recognizable voice.
5. **Kalay / Tolbi / Colosso / Babi:** Babi's urgency is understandable but should not erase his responsibility for the cost borne by workers and Lalivero. Distinguish the period when Babi is missing from the later audience. Keep the optional kindness/miner callbacks subordinate to the main plot.
6. **Suhalla / Babi Lighthouse / Lalivero:** The soldiers and civilians have increasingly specific perspectives. Review repeated descriptions of Sheba as a savior and avoid allowing certainty of her survival before anyone has evidence. The first and return visits to Lalivero must not share post-beacon knowledge.
7. **Venus Aerie (phases61–63):** Highest-priority substantive revision. The confrontation currently devotes many consecutive exchanges to Felix's custody of Sheba and the Shaman's Rod; preserve the actual bargain and battle triggers, but sharpen Saturos and Menardi's tragic mission without inventing revelations the protagonists cannot yet know. Check the early beacon-order exchange (10071–10074): the line about Jupiter being last and Mars being 'before it' is ambiguous and needs comparison with original event meaning before editing. Avoid treating their deaths as a triumphant moral resolution.
8. **Aerie fall and aftermath (phase63):** Separate the emotional beats of victory, the beacon lighting, Sheba's fall, Felix's leap, and Jenna's continuing absence. Current 10301 ('I forgot about Jenna') risks making Garet seem callous after the crisis; revise carefully with original speaker and branch context. Preserve the physical escape/puzzle state and all conditional replies.
9. **Return to Lalivero / Black Orb / ship / ending (phases54–58, 69–70):** The new Iodem, Faran, ship and epilogue dialogue better preserves uncertainty. Avoid implying that Jenna is definitively safe. Keep the Idejima ship distinct from Babi's Lemurian vessel, and retain the promise to seek Lemuria as a separate obligation.
10. **Ash Jenna (phases35, 47 and related custom encounters):** Her claim about the Wise One is testimony from a damaged alternate-world survivor, not established cosmological fact. Isaac's accept/refuse branch should change his expressed trust, not silently replace canonical plot obligations. Her presence must never be confused with the actual Jenna.

### Character-voice checklist

- **Isaac:** brief, purposeful responses; choices matter without making him omniscient.
- **Garet:** urgency, warmth, occasional humor; avoid reducing him to a running joke or a constant scold.
- **Ivan:** observant and questioning, not clairvoyant beyond established Jupiter abilities.
- **Mia:** caring and practically decisive; avoid repetitive speeches about mercy.
- **Felix:** protective of Jenna and Sheba, withholding information for grounded reasons, not arbitrary melodrama.
- **Saturos / Menardi:** committed to the beacons because Prox is dying; desperation must coexist with responsibility for the harm they cause.
- **Faran / Lalivero:** distinguish a father's fear from a town's political, religious, and economic anxieties.
- **Ash Jenna:** wounded, persuasive, possibly unreliable; no Bloom or sleeper lore.

### Release gates

- Verify per-message placeholders, expanded name widths, style token ordering, page breaks, and ending controls with the project validator.
- Audit conditional states against scene source; an entry's presence in a TSV is not proof it fires correctly.
- Obtain a successful full build at the latest commit.
- Test in game: Vale choices/revisits; Mercury and Kolima flags; Mogall/Altin/Lamakan custom gates; Colosso and Babi audience; both Lalivero visits; both Aerie battles; Sheba's fall; Black Orb/ship departure; ending.
- Conduct a read-aloud pass for voice, pacing, and repeated exposition after the event/state tests. Only then describe the narrative as final.

## Sheba and Lalivero state checkpoint (3 November 2026)

This checkpoint follows the dialogue and scene-script audit; it does **not** replace gameplay testing.

- **Before Colosso / Babi missing:** In Babi Palace, Sheba is held away from home to compel Lalivero's lighthouse construction (phase49: 08269–08274). She is Faran's daughter and Lalivero's revered child, but those labels do not erase her own wishes. Her spoken response and Mind Read should remain distinguishable from what the attendants assume.
- **Finals day:** The palace attendants report that Sheba may be allowed to return after the tournament (phase49: 08777–08782). This is a promise or expectation, not certainty and not a permanent resolution.
- **After Colosso:** Sheba is sent back toward Lalivero (phase49: 09049–09052). **Later, in Lalivero, she is taken again by Saturos/Menardi's party** as the Venus Lighthouse pursuit advances. Do not confuse Babi's confinement with that subsequent abduction.
- **Lalivero before Venus:** Town conversations (phase54: 09901–09924; phase55: 09929–09975) mix concern for Sheba, responsibility for Tolbi's earlier coercion, Faran's search, and uncertainty about what her powers can do. Preserve different opinions, including skepticism. Do not make every villager deliver the same speech of guilt.
- **Lalivero after Venus:** Later dialogue (phase55: 10454–10460) follows Sheba's fall toward the sea. Locals have **no confirmation** that she survived. Any belief that Venus's light will bring her back is a villager's hope, not worldbuilding established as fact. Refer to the fall rather than inventing a deliberate dive.
- **Test gates:** Revisit the palace in the missing-Babi, finals, and post-Colosso states; check Sheba's spoken line and Mind Read in both earlier states; check Lalivero before entering Venus and after the beacon/fall. In-game text box expansion and state transitions remain unverified.

## Venus fall and Faran post-fall branch checkpoint (3 November 2026)

Source-checked against `games/tbs/src/scene/venus_lighthouse_aerie.c` and `games/tbs/src/scene/lalivero_interiors.c`.

- After the defeated Saturos and Menardi fall, the Venus platform breaks. Sheba loses her grip, Felix leaps after her, and Isaac's party **cannot see where either lands**. Do not assert that either survived or died. The sequence in `phase63_aerie_fall_aftermath.tsv` must retain that uncertainty, and Garet's immediate response should express shock rather than belittling Felix's choice.
- After Felix leaps, Garet addresses Isaac, and Isaac's response about looking for Jenna branches into two short reactions. This dialogue is not a new moral alignment flag and both responses return to the same urgency: locating Jenna and telling her what happened to Felix, while acknowledging they do not know his fate.
- In Faran's report after Venus (`phase70_lalivero_interior_sequences.tsv`), the initial report branches on `FLAG_SAW_SHIP_AT_IDEJIMA`. Neither path proves Jenna is dead. A later Yes/No prompt about continuing the search for Sheba has separate replies from Faran. Both converge on his personal hope for his daughter, not on a miraculous survival guarantee.
- Sheba's last words remain spoken by **Sheba**, not Felix. The script then gives Felix his leap and Isaac, Garet, Ivan and Mia their own reactions. Keep that speaker order and all message IDs stable.
- Required gameplay verification: both `FLAG_SAW_SHIP_AT_IDEJIMA` states; both answers to Faran; both answers after Felix's leap; full beacon-rupture animation, Sheba's fall, Felix's leap, return to Lalivero, and line widths after name substitution. A passing CI build alone does not establish these in-game outcomes.



## Finale dialogue speaker and branch audit — 3 November 2026

Source checked against `games/tbs/src/scene/lalivero.c`, `lemurian_ship.c`, and `world_map.c`. This is a connected 47-entry **dialogue-only** finale pass. It does not certify a fresh ROM build or an in-game playthrough.

- **Iodem's farewell (phase69, 10383–10415):** The script's speaker sequence matters: 10386 is **Ivan**, 10389 is **Mia**, 10390 is **Iodem**, 10391 is **Garet**, 10392 is **Iodem**, 10393 is **Ivan**, 10394–10395 are **Iodem**, 10396 is **Mia**, 10397 is **Iodem**, and 10398 is **Garet's question** to Isaac. Iodem supplies separate replies at 10399 and 10400, converging at Ivan's 10401. Iodem speaks 10402 before **narration** at 10403 describes the orb he draws; **Mia** reacts at 10404. Earlier text incorrectly gave Ivan Iodem's own welcome, had Mia describe a return as though she had not taken part, put the Black Orb narration into Iodem's speech, and placed the Black Orb reaction into the narration. The revised exchange now preserves each speaker, makes Garet's Yes/No prompt an actual question, and keeps both responses consistent with the unresolved search for Jenna. The Idejima sighting remains an optional 10417–10422 insert; the script resets to its common Iodem sequence afterwards. No assumption that Jenna is safe has been added.
- **Lemurian ship departure (phase57, 10494–10514):** `LemurianShip_SetSail` has three distinct Yes/No checks: Garet asks whether finding Jenna will end the journey (10497, replies 10498/10499), Mia asks whether she should be found before Lemuria (10504, replies 10505/10506), and Mia asks about the rough sea (10509, replies 10510/10511). These are expressions of hope, priority and confidence, not game-state changes. The revised lines distinguish Ivan's wonder, Garet's anxious warmth and sea joke, and Mia's Imil origin and practical concern. The previous text made Mia reminisce about leaving **Vale**, where she had never lived; this is corrected. Garet has already crossed the Karagol Sea, so his joke acknowledges that experience rather than claiming this is his first sea voyage. Existing untouched original messages at 10501, 10502, 10505, 10512 and 10513 still require a read-through in context.
- **Jenna and Kraden on Idejima (phase58, 10515–10534):** The script has 13 consecutive exchanges by Jenna and Kraden, then two lines by Alex, then a simultaneous reaction and three closing lines. **10523 and 10524 are both Kraden**, and **10525 is Jenna**. The terminal **10534 is spoken by Kraden after the camera reveals Felix and Sheba**, not Alex inviting anyone to follow him. The old 10534 erroneously told the already-arrived party to follow the speaker; it now reacts to the survivors. Jenna's fear, Kraden's uncertainty, and the existing food-related comic beat are retained. The ending confirms Felix and Sheba have survived **to Jenna and Kraden at that moment**, not retroactively to the lighthouse party or to Faran in Lalivero.

**Technical protection:** Only existing TSV message payloads changed; no scene source, state flags, speaker IDs, battle scripts, branching logic or original event order were edited. The batch was checked for a maximum of three display lines per page, 27 visible characters per line with eight-character runtime names, and exact preservation of each edited row's control tokens, including pauses, style and end markers. The repository's full dialogue validator and modified-edition build are a separate CI gate.

**Remaining release gates:** Verify this commit's workflow result; inspect both responses to all three ship questions, both Iodem responses and Idejima branches, item acquisition and orb use, the transition to clear data, and the post-clear ending with the actual speaker portraits. Check the untouched in-between dialogue lines against the new surrounding text before calling the finale polished. Full sequential playtesting and earlier-scene coverage are still required for a 10/10 release claim.


## Venus Aerie dialogue speaker/branch continuity pass — 3 November 2026

This connected editorial pass rewrites 157 existing dialogue messages in the overheard Felix–Saturos–Menardi dispute, the Shaman's Rod coercion, the initial fight, Venus beacon, Fire Clan transformation, and the Sheba fall. The source is `games/tbs/src/scene/venus_lighthouse_aerie.c`; the English player-facing replacement rows are `phase61_aerie_first_battle.tsv`, `phase62_aerie_beacon_fusion.tsv` and `phase63_aerie_fall_aftermath.tsv`.

### Explicit canonical and dramatic constraints

1. Felix sent Jenna, Kraden and the others ahead to Idejima before he returned for Sheba. Felix is not freely abandoning his lighthouse mission; he is confronting the captors about a broken promise and the danger posed by lighting Venus.
2. Saturos and Menardi need a Jupiter Adept for Jupiter Lighthouse. Their duty and fear of failure make them coercive; the story does not invent facts about Prox or the remaining beacons that the observing party could not already reasonably deduce. Sheba is a person with preferences, not a prize the others may endlessly bargain over.
3. The Shaman's Rod exchange distinguishes the literal guarantee **not to harm Sheba** from the party's mistaken expectation of **release**. Both Isaac Yes/No replies converge on the original handover; Ivan expresses reluctant concern without claiming the rod was willingly surrendered in a refusal branch.
4. The overheard party choice (10123), Shaman's Rod bargain question (10159), Garet's question about stopping Felix (10202) and the power-question (10212) have actual question-shaped prompts. Keep their existing branching and outcome logic; the alternatives are dialogue responses, not new flags or alternate story routes.
5. In the original script, 10213 and 10214 are both **Garet's** responses to Isaac about Venus restoring Fire Adepts. Menardi then gives the Earth/Fire explanation at 10215. Similarly, 10237 is **Felix asking Saturos** whether he doubts him; 10238 is **Saturos's reply**. These speaker bindings govern the rewritten lines.
6. After the Fire Clan fight, the party does not retroactively know Felix and Sheba survived their fall. Sheba's two pauses in 10285 describe the breaking platform, while the later story keeps the height and uncertainty intact. The eventual post-clear revelation belongs to Jenna and Kraden, not to Faran or Isaac's group.

### Technical and final-acceptance boundaries

Only dialogue TSV payloads and this ledger were edited in this pass; no actor IDs, event conditions, battle slots, items, text message IDs, or engine source were changed. All edited text was locally checked against the exact multiset of existing runtime/control tokens, three lines per page, and a width ceiling of 27 visible characters with eight-character actor-name expansion. The full project validator, ROM compilation, successful patch generation, scripted event variants, and real gameplay remain separate release gates. A passing workflow is not proof the complete story is a 10/10.


### Immediate in-context line readback — 3 November 2026

The Venus pass received a focused post-commit correction: Menardi's consecutive lines 10081–10082 no longer make her answer her own question; Felix now recognizes that Wind is **their prisoner** in 10093 instead of claiming there is no Wind Adept when Sheba is standing there; and Garet's 10202 Yes/No prompt asks Isaac clearly whether they must stop Felix. These are strictly dialogue amendments with the original text controls preserved; in-game behavior remains to be tested.


## Ash Jenna character-arc continuity and reachability repair — 3 November 2026

**Source anchors:** `games/tbs/src/scene/lamakan_desert.c`, `tolbi.c`, and `games/tbs/include/flags.h`. The Mercury Lighthouse local power flag (`FLAG_MERCURY_LIGHTHOUSE_LIT`, 0x111) only remains set while inside the lighthouse; `Scene_Arrive` clears it on area change. The previous Lamakan and Tolbi appearance checks incorrectly tested that local flag, so Ash Jenna's scripted arc and Mia's post-Manticore scene could be inaccessible after traveling away from Mercury. The two Lamakan checks now use persistent `FLAG_SATUROS_BEATEN_AT_MERCURY` (0x881). Tolbi now requires `FLAG_COLOSSO_OVER` and the persistent `FLAG_DARK_FINALE_DONE`, not the temporary Mercury flag. The Tolbi actor remains parked until both milestones are met. This is source-backed progression repair, not a new requirement for the player.

**Actual chronology:** (1) first Lamakan meeting is optional before the Manticore; the grey apparition resembles Jenna but does not identify her; (2) after Manticore, `LamakanDesert_ManticoreAftermath` plays once and, unless `FLAG_DARK_FINALE_DONE` is already set, the full Lamakan confrontation follows. If the early meeting occurred, the scene uses `N224/N225`; otherwise `N195/N196`. Both branches converge on `N197` onward. (3) Isaac chooses to help Ash Jenna question the Wise One or to withhold agreement. The original `FLAG_DARK_ASH_JENNA_ACCEPTED` and `FLAG_DARK_ASH_JENNA_REFUSED` persist. (4) After Colosso, the one-time Tolbi encounter tests that earlier choice, delivers one new, branch-specific line (`N240/N241`), then explicitly resets the message cursor to `MsgDarkTolbiJennaAsh` (N76) so the main scene's original ten messages remain aligned. (5) The existing Mia and Ivan reactions follow, with no new combat or ending flags.

**Narrative intent:** In Lamakan, her likeness is an unsettling question, not proof she is the original Jenna. At the reveal she identifies as another Jenna, claims to have survived a world where the beacons were lit, and asks Isaac to use his connection to the Wise One to seek an explanation. Her testimony is emotionally sincere but remains **a claim**, not externally established game lore or proof that the Wise One is malicious. Ivan questions certainty; Mia insists on evidence; Garet asks why Isaac is needed. Isaac's Yes/No response changes his degree of commitment, not the canonical rescue quest or eventual lighthouse events. Tolbi acknowledges that prior choice, then tests Mia's ability to recognize and take responsibility for her fear without letting Ash Jenna define her. Ash Jenna has not yet supplied proof or an explanation for crossing worlds; later scenes must not imply those questions are answered.

**Technical QA:** All existing changed message texts keep their original control-token multisets, including page breaks and end markers. Every replacement and both new lines are checked for three display lines maximum per page and 27-character maximum width after eight-character runtime-name expansion. The local source scan ensures the temporary Mercury lighthouse flag is gone from the two Lamakan gates and the Tolbi appearance gate; the full dialogue validator, compilation, patch and in-game branch testing remain independent checks.

**Playtest matrix:** Lamakan prior glimpse yes/no; Manticore aftermath triggered exactly once; Lamakan choice Yes/No; save/reload before Tolbi; post-Colosso Tolbi appearance if Lamakan is done; Tolbi absent before required milestones; no duplicate Tolbi apparition after `FLAG_DARK_ASH_JENNA_TOLBI` is set; Mia's reaction immediately follows and speaker/dialogue cursor remain correct; verify Isaac's two different callback lines do not misalign N76–N83.


## Mia across Mercury, Altin, Lamakan and Tolbi — connected character pass (3 November 2026)

Purpose: Mia remains an Imil healer and Mercury Adept: capable, kind, and occasionally frightened or angry, while responsible for her decisions. The character demonstrates care through action, not unexplained corruption.

1. Mercury Aerie (phase24, MercuryLighthouseAerie_MiaInterrupts and MiaYields): the initial wary alliance gives way to Mia's decision to pursue Menardi and Jenna, with Isaac, Garet and Ivan left to face Saturos. The apology acknowledges misjudgment; no battle or party transition changed.
2. Altin Peak (phase40, phase44, AltinPeak_TalkToTrappedMiner): after the optional rescue is accepted, Mia warns of unsafe supports and Garet braces the roof while Ivan reports rising water. The miner stays shaken after the rescue, and a second Yes/No choice asks Isaac to remain with him. If Isaac declines to stay, Mia still offers to help him outside. The Power Bread reward, rescue flag, and stay flag are unchanged.
3. Lamakan Desert (phase42, phase43, LamakanDesert_ManticoreAftermath): Mia, Garet, Mia, Mia, Isaac and Ivan speak in that order. Mia admits that she wanted to hurt the Manticore beyond what was necessary; Garet had feared she was physically injured; Isaac and Ivan stay with her. Ash Jenna can interrupt soon afterward, so no extended rest is invented.
4. Tolbi Ash Jenna (phase30, phase37): Ash Jenna notices visible fear after the Manticore rather than claiming supernatural access to Mia's private emotions. Mia speaks for herself and Isaac supports her without declaring that feeling anger carries no responsibility. Ash Jenna and the original Jenna remain distinct.
5. Tolbi Kegare (phase33, Tolbi_TalkToKegare): optional seven-speaker order is Kegare, Isaac, Kegare, Mia, Kegare, Mia, Isaac. Kegare imitates Mia's face and voice, but Mia points to time spent caring for the sick in Imil. Kegare is a separate optional antagonist and can be fought before or after Ash Jenna's Tolbi meeting; the new lines work in either order. No new connection or common mastermind is implied.
6. Kolima Heart remains separate and unchanged: her mistaken recognition of Isaac as Matthew is not merged with Kegare or the awakened storyline.

Validation scope: 47 existing dialogue message payloads revised in eight TSVs; original IDs and the exact text-control token multisets preserved; maximum three display lines per page and 27 visible characters per line checked. One incorrect Tolbi source comment left by the earlier Lamakan-gate repair was corrected without executable logic changes.

Still required: replay Mercury battle/return branches, both Altin rescue questions, Manticore aftermath and its Ash Jenna handoff, both orders of the optional Tolbi encounters, Kegare defeat/retry, portraits and text layout; run the complete validator and build; verify the story in an actual playthrough. This checkpoint is not a claim of completed narrative acceptance.


### Manticore target-variation QA correction — 3 November 2026

The Manticore fight can target different party members. The first Mia-pass revision of N149 specified that the beast attacked Garet, although the combat script does not guarantee that event. The revised line says it attacked the party, preserving Mia's frightening anger without inventing a fixed battle target. All original text controls remain unchanged. This was caught during a later source-knowledge pass and still needs gameplay verification.
