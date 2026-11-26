# Golden Sun: Ashfall — current narrative canon

Status: consolidation of the author's explicit decisions and the currently implemented story, not approval of any new lore. Baseline: 9c635b3bea86b9ba3456f3f2a8b95cd3ade00072. Latest author instructions take precedence over historical design documents. This file distinguishes established facts, character claims, and unresolved questions. Do not treat a hypothesis or a testing placement as a new canon fact.

## 1. The story's foundation

- Golden Sun: The Broken Seal remains the spine, including the storm, Sol Sanctum, the stolen Stars, Jenna and Kraden's capture, Mercury Lighthouse, the Kolima curse, Ivan's origins and obligation, Babi's search for Lemuria, Colosso, Sheba's capture, Venus Lighthouse and the original ending.
- The returning power of Alchemy and the gradual deterioration of Weyard provide the atmosphere. The present renderer starts rain in opt-in scenes after Mercury Lighthouse lights; global ash tint is disabled. Local effects of the original volcanic eruption and ordinary local concerns are not forbidden.
- Ordinary citizens, shops, children, travelers and original side stories remain recognizable. Do not invent universal ash contamination, mass death, possession or supernatural causes simply to darken a line.
- Original base dialogue is the fallback when a rewrite is obsolete. Keep the original progression, names, choice logic, gameplay hints and the party's knowledge. Do not replace a removed storyline with another invented one.

## 2. Established custom characters

### Ash Jenna
The evil alternate Jenna from the author's sprite animation. She lost her world, is cruel and unrepentant, and fears abandonment. Her claim concerning the Wise One is her own belief, not independently proven by Isaac. Her hostility toward the party and its bonds is intentional. Her permanent Vale superboss placement is an author decision; do not move it. Existing Lamakan, Tolbi, Suhalla and Lalivero scenes are implemented and remain untouched unless the author separately approves changing their presence or dialogue. The current Suhalla medicine incident is retained; it is not a new recruitment or redemption arc.

### ???
Keep the original protected dialogue in phase118_mystery_leader.tsv and approved_mystery_prebattle.txt, and the fight-together battle dialogue. Her Vale placement is temporary for testing and is not her intended final story location. Prior encounters/attempts are presumed for the approved test exchange; optional bosses have no required defeat sequence. Do not rewrite her approved lines to accommodate a temporary location. Her identity remains undisclosed; she is interested in Isaac as the original and in the properties of his Psynergy. Heart answers to her. Her Rift research concerns stabilizing a passage; do not state that she intends to return to her destroyed home world. The precise thing she seeks and destination remain undisclosed, not license to invent one.

### Heart
Chalice from Dark Dawn, using her Japanese name in the author's sprite animation. Her trauma and hatred concern Matthew and the disfigurement he caused, not an act committed by Isaac. She mistakes Isaac for Matthew. Her prior relationship to ???, the Apollo Lens history involving Spade and Ace/Alex, and her command relationship are part of the current Rift exchange. Do not merge her with Ash Jenna or Kegare. Do not reveal ???'s identity to explain her.

### Kegare
Independent demon who deliberately wears Mia's face to deceive and replace her. The approved ??? dialogue also describes her loneliness and desire for companionship. No Tideglass Queen, shared-tide origin, kindness-gated awakening or harbor-child connection. Keep the current post-Colosso optional encounter in Vault unless the author decides otherwise.

### Sarah
A knight searching for a lost family member, following rumors. Current four encounters: Vault, Kalay, Tolbi and Lalivero. Sheba is a meaningful clue; current player-facing text does not confirm the relationship. Do not assert the precise family relationship or that she has found Sheba. The November 24 writer-only notes asserted Sheba as the relative, while later player-facing text restores uncertainty; preserve that distinction and do not resolve any remaining author-only ambiguity without approval.

### Vengeful Wraith
The alternate-world Karis in the implementation, not named as Karis to the player. Her hatred of Ivan is intentional; her final revelation ("Dad...") is protected. The party cannot know the precise history or relationship before the encounter reveals it. Do not change her final words to explain the plot. The encounter is separate from Heart and Kegare.

## 3. Umbral Rift

A tear involving familiar locations from different worlds/eras; atmosphere should emerge from recognizable spaces with disturbing changes. Current rooms: Fountain, Crossbone, Maze, Memory (Isaac's house), optional Ritual/Wraith, Causeway, Beacon, Throne and the return to the fountain. Preserve the disturbing ritual mark and silhouettes. Dialogue must not describe unverified map features. The source establishes that ??? studies the breach, Heart senses weak points, Isaac's Psynergy stabilizes it during battle, and the anchor can be closed without claiming all rooms cease to exist. The destination and ultimate objective are unresolved. Existing "in Vale" references in the Rift are relocation-dependent and are not a reason to change the protected test encounter now.

## 4. Retired content — never resurrect

Bloom; sleeper/awakened faction or cosmology; phantom Ivan voices; custom Mogall keeper/camp and its Alex cameo; custom Altin Alex cameo; caravan awakening and mercy branches; harbor child; Tide Shard kindness gates; Tideglass Queen/shared-tide lore; sentient blade, Mia possession/anger and departure subplot; Isaac's recruitment/accept-refuse pact with Ash Jenna; trapped-miner rescue, staying with the miner and its callback; separate retired Mia/Tolbi and Manticore follow-ups; obsolete global-apocalypse NPC overlays.

The original game's Psynergy Stones, original Hammet caravan, canonical NPCs, original water beasts, original Djinn and ordinary uses of words like "awakening" are not retired material. Reserved flags/message slots may remain for compatibility; they must not be given new narrative meaning or made reachable.

## 5. Approval and validation

- Source-backed cleanup of clearly obsolete ordinary NPC overlays may restore original catalogue text; approved custom dialogue is not editable without explicit permission.
- Do not expand character histories, relocate superbosses, add progression restrictions, alter map geometry, add fights, or modify gameplay to "fix" a story without the author's approval.
- Review actual source trigger, speaker, party members, flags, order, and both outcomes of choices. A named message may be sequentially invoked even if no direct symbol reference exists.
- Static source review, full catalogue scan, compiled ROM, and emulator verification are separate gates. Do not certify untested paths. Never initiate, cancel, rerun or modify a build/workflow without explicit author authorization.

## 6. Sources

- Author's current decisions: Ash Jenna stays in Vale; ??? in Vale is testing-only; miner is retired; old concepts must be removed, not reintroduced.
- tools/dark_story/approved_mystery_prebattle.txt; phase118_mystery_leader.tsv; phase_fight_together.tsv; phase38_heart.tsv; phase33_kegare.tsv; phase80_sarah.tsv; phase_karis.tsv; phase47_finale.tsv; phase30_tolbi_ash_jenna.tsv; phase76_lalivero_ash_jenna_coda.tsv; phase77_ash_jenna_fights.tsv; phase120_umbral_rift.tsv.
- games/tbs/src/scene/umbral_rift.c, vale.c, vault_revisit.c, lamakan_desert.c, tolbi.c, suhalla_gate.c, lalivero.c; games/tbs/include/world_state.h.
- tools/dark_story/CONTINUITY_LEDGER.md (historical, especially the November 14 superseding entry); docs/ashfall-full-game-rewrite-reset.md and docs/ashfall-narrative-cohesion-2026-11-24.md (historical where superseded).
