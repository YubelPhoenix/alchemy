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

### Babi's Palace

The script documents separate pre-Colosso, Colosso, and post-Colosso dialogue states. Sheba's captivity, the soldiers' search, and the audience with Babi must not be collapsed into one state. `FLAG_COLOSSO_OVER` and `FLAG_BABI_SPOKE_AFTER_COLOSSO` are essential distinctions. The Babi's Palace batch currently rewrites 89 named palace messages, with a further 19 scholars' room entries in `phase50_babi_scholars.tsv`. A source-code pass has since identified large sequential blocks beginning at `MsgTolbiGetUp`, `MsgTolbiLikeSleep`, `MsgTolbiIodemIodem`, `MsgTolbiCallsName`, and `MsgTolbiWaitingCompanions`, plus smaller question/answer sequences. These additional lines are not yet covered; the 89+19 count is partial.

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
