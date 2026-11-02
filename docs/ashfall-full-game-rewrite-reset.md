# Ashfall: Full-Game Rewrite Reset

Branch: `dark-story-rewrite`
Scope: the complete Golden Sun: The Broken Seal story, from the opening storm in Vale through the original ending and final ship departure.
Status: rewrite charter; implementation proceeds in chronological, source-verified passes.

## Purpose

The current rewrite has accumulated too many disconnected additions, revisions, and continuity patches. This reset establishes one coherent narrative baseline. The goal is not to preserve every line written in earlier phases. The goal is to produce one complete, readable, grammatically sound story that respects the original game's progression while integrating the Ashfall material deliberately.

## Non-negotiable principles

1. **The original game remains the spine.** Preserve its events, locations, character relationships, revelations, progression gates, and ending. Ashfall additions must fit around that spine; they must not accidentally replace or contradict it.
2. **Chronology comes from source code.** Follow scene scripts, event triggers, flags, actor templates, entrances, exits, and conditional states. Phase numbers and filenames are not chronology.
3. **Every player-facing line is in scope.** This includes mandatory dialogue, optional NPC conversations, Mind Read, signs, examinations, shops, guards, children, travelers, conditional variants, and post-event revisits.
4. **Character knowledge must be earned.** No one reacts to information before learning it. Track who is present, what they have witnessed, what they believe, and what remains unknown at each scene.
5. **Grammar and natural speech are release requirements.** Correct sentence structure, punctuation, tense, pronouns, line breaks, and conversational flow. Avoid awkward fragments unless the character or moment clearly calls for one.
6. **Darkness must have purpose.** Keep the mature, unsettling tone, but do not make every character speak in ominous abstractions. Give ordinary people ordinary voices and let horror emerge from events, consequences, and contrast.
7. **Do not preserve a broken scene for the sake of sunk cost.** Rebuild scenes whose premise, emotional progression, or branch logic is unsound. Preserve good material where it genuinely fits.
8. **Protect technical behavior.** Preserve message IDs, runtime tokens, control codes, placeholders, event structure, flags, rewards, battle behavior, and text-box limits unless a source-backed repair requires a deliberate change.
9. **No unverified completion claims.** A commit is not a build; a build is not a playthrough; a playthrough of one path is not branch coverage.

## Canonical route and rewrite passes

The rewrite will be performed in actual game order, with a continuity checkpoint at the end of each pass.

1. **Vale storm prologue and three-years-later opening:** storm events, homes, plaza, villagers, Garet, Jenna, Dora, Kraden, Sol Entrance and Sol Sanctum.
2. **Vale departure, Bilibin and Kolima:** post-eruption states, Bilibin, Treasury, Barricade, Kolima, Tret, forest, Mind Read and all curse-dependent dialogue.
3. **Imil and Mercury Lighthouse:** sick-village states, Mia's introduction, lighthouse progression, Aerie confrontation, healing fountain, Imil recovery and farewell.
4. **Bilibin riverbank and western journey:** Gang of Three, Jill rescue states, Mogall Forest, Xian, Altin, mine and water-beast progression.
5. **Altin Peak and Lamakan Desert:** miner rescue and aftermath, awakened/voice storyline, Manticore, Mia's aftermath, caravan choice, Ash Jenna's first revelation and all consequences.
6. **Kalay and Karagol Sea:** palace visits, Layana/Ivan state, crossing, ship events and transition to Tolbi.
7. **Tolbi, Colosso and Altmiller Cave:** festival states, Babi's absence and rescue, tournament progression, Colosso aftermath, Ash Jenna continuation, harbor storyline and optional Kegare access.
8. **Post-Tolbi journey:** Gondowan Passage, Suhalla, Babi Lighthouse and Lalivero, with all pre-/post-event variants.
9. **Venus Lighthouse and Aerie:** approach, puzzles, confrontations, battles, beacon sequence, Sheba's fall and the immediate aftermath.
10. **Return to Lalivero and finale:** Iodem's farewell, Black Orb, wharf, Lemurian ship, final scenes and ending.

The exact ordering of optional encounters and revisits will be confirmed against source triggers. This list is a route framework, not permission to move an event to a convenient phase.

## Ashfall continuity bible

Before a custom storyline is expanded, its core facts must be written once and kept consistent across every appearance. At minimum, track:

- the lighthouses, their effect on the awakened, and what lighting each beacon changes;
- the awakened, the voices Ivan hears, and the relationship between separate encounters;
- Ash Jenna's identity, history, knowledge, objective, and progression from Lamakan through Tolbi and later scenes;
- Mia's emotional progression, including the Manticore aftermath and her later decisions;
- the harbor child and the cause and consequences of the voices at Tolbi;
- Kegare's distinct identity and intention to imitate and replace Mia;
- Heart's distinct identity, purpose, battle, and dialogue;
- all branch choices, flags, callbacks, and ending consequences.

Do not conflate separate cameos or custom story threads to force a single explanation. Do not introduce an explanation in dialogue until the audience and characters have enough evidence to understand it.

## Required source-to-dialogue audit

For each scene, maintain a mapping of:
- original scene and source file;
- actor/template and trigger;
- message ID and current rewrite row;
- prerequisite and state flags;
- repeat/one-time behavior;
- party members present;
- character knowledge at that point;
- optional and Mind Read coverage;
- text controls, tokens, and box constraints;
- review status and validation evidence.

A scene is not complete until mandatory and optional player-facing dialogue have been compared against the source, not merely until its main cutscene reads well.

## Quality gates for every pass

**Narrative gate**
- The scene follows the original route and custom continuity.
- Character motivation and emotional transitions are credible.
- Dialogue is understandable on first reading and grammatically correct.
- Branches produce distinct, coherent outcomes and callbacks.
- No unresolved setup is accidentally presented as a resolved fact.

**Technical gate**
- Message IDs and event references resolve.
- Required tokens and control codes remain intact.
- TSV validation passes.
- Build workflow passes.
- Relevant event branches and state variants are exercised.

**Coverage gate**
- NPCs, Mind Read, signs, examinations, shops, and conditional dialogue are accounted for.
- No source-backed player-facing message is silently omitted.
- Re-entry and post-event states are checked.

## Working policy

- Audit first, then rewrite; do not make speculative bulk substitutions.
- Rewrite in manageable chronological batches and keep a clear record of what changed.
- Do not silently delete custom content. If it is contradictory, relocate, redesign, or mark it for a deliberate decision in the continuity notes.
- Do not change original game mechanics merely to make a line fit.
- Keep a list of known blockers and unresolved design questions; do not disguise them as finished work.
- Run validation after each meaningful batch and report exactly what passed and what remains untested.

## Definition of done

The full rewrite is complete only when the entire route from Vale to the final ending has been reviewed, all player-facing dialogue is accounted for, the custom story is internally consistent, the relevant branches and revisits have been tested, the build passes, and a full-game playthrough has confirmed that the story works in context.
