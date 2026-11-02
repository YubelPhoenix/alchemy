# Ashfall Rewrite — Pass 1: Vale Storm Prologue

Branch: `dark-story-rewrite`
Scope: the storm-night sequence from Isaac waking in his home through the battle with the two strangers and the end of the storm.
Status: source chronology verified; dialogue rewrite not yet marked complete.

## Source files checked

- `games/tbs/src/scene/vale_stormy_night.c`
- `games/tbs/src/scene/vale_plaza.c`
- `games/tbs/src/scene/cottage_rooms_a.c`
- `games/tbs/src/scene/vale.c`
- `tools/dark_story/phase1_vale.tsv`
- `tools/dark_story/phase2_vale.tsv`

The scene-source comments and event functions establish the following order. This is the controlling order for all dialogue revisions; the phase file is only a message collection.

## Verified event order

1. Isaac wakes in the cottage as the mountain shakes. Dora and Kyle hurry him downstairs and toward the plaza. The tunic and belongings exchanges occur inside the house, before Isaac reaches the village paths.
2. Kyle stays behind because villagers are still trapped. Dora takes Isaac toward safety. The dialogue must preserve the parents' urgency and Kyle's decision to help without implying that Dora knows what will happen to him.
3. Isaac encounters villagers fleeing through the storm. The shoving-man exchange is triggered by trying the south door of Cottage Rooms A; it is not a freely placed conversation.
4. Garet is found trying to save his chest. Speaking to him or walking past him brings him into the party; the chest remains behind. The two possible dialogue routes must remain consistent with whether Isaac agrees to leave the belongings.
5. Four separate rockfall events block paths. With Garet in the party, he prevents Isaac from proceeding north toward Mt. Aleph or through a fallen-rock path. Dialogue must not make the Boulder seem to have already swept downriver at this stage.
6. The elders hold the Boulder back. Their strength is failing, and the party is sent toward the plaza. The exhausted villagers and the remaining Psynergy exchanges belong to this stage.
7. Felix is seen clinging to the riverbank. Jenna's parents try to save him; Jenna and others seek help. The rope cannot reach, and the available Adepts are exhausted or have little Psynergy left.
8. Isaac and Garet return to the plaza. The mayor sends two strongmen to aid the elders and sends the boys back toward the river with Jenna and a strongman whose Psynergy has been restored by the Psynergy Stone.
9. The Boulder sweeps Kyle, Jenna's parents, and Felix downriver. The riverbank is rebuilt and the surviving characters react to what they have witnessed. Do not let dialogue imply that Felix was rescued or that Kyle's fate is known before this event.
10. Garet follows Isaac back toward the plaza. Only after the storm sequence reaches this point do the two strangers discuss surviving Sol Sanctum. The boys overhear them, are challenged, and fight. Whether the boys win or lose, the strangers leave them unconscious; the storm ends and the story advances three years.

## Continuity constraints

- The childhood scenes must stay within what Isaac, Garet, and Jenna can understand. The children do not know the strangers' identities at this point.
- The strangers' names, Saturos and Menardi, are established later. The prologue should not identify them prematurely.
- The hooded figure is only a brief, silent appearance in the storm sequence. Do not assign it an identity or motive without a later source-backed reveal.
- Keep the distinction between the Boulder falling, the elders holding it, and the Boulder finally sweeping the riverbank. These are separate story beats.
- The Psynergy Stone restores one strongman's ability to help; it does not restore everyone's Psynergy.
- The fight with the strangers happens after the river tragedy and after Garet rejoins Isaac. The outcome does not change the fact that the boys are left unconscious.
- Keep all one-time events, conditional actor placement, message IDs, and engine control tokens intact.

## Initial text review notes

The existing `phase1_vale.tsv` contains a complete dramatic draft, but this pass has not yet been approved as final dialogue. The full line-by-line rewrite must be checked against the event order above, the actual speaker for each generic `message` row, and the runtime text limits.

Specific editorial checks for the rewrite:
- Replace awkward colloquialisms such as “The Boulder's going to drop any second” where a more natural urgent line is available.
- Preserve emotional restraint around the river tragedy; avoid giving every character polished, adult-sounding speeches while they are frightened and exhausted.
- Review repeated reassurance and repeated questions so urgency does not become redundant.
- Check every generic message row against the event function that displays it; a correct sentence attached to the wrong speaker is still an error.
- Preserve the two Garet belongings branches and the repeated/alternate rows used by the event.
- Check all message rows for punctuation, grammar, capitalization, placeholders, control codes, and text-box line width.

## Completion checklist

- [x] Core storm chronology checked against scene source.
- [x] Plaza return and strangers' battle placement checked.
- [x] Major story-state constraints recorded.
- [ ] Every message row mapped to its speaker and trigger.
- [ ] Full dialogue rewrite completed.
- [ ] Optional talks, Mind Read, signs, examinations, and state variants audited.
- [ ] TSV validation passed.
- [ ] Build and event-path verification completed.

This document records a source-verified starting point. It does not claim the Vale storm dialogue or the full Vale pass is complete.
