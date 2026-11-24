# Ashfall Pass 01 — Suhalla Gate checkpoint audit

Status: named checkpoint triggers and the sequential Iodem confrontation (09812–09830) are mapped and drafted; validator/build and in-game checks are pending.
Branch: `dark-story-rewrite`
Source: `games/tbs/src/scene/suhalla_gate.c`
Dialogue batch: `tools/dark_story/phase71_suhalla_gate_checkpoint.tsv`

## Scene chronology

The gate has two distinct states selected by `FLAG_BABI_SPOKE_AFTER_COLOSSO`.

1. **Before Babi's audience:** two soldiers stand in front of the north passage. Approaching the passage triggers `SuhallaGate_GuardsBlockPassage`; they move together and block the way. The west guard's normal talk is the request for help from Babi Lighthouse. Mind Read on the west guard is the ashamed thought about facing Iodem. Mind Read on the east guard is the wish to see Colosso next year. The east guard's talk is a short question about whether the party is going to Babi Lighthouse, followed by the original yes/no branches.
2. **After Babi's audience, before the attack has been confronted:** the actor table replaces the standing guards with wounded soldiers and adds the vanishing soldier and Iodem. The west guard's talk now uses the travel-papers line; the east guard's talk takes the wounded Colosso-victor line. The west guard's Mind Read changes to the thought about obeying Babi's orders; the east guard's Mind Read changes to the survivor's account of the attack.
3. **First approach to the blocked passage after the audience:** metatile behavior 10 triggers `SuhallaGate_IodemQuestionsGuards` once, gated by `FLAG_SUHALLA_GATE_ATTACK_SEEN`. Iodem steps out from the party, questions the guards, asks whether Felix was responsible, and rejoins the party. The event's yes/no choice and the conditional `FLAG_IODEM_MET_WOUNDED_SOLDIERS` branch must remain intact.
4. **The third wounded soldier:** talking to him or using Mind Read triggers `SuhallaGate_SoldierVanishes` until `FLAG_SUHALLA_GATE_SOLDIER_VANISHED` is set. He warns that Venus Lighthouse was attacked, flickers, and disappears. This is a separate event from Iodem's questioning of the two guards.
5. **Travel and return behavior:** the party can enter the checkpoint from the south or east. The scene records the entry side for Retreat from the house, then clears that remembered side when leaving for the World Map. After Iodem's questioning, defeat returns the party to the house beside the gate. Do not rewrite dialogue in a way that implies the party has already reached Babi Lighthouse or Venus Lighthouse before the source event says so.

## Named message coverage

All nine named message references in `gSuhallaGateTriggersOther` have rows in phase 71:

| Message ID | Source role / trigger |
| --- | --- |
| 09805 | West guard asks for travel papers after Babi's audience |
| 09806 | East guard asks whether the party is going to Babi Lighthouse |
| 09810 | West guard's post-audience Mind Read: obedience to Babi's orders |
| 09811 | East guard's pre-audience Mind Read: regret at missing Colosso |
| 09812 | Iodem's opening confrontation when he sees the wounded guards |
| 09831 | West guard's ordinary talk: asks the party to send help from Babi Lighthouse |
| 09832 | East guard's post-attack talk: injured Colosso victor vows to settle the score |
| 09833 | West guard's pre-audience Mind Read: shame at facing Iodem |
| 09834 | East guard's post-attack Mind Read: account of surviving the attack |

The trigger conditions matter. In particular, 09810/09811 and 09833/09834 are not generic alternate thoughts: the source switches them according to `FLAG_SUHALLA_GATE_ATTACK_SEEN`. The west guard's ordinary talk also switches between 09831 and 09805 according to that flag. The east guard's talk is an event with yes/no branches before the attack is confronted, then a single wounded-state line afterward.

## Sequential Iodem confrontation now covered

The source event advances through the generic message IDs 09813–09830 after the named opening line 09812. Those 18 sequential entries were absent from the earlier phase 71 draft. They have now been added in source order, preserving the original `{pause_20_skippable}` counts, `{end_wait}` / `{end_now}` controls, and `{actor_name:5}`, `{actor_name:7}`, and `{actor_name:1}` placeholders. The dialogue follows the actual event beats: the guards recognize Iodem, describe the paperless group and their powers, Iodem identifies the likely culprit, the party discusses finding Sheba and pursuing the attackers, and the wounded soldiers insist the party continue.

The separate vanishing-soldier event uses the shared `MsgFieldVenusLighthouseWasAttackedBy`; do not duplicate it as a Suhalla-specific message without first checking the shared-message phase index.

A source-catalogue check of all 27 phase 71 rows confirms matching message contexts, all original brace-delimited controls and runtime placeholders, no page over three lines, and no line over the 27-character validator limit (dynamic actor names reserved at eight characters). This is a local structural check; the GitHub Actions run must still complete before the batch is called build-validated.

## Quality and implementation constraints

- Keep the gate's before-/after-audience dialogue states distinct.
- Preserve Iodem's yes/no choice and the conditional branch tied to `FLAG_IODEM_MET_WOUNDED_SOLDIERS`.
- Do not conflate the Iodem confrontation with the vanishing soldier's warning.
- Do not change flags, actor placement, metatile triggers, entrance/exit routing, Retreat behavior, or battle restart behavior as part of dialogue work.
- The nine named rows in phase 71 are a dialogue draft, not yet proof of validator success, a successful build, or in-game progression.
- After the sequential offsets are mapped, check the lines for grammar, natural speech, chronology, and text-box fit, then run the dialogue validator and full build. Test both sides of the audience flag, the east guard's yes/no choices, the one-time Iodem confrontation, both Mind Read states, and the vanishing soldier's talk/Mind Read behavior in-game.
