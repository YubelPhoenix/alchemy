# Ashfall — Isaac Voice and Dialogue Layout Standard

Status: design constraint; implementation not yet approved  
Branch: `dark-story-rewrite`  
Scope: Isaac's dialogue across the full Golden Sun: The Broken Seal rewrite

## Narrative decision

Isaac may speak in Ashfall, but he must remain recognizably the player-character from the original game. The rewrite will not turn him into a constant narrator or give him long explanatory monologues.

His voice should be restrained, concrete, and emotionally legible. He speaks when a moment genuinely requires his response: a consequential decision, an emotional exchange, a moral disagreement, or a relationship beat that cannot be conveyed clearly through action alone. Silence remains useful and intentional elsewhere.

The aim is not to replace player interpretation with exposition. Isaac's words should clarify his immediate position without explaining the entire scene or dictating what the player must feel.

## Three permitted forms

1. **Short direct lines.** Isaac speaks through an existing event message only when the event's speaker presentation and actor context support it.
2. **Player-directed responses.** Where the original event already supports a choice, choices may express different attitudes or decisions. Do not add a new choice merely to create more dialogue.
3. **Nonverbal response.** When a direct line would be redundant or technically disruptive, preserve a meaningful pause, movement, animation, or another character's response to Isaac's action.

Do not make other characters speak Isaac's thoughts for him. Their reactions should be grounded in what he actually says or does.

## Voice and characterization

- Prefer concise, specific language over abstract speeches.
- Let his vocabulary and emotional openness develop gradually with experience.
- Allow anger, fear, grief, tenderness, doubt, and resolve; do not make every response stoic.
- Avoid modern slang, theatrical declarations, and philosophical speeches that do not fit the scene.
- Do not give Isaac knowledge the party has not acquired.
- Do not make him responsible for explaining another character's trauma or resolving every conflict.
- Keep the player free to interpret pauses and actions where words are unnecessary.

## Illustrative tone samples (not game-script replacements)

These examples demonstrate the intended restraint. They are not mapped to message IDs, actors, event calls, or approved chronology.

```text
We should go back.
I won't leave them.
I was afraid, too.
That doesn't make it right.
```

The examples are deliberately brief. Final wording must be written against the actual scene, speaker, and branch rather than inserted as standalone lines.

## Text-box and message constraints

The project has raised a 27-character line constraint. Until the exact engine rule and validator behavior are confirmed, treat **27 visible characters per rendered line** as a conservative working ceiling, not as a verified engine specification.

For every proposed Isaac line:

1. Count the rendered line after expanding actor-name and other visible placeholders.
2. Exclude non-rendering control tokens from the visible-character count, but preserve them exactly.
3. Check explicit line breaks and page breaks independently; do not concatenate text across control tokens when measuring.
4. Check the actual font width and text-box rendering where the engine's validator or ROM test permits. Character count alone does not guarantee visual fit.
5. Do not split a word, remove a meaningful pause, or damage a control sequence merely to meet the ceiling.
6. If the line cannot fit naturally, rewrite it more concisely rather than shrinking the font or forcing a crowded box.

## Technical acceptance gates

No Isaac line is ready to merge until all of the following are established:

- The relevant event function and branch have been identified in the original scene source.
- The intended speaker value is valid for that event and displays correctly in the message system.
- The line does not require an unsupported portrait, actor, or party-leader presentation.
- Existing message IDs, sequential message offsets, placeholders, control tokens, and event flags remain valid.
- Both sides of any existing choice are checked for continuity and correct state.
- The dialogue does not cause the same line to repeat on revisits or appear before its trigger.
- The text validator passes, and the relevant scene is checked in-game or in an equivalent rendered test.

Do not insert a new message into an event solely because a message ID is available. Sequential message blocks and arithmetic message offsets must be audited before any insertion or replacement.

## Current Vale-specific caution

The Vale storm phase includes many lines spoken by Dora, Kyle, Garet, Jenna, villagers, and elders that refer to Isaac through `{actor_name:1}`. Those references are not evidence that Isaac himself currently has a speaking line. The scene source must be checked for the exact message call and speaker argument before assigning any dialogue to him.

The storm's emotional progression must remain intact: Isaac is a child; Dora sends him toward safety; Garet joins him; the elders struggle to hold the Boulder; the river rescue fails; and the strangers are encountered only after the tragedy. Isaac's dialogue must respect what he could understand at each point.

## Definition of done

Isaac's voice is successful when the player can recognize his emotional development across the journey without feeling that the original silent protagonist has been replaced by a different character. Technical validity, text fit, chronology, and branch integrity are mandatory—not optional polish.
