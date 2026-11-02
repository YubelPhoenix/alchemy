# Ashfall Pass 01 — Kraden's Cottage and Sol Sanctum Opening Audit

Status: source-mapped; dialogue rewrite and event changes pending  
Branch: `dark-story-rewrite`

## A. Kraden's cottage: story states and scene order

Source: `games/tbs/src/scene/vale_kradens_cottage.c`.

The cottage approach is not one static scene. Its actor placement and trigger behavior change with the story:

1. **Storm night.** The rockslide has broken the fence and monsters have entered the area. Two immovable rocks block the route. A wounded survivor lies by the fence. Talking to him or walking up to him triggers the same event. Two cells each start a one-time monster battle. The survivor's yes/no response is consequential: one route has him give up; the other has him discover he is not badly hurt, warn the party about monsters heading toward the plaza, and flee. These outcomes set separate flags.
2. **Three years later, before the party leaves.** Saturos and Menardi stand outside the cottage. Walking past them triggers the overheard conversation, the children's confrontation, and their release. The event sets `FLAG_MET_SATUROS_AND_MENARDI`. Near the cottage, the party can overhear Kraden wondering what the strangers know about the Elemental Stars. Talking to Kraden starts the secret Sol Sanctum visit plan.
3. **After the party leaves Vale.** The little boy at the fence has changed his intention to climbing it someday. Kraden and the strangers are gone.
4. **After Kalay.** A fair-haired woman visits the empty cottage and reflects on Kraden. This is a separate state, not a continuation of the child's earlier event.

The cave entrance is a side route. The source comments identify it as a three-room Psynergy puzzle, with Kite the Jupiter Djinni in the second room. The cave file says it has no story message or Mind Read of its own; do not invent plot dialogue for the puzzle rooms.

## B. Storm survivor event

Function: `ValeKradensCottage_TalkToRockslideSurvivor`.

The survivor's question is not a cosmetic choice. A yes causes him to give up and sets `FLAG_VALE_ROCKSLIDE_SURVIVOR_GAVE_UP`; a no produces the escape warning and sets `FLAG_VALE_ROCKSLIDE_SURVIVOR_ESCAPED`. The source removes him after the escape branch. The event can be triggered by either direct interaction or walking into his metatile.

**Rewrite guard:** both outcomes must remain intelligible and distinct. The escape branch must warn of monsters heading toward the plaza, because that warning is the event's practical consequence. Do not have the survivor both give up and run away, or let him appear after the escape flag.

## C. The strangers' first reveal in Vale

Function: `ValeKradensCottage_MeetSaturosAndMenardi`.

The event begins with Saturos speaking about the villagers' limited knowledge of Sol Sanctum. Isaac hurries forward; Garet and Jenna step beside him. Saturos and Menardi continue discussing the elders and Kraden before noticing the children. They turn to face the party. Saturos challenges them, Garet answers, and Menardi asks whether they were eavesdropping. The player answers through a yes/no prompt. Garet then accuses them of sneaking around; Menardi infers Kraden's engagement was with the children; Jenna says they are going to meet him. A second player choice follows Saturos's question about their appointment. Saturos ultimately lets the children go; Jenna is surprised, and Menardi questions the decision.

The source sets the meeting flag at the start of the event, so this sequence runs once. The strangers remain to watch the party.

**Knowledge guard:** this is the first identification by name. The storm-night strangers must remain unnamed. The childhood party knows the names only after this event.

## D. Kraden's plan: player choices and continuity

Function: `ValeKradensCottage_KradenPlansSanctumVisit`.

This is a long, multi-stage event with several player yes/no prompts and sequential message offsets. The source confirms these beats:

- Kraden greets Isaac; Garet and Jenna join the conversation.
- Jenna notices Kraden is troubled. Kraden explains the strangers spoke as if they had seen Mt. Aleph and Sol Sanctum.
- Garet names Saturos and Menardi; Kraden acknowledges their persistence.
- Jenna wonders whether they might be thieves; Garet wants to report them to the high elders.
- The party agrees to hear Kraden out, but he stops them until he can confirm what he was told.
- Kraden proposes going to Sol Sanctum. Garet and Jenna react to the danger and the prohibition against climbing Mt. Aleph.
- A player choice about the prohibition leads to one of two reassurance lines; both routes remain a plan to look.
- Garet asks whether the others can sneak without being seen; another player choice selects the response.
- Jenna asks the party to keep the plan secret. One response includes a stronger warning not to tell Isaac's mother; the other advances the message pointer without displaying that extra line.
- Kraden confirms the plan and assigns Isaac as leader. Further prompts shape companion banter, not the destination.
- Kraden goes inside to prepare. The party enters his cottage for the Mythril Bags; when they return outside, Kraden joins them and the party sets off.

**Critical technical guard:** the event uses explicit `gFieldWork->message++` and arithmetic offsets such as `sneakingMessage + 1` / `+ 2`. Never insert or remove a TSV row inside these blocks without recalculating every dependent pointer and checking both answers. Do not turn the player prompts into branches with different world outcomes unless the event logic is separately redesigned and tested.

## E. Sol Entrance and first relief rooms

Source: `games/tbs/src/scene/sol_sanctum_entrance.c`.

The party reaches Sol Entrance from Vale. Walking into the main door opens it and takes the leader inside; searching the other door finds it tightly locked. Retreat does not work. The route back down changes during the eruption: before the party leaves Vale, it returns to the eruption version of Vale; otherwise it returns to ordinary Vale. Once Isaac and Garet have returned from Mt. Aleph, the Sanctum door is locked and no longer opens.

Inside, the first rooms are one scene with different actor and trigger tables selected by the entrance used. Two minotaur reliefs have empty eye sockets; Small Jewels open the way onward. The first jewel comes from a chest in the first relief room; the second comes from the chest in the maze. Kraden has separate scripted conversations on the first entry, in the first relief room, and in the second relief room. Pushable statues reset to their initial positions on leaving the area; do not treat their temporary positions as permanent story flags.

The corridor itself is a connector with two exits and no actors or events of its own.

## F. Statue puzzle and trap chronology

Source: `games/tbs/src/scene/sol_sanctum_statue.c`.

- Four statues can be moved onto floor seals.
- Two beam statues must be moved so their light reaches the central statue.
- Two statues never move.
- Opening the first seal too early springs the trap: the party is cut away to the Luna and Sol rooms and sees falling lights.
- Kraden then explains that moving one statue can trigger the trap. Until the centre statue has been moved, opening a seal too early causes that statue to slide back and the leader to jump clear.
- Once both beams open the floor hole and the central statue is moved into it, the trap is disarmed. Seals then remain open.
- All four seals must be opened before the way onward is found in the Luna and Sol rooms.

**Rewrite guard:** the trap is a deliberate puzzle mechanic and a character beat for Kraden. Do not make him explain the solution before the first trap event or let a prematurely opened seal stay open.

## G. Elemental Star Room: major reveal order

Source: `games/tbs/src/scene/sol_sanctum_elemental_star_room.c`.

The source comments and event functions establish this progression:

1. First entry: Isaac, Garet, Jenna, and Kraden rise into the Elemental Star Room. Kraden explains the four pedestals and gives the party four Mythril Bags. He calls the party back if it tries to leave before taking the stars.
2. The Venus and Mercury Stars can be bagged first; each changes which crossings are available.
3. Bagging the Jupiter Star triggers the hostage confrontation. Saturos and Menardi appear with Jenna and Kraden held; the masked companion is revealed as Felix.
4. Menardi offers a guarantee of the hostages' safety if the masked man removes his mask. Jenna recognizes Felix, her brother, whom the party believed lost when the Boulder swept the riverbank. Garet and the others react.
5. Felix explains that Saturos and Menardi saved him. The player is asked about handing over the stars, but the event takes the stars regardless; do not invent a branch in which the party retains them.
6. Alex arrives and takes the three stars already collected. The captors remain in place, each with further dialogue about the last star.
7. Taking the Mars Star causes the room to quake and sends the party into the eruption sequence.

The source uses dedicated actor speakers for Felix, Saturos, Menardi, Kraden, Jenna, Garet, and Alex. This gives us clear speaker attribution for the established characters. It does not by itself prove that an arbitrary new Isaac portrait line is supported.

**Continuity guard:** the reveal that Felix survived is the emotional reversal of the Vale storm. Before the unmasking, Isaac and Garet have believed Felix was lost. The rewrite must preserve the impact and avoid having the party speak as though they knew Felix survived.

## H. Isaac speaker finding

Across the inspected Vale and Sol events, Isaac is used for movement, reactions, emotes, and player yes/no input. Existing dialogue calls explicitly pass the speaking actor (for example, Kraden, Jenna, Garet, Saturos, Menardi, and Felix). No verified call in the inspected excerpts establishes a new Isaac speaking convention.

Therefore the safe policy remains:
- Do not add Isaac's dialogue by guessing that `ACTOR_PARTY_LEADER` is a valid speaker.
- Inspect the message speaker implementation and confirm the valid actor/portrait encoding first.
- Keep player choices and nonverbal reactions where they already serve the scene.
- If Isaac's voice is supported, use it selectively and retain the 27-visible-character working ceiling until rendered tests establish the true limit.

## I. Next source checks

1. Finish the rest of Kraden's plan event and its return-from-cottage continuation; map all sequential message IDs to speakers and branches.
2. Inventory every optional talk, examine, and Mind Read row in the cottage approach, Sol Entrance, relief rooms, maze, Luna/Sol rooms, and Star Room. The Star Room's own header confirms that its triggers include talk and Mind Read rows; they must not be overlooked.
3. Trace the exact message blocks for the Felix reveal, the stars handover, and Alex's arrival.
4. Inspect the message speaker implementation and an existing leader-speaker example before approving Isaac dialogue.
5. Run grammar, placeholder expansion, 27-character working-ceiling, and rendered-width checks only after all live dialogue rows are mapped.
6. Rewrite complete chronological scenes, not isolated fragments, and validate each branch in-game or through a reliable event test.
