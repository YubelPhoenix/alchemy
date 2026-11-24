# Ashfall Pass 01 — Cottage Rooms A Dialogue and Trigger Audit

Status: source-mapped; no dialogue or event logic changed  
Branch: `dark-story-rewrite`  
Sources: `games/tbs/src/scene/cottage_rooms_a.c`, `tools/dark_story/phase2_vale.tsv`

## Scene-state selection

Cottage Rooms A is a shared map containing Garet's family home, Jenna's grandparents' home, two other houses, the three shops, and three houses near the plaza. The ninth drawn room has no entrance. Dialogue and residents are selected by story state:

1. Storm night: every resident is removed. All doors lead back into the storm scene. Jars and barrel are empty; additional bookcases, including the notebook *Study of Alchemy*, are readable.
2. Opening day: ordinary residents and shopkeepers are present; jars and barrel contain one-time items.
3. After the party leaves Vale: Jenna has been taken on Mt. Aleph; Jenna's grandmother is sick in bed; villagers speak about the quest and Felix; the item merchant offers Isaac a Herb once.
4. After returning from Kalay: Garet, Ivan, and Mia are present; Garet's family reunion runs once under `FLAG_GARET_CAME_HOME`; Dora's illness and other changed dialogue are active.

The storm trigger table is intentionally sparse: it contains exits and bookcase/jar/barrel examinations, not resident talk or Mind Read. This agrees with the initialization code removing the residents. Do not add storm-night family dialogue to this room; the family are outside in the storm scene.

## Opening-day talk inventory

The ordinary trigger table includes:
- Garet's grandfather and grandmother.
- Garet's father and mother.
- Jenna's grandfather and grandmother.
- A woman commenting on Jenna's resemblance to her family.
- A man discussing Kraden's studies (event-based follow-up).
- A woman discussing visitors in town.
- A young man dreaming of seeing the world.
- A woman discussing Vale's permission rules.
- A strongman who wants to scare Kraden's visitors (event-based follow-up).
- Weapon, armor, and item merchants (stateful shop events).

The three merchant event handlers are not interchangeable. The weapon and armor merchants have return-state dialogue; the item merchant has the one-time farewell Herb event after the party leaves Vale. Keep the gift, item flag, and follow-up dialogue synchronized.

## Post-departure talk and Mind Read inventory

The post-departure talk table changes all of the family and villagers' lines. It includes:
- Garet's grandfather asking Isaac to look after Garet.
- Garet's grandmother reflecting on the Wise One's choice.
- Garet's father expressing pride in his son.
- Garet's mother speaking as another mother who understands Dora.
- Jenna's grandparents pleading for Jenna's return.
- The woman reacting to Jenna's abduction.
- The man discussing Kraden and Alchemy.
- The visitors-in-town woman asking about strange powers through an event.
- The young man envying the journey.
- The permission-to-leave woman giving travel advice.
- The strongman reflecting on the visitors.
- The three merchants with their own return-state events.

The same state has Mind Read triggers for the family, Jenna's grandparents, villagers, and all three merchants. These lines add private fear, guilt, pride, and speculation. They are not optional filler: they must be checked for grammatical quality and knowledge continuity alongside spoken dialogue.

The item merchant has two Mind Read outcomes, selected by `FLAG_VALE_FAREWELL_HERB_RECEIVED`. Preserve the condition order and ensure the gift event cannot repeat or contradict the thought text.

## Post-Kalay talk and Mind Read inventory

After Kalay, the room changes again:
- Garet's grandfather comments on Mia.
- Garet's grandmother comments on Ivan.
- Garet's father has an event asking about Dora.
- Garet's mother has an event worrying about the travelers' health.
- Jenna's grandfather still asks about rescuing Jenna.
- Jenna's grandmother says she recovers quickly from colds.
- Other villagers discuss the cold, Alchemy, tremors, Mt. Aleph, healers, and the state of the world.
- The three shops retain their own stateful talk events.

Mind Read is also state-specific. It covers Garet's family, the merchants, Jenna's grandparents, and the villagers. The item merchant again has conditional thoughts depending on whether the farewell Herb was given.

## Garet's family reunion event

`CottageRoomsA_GaretComesHome` is a scripted event, not ordinary talk dialogue. It runs when the party first enters Garet's home after Kalay and before `FLAG_GARET_CAME_HOME` is set.

Verified staging:
1. The party enters while Garet's grandfather is asleep; sleep sprites drift above him.
2. The camera pans to Garet's parents. His father worries about whether they should look for Garet; his mother teases him for missing their son.
3. Garet's grandmother sees the party and struggles to speak. The family gradually realizes it really is Garet.
4. The grandfather wakes and asks whether the Wise One's mission is complete. The player's yes/no response advances the message pointer on one branch; it does not create a separate reunion outcome.
5. Garet's mother recognizes he will leave again soon. His grandparents express relief and happiness.
6. Garet introduces Isaac, Ivan, and Mia. Ivan and Mia each step forward and introduce themselves.
7. His mother asks the companions to look after Garet; his father welcomes them and tells them to enjoy their stay.
8. The party leaves the room; Garet's father resumes pacing; the one-time reunion flag is set.

The scene includes Isaac's movement, facing, and a nod, but its displayed dialogue is assigned to Garet's relatives, Garet, Ivan, and Mia. This is not evidence that the engine supports an arbitrary Isaac speaker message. Do not add Isaac lines here until the message speaker contract is verified.

## Text and continuity issues to review

- The phase TSV contains many generic `message` rows for sequential event blocks. The correct speaker and branch must be traced from each event call and message pointer; the TSV key is not a speaker label.
- The farewell Herb sequence and its Mind Read condition must remain aligned.
- The family reunion's yes/no question advances a sequential message pointer. Do not insert or remove rows in that block without recalculating the branch.
- Book and examination text differs by state. The storm-only notebook and additional bookcases must not be exposed in later states unless the source permits them.
- The phase TSV contains placeholders and control tokens. Runtime actor names, `{protagonist_name}`, `{possessive_suffix}`, page breaks, pauses, and text effects require separate validation.
- Several post-departure thoughts speculate about Felix, Jenna, the Wise One, and the strangers. Keep each speaker's knowledge limited to what Vale could have learned by that point.
- Do not confuse the post-Kalay visit with the later return to Vale after the main quest; this shared room has explicit state selection and the scene's later dialogue may be revisited.

## Remaining work before Pass 01 dialogue rewrite

1. Finish the full trigger/examination inventory for each room entrance and state, including the complete bookcase/jar/barrel trigger rows.
2. Trace every sequential message block in the family reunion and the merchant events, including conditional message-pointer increments.
3. Audit the phase-2 rows that belong to Vale against the exact source message calls; do not treat unrelated later-game rows in the same TSV as Vale content.
4. Complete grammar, voice, knowledge, placeholder, and 27-character/rendered-width checks for all Vale and Cottage Rooms A rows.
5. Verify a supported Isaac speaker encoding before adding any protagonist speech.
6. Once the full Vale/Sol Sanctum opening inventory is closed, draft the complete rewritten dialogue as a reviewed, source-mapped pass rather than isolated patches.
