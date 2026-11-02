# Ashfall: Early-Game Continuity Audit

Branch: `dark-story-rewrite`  
Scope: Vale storm prologue, Vale three years later, Sol Entrance and the opening Sol Sanctum rooms.  
Status: source-verified audit; dialogue edits intentionally deferred until every affected message ID, actor, trigger and story state has been mapped.

## Why this audit exists

The rewrite must follow the game's actual event progression. A line that is emotionally effective but appears before the speaker could know the relevant fact, after the character has left, or in a scene state where the actor is absent is still a continuity error. This audit records the source-backed sequence that dialogue must obey.

## 1. Vale storm night: mandatory chronology

The storm is a separate scene state, `SceneId_ValeStormyNight`, selected while `FLAG_VALE_STORM` is set. Vale's ordinary daytime scene must not be treated as the same visit.

1. Isaac begins in the cottage rooms. Dora and Kyle send him toward the plaza; `FLAG_VALE_STORM_SENT_TO_PLAZA` records that event.
2. The four falling-rock events are distinct. Each has a `_FELL` flag that restores the obstacle and a corresponding `_PASSED` area flag that prevents replay during that visit. The passage flags are cleared when the party leaves Vale.
3. The shoving villager event is tied to Isaac trying the south door of the cottage rooms; it is not a free-standing conversation that can be inserted anywhere.
4. Garet is encountered at his chest. Speaking to him or walking past him can bring him into the party; the chest remains by his door. Once Garet has joined, he turns Isaac back from a fallen rock and from the north path to Mt. Aleph.
5. The elders' attempt to hold back the Mt. Aleph Boulder precedes the scene of Felix in the river. The river sequence includes Felix clinging on, Jenna's parents trying to save him, and Dora going for help.
6. The Boulder sweeps Felix, Jenna's parents and Kyle downriver. The scene then rebuilds the riverbank and the storm sequence proceeds toward its ending.
7. Garet follows Isaac as Isaac returns toward the plaza. The storm ends through the plaza sequence, not through an invented independent departure.

**Dialogue constraints:** Do not let Isaac, Garet, Jenna, Dora or villagers speak as though the outcome of the river rescue is known before the Boulder has passed. Do not place adult-knowledge explanations in the children's mouths. The hooded figure is a brief silent appearance in this scene; no identity, allegiance or explanation is established by this source.

## 2. Vale by day: three distinct story states

The daytime Vale scene selects actor templates and triggers according to the story flags. Dialogue must be written against the correct state, not as one continuous set of interchangeable village conversations.

### Opening visit, three years after the storm

The game opens with Isaac mending the roof. Dora calls to him; Garet trains his Psynergy nearby; Jenna arrives and the three speak before going to Kraden's cottage. After the roof is mended, Dora praises Isaac's work, remembers Kyle and sends the children to climb Mt. Aleph with Kraden.

### Before the party leaves Vale

Until `FLAG_SANCTUM_VISIT_PLANNED`, Jenna stops Isaac on the path to Mt. Aleph. A bearded man warns Isaac against sneaking up the sacred mountain and continues watching him on later approaches. The puppies are present and can bark when approached. They are removed after `FLAG_MET_SATUROS_AND_MENARDI`.

Villager dialogue in this state includes the mayor, Garet's grandfather, the boundary around Kraden's cottage, Garet's sister and Dora's concern about the roof. Do not give these villagers post-eruption knowledge in this state.

### After the party has left Vale

With `FLAG_VALE_PARTY_LEFT`, Dora refuses to open Isaac's house door and tells him to go away. Villagers speak about the tremors and Kraden's failure to return. They must not behave as though the party is still preparing for the first trip to Sol Sanctum.

### Return from Kalay

With `FLAG_KALAY_REACHED`, Vale has another actor/trigger setup. Garet can meet his sister; family-protection dialogue is conditional on `FLAG_VALE_GARET_ASKED_TO_PROTECT_FAMILY`; the questions about Jenna's return and the lack of travellers have their own area flags. Isaac's house opens again, and Dora is ill inside. Do not use the pre-departure version of Dora's dialogue here.

## 3. Sol Entrance and opening Sol Sanctum rooms

Sol Entrance and the first rooms inside Sol Sanctum are served by the same source unit but are different scene states.

- Vale reaches Sol Entrance by the Mt. Aleph exit. The main door opens when the leader walks into it; the other door is tightly locked.
- Before the eruption and before the party leaves Vale, retreat from Sol Entrance returns to ordinary Vale. Between `FLAG_SOL_SANCTUM_ERUPTED` and `FLAG_VALE_PARTY_LEFT`, the return leads to Vale's eruption scene. After the party has left, a man blocks the path and warns people away.
- Inside the relief rooms, Isaac, Garet, Jenna and Kraden investigate the minotaur reliefs. A Small Jewel from the first room opens the first relief; the second Small Jewel comes from the chest in the maze and opens the second.
- Kraden has separate scripted beats at the entrance, at the first relief room's hidden passage, and at the second room's statues. These are not interchangeable generic exposition.
- Statue positions are tracked with area flags and restored on re-entry. The second-room condition is explicitly scoped to that room; dialogue should not imply the statues retain arbitrary positions across unrelated visits.
- Once Isaac and Garet return to Vale with `FLAG_VALE_RETURNED_FROM_MT_ALEPH`, the Sol Entrance door is locked. A rewrite must not allow a second voluntary expedition through it.

## 4. Required dialogue audit before rewriting these scenes

The source comments establish scene mechanics and chronology, but they do not by themselves prove that every optional conversation, Mind Read line, examination message or conditional NPC variant has been included in the rewrite tables. Those must be inventoried against the actual actor-template, trigger and message-ID tables before changing dialogue.

For every message in this opening sequence, record:

- message ID and original context;
- scene and actor/template that can invoke it;
- trigger type (talk, Mind Read, examine, item use, event, or conditional state);
- prerequisite flags and the state in which it is reachable;
- whether it can repeat, and whether it is one-time/area-flagged;
- the speaker's knowledge at that exact point in the story;
- required runtime tokens, text controls and line-width constraints.

Do not invent a new line or assign a replacement ID until its source message and trigger have been verified. Keep all NPC and optional dialogue in scope; this audit is not permission to reduce coverage to mandatory cutscenes.

## 5. Next source files to audit

Continue through the source units that own the transitions and dialogue for the opening sequence: `vale_stormy_night.c`, `vale.c`, `vale_plaza.c`, `cottage_rooms_a.c`, `cottage_rooms_b.c`, `vale_kradens_cottage.c`, `sol_sanctum_entrance.c`, and the remaining Sol Sanctum scene units. Then reconcile each discovered message ID against the rewrite TSVs.

## 6. Guardrails

- Preserve the original scene and flag progression; do not create shortcuts between story states.
- Keep the children's perspective in the storm and the older characters' knowledge appropriately bounded.
- Treat the hooded figure as unexplained unless later source-backed story material establishes more.
- Include ordinary NPCs, optional talks, Mind Read, object examinations and conditional variants.
- Retain all engine control codes and runtime name tokens; validate every changed row with `tools/dark_story_rewrite.py --check`.
- A successful ROM build proves technical integration, not narrative completeness. Narrative coverage and playthrough verification remain separate gates.


## 7. Additional source checks: plaza, homes and Kraden's cottage

The connected scene files add several important transitions that must be represented in the opening dialogue pass:

- During the storm, Isaac and Garet return from the river to Vale Plaza after Felix falls in. The mayor sends two strongmen to aid the elders, then sends the boys back toward the river with Jenna and a strongman whose Psynergy the Psynergy Stone restored. Only after the Boulder has swept Kyle, Jenna's parents and Felix away, and Garet has gone after Isaac, does the plaza play the encounter with the two surviving travelers. The strangers say they alone survived Sol Sanctum's fury, fight the boys, and leave them lying in the storm whether the boys win or lose. The storm then ends and the title sequence advances three years.
- The three-years-later plaza state is distinct from the storm. Its villagers can discuss the travelers, the old disaster and the loss of Isaac's father and Jenna's family. The farewell at the town gate occurs only after the party accepts the Wise One's quest in the Sanctum. After departure, the town gate opens to the world map; on the return from Kalay, villagers and the hut owner have another state.
- During the storm, Cottage Rooms A has no residents; its doors lead back into the storm scene. Its jars and barrel are empty, and extra bookcases can be examined. By day the houses and shops are occupied, with their own objects and one-time finds. After the party leaves, Jenna's grandmother is ill and the item merchant can give Isaac a farewell Herb. After Kalay, Garet's family reunion introduces Ivan and Mia, while villagers worry about Dora.
- Cottage Rooms B contains Isaac's house, the inn, forge, Kraden's study and a separate room in Babi's Palace. During the storm, Dora wakes Isaac upstairs, gives him his tunic, and Kyle calls them downstairs before the run to the plaza. By day, the masked man is at the inn and the three strangers are discussed there. After the party leaves, villagers discuss the eruption, Jenna's kidnapping and whether the masked man was Felix. After Kalay, Dora's illness has distinct visit and Mind Read states; the Mind Read flag is shared by the two relevant actors, and Dora's out-of-bed state is visit-specific.
- At Kraden's cottage on the stormy night, a rockslide has broken the fence, monsters have entered, and a wounded survivor can either give up or discover he is unhurt and run to warn the plaza. Three years later, the party overhears Saturos and Menardi speaking about Sol Sanctum before Kraden plans the secret visit. Kraden then prepares the Mythril Bag; only after the party returns outside does he set off with them and set `FLAG_SANCTUM_VISIT_PLANNED`. The child at the fence and the later woman visiting the empty cottage belong to later states.

## 8. Silent watcher: a second verified appearance

The Sol Sanctum corridor source places a silent, cloaked figure off-map until a one-time step trigger. When the party reaches the middle of the long hall, the figure appears a few steps ahead, watches for 100 frames, and vanishes; `FLAG_DARK_WATCHER_SANCTUM_CORRIDOR` prevents a repeat. She says nothing. This establishes a second deliberate glimpse after the Vale storm appearance, but still does not establish her identity, motives, or relationship to any faction. Keep both appearances silent and observational unless a later source-backed event explicitly changes that.

## 9. Additional coverage checks still required

The source summaries above identify scene states and event ownership, but the full trigger tables and dialogue catalogues still need to be cross-checked. In particular, enumerate the plaza's Psynergy Stone and ivy examinations, the cottage bookcases and containers, inn/forge residents, the survivor's yes/no branch, the strangers' battle outcome branch, the Mythril Bag sequence, and all Mind Read variants after Kalay. Do not infer that a scene has no optional dialogue merely because its opening source comment does not list every message.
