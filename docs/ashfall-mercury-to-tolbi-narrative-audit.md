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

### 3. Kolima: clarify the protective Psynergy and the stones' effect

The Kolima event source explicitly says the companions discover that their Psynergy formed the barriers that protected them from Tret's transformation. Message `05257` only said, "It was our Psynergy," which was too vague to communicate that discovery. It now reads, "Our Psynergy protected us."

Message `05381` described the elder trees' response to the falling stones as "Our actions spoke our hearts' desires," an abstract phrase that obscured the causal point. Tret is explaining that the stones drew out and amplified what was already within them. The line now reads: "The gems drew out what we felt most deeply. We did not understand..." This keeps the mystery and emotional darkness while making the sentence understandable on first hearing. Message IDs and control tokens are unchanged.

### 4. Tolbi: incompatible story states are mixed together

`phase28_tolbi.tsv` combines lines that describe different points in the Colosso sequence:

- `08079` says the trials have started and the speaker expects to watch the finals.
- `08080` says Colosso should have started but nobody is present, while Babi's bodyguards search the streets.
- `08118`–`08120` are the soldiers' search for Babi.
- `08668`–`08670` refer to the finals approaching or already underway.
- `09071`–`09076` refer to the aftermath, including Colosso ending and ships no longer sailing.

These are not one simultaneous town state. Each line must be attached to the original trigger and the appropriate flag/state. A player should not hear a resident say the trials have started, then hear another say they have not started, unless the game has advanced to a different state between visits.

The new rain/flood/harbor-patrol framing also needs a continuity map. It cannot silently replace the original Tolbi states or make Babi simultaneously absent, present, and already returned.

### 5. Tolbi: unsupported or confusing causal statements

Several new lines use striking imagery but do not establish what happened:

- `08077` says Babi believes stopping the festival would start a panic, then claims there is already a quiet panic. Who is reporting Babi's reasoning, and how would this ordinary resident know it?
- `08088` says soldiers took half a vendor's stock for the harbor. This is a new event and needs an established on-screen cause, not a line that appears as unexplained background fact.
- `08103` says soldiers are hauling carts to the pier at night. The dialogue does not say what is being moved, why, or how the speaker knows.
- `08110` describes fighters with grey eyes who do not speak. This may be an Ashfall clue, but the line needs to be placed where the speaker could have seen them and where the party can understand the observation as a clue rather than an unrelated anomaly.
- `09076` says sea monsters block the crossing. This is an aftermath state and must not appear during the initial festival visit.

The solution is not to remove every dark detail. It is to give each detail a clear cause, witness, chronology, and payoff.

### 6. The "Ash Jenna" Tolbi encounter is not presently supported by the original story state

`phase30_tolbi_ash_jenna.tsv` stages an antagonist who looks like Jenna and speaks as though she is a changed or alternate Jenna. Yet in the original route Jenna remains a hostage of Saturos and Menardi until the later Venus Lighthouse events. The current lines do not explain how this figure can be in Tolbi, why she has Jenna's face, whether she is a copy, a vision, a possession, or something else, or how the party distinguishes her from the real Jenna.

The line "I'm a Jenna who stopped waiting to be saved" is evocative but does not answer the scene's basic dramatic question. Garet's objection and Mia's response then treat the figure as both recognizably Jenna and not Jenna without giving the audience a stable reason. Mia's "voice in that blade" introduces another unexplained element.

This sequence must be held out of the active dialogue pass until the Ashfall premise, the figure's identity, the blade's role, and the party's knowledge at this exact point are established in the continuity ledger. Do not solve this by inventing an explanation inside one NPC line.

### 7. Altin: clarify the cost to families

Message `06391` described people losing someone "who's still standing right in front of them." The intended horror is that some miners returned physically, but were no longer emotionally or mentally present as the people their families knew. The original phrasing was evocative but too oblique to land clearly. It now reads: "Some have lost loved ones who are still standing right in front of them." This keeps the disturbing implication while making the sentence grammatical and immediately comprehensible. The exact trigger for `06391` has not yet been mapped to its source event, so it remains an open verification item. This was a sentence-level correction only; no event condition or message ID was changed.

### 8. Altin: the crisis and recovery states need to be separated

`phase29_altin.tsv` contains dialogue for the flooded state, the water-receded state, the aftermath of defeating the hydros statues, the return of residents, and later discoveries beneath the mine. Some of these lines can only be heard after the player has completed the corresponding event. The file should be audited against the trigger conditions in `altin.c` and the mine scene scripts before any text is moved or rewritten.

Particular care is needed with the Xian traveler and the Silk Road blockage. The party must not receive information about the girl's search, the blocked road, or the passage west before those details become available in the actual route.

### 9. Lamakan Desert: Ash Jenna's optional meeting must carry into the finale

The source allows the party to speak to Ash Jenna in the Manticore area before the Manticore/caravan sequence is complete. That optional scene sets `FLAG_DARK_ASH_JENNA_LAMAKAN_MET`. Later, the Manticore return runs the caravan sequence and automatically starts the finale. The finale previously used the same opening whether or not Isaac had already encountered her, making him ask who she was as though the earlier conversation had never happened.

The finale now branches on that existing encounter flag. A first-time meeting keeps the original opening; a returning meeting acknowledges that she watched the party in the desert before Isaac asks who she is. The following dialogue IDs are set explicitly so both branches resume at the correct shared reveal and cannot drift into the wrong sequential message.

The new rows use unused message IDs `N224` and `N225`; they were checked against the full dark-story TSV set to avoid collisions. The encounter flag and scene progression are unchanged.

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


## Chronological source audit: Bilibin, Kolima, and the riverbank

This pass checked the current dialogue batches against `games/tbs/src/scene/bilibin.c` and `games/tbs/src/scene/kolima.c`. It establishes the event-state boundaries before further line edits.

### Bilibin town has two distinct population states

The Bilibin town scene is controlled primarily by `FLAG_KOLIMA_CURSE_LIFTED`, which is set when Tret is healed in Kolima Forest.

- **Before the curse is lifted:** the tree-shaped man remains at the town entrance; his Mind Read is the trapped plea in `05040`. The ten town NPCs use their pre-cure talk and Mind Read lines.
- **After the curse is lifted:** the tree actor is removed and the restored man appears; the ten NPCs switch to their post-cure dialogue; the old man and old woman turn to face the party and their talk changes. The restored man's talk and Mind Read are separate from the tree's earlier interaction.
- The two groups of dialogue are selected by the scene's ordered trigger rows. Do not move a post-cure response into the pre-cure state merely because it reads better in isolation.

### The Bilibin Barricade has a separate, independent progression axis

The riverbank scene is not governed by the Kolima curse flag alone. Its tree arrangement changes when `FLAG_SATUROS_BEATEN_AT_MERCURY` is set:

- Before that flag, the Gang of Three are stacked as trees and Jill remains at the top.
- After that flag, the middle tree is laid across the river and Jill's tree is placed in the water. The player can use Move on Jill to pull her ashore.
- `FLAG_BILIBIN_JILL_RESCUED` changes Jill's Mind Read and the two boys' later dialogue.
- Once `FLAG_KOLIMA_CURSE_LIFTED` is set, all three trees are removed and the children return to the bank. Jill is absent if she was not rescued. If rescued, the step trigger gives the Hard Nut and sets `FLAG_BILIBIN_JILL_GIFT_RECEIVED`.

These flags must remain independent. In particular, the post-Mercury river event can occur while the Kolima curse is still active; rescuing Jill is not the same event as healing Tret.

### Dialogue review findings

- `phase8_bilibin_a.tsv` and `phase8_bilibin_b.tsv` contain both pre- and post-curse dialogue. The source trigger table confirms that many of the paired lines are intentional state changes, not contradictions. They must be audited as pairs.
- `phase21_bilibin_riverbank.tsv` includes the Jill rescue aftermath and the Gang of Three's changed dialogue. The rescued/not-rescued variants in `06002`–`06004`, `06015`–`06021`, and the gift sequence must remain tied to their existing flags.
- `05993`–`05999` contain retrospective Bilibin dialogue about the party's trip to Kolima, the barricade, and the reward. These lines must be checked against their actual palace/town actor triggers before any wording change; their retrospective framing is not inherently a chronology error.
- `phase19_bilibin_tone.tsv` is not a clean location-only batch: it includes Kolima villagers and interiors alongside Bilibin inn dialogue. Its filename must not be used to infer where or when a message is spoken.
- The Kolima source confirms the party's protective Psynergy explanation and Tret's explanation of the falling Psynergy Stones. The existing corrections to `05257` and `05381` are consistent with those events. The remaining Tret/Laurel explanation (`05372`–`05399`) should be checked as one continuous conversation, including the transition to the forest south of the river, rather than edited line by line without its preceding and following turns.

### Open checks before declaring this stretch complete

1. Map every row in the three Bilibin phase batches to the exact town, palace/interior, or barricade actor and trigger; include all Mind Read and examination entries.
2. Confirm the event order of the Imil travelers crossing the river against the Mercury Lighthouse flag and the player's actual return route.
3. Verify both Jill branches in-game: rescued before Tret is healed, and not rescued before Tret is healed.
4. Check the Kolima post-Tret NPC and interior rows in `phase19_bilibin_tone.tsv` against their scene-specific triggers; do not assume the phase filename denotes one location.
5. Only make text edits when a specific trigger/state or clear language defect has been established.

No Bilibin or Kolima dialogue was changed during this pass. This is a source-backed state map, not a claim that every row has been individually validated.

## Superseding story decision: harbor child removed; Kegare is a post-Colosso cameo

This section supersedes earlier notes in this document that describe the harbor child as an active Ashfall thread or describe Kegare's encounter as gated by child-rescue / kindness flags.

- The custom harbor-child storyline has been removed, including its Tolbi introduction, dock actor and interaction, dedicated dialogue, flags, Mogall callbacks, and Lamakan finale callback. It is not part of the current story and must not be reintroduced as Kegare's origin.
- Kegare comes from the user's existing sprite-animation continuity: she is a demon from a different period who has taken Mia's appearance and intends to replace her. Do not invent a new origin or merge her with the lighthouse/awakened plot.
- Kegare's optional cameo superboss encounter is available only after `FLAG_COLOSSO_OVER`. The harbor-child and three-kindness flags do not gate her.
- Mia directly confronts Kegare's claim that wearing her face gives Kegare her identity or place among the party.
- GitHub Actions Run 394 (`41459976297`) completed successfully on the current branch head, including dialogue validation, modified English edition compilation, unmodified baseline verification, IPS generation, and test-patch upload. This verifies the build pipeline for that commit; in-game encounter and route testing remain separate requirements.


### Corrected early-game route: Kolima and Mercury are interleaved

The source check makes the route more specific than the broad location list above. Do not describe this stretch as simply "Mercury, then Bilibin, then Kolima."

1. **Initial Bilibin visit:** the Kolima road is blocked and the tree-shaped man is at the town entrance.
2. **First Kolima / Tret visit:** the party witnesses the curse and reaches Tret. Tret's wrathful side rejects an attempt to use ordinary progress at this point; Laurel's Mind Read points toward the healing waters of Mercury Lighthouse, whose fountain has dried up.
3. **Imil and Mercury Lighthouse:** Mia joins the party; the party reaches the lighthouse, lights its beacon, and defeats Saturos at the Aerie. The source documents that the Fountain of Healing begins flowing only after Saturos is beaten, allowing an Empty Bottle to become Hermes' Water.
4. **Bilibin Barricade river event on the return:** `FLAG_SATUROS_BEATEN_AT_MERCURY` changes the Gang of Three's tree arrangement while `FLAG_KOLIMA_CURSE_LIFTED` is still clear. The travelers from Imil have crossed using the fallen trees; Jill is in the river and can be rescued with Move. This is the window for the optional Jill rescue.
5. **Return to Tret:** use Hermes' Water on Tret. The Water of Hermes seeps into him, the party restores his gentle side, and `FLAG_KOLIMA_CURSE_LIFTED` changes Kolima and the forest to their post-curse states.
6. **Post-curse Bilibin revisit:** the tree-shaped man is restored, the town NPCs switch to their post-curse talk and Mind Read, the road opens, and the Gang of Three are children again. Jill's presence and gift depend on the earlier rescue flag.
7. **Only after this stretch does the party proceed into the westward route through Mogall Forest, then Xian and Altin.** Mogall is before Altin.

The crucial distinction is that the Mercury victory and the Tret cure are separate milestones. `FLAG_SATUROS_BEATEN_AT_MERCURY` opens the fountain and changes the riverbank scene; it does not itself lift Kolima's curse. `FLAG_KOLIMA_CURSE_LIFTED` is set later, when Tret is healed. Dialogue must respect the interval between those events.
