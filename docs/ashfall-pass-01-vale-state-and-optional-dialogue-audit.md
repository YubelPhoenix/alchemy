# Ashfall Pass 01 — Vale State and Optional Dialogue Coverage Audit

Status: source inventory in progress; no dialogue changes in this pass  
Branch: `dark-story-rewrite`

## 1. Storm plaza optional dialogue

Source: `games/tbs/src/scene/vale_plaza.c`, `gValePlaza_StormActorTemplates`, `gValePlaza_StormTriggers`.

The storm plaza has six talkable optional actors before the mayor's dispatch event:
- Curious old man: a short event asking whether the party has seen anything interesting; his reply changes according to the yes/no choice.
- Old woman: says she cannot use Psynergy.
- Exhausted young man: says he spent his Psynergy deflecting falling rocks.
- Woman who has heard about Felix: reacts to the news that he fell into the river and connects it to Jenna's distress.
- Small boy: demonstrates lifting a small rock; the rock and shadow are separate visual actors.
- Little girl who saw Jenna: her event changes its response after the elders' aid dispatch flag is set.
- Garet's grandfather: has a separate talk line about racing against time.

The storm trigger table has **no Mind Read entries**. That is a verified source fact, not an omission in this inventory. The storm has the Psynergy Stone examination event and movement/dispatch triggers as well.

The two strongmen sent to the elders are actors in the storm template, but their lines belong to the mayor's event sequence, not ordinary talk triggers. The charged strongman is brought into the return-to-river sequence.

## 2. Vale plaza story states

The plaza does not have one interchangeable NPC set. Its actor and trigger tables are selected by story state:
- Ordinary day before departure.
- Storm night.
- Farewell at the town gate.
- After leaving Vale.
- Return after reaching Kalay.

The day and post-departure states include multiple Mind Read triggers. Those are not storm-night lines and must not be merged into the prologue. The post-departure state also has event-based dialogue for the curious old man and hut owner, in addition to ordinary talk rows. The farewell trigger table is empty because the farewell is driven by its event sequence rather than optional talk triggers.

This state separation is essential: the same sprite may have a different role, line, or trigger in each state.

## 3. Vale exterior story states

Source: `games/tbs/src/scene/vale.c`.

The exterior actor templates change for:
- Opening day before the party leaves.
- After the party leaves.
- Return after Kalay.
- The repair/roof sequence.

The day-state talk table includes the woman admiring Mt. Aleph, a woman speaking about Vale's purity, a girl jealous of Garet, a young man recalling the storm, a strongman warning Isaac away from the river, a man defending Vale's secrecy, a woman warning about the road beyond Kraden's cottage, Garet's sister, Garet's younger brother, Dora, and the Mt. Aleph guard. The corresponding state has additional step triggers, Psynergy interactions, and an examination event.

The post-departure and post-Kalay tables have their own dialogue and Mind Read rows. They must be audited independently rather than assuming a shared NPC script. The repair sequence also has a separate actor set and event dialogue.

## 4. Dialogue and technical issues flagged for review

These are audit flags, not automatic proof that every line is wrong:

- `MsgValeHearAwfulGrowls` (phase row 03958) ends without an explicit `{end_wait}` or `{end_now}` token in the TSV. Confirm whether this is an intentional message terminator convention or a malformed row before editing it.
- Phase-1 rows use generic key `message` for many sequential message IDs. The correct speaker and branch must be derived from the event call and sequential message offset, not guessed from the row label.
- Several lines contain actor-name, protagonist-name, or possessive placeholders. They need runtime expansion checks; a raw 27-character count is not enough.
- Some lines use `{page_break}`, `{pause_20_skippable}`, and `{text_effect:4}`. These tokens must be preserved and tested as control sequences.
- The post-storm dialogue states that Kyle died, while the storm scene stages him being swept away and not recovered on screen. The later village treats him as dead; preserve that established understanding, but do not make the storm-night children claim to have witnessed a confirmed body or rescue outcome.
- Vale's opening dialogue includes villagers who frame the storm through religious certainty, secrecy, guilt, and fear. The rewrite should preserve distinct attitudes rather than making every villager sound like the same narrator.
- Optional Mind Read text is part of the story's characterization and must receive the same grammar and continuity review as spoken dialogue.

## 5. Scope and next checks

This pass confirms the storm plaza has no Mind Read triggers and identifies the state tables that require separate coverage. It does not yet constitute a complete dialogue audit of all Vale scenes.

Remaining:
1. Extract every actor and trigger row for each Vale state into a message-to-speaker ledger.
2. Trace each event-based talk trigger to its exact message sequence and branch.
3. Audit Cottage Rooms A, including Garet's family, Jenna's grandparents, merchants, books, containers, and Mind Read.
4. Check all phase-1 and phase-2 rows against source calls, including gaps and sequential message IDs.
5. Resolve the row-03958 terminator and other control-token anomalies.
6. Complete grammar, chronology, voice, placeholder, and 27-character/rendered-width validation before rewriting.
