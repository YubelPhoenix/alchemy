# Ashfall Pass 01 — Vale Storm Dialogue-to-Event Map

Status: source mapping in progress; no dialogue rewrite or event logic change in this pass  
Branch: `dark-story-rewrite`  
Sources checked:
- `games/tbs/src/scene/vale_stormy_night.c`
- `games/tbs/src/scene/vale_plaza.c`
- `tools/dark_story/phase1_vale.tsv`

## Findings: Isaac's dialogue and speaker presentation

The storm scene uses `ACTOR_PARTY_LEADER` as Isaac's moving actor in event choreography. That alone does **not** make a message an Isaac line. The event must explicitly pass the intended speaker to the message command.

A concrete example is `ValeStormyNight_GaretFollowsIsaac`: it sets `MsgValeIsaac`, then calls `Event_ShowMessage(SPEAKER_PORTRAIT_LEFT | ACTOR_GARET_CHILD, 0)`. The speaker is Garet, not Isaac. The following two message calls also use Garet. This sequence must not be mistaken for an existing Isaac speaking convention.

The riverbank event `ValeStormyNight_DoraGoesForHelp` uses `ACTOR_PARTY_LEADER` for movement and reaction, while the displayed dialogue is explicitly assigned to Dora or Jenna. It also contains two existing player yes/no decisions. These are natural places to preserve player agency, but the current event does not establish that arbitrary leader-attributed dialogue is supported.

**Implementation decision:** do not add an Isaac speaker call until the message system's speaker encoding and a working in-game example are confirmed. The current evidence supports Isaac's actor participation and player choices, not yet a safe new portrait/speaker convention.

## Event-to-dialogue map

### 1. Dora sends Isaac toward the plaza

Function: `ValeStormyNight_DoraSendsIsaacToThePlaza`

The source explicitly sequences Dora asking Kyle whether the elders can stop the Boulder; Kyle answers; Dora and Kyle discuss evacuating villagers; Dora offers to help; Kyle refuses because it is dangerous; Dora tells Kyle Isaac can reach the plaza; Dora asks Isaac whether he knows the way. A repeated yes/no prompt makes Dora reassure him before he leaves south. Dora and Kyle then run north.

The hooded figure appears only after Isaac turns south, stands behind him, waits, and disappears. It has no dialogue. Do not assign it an identity or motive here.

**Rewrite constraint:** keep Isaac a child and do not give him adult hindsight. The existing yes/no response is the player's direct participation; it should not be replaced with a long monologue.

### 2. The shoving villager

Function: `ValeStormyNight_BumpIntoShovingMan`

Triggered when Isaac tries the south door of Cottage Rooms A. The man knocks him back, recognizes him, asks whether he came back, and then tells him to move because he is trying to escape.

**Rewrite constraint:** this is a brief collision during evacuation, not a full conversation. Keep the man frightened and abrupt without turning him into a villain.

### 3. Garet and the chest

Function: `ValeStormyNight_GaretLeavesHisChest`

The event presents a player yes/no choice. One branch asks whether Garet should leave his belongings; the other frames the danger of being struck while dragging a chest. Garet's response is branch-specific, but both routes have him abandon the chest and join Isaac.

**Rewrite constraint:** preserve the two distinct player responses and Garet's corresponding acceptance. Do not make the chest follow the party or alter the join flag.

### 4. Dora and Jenna seek help at the river

Function: `ValeStormyNight_DoraGoesForHelp`

Dora and Jenna run through the riverside house. Dora returns, sends Jenna north toward the plaza, and then asks Isaac and Garet to help. The event has two separate yes/no decisions: whether the boys will go after Jenna, and whether they will help Dora. The boys are sent toward the plaza in either case; the refusal branch changes Dora's response, not the underlying rescue progression.

**Rewrite constraint:** the refusal response cannot claim the boys remain behind or that Felix is abandoned. Their next action remains leaving to get help. Isaac's player choices should reflect that event logic.

### 5. Boulder sweeps downriver

Functions: `ValeStormyNight_BoulderSweepsThemAway` and `ValeStormyNight_ShowBoulderSweepingDownriver`

The source stages the party at the riverbank, shows the Boulder descending, freezes the image with lightning flashes, then redraws the riverbank without Felix, Jenna's parents, or Kyle. This is the irreversible loss event.

**Rewrite constraint:** do not place rescue dialogue after the impact as if the family remains reachable. Do not let anyone know the precise fate of the missing people before the event establishes it.

### 6. Garet follows Isaac

Function: `ValeStormyNight_GaretFollowsIsaac`

After the Boulder has swept the riverbank, Garet refuses to let Isaac go alone. The message ID `MsgValeIsaac` is spoken by Garet via `SPEAKER_PORTRAIT_LEFT | ACTOR_GARET_CHILD`. It is not an Isaac line.

**Rewrite constraint:** Garet's decision is an important character beat and should remain his. Do not reassign his message to Isaac.

### 7. Strangers and the aftermath

The Vale Plaza source comment and event path place the strangers' conversation only after the river tragedy and after Garet catches up. Isaac overhears two survivors of Sol Sanctum; the game does not name them until three years later. The battle occurs after this exchange. Win or loss leads to the same unconscious aftermath and end of the storm.

**Rewrite constraint:** do not identify Saturos and Menardi in the childhood scene, and do not make the battle result alter the established aftermath.

## Initial 27-character layout check

A programmatic pass over 139 non-empty phase-1 rows in the storm message range (IDs 03666–03815) found no explicit text line longer than 27 characters after:
- interpreting literal `\\n` as a line break;
- interpreting `{page_break}` as a line break;
- excluding brace-delimited control tokens and placeholders from the raw visible-text count.

This is only a preliminary raw-text check. It does **not** prove that every rendered line fits: actor-name and possessive placeholders expand to runtime text, and the font uses rendered width rather than character count alone. Those expansions and actual in-game rendering still require validation.

## Open checks before dialogue edits

- Confirm the exact speaker encoding supported for Isaac, including portrait and non-portrait presentation.
- Find a verified working event elsewhere that displays a message with `ACTOR_PARTY_LEADER` as speaker, or inspect the message system implementation and event command contract.
- Resolve the missing/unused message-ID gaps in this storm range against the source and message table before treating every phase row as live.
- Map every generic `message` row to its precise event call, actor, branch, and trigger.
- Check all NPC, Mind Read, sign, examination, and revisit-state rows across the remaining Vale phase files.
- Expand placeholders and validate rendered width.
- Only then draft and merge the storm dialogue; no event flags or event logic should be altered without a separately reviewed repair plan.
