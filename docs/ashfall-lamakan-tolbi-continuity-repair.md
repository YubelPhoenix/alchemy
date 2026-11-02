# Ashfall: Lamakan-to-Tolbi continuity failure report

Status: initial source-backed audit; current verified repairs are recorded at the end of this document  
Branch: `dark-story-rewrite`

**Reading note:** the numbered findings and immediate blockers below record the pre-repair state. The verified repair section at the end supersedes them where they conflict with the current branch.  
Scope: the post-Manticore Lamakan sequence, Ash Jenna's later Tolbi encounter, and Kegare.

## Finding

The initial audit found more than isolated awkward lines: several concepts arrived without a clear causal order, and some dialogue contradicted the player's earlier knowledge. It also found a branch-state mismatch in the former Ondra/Kegare introduction. Those findings are retained below as the pre-repair record.

This is a continuity repair, not a request to make the prose more ominous. The event order and the party's knowledge must be corrected before polishing individual sentences.

## Verified route and event behavior

1. **Lamakan Desert is before Kalay and Tolbi in the original route.** The Manticore is encountered before the Kalay visit and Karagol Sea crossing. The Ashfall post-Manticore sequence therefore occurs before the party reaches Tolbi and before Colosso.
2. **The post-Manticore return launches a large custom sequence automatically.** In `LamakanDesert_Initialize`, when the party returns from the Manticore battle (or the Manticore is already beaten), Mercury Lighthouse is lit, and the caravan sequence has not run, the game calls `LamakanDesert_MiaTakesOver()`. That event contains Mia's post-battle episode and the caravan choice, then sets `FLAG_DARK_CARAVAN_DONE`. The initializer then places Ash Jenna and calls `LamakanDesert_AshJennaFinale()` immediately. The finale sets `FLAG_DARK_FINALE_DONE`.
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
- What “the awakened” are, how they are connected to the Manticore, the caravan, the people in Mogall, and the voices Ivan hears.
- Why Mia reacts with anger after the Manticore, recognizes that anger as her own, and accepts support from the party.
- Who Ash Jenna is, what she knows at Lamakan, what she wants at Tolbi, and why she is watching the harbor.
- What the harbor child hears and how that separate Ashfall thread develops after Tolbi.
- Why Kegare deliberately mimics Mia and intends to replace her, while keeping the kindness flags as encounter-access conditions only.

These explanations do not all need to be spoken aloud at once. They do need to be settled in the continuity ledger so every scene is written from the same story.

### B. Rewrite the route in actual play order

1. Mercury Lighthouse aftermath and the party's first exposure to the consequences of lighting it.
2. Mogall and Altin Peak: establish the awakened, the voices, and Ivan's growing sensitivity before using those terms as shorthand.
3. Lamakan / Manticore: make Mia's episode a consequence of what the party has already witnessed; give the caravan encounter a clear relationship to the awakened; then let Ash Jenna's revelation answer questions the route has deliberately raised.
4. Kalay and the Karagol crossing: preserve the original route and let the party carry the Lamakan revelation forward.
5. Tolbi after Colosso: Ash Jenna must acknowledge the Lamakan meeting and advance her plan. Resolve or deliberately defer the fishermen question.
6. Tolbi Docks: introduce the child as a consequence of the harbor situation, not as an unrelated new horror beat.
7. Kegare: preserve the two optional access routes without making either one her origin; her dialogue should establish imitation and replacement. Keep the harbor child as a separate story thread.

### C. Protect the existing game

Do not alter original route flags, Colosso states, scene entrances, or battle behavior merely to make the dialogue fit. Preserve all ordinary NPCs, Mind Read, signs, examinations, shops, and conditional dialogue. Any proposed new branch dialogue or event change must be checked against the actual triggers and all player paths before implementation.

## Immediate rewrite blockers

- `phase35_lamakan_jenna.tsv` is an optional talk on the Manticore pass; the normal post-Manticore return separately runs the automatic Mia/caravan sequence and Ash Jenna's main revelation.
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



## Verified finding: the post-Manticore caravan choice is not currently earned

The caravan sequence was checked against both `phase42_manticore_mia.tsv`, `phase46_awakening.tsv`, `phase47_finale.tsv`, and the actual `LamakanDesert_ManticoreAftermath` / `LamakanDesert_AshJennaFinale` event code in `games/tbs/src/scene/lamakan_desert.c`.

### 1. Mia's emotional progression jumps too sharply

Immediately after the Manticore, Mia says she wanted it dead and wishes it had suffered less. When Garet notices her reaction, she acknowledges that anger got the better of her and says it is not who she wants to be. Isaac reassures her, and Ivan observes that she is trying to hide how badly the encounter shook her.

The caravan scene then gives Mia this line:

> Turn back? Why? We could just burn them where they stand. It would be cleaner.

That is a much more extreme position than the anger she has just acknowledged. The current sequence does not show an intervening event, thought, or deterioration that would explain why she moves from regret to advocating the killing of forty frightened people. Ash Jenna later uses the remark against Mia in Tolbi, so the line becomes a defining character beat without sufficient development.

**Finding:** the problem is not that Mia is allowed to say something disturbing. It is that the story has not earned this particular escalation. The Manticore aftermath and caravan scene need to be revised together, with a visible emotional progression and a response from Mia that preserves her accountability.

### 2. The caravan prompt promises an outcome the event never shows

The prompt asks whether Isaac will try to calm the caravan. On the yes branch, Isaac says he will talk to them; Ivan says they are afraid of what is in their own heads; Mia warns Isaac that he will get himself killed. The event then moves directly to Mia taking point. There is no exchange with the caravan, no indication that anyone was calmed, and no result for the people themselves.

Despite that, the yes branch sets `FLAG_DARK_CARAVAN_CALMED`. The finale counts this flag as one of three mercy points and conditionally gives Ivan the line, “Forty of them were awake, and you walked in without drawing a weapon.” The event records Isaac's intention to help as though it were a successful act of mercy.

On the no branch, Isaac says they cannot help and tells the party to keep moving. Garet hears the caravan calling Isaac's name, and Mia says they should not stop for ghosts. No corresponding outcome flag is recorded.

**Finding:** the choice currently measures which response Isaac selected, not what happened to the caravan. The flag name and finale callback overstate the result. Either the scene must depict a meaningful consequence that justifies a mercy flag, or the flag/callback must be redesigned so an attempted intervention is not presented as a successful rescue.

### 3. Mia takes point regardless of Isaac's choice

Both branches converge on the same unconditional Mia line: “Keep up, Isaac. I'll walk point from here, because Kalay won't wait for us.” Garet then remarks that she did not look back.

The event code does not give the two choices distinct aftermaths beyond the yes branch's mercy flag and altered preceding dialogue. Mia takes point in either case. This makes the prompt feel more consequential than the actual scene behavior, and it leaves unclear whether Mia is protecting the party, avoiding the caravan, punishing Isaac for hesitating, or simply forcing the group onward.

**Finding:** the shared ending can remain if the story deliberately establishes why Mia takes point in both outcomes. Otherwise, the scene needs branch-specific reactions and a clearer emotional reason for her action.

### 4. The finale compounds the problem

Ash Jenna's finale follows automatically after the caravan event on the Manticore return. Mia is then asked to speak again, and her line is “Do it, Isaac. Then all of this will be over.” The player has just watched her advocate burning the caravan, so the line currently reinforces the same extreme position rather than revealing a new conflict or testing the limits of her anger.

The finale's mercy calculation currently uses three independent flags: the miner stayed with, the Mogall door opened, and the caravan-calmed flag. The code comment still mentions the removed harbor-child choice, which is stale documentation. The actual calculation is three points, but the caravan point is not presently supported by an observed outcome.

**Finding:** the caravan choice, Mia's role in the finale, and the mercy-ending threshold must be considered as one connected design. Rewriting only N185 or N193 would leave the underlying contradiction intact.

### Required repair before this sequence is considered complete

1. Revisit Mia's post-Manticore lines and the caravan scene as one continuous character arc.
2. Decide what the caravan choice actually does in the story. Do not label the outcome “calmed” unless the scene demonstrates that the people were calmed or helped.
3. Give the yes and no choices legible consequences, even if both paths eventually continue toward Kalay.
4. Establish why Mia takes point and what her action means in each branch.
5. Rework Mia's line in Ash Jenna's finale so it follows from the revised caravan scene rather than simply repeating the same extreme impulse.
6. Update stale event comments that still refer to the removed harbor-child choice.
7. Test both caravan branches and all combinations of the three mercy flags, including the resulting Complicit, Mercy, and Divided finale paths.

No dialogue, flags, or event logic were changed as part of this audit. This is a source-verified defect report and a blocker for treating the Lamakan-to-Tolbi narrative as complete.
