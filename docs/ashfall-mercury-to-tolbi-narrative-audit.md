# Ashfall: Mercury Lighthouse to Tolbi — Narrative and Sentence Audit

Branch: `dark-story-rewrite`  
Status: source-backed audit in progress. This document identifies defects and establishes the route order before dialogue is rewritten. No original event logic or message IDs are changed by this audit.

## Why this stretch needs a reset

The current phase files are not a reliable chronology. The project's continuity ledger explicitly says phase filenames are organizational labels, not chronological order. The post-Mercury route must be reconstructed from scene scripts, flags, entrances, exits, and event triggers before dialogue is edited. The present batch mixes the original route, post-event variants, and new Ashfall material without a sufficiently clear state map.

## Verified original route after Mercury Lighthouse

The source-backed route is:

1. **Mercury Lighthouse / Imil aftermath.** Mia joins the party inside Mercury Lighthouse; Saturos is fought in the Aerie; only after he is beaten does the Fountain of Healing flow. The party can then return to Imil, where the fountain's Water of Hermes heals the sick. Imil's residents have distinct before-and-after recovery dialogue, and Mia's departure is a separate emotional scene.
2. **Kolima and Kolima Forest.** Kolima is first encountered under Tret's curse. The villagers are trees and their thoughts are heard through Mind Read. Tret and Laurel direct the party into the forest. Tret is restored using the healing water; he then restores the villagers. The party learns that falling Psynergy Stones affected the elder trees and other living things, and Laurel reports the evil forest beyond the river.
3. **Bilibin and the riverbank.** Bilibin's curse-dependent NPC states change only after Tret is healed. Once Saturos has been defeated at Mercury Lighthouse, the Imil travelers have crossed the river using the Gang of Three trees; Jill can be pulled from the water. After the curse is lifted, Jill's presence and gift depend on whether she was rescued. These states must not be collapsed.
4. **Mogall Forest, Xian, and Altin.** These belong to the original westward journey after the Bilibin/Kolima events and before the Lamakan crossing. Altin's water-beast crisis and mine progression have several separate states; dialogue must distinguish the flooded village, the partial recession, the defeated hydros statues, and the deeper mine discoveries.
5. **Lamakan Desert and the Manticore.** This crossing occurs before Kalay and Tolbi. The party's knowledge and any companion dialogue must reflect the desert events already completed, not later Tolbi events.
6. **Kalay and the Karagol Sea.** Kalay has multiple states. The first Hammet Palace visit precedes Ivan's report to Layana; the Karagol crossing then takes the party to Tolbi.
7. **Tolbi and Colosso.** The party arrives while the festival is underway. The trials have begun, Babi is missing, and his soldiers search the town. Babi is found in Altmiller Cave; after he is saved, he appears at the finals. After Colosso, visitors leave and the remaining residents discuss the quiet and the ships that no longer sail the Karagol.

## Concrete defects already visible in the current dialogue

### 1. Mercury Lighthouse: Elemental Star count — verified, no dialogue correction needed

An earlier audit note incorrectly claimed that message IDs `05537` and `05540` referred to **three** Elemental Stars. The current branch already says **four** in both rows, which is correct. The live text and the Aerie scene context agree: Isaac and Garet came from Vale to recover the four Stars stolen from Sol Sanctum. Do not change these rows. This finding is closed as a stale audit note, not an outstanding dialogue defect.

### 2. Imil farewell: Mia's stated purpose contradicted the scene

In `phase17_imil_mercury_b.tsv`, message `05738` originally said Mia was leaving to protect the **Mercury Clan**. The surrounding farewell exchange establishes that she is joining Isaac's quest because the world is in danger; the Imil scene source also explicitly describes her promise to join that quest to protect the world. The apprentices, not Mia, promise to protect Imil as members of the Mercury Clan. Corrected `05738` to say she is trying to protect the **world**. This preserves the scene's intended distinction between Mia's wider mission and the apprentices' responsibility at home.

### 3. Tolbi: incompatible story states are mixed together

`phase28_tolbi.tsv` combines lines that describe different points in the Colosso sequence:

- `08079` says the trials have started and the speaker expects to watch the finals.
- `08080` says Colosso should have started but nobody is present, while Babi's bodyguards search the streets.
- `08118`–`08120` are the soldiers' search for Babi.
- `08668`–`08670` refer to the finals approaching or already underway.
- `09071`–`09076` refer to the aftermath, including Colosso ending and ships no longer sailing.

These are not one simultaneous town state. Each line must be attached to the original trigger and the appropriate flag/state. A player should not hear a resident say the trials have started, then hear another say they have not started, unless the game has advanced to a different state between visits.

The new rain/flood/harbor-patrol framing also needs a continuity map. It cannot silently replace the original Tolbi states or make Babi simultaneously absent, present, and already returned.

### 4. Tolbi: unsupported or confusing causal statements

Several new lines use striking imagery but do not establish what happened:

- `08077` says Babi believes stopping the festival would start a panic, then claims there is already a quiet panic. Who is reporting Babi's reasoning, and how would this ordinary resident know it?
- `08088` says soldiers took half a vendor's stock for the harbor. This is a new event and needs an established on-screen cause, not a line that appears as unexplained background fact.
- `08103` says soldiers are hauling carts to the pier at night. The dialogue does not say what is being moved, why, or how the speaker knows.
- `08110` describes fighters with grey eyes who do not speak. This may be an Ashfall clue, but the line needs to be placed where the speaker could have seen them and where the party can understand the observation as a clue rather than an unrelated anomaly.
- `09076` says sea monsters block the crossing. This is an aftermath state and must not appear during the initial festival visit.

The solution is not to remove every dark detail. It is to give each detail a clear cause, witness, chronology, and payoff.

### 5. The "Ash Jenna" Tolbi encounter is not presently supported by the original story state

`phase30_tolbi_ash_jenna.tsv` stages an antagonist who looks like Jenna and speaks as though she is a changed or alternate Jenna. Yet in the original route Jenna remains a hostage of Saturos and Menardi until the later Venus Lighthouse events. The current lines do not explain how this figure can be in Tolbi, why she has Jenna's face, whether she is a copy, a vision, a possession, or something else, or how the party distinguishes her from the real Jenna.

The line "I'm a Jenna who stopped waiting to be saved" is evocative but does not answer the scene's basic dramatic question. Garet's objection and Mia's response then treat the figure as both recognizably Jenna and not Jenna without giving the audience a stable reason. Mia's "voice in that blade" introduces another unexplained element.

This sequence must be held out of the active dialogue pass until the Ashfall premise, the figure's identity, the blade's role, and the party's knowledge at this exact point are established in the continuity ledger. Do not solve this by inventing an explanation inside one NPC line.

### 6. Altin: the crisis and recovery states need to be separated

`phase29_altin.tsv` contains dialogue for the flooded state, the water-receded state, the aftermath of defeating the hydros statues, the return of residents, and later discoveries beneath the mine. Some of these lines can only be heard after the player has completed the corresponding event. The file should be audited against the trigger conditions in `altin.c` and the mine scene scripts before any text is moved or rewritten.

Particular care is needed with the Xian traveler and the Silk Road blockage. The party must not receive information about the girl's search, the blocked road, or the passage west before those details become available in the actual route.

## Sentence-level editorial rules for this entire stretch

Every line must pass both a continuity test and a spoken-language test.

- **One clear thought per sentence.** Avoid compressed fragments that sound like notes from a plot outline.
- **Clear referents.** Names, pronouns, "they," "it," "the light," "the voice," and "the gems" must point to something the speaker and player can identify.
- **Natural speech.** A villager should sound like a villager, a child like a child, and a companion like that companion. Do not make every NPC deliver polished ominous exposition.
- **No unexplained metaphors.** A metaphor can deepen an established event; it cannot substitute for explaining who did what.
- **No duplicated exposition.** If one character has just explained a fact, the next line should react, question, challenge, or add new information rather than repeat it.
- **Knowledge is local and timed.** A speaker may only know what they witnessed, were told, or could reasonably infer by that scene state.
- **State-specific language.** A line about a crisis, recovery, departure, or aftermath must only appear in its corresponding state.
- **Preserve technical text.** Keep message IDs, actor-name tokens, control codes, branching endings, and line-width limits intact.

## Required next work

1. Read the full original source for Imil, Mercury Lighthouse, Kolima Forest/Tret, Bilibin, Mogall Forest, Xian, Altin and its mine, Lamakan Desert, Kalay, Karagol Sea, Tolbi and Colosso.
2. Build a message-to-trigger/state matrix for every affected TSV row, including ordinary NPC dialogue, Mind Read, signs, examinations, shops, children, and conditional responses.
3. Mark each line as: factually wrong, chronologically misplaced, unclear referent, unnatural sentence, redundant, or sound.
4. Rewrite in small batches, preserving IDs and controls, then run the dialogue validator and ROM build.
5. Keep the Ash Jenna scene quarantined until its identity and event placement are coherent with Jenna's actual captivity and the wider Ashfall story.
6. Do not mark the stretch complete until every row has been accounted for and the route has been checked in-game.

## Scope boundary

This audit does not declare all current dialogue defective, and it does not authorize broad replacement of the original event structure. It records concrete contradictions already found and defines the source checks required before a safe rewrite.
