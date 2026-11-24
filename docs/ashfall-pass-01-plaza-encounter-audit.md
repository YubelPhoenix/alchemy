# Ashfall Pass 01 — Plaza Encounter and River Return Audit

Status: source-mapped; dialogue rewrite remains pending  
Branch: `dark-story-rewrite`

## Source-backed sequence

### Plaza: aid to the elders

`ValePlaza_SentToAidElders` is reached by stepping on the storm plaza trigger while the storm flag is set and the dispatch flag is clear. The mayor (Garet's grandfather) tells the boys to aid the elders. Two strongmen agree and leave. Isaac and Garet then step forward; Garet calls to his grandfather and Jenna. Jenna asks whether they came to help her. The grandfather's yes/no question is a knowledge check: if the boys already know about Felix, the corresponding reply is shown; otherwise the event advances to the alternate response. The charged strongman then confirms he has enough Psynergy after the Psynergy Stone restored him. The grandfather sends Jenna and the strongman back to the river, while Isaac and Garet are sent to show them the route.

The event sets the dispatch flag after the sequence. On later plaza initialization, the two aides who left are removed from the scene. The storm scene removes Jenna and the charged strongman when the party has been dispatched.

**Continuity guard:** the Psynergy Stone restores the one strongman in this sequence. It does not restore all villagers or the exhausted riverbank group. Isaac and Garet are guides, not the rescuers who independently solve Felix's predicament.

### Plaza: returning to the river

The river return trigger is in the storm scene after the dispatch flag. The party returns with Jenna and the charged strongman. The river sequence then runs to the Boulder impact. Do not let optional plaza dialogue imply the party has already returned or that Felix is safe before this trigger.

### After the Boulder: Garet follows

`ValeStormyNight_GaretFollowsIsaac` runs after the Boulder event. Isaac walks off first; Garet follows and delivers the message block beginning at `MsgValeIsaac`. The message speaker is explicitly `SPEAKER_PORTRAIT_LEFT | ACTOR_GARET_CHILD`. Garet is speaking to Isaac. The block's ID is not evidence of Isaac's voice.

The event sets `FLAG_VALE_STORM_GARET_LEFT`. The plaza initialization then calls `ValePlaza_MeetSurvivingTravelers`. This confirms the order: the tragedy happens, Garet follows, and only then do the boys encounter the two travelers.

### Travelers: conversation and battle

`ValePlaza_MeetSurvivingTravelers` opens with the first traveler saying only two survived. The second enters and they discuss Sol Sanctum's aftermath, the switch/trap, Alchemy, and their intention to try again. The game does not name them in this childhood scene. The travelers' theme begins as the second arrives.

`ValePlaza_FightTravelers` brings Garet into view. The first traveler asks whether Isaac was listening; the party leader receives the yes/no prompt. Garet comments on their frightening appearance. The second traveler tells the boys to forget what they heard; the first follows with the threat to help them forget. The two attack. The encounter is a no-escape scripted battle.

Both victory and defeat destinations are explicitly set to `VALE_PLAZA_AFTER_TRAVELERS_BATTLE`. The battle outcome therefore does not branch the story's aftermath.

### After battle: storm ends

`ValePlaza_TravelersLeaveAfterBattle` stages Isaac and Garet lying beaten while the travelers depart. The scene plays the final lightning flashes, stops the storm, clears `FLAG_VALE_STORM`, and exits to the title sequence. The title then opens three years later.

**Continuity guard:** do not write a victory-specific escape, a different defeat fate, or a childhood identification of Saturos and Menardi. The original code fixes the same aftermath for both battle outcomes.

## Optional dialogue coverage still required

The storm plaza has more than its main dispatch and encounter events. The actor and trigger tables must be walked to inventory every optional talk and Mind Read row in each state. Already verified examples include:

- The small boy with remaining Psynergy demonstrates lifting a rock through `ValePlaza_BoyLiftsSmallRock`.
- The little girl who saw Jenna changes her line after `FLAG_VALE_STORM_SENT_TO_AID_ELDERS`: before dispatch she says Jenna went that way; after dispatch she asks the party to help Felix.
- The storm curious old man uses `MsgValeCanIUsePsynergy` through a yes/no interaction.
- Other storm actors and generic message rows need exact actor/trigger mapping; the TSV label `message` alone does not identify the speaker.

The day, departure, post-departure, and post-Kalay actor tables are distinct. A storm line must not leak into a later state, and a day-state line must not be treated as an event that occurs during the storm.

## Isaac voice implementation status

This audit confirms that the existing storm plaza uses Isaac's actor for movement, facing, nodding, and the yes/no prompt, but the displayed lines in the dispatch and traveler scenes are assigned to named NPCs. The existing player choices already let the player answer without creating an unverified Isaac portrait call.

No new Isaac message has been inserted. Before doing so, inspect the message speaker encoding and a confirmed working event example. The player-character should speak only where the scene benefits from it and where the engine supports it safely.

## Remaining work for this pass

1. Complete actor/trigger/Mind Read inventory for storm Vale and the Vale three-years-later state.
2. Map every live storm message ID to the precise event call and speaker, including the sequential offsets used in yes/no branches.
3. Check all dialogue for grammar, voice, chronology, and 27-character working line ceiling, expanding placeholders separately.
4. Verify the actual Isaac speaker mechanism before introducing lines.
5. Draft dialogue changes only after the above mapping; preserve flags, event calls, actor choreography, and both battle outcomes.
