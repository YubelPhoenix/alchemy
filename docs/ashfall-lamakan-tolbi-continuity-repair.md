# Ashfall: Lamakan-to-Tolbi continuity failure report

Status: source-backed audit; dialogue and event logic not yet changed  
Branch: `dark-story-rewrite`  
Scope: the post-Manticore Lamakan sequence, Ash Jenna's later Tolbi encounter, the harbor child, and Ondra.

## Finding

The player's experience is not failing because of one awkward line. The current route introduces several major story concepts without establishing their relationships, and later scenes behave as though the party has not already learned information from earlier scenes. There are also concrete branch-state mismatches in Ondra's introduction.

This is a continuity repair, not a request to make the prose more ominous. The event order and the party's knowledge must be corrected before polishing individual sentences.

## Verified route and event behavior

1. **Lamakan Desert is before Kalay and Tolbi in the original route.** The Manticore is encountered before the Kalay visit and Karagol Sea crossing. The Ashfall post-Manticore sequence therefore occurs before the party reaches Tolbi and before Colosso.
2. **The post-Manticore return launches a large custom sequence automatically.** In `LamakanDesert_Initialize`, when the party returns from the Manticore battle (or the Manticore is already beaten), Mercury Lighthouse is lit, and the caravan sequence has not run, the game calls `LamakanDesert_MiaTakesOver()`. That event contains Mia's post-battle episode and the caravan choice, then sets `FLAG_DARK_CARAVAN_DONE`. The initializer then places Ash Jenna and calls `LamakanDesert_AshJennaFinale()` immediately. The finale sets `FLAG_DARK_FINALE_DONE`.
3. **That means the first meaningful Ash Jenna encounter is the Lamakan finale, not the short N106–N110 exchange in `phase35_lamakan_jenna.tsv`.** The actual automatic sequence uses N195 onward in `phase47_finale.tsv`. The short watch scene is not the dialogue the player receives on the normal post-Manticore return; after the finale flag is set, the actor is no longer placed for that first-meeting path. Any alternate path that might make N106–N110 reachable still needs to be checked before those rows are removed or repurposed.
4. **The party then continues to Kalay, crosses the Karagol Sea, reaches Tolbi, and completes Colosso.** Only after `FLAG_COLOSSO_OVER` and `FLAG_MERCURY_LIGHTHOUSE_LIT` does `Tolbi_ApplyEntryState` place Ash Jenna in Tolbi.
5. **Tolbi's Ash Jenna scene is written as though this is the first meeting.** `phase30_tolbi_ash_jenna.tsv` has Isaac ask, “Who are you?”, Garet challenge her as if the party has not met her, and Ash Jenna repeat her “Jenna who stopped waiting to be saved” line. But the party has already heard her identify herself in the Lamakan finale as a Jenna from a world the Wise One burned. The Tolbi scene must be a continuation: Isaac should recognize her, the party should refer to what she revealed, and her new purpose at the harbor should advance the story rather than restart the introduction.
6. **The fishermen line is an unanswered setup.** Ash Jenna asks what fishermen keep pulling out of the water, but the scene does not answer that question or clearly connect it to the harbor child who is introduced moments later. The later child is not explicitly what the fishermen have been finding. This is a dangling question, not an earned mystery yet.
7. **The harbor child is introduced as a sound cue inside the Tolbi Ash Jenna event.** After she fades, Ivan hears crying at the docks, Garet identifies it as a child's voice, and Mia dismisses it. The event sets `FLAG_DARK_HARBOR_CALLED`; the boy then appears in the separate Tolbi Docks scene. His actual line says voices are telling him to walk into the sea. The scene needs to establish why he hears the awakened, why he is at the docks, what the voices want, and why helping him matters to the larger tide / lighthouse plot.
8. **Ondra has two different activation routes, but only one unconditional introduction.** `Tolbi_ApplyEntryState` places Ondra if either `FLAG_DARK_HARBOR_SHELTERED` is set **or** all three of `FLAG_DARK_TIDE_ALTIN`, `FLAG_DARK_TIDE_IMIL`, and `FLAG_DARK_TIDE_TOLBI` are set. In other words, the child-rescue route can awaken her on its own, while the three local kindness payments can also awaken her without the child being sheltered.
9. **Ondra's current opening is wrong on the three-kindness route.** N102 in `phase33_ondra.tsv` says, “You went down to the docks for a stranger's child, and the tide noticed.” That is false if she appears because the player completed the three payments but did not shelter the child. The introduction must branch or use a cause-neutral opening. It must not attribute an action to Isaac that he may not have taken.
10. **Ondra's relationship to Mia is introduced without groundwork.** Her line “Mia comes from my tide, so we share a face” asserts a major connection, but the player has not been given a clear basis for it. The Tideglass Blade's voice, Mia's other self, the awakened, and Ondra's “tide” are currently arriving as separate terms instead of one understandable chain of cause and effect.

## Additional Lamakan mismatch

`phase34_mogall_lamakan.tsv` changes desert reactions to describe ankle-deep mud, water everywhere, ash-tasting water, and steaming ground. The source scene still models Lamakan as a heat-hazard desert: its comments and logic describe sand cells, a heat gauge, oases, and heat damage. If Ashfall intends the desert to be flooded or altered, the story and environment need to establish that transformation. Otherwise these lines contradict the place the player is looking at.

The same phase adds “Don't follow the lights at night. They're awake” to a Mogall sign. That may be a useful warning, but its meaning must be supported by the Mogall encounters and the party's subsequent discoveries, not left as an isolated ominous phrase.

## What must be repaired

### A. Lock the causal chain before rewriting

Write one canonical explanation, in plain language, for each of these and how they connect:

- What the lighthouses are doing to the awakened, and why lighting Mercury Lighthouse matters.
- What “the awakened” are, how they are connected to the Manticore, the caravan, the people in Mogall, and the voices Ivan hears.
- What the Tideglass Blade contains or represents, why Mia hears it, and why her behavior changes after the Manticore.
- Who Ash Jenna is, what she knows at Lamakan, what she wants at Tolbi, and why she is watching the harbor.
- What the fishermen are finding, what the harbor child hears, and how the child relates to Ondra.
- Why Ondra resembles Mia, what “my tide” means, and why either kindness route can wake her.

These explanations do not all need to be spoken aloud at once. They do need to be settled in the continuity ledger so every scene is written from the same story.

### B. Rewrite the route in actual play order

1. Mercury Lighthouse aftermath and the party's first exposure to the consequences of lighting it.
2. Mogall and Altin Peak: establish the awakened, the voices, and Ivan's growing sensitivity before using those terms as shorthand.
3. Lamakan / Manticore: make Mia's episode a consequence of what the party has already witnessed; give the caravan encounter a clear relationship to the awakened; then let Ash Jenna's revelation answer questions the route has deliberately raised.
4. Kalay and the Karagol crossing: preserve the original route and let the party carry the Lamakan revelation forward.
5. Tolbi after Colosso: Ash Jenna must acknowledge the Lamakan meeting and advance her plan. Resolve or deliberately defer the fishermen question.
6. Tolbi Docks: introduce the child as a consequence of the harbor situation, not as an unrelated new horror beat.
7. Ondra: provide distinct, truthful introductions for the child-rescue route and the three-kindness route, then explain the Mia connection in a way the player can understand.

### C. Protect the existing game

Do not alter original route flags, Colosso states, scene entrances, or battle behavior merely to make the dialogue fit. Preserve all ordinary NPCs, Mind Read, signs, examinations, shops, and conditional dialogue. Any proposed new branch dialogue or event change must be checked against the actual triggers and all player paths before implementation.

## Immediate rewrite blockers

- `phase35_lamakan_jenna.tsv` does not match the normal post-Manticore event path and must not be treated as the scene the player sees without further trigger verification.
- `phase30_tolbi_ash_jenna.tsv` repeats a first-meeting exchange after the Lamakan revelation.
- `phase33_ondra.tsv` contains a provably false child reference on the three-kindness activation route.
- `phase34_mogall_lamakan.tsv` describes a flooded/muddy desert without a corresponding established environmental explanation.
- `phase44_bloom.tsv`, `phase48_docks.tsv`, and the Tolbi / Tolbi Docks event code need to be read as one connected child sequence.
- The Mia / blade / awakened terminology needs one consistent introduction order across `phase42_manticore_mia.tsv`, `phase43_ivan.tsv`, `phase37_blade.tsv`, and `phase47_finale.tsv`.

No dialogue or event code is changed by this audit. The next safe edit is to establish the canonical causal chain and then rewrite the Tolbi follow-up and Ondra's two activation paths in small, validated batches.


## Canonical correction: Kegare, not Ondra

The character currently named Ondra is to be renamed **Kegare (穢れ, “impurity” / “defilement”)**. This is a cameo super boss from the user's sprite-animation continuity, in the same broad category as Heart. She is not a native Golden Sun sea goddess, a benevolent Tideglass Queen, or an entity awakened by the party's kindness.

### Established character truth

- Kegare is deliberately mimicking Mia.
- Her ultimate objective is to replace Mia.
- The resemblance is intentional and is the central source of unease; it is not a family resemblance or a shared elemental origin.
- She should be presented as an unsettling cameo super boss, with enough self-contained context for a Golden Sun player to understand the immediate threat. Her full origin and wider sprite-animation context should remain restrained rather than being dumped into the game's dialogue.
- Her appearance should feel like an intrusion from the larger sprite-animation continuity, as Heart does, without displacing the main Golden Sun plot.

### Consequences for the current rewrite

1. Remove the “Tideglass Queen,” “Mia comes from my tide,” and shared-face mythology. Those claims contradict the established premise.
2. Do not describe Kegare as being awakened by the child's rescue or by three kindnesses. Those choices may remain as optional conditions for discovering or gaining access to the encounter, but they are not her origin, motive, or source of power.
3. The harbor child must not be used as the explanation for Kegare's existence. If retained, his scene needs its own coherent purpose in the wider Ashfall plot; otherwise it should be audited separately rather than retrofitted into Kegare's backstory.
4. Reframe the optional kindness flags as encounter/access conditions only if the existing route and player experience support that design. They must not cause Kegare to claim that Isaac performed an action on a path where he did not.
5. Rewrite Kegare's dialogue around observation, imitation, and replacement. She should know Mia well enough to unsettle her, but should not explain every detail of her origin or reveal the entire sprite-animation plot.
6. Preserve her status as a cameo super boss: a memorable, optional or specially gated confrontation, not a new central antagonist who hijacks the Tolbi chapter.
7. The Ash Jenna / Heart continuity must remain separate. Heart and Kegare are distinct cameos with distinct purposes; do not merge their origins or imply that one is the other.

### Naming and localization

Use “Kegare” consistently as the character's display name and in documentation. The Japanese word 穢れ carries the sense of impurity, defilement, or ritual pollution; it is not simply a synonym for “evil.” Keep that nuance in mind when writing her characterization. The exact in-game name rendering should follow the project's text-width and naming conventions.

This correction supersedes the earlier speculative explanation of Ondra in this report. The prior audit remains useful for identifying the incorrect encounter timing and branch dialogue, but its “Tideglass Queen” interpretation is no longer canonical.
