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
| `phase32_imil_tolbi_kindness.tsv`, `phase33_ondra.tsv` | Kindness / Ondra branch material. Preserve the underlying decision flags and conditional availability. |
| `phase34_mogall_lamakan.tsv`, `phase35_lamakan_jenna.tsv` | Mogall and Lamakan custom material. Verify each encounter's trigger and ensure Ash Jenna's later appearance acknowledges the earlier meeting. |
| `phase36_peak_alex.tsv`, `phase39_mogall_alex.tsv` | Alex's separate encounters. His knowledge and warnings must develop between appearances rather than repeat. |
| `phase37_blade.tsv`, `phase38_heart.tsv` | Tideglass Blade / Mia storyline. Track the blade's influence and Mia's memory of each episode. |
| `phase40_altin_peak_miners.tsv`, `phase41_altin_peak_mood.tsv` | Altin Peak rescue and aftermath. Preserve the rescue choice and the miner's subsequent condition. |
| `phase42_manticore_mia.tsv` | Mia's post-Manticore episode. This must follow the Manticore encounter and be reflected in later party dialogue. |
| `phase43_ivan.tsv` | Ivan's developing sensitivity to the awakened and the blade. His observations must match what he has actually heard. |
| `phase44_bloom.tsv` | Branching kindness material involving the harbor child and miner, with later callbacks. |
| `phase45_mogall_door.tsv` | Mogall camp-door decision. Keep the yes/no outcomes distinct and preserve the humming-girl callback. |
| `phase46_awakening.tsv` | Caravan awakening and the party's response. The choice must be carried into the finale. |
| `phase47_finale.tsv` | Lamakan finale and Ash Jenna's major revelation. This is not the overall Golden Sun ending; it directs the party onward to Kalay. |
| `phase48_docks.tsv` | Tolbi harbor child material. Its placement and dialogue state must be checked against the post-Colosso Tolbi return. |
| `phase49_babi_palace.tsv` | 89 non-empty Babi's Palace message entries rewritten across pre-Colosso, Colosso, and post-Colosso states, including residents, Sheba-related dialogue, Mind Read, examinations, and event prompts. |
| `phase50_babi_scholars.tsv` | 19 Babi scholars' room entries rewritten, covering Alchemy, the Venus Ruins, the lighthouse, and Kraden's absence. |
| `phase51_suhalla.tsv` | 30 Suhalla town messages rewritten across the pre- and post-audience states, including villagers' dialogue and Mind Read. |
| `phase52_suhalla_interiors.tsv` | 44 Suhalla interior messages rewritten, including merchants, travelers, wounded soldiers, Mind Read, and environmental examinations. |
| `phase53_babi_lighthouse.tsv` | 38 Babi Lighthouse messages rewritten, covering workers, injured guards, Faran's pursuit, Sheba's rescue, the sealed door, and the ruins clue. |
| `phase54_lalivero.tsv` | 51 Lalivero town-map messages rewritten, covering Sheba's absence, the soldiers, the aftermath of Venus Lighthouse, and the wharf. |
| `phase55_lalivero_interiors.tsv` | 95 interior messages rewritten, including Sheba's family, town residents, Mind Read, wounded soldiers, Iodem, and the ship. |
| `phase56_black_orb.tsv` | 3 world-map messages rewritten for the Black Orb / Babi's ship interaction and optional shipwreck inspection. |
| `phase57_lemurian_ship.tsv` | 16 messages rewritten for the departure from Gondowan and the voyage toward Lemuria. |
| `phase58_true_ending.tsv` | 13 non-empty messages rewritten for the post-game drifting-island scene with Jenna, Kraden, and Alex. |
| `phase59_tunnel_ruins.tsv` | 8 Tunnel Ruins statue messages rewritten, preserving the lady/statue riddle and the four directional pillar clues. |
| `phase60_venus_lighthouse.tsv` | 25 Venus Lighthouse messages rewritten, including scholars, guards, relief inscriptions, statue dialogue, and the route clue. |
| `phase61_aerie_first_battle.tsv` | 100 Aerie messages rewritten for the first confrontation, Sheba's captivity, the Shaman's Rod bargain, and the first battle. |
| `phase62_aerie_beacon_fusion.tsv` | 57 Aerie messages rewritten for Felix's decision, beacon activation, Saturos and Menardi's return, and the fusion battle. |
| `phase63_aerie_fall_aftermath.tsv` | 52 Aerie messages rewritten for the collapse, Sheba's fall, Felix's sacrifice, and the party's return. |




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

Phases 49–63 contain **640 rewritten source-message entries**: Babi's Palace and scholars (108), Suhalla and its interiors (74), Babi Lighthouse (38), Lalivero and its interiors (146), Black Orb interactions (3), Lemurian ship departure (16), post-game ending (13), Tunnel Ruins (8), Venus Lighthouse (25), and the Aerie (209). All 640 drafted rows passed a manual source-catalog check for message ID/context, runtime placeholders, ending controls, pause/style controls, text-box width, and page-line limits. No duplicate message IDs were found within these phases or against the prior phase files listed in this ledger. **This is not yet complete scene coverage:** a deeper source audit found sequential event-message blocks that are not represented by the named-message inventory. These still need to be rewritten and added before any location is marked complete. The repository's full validator/build and in-game checks also remain pending.

### Important custom-state observations

- Ash Jenna has at least two distinct encounters: the Lamakan revelation and the later Tolbi confrontation. Dialogue must acknowledge the earlier meeting.
- Alex appears in separate Mogall and Altin Peak encounters. His information and urgency must progress.
- The post-Mercury custom events are gated by story conditions; their phase numbers do not mean they occur before the original Altin or Lamakan visits.
- The Lamakan finale recalls earlier choices involving the harbor child, miner, camp, caravan, and Tideglass Blade. Those callbacks must agree with the actual flags and with the player's route.
- The Tolbi Ash Jenna encounter is a later event, gated by Colosso being over and Mercury Lighthouse being lit.
- Ondra's appearance is conditional. Do not write her as a guaranteed encounter for every playthrough.

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
