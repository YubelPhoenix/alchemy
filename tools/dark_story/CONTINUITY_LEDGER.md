# Ashfall Story Rewrite — Continuity Ledger

Status: working audit document  
Branch: `dark-story-rewrite`  
Scope: narrative chronology, story-state dependencies, and rewrite coverage  
Last audited revision: `d0b0e2861730a9e84065595c4ccfa760cfd60acd`

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

The script documents separate pre-Colosso, Colosso, and post-Colosso dialogue states. Sheba's captivity, the soldiers' search, and the audience with Babi must not be collapsed into one state. `FLAG_COLOSSO_OVER` and `FLAG_BABI_SPOKE_AFTER_COLOSSO` are essential distinctions. The first source-message rewrite batch is now drafted: 89 non-empty palace messages in `phase49_babi_palace.tsv`, plus 19 scholars' room messages in `phase50_babi_scholars.tsv`. Message IDs, contexts, runtime placeholders, ending controls, and the pause/em-dash controls were checked against the source catalog. Build validation and in-game testing are still pending.

### Suhalla

Before `FLAG_BABI_SPOKE_AFTER_COLOSSO`, villagers discuss the sandstorms, Angaran distrust, and Sheba's hostage status. After the audience, their dialogue reflects soldiers caught in the storms on the way to Babi Lighthouse. The party crosses the desert with Iodem after Babi's audience. The town rewrite covers 30 non-empty messages. Its interiors have a further 44 messages across the pre- and post-audience states; `FLAG_IODEM_MET_WOUNDED_SOLDIERS` and `FLAG_BABI_LIGHTHOUSE_IODEM_ARRIVED` distinguish the wounded-soldier and Iodem-arrival dialogue.

### Lalivero

The first visit occurs with Iodem; townspeople discuss Sheba's capture, injured soldiers explain where her captors went, and the wharf guard blocks access. After Venus Lighthouse, the party returns. Iodem's farewell and the Black Orb handover lead to the wharf opening. Preserve the relevant conditions, including `FLAG_VENUS_LIGHTHOUSE_PARTY_RETURNED`, `FLAG_IODEM_FAREWELL_SEEN`, `FLAG_SAW_SHIP_AT_IDEJIMA`, and `FLAG_LALIVERO_WHARF_OPEN`.

### Venus Lighthouse and Aerie

Audit the outside approach, scholars and soldiers, ground-floor NPCs and environmental text, all four floors, puzzles, encounters, and the Aerie. The Aerie sequence includes the initial confrontation and battle, beacon lighting and second battle, the party's world-map transitions, Sheba hanging from the broken Aerie, and her fall. Do not treat the second battle as the final scene of the game. The Babi Lighthouse approach and sealed-door dialogue now has a 38-message rewrite batch; its `FLAG_BABI_LIGHTHOUSE_DOOR_SHOWN`, `FLAG_BABI_LIGHTHOUSE_DOOR_OPEN`, `FLAG_BABI_LIGHTHOUSE_ASKED_TO_FOLLOW`, `FLAG_BABI_LIGHTHOUSE_BACK_FROM_STONE_DOOR`, and `FLAG_BEYOND_DOOR` states still require in-game verification.

### Ending

The world-map ending and Lemurian ship departure are separate from the Aerie event. The world-map script documents the ending after the cleared game is saved; the Lemurian ship departure sequence leads into the final scene path and return to the title. The rewrite must cover this material rather than stopping at Venus Lighthouse.

## Coverage status

The current rewrite directory contains phase files through `phase48_docks.tsv`. That does **not** establish complete late-game coverage.

| Area | Audit status |
|---|---|
| Early game through Mercury Lighthouse | Existing phase files present; comprehensive NPC / Mind Read / branch coverage still needs verification. |
| Post-Mercury custom encounters | Existing phases present; event-order and callback audit in progress. |
| Kalay / Karagol / Tolbi / Altmiller / Colosso | Original progression verified in scene scripts; Ashfall message-by-message coverage remains to be checked. |
| Babi's Palace and scholars' rooms | Source-message rewrite drafted (89 + 19 entries); automated build and in-game state validation pending. |
| Babi's audience / Gondowan Passage | Requires full dialogue coverage audit. |
| Suhalla / desert / Babi Lighthouse | Drafts exist for 30 town, 44 interior, and 38 Babi Lighthouse messages; automated build and in-game state validation pending. |
| Lalivero, first and second visits | Original state split verified; Ashfall coverage remains to be checked. |
| Venus Lighthouse, all floors | Requires full dialogue, sign, Mind Read, puzzle, and event-message audit. |
| Venus Aerie | Event sequence verified; Ashfall dialogue coverage and character-knowledge audit required. |
| Lemurian ship / true ending | Ending path identified; full Ashfall dialogue coverage not yet established. |

## Known caution items

- `phase13_menardi_aerie.tsv` is currently only a tiny stub; inspect before treating it as meaningful coverage.
- Do not infer a missing scene from a missing phase file alone. First inspect the game's text tables, scene triggers, and the existing rewrite tooling to identify the actual source messages.
- Do not rename or reorder existing phase files merely to make their numbering look chronological. Document the actual chronology separately.
- Do not invent new story flags or alter event logic as a shortcut to narrative continuity.
- Before editing a dialogue batch, capture its source message ID, original text, scene, trigger condition, and any state variants. Then validate text length, control codes, and branch completeness.

## Next audit actions

1. Inventory the game's text data and determine how the current TSV phase files are applied.
2. Build a source-message coverage index for every late-game scene listed above. Babi's Palace, scholars' rooms, Suhalla, and Babi Lighthouse now have draft batches; validate them before marking coverage complete.
3. Audit custom branch flags and callbacks against their event scripts.
4. Draft missing dialogue in small, location-complete batches, including optional NPCs and Mind Read text. Next: Lalivero's first and second visits, its interiors, wharf, and Iodem's farewell / Black Orb sequence.
5. Run the existing rewrite/build tooling and inspect the resulting ROM in-game across representative branches.
6. Extend this ledger as each area is verified; mark coverage complete only after source-message comparison and in-game validation.
