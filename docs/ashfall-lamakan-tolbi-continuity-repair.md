# Ashfall: Lamakan-to-Tolbi continuity failure report

Status: historical source-backed audit; superseded decisions are recorded below  
Branch: `dark-story-rewrite`

**Reading note:** the numbered findings and immediate blockers below record the pre-repair state. The harbor-child decision in the canonical correction section and the caravan-removal decision at the end supersede all earlier references to those storylines.  
Scope: the post-Manticore Lamakan sequence, Ash Jenna's later Tolbi encounter, and Kegare.

## Finding

The initial audit found more than isolated awkward lines: several concepts arrived without a clear causal order, and some dialogue contradicted the player's earlier knowledge. It also found a branch-state mismatch in the former Ondra/Kegare introduction. Those findings are retained below as the pre-repair record.

This is a continuity repair, not a request to make the prose more ominous. The event order and the party's knowledge must be corrected before polishing individual sentences.

## Verified route and event behavior

1. **Lamakan Desert is before Kalay and Tolbi in the original route.** The Manticore is encountered before the Kalay visit and Karagol Sea crossing. The Ashfall post-Manticore sequence therefore occurs before the party reaches Tolbi and before Colosso.
2. **The post-Manticore return launches Mia's aftermath and Ash Jenna's finale automatically.** In `LamakanDesert_Initialize`, when the party returns from the Manticore battle (or the Manticore is already beaten), Mercury Lighthouse is lit, and the aftermath has not run, the game calls `LamakanDesert_ManticoreAftermath()`. The initializer then places Ash Jenna and calls `LamakanDesert_AshJennaFinale()` immediately. The aftermath and finale each have a completion flag.
3. **That means the first meaningful Ash Jenna encounter is the Lamakan finale, not the short N106–N110 exchange in `phase35_lamakan_jenna.tsv`.** The actual automatic sequence uses N195 onward in `phase47_finale.tsv`. The short watch scene is not the dialogue the player receives on the normal post-Manticore return; after the finale flag is set, the actor is no longer placed for that first-meeting path. Any alternate path that might make N106–N110 reachable still needs to be checked before those rows are removed or repurposed.
4. **The party then continues to Kalay, crosses the Karagol Sea, reaches Tolbi, and completes Colosso.** Only after `FLAG_COLOSSO_OVER` and `FLAG_MERCURY_LIGHTHOUSE_LIT` does `Tolbi_ApplyEntryState` place Ash Jenna in Tolbi.
5. **Tolbi's Ash Jenna scene is written as though this is the first meeting.** `phase30_tolbi_ash_jenna.tsv` has Isaac ask, “Who are you?”, Garet challenge her as if the party has not met her, and Ash Jenna repeat her “Jenna who stopped waiting to be saved” line. But the party has already heard her identify herself in the Lamakan finale as a Jenna from a world the Wise One burned. The Tolbi scene must be a continuation: Isaac should recognize her, the party should refer to what she revealed, and her new purpose at the harbor should advance the story rather than restart the introduction.
6. **The fishermen line is an unanswered setup.** Ash Jenna asks what fishermen keep pulling out of the water, but the scene does not answer that question or clearly connect it to the harbor child who is introduced moments later. The later child is not explicitly what the fishermen have been finding. This is a dangling question, not an earned mystery yet.
7. **The harbor child is introduced as a sound cue inside the Tolbi Ash Jenna event.** After she fades, Ivan hears crying at the docks, Garet identifies it as a child's voice, and Mia dismisses it. The event sets `FLAG_DARK_HARBOR_CALLED`; the boy then appears in the separate Tolbi Docks scene. His actual line says voices are telling him to walk into the sea. The scene needs to establish why he hears the awakened, why he is at the docks, what the voices want, and why helping him matters to the larger tide / lighthouse plot.
8. **Kegare has two different encounter-access routes.** `Tolbi_ApplyEntryState` places Kegare if either `FLAG_DARK_HARBOR_SHELTERED` is set **or** all three of `FLAG_DARK_TIDE_ALTIN`, `FLAG_DARK_TIDE_IMIL`, and `FLAG_DARK_TIDE_TOLBI` are set. These are optional access conditions only; neither is the source of Kegare's identity or power.
9. **The former Kegare opening falsely attributed the child rescue to Isaac.** That line has been removed. The current Kegare dialogue in `phase33_kegare.tsv` focuses on observation, imitation, and replacement without claiming that the player took the child to safety.
10. **Kegare's resemblance to Mia is intentional imitation, not shared mythology.** Kegare studies Mia's voice and movements because she intends to take Mia's place. She is a distinct cameo from the user's wider sprite-animation continuity; she is not connected to the harbor child or to Mia through a shared tide.

## Additional Lamakan mismatch

`phase34_mogall_lamakan.tsv` changes desert reactions to describe ankle-deep mud, water everywhere, ash-tasting water, and steaming ground. The source scene still models Lamakan as a heat-hazard desert: its comments and logic describe sand cells, a heat gauge, oases, and heat damage. If Ashfall intends the desert to be flooded or altered, the story and environment need to establish that transformation. Otherwise these lines contradict the place the player is looking at.

The same phase adds “Don't follow the lights at night. They're awake” to a Mogall sign. That may be a useful warning, but its meaning must be supported by the Mogall encounters and the party's subsequent discoveries, not left as an isolated ominous phrase.

## What must be repaired

### A. Lock the causal chain before rewriting

Write one canonical explanation, in plain language, for each of these and how they connect:

- What the lighthouses are doing to the awakened, and why lighting Mercury Lighthouse matters.
- What “the awakened” are, how they are connected to the Manticore, the people in Mogall, and the voices Ivan hears.
- Why Mia reacts with anger after the Manticore, recognizes that anger as her own, and accepts support from the party.
- Who Ash Jenna is, what she knows at Lamakan, what she wants at Tolbi, and why she is watching the harbor.
- What the harbor child hears and how that separate Ashfall thread develops after Tolbi.
- Why Kegare deliberately mimics Mia and intends to replace her, while keeping the kindness flags as encounter-access conditions only.

These explanations do not all need to be spoken aloud at once. They do need to be settled in the continuity ledger so every scene is written from the same story.

### B. Rewrite the route in actual play order

1. Mercury Lighthouse aftermath and the party's first exposure to the consequences of lighting it.
2. Mogall and Altin Peak: establish the awakened, the voices, and Ivan's growing sensitivity before using those terms as shorthand.
3. Lamakan / Manticore: make Mia's episode a consequence of what the party has already witnessed, then let Ash Jenna's revelation answer questions the route has deliberately raised.
4. Kalay and the Karagol crossing: preserve the original route and let the party carry the Lamakan revelation forward.
5. Tolbi after Colosso: Ash Jenna must acknowledge the Lamakan meeting and advance her plan. Resolve or deliberately defer the fishermen question.
6. Tolbi Docks: introduce the child as a consequence of the harbor situation, not as an unrelated new horror beat.
7. Kegare: preserve the two optional access routes without making either one her origin; her dialogue should establish imitation and replacement. Keep the harbor child as a separate story thread.

### C. Protect the existing game

Do not alter original route flags, Colosso states, scene entrances, or battle behavior merely to make the dialogue fit. Preserve all ordinary NPCs, Mind Read, signs, examinations, shops, and conditional dialogue. Any proposed new branch dialogue or event change must be checked against the actual triggers and all player paths before implementation.

## Immediate rewrite blockers

- `phase35_lamakan_jenna.tsv` is an optional talk on the Manticore pass; the normal post-Manticore return separately runs Mia's aftermath and Ash Jenna's main revelation.
- `phase30_tolbi_ash_jenna.tsv` has been rewritten as a continuation of the guaranteed Lamakan revelation.
- `phase33_kegare.tsv` now focuses on Kegare's Mia imitation and replacement intent, with no false child-rescue claim.
- `phase34_mogall_lamakan.tsv` has been corrected to match Lamakan's heat, sand, dust, and ash-thick air.
- `phase44_bloom.tsv`, `phase48_docks.tsv`, and the Tolbi / Tolbi Docks event code have been reviewed as one connected child sequence; that sequence remains separate from Kegare.
- Mia's post-Manticore emotional arc is simplified; no sentient blade, second self, or possession explanation remains in the current story.

The initial audit itself did not change dialogue or event code. Subsequent dialogue corrections and source-backed clarifications are recorded in the verified repair section below.


## Canonical correction: Kegare, not Ondra

The character previously named Ondra is **Kegare (穢れ, “impurity” / “defilement”)**. This is a cameo super boss from the user's sprite-animation continuity, in the same broad category as Heart. She is not a native Golden Sun sea goddess, a benevolent Tideglass Queen, or an entity awakened by the party's kindness.

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


### Current build verification

Run 358 passed every workflow stage on commit `d3fe8b2bd35369c93a4e078fb37f7587944c62f9`, including dialogue validation, modified-edition compilation, baseline verification, IPS generation, and test-patch upload. This validates the current Aerie sequential-dialogue additions and the width correction; it does not replace in-game progression checks.


## Canonical decision: remove the harbor child; move Kegare after Colosso

This section supersedes the earlier harbor-child and Kegare access-route findings above.

### Harbor-child storyline removed

The harbor-child storyline is removed in full. The Tolbi Ash Jenna event no longer hears or introduces a crying child; Tolbi Docks no longer spawns or hosts the custom child actor or interaction; Mogall no longer branches on whether the child was sheltered or left behind. The associated dialogue rows and dedicated flags have been retired. The original Tolbi festival family's child remains part of the unmodified town population and is unrelated to the removed custom storyline.

### Kegare's revised encounter

- Kegare is a demon from another age who has taken Mia's visage.
- She intends to replace Mia; her resemblance is deliberate imitation, not a shared origin.
- She is an optional cameo superboss and appears in Tolbi only after `FLAG_COLOSSO_OVER`.
- Her appearance no longer depends on the harbor-child choice or the three Tide Shard kindness flags. Those kindness events remain independent side content.
- Her opening now identifies her as a demon from an age long past. Mia directly rejects the claim that wearing her face grants Kegare her identity or place among the party.
- The encounter continues to use the existing scripted battle slot and return-to-Tolbi behavior. The battle must still be tested for both victory and defeat: defeat should leave Kegare available to challenge again; victory should mark her beaten and prevent another appearance.

### Verification still required

The source and dialogue edits are committed, but this decision is not considered build-verified until the dialogue validator and full modified-edition workflow pass. A successful compile also does not replace in-game checks of the post-Colosso appearance, Mia's dialogue sequence, and retry/defeat behavior.



## Canonical decision: remove the caravan storyline

The caravan awakening sequence has been removed from the story and implementation. It is not a branch, a mercy choice, or part of Mia's post-Manticore character arc.

The post-Manticore return now has a simpler sequence: Mia's existing aftermath plays once, then Ash Jenna's revelation/finale begins automatically. The obsolete phase46_awakening.tsv dialogue file has been deleted. The caravan dialogue, choice, callback, and mercy flag have been removed from the event flow. The existing FLAG_DARK_MIA_MANTICORE_SEEN flag now gates the one-time aftermath; no separate caravan or aftermath completion flag is needed.

The Lamakan confrontation now has one clear choice: accept or refuse Ash Jenna's offer to confront the Wise One. Staying with the injured miner is remembered as a character choice but does not determine the finale branch. Mia no longer leaves the party because of that earlier decision.

This removal is intentional. Do not restore the caravan, its dialogue, its flag, or its finale callback when continuing the Lamakan rewrite. The Manticore aftermath and Ash Jenna's reveal should carry the story forward without it.


## Canonical decision: remove the Bloom and its dependent storyline

The Bloom, awakened/sleeper mythology, and supernatural voice-hearing plot have been removed from the current story. The earlier findings in this report that discuss those concepts are historical audit notes and are superseded by this decision.

The Mogall keeper/camp encounter and its associated Alex appearance have been removed. Alex's custom Altin Peak appearance has also been removed because it served only to foreshadow the discarded Bloom plot. The Mogall sign no longer contains an unexplained warning about lights being awake.

Altin Peak's trapped-miner encounter remains as a grounded rescue after a mine collapse. The supports fail, miners are trapped behind rubble, and water is rising. Mia's hesitation now comes from the danger of causing another collapse, not from fear that the miners will transform. After the rescue, Isaac may stay with an injured miner while he recovers. There is no grey transformation or supernatural aftermath.

Ivan does not hear the thoughts or voices of the awakened. His dialogue now reflects ordinary observation: he notices Ash Jenna's attempt to frighten the party and warns that the rising water is reaching the trapped miners.

Ash Jenna's conflict is now personal and direct. She says the Wise One destroyed the world she came from and asks Isaac to help her confront him. The story treats this as her account and her motive, not as an explanation of a new supernatural system. The Tolbi scene continues that conflict without sleepers, awakened people, harbor voices, or lighthouse doors.

Isaac's response to Ash Jenna is a straightforward accept/refuse choice. The miner's recovery choice is a separate character moment. The discarded Mogall door choice, its callback, the supernatural Ivan material, and the divided ending in which Mia leaves have been removed. Do not restore those elements.
