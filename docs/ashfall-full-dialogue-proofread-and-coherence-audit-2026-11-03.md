# Ashfall full-dialogue pre-play QA: grammar and narrative coherence (3 November 2026)

**Reviewed branch head:** `b66186f2001fbce903c04024ce5816c615380aa0`  
**Scope:** all **77** TSV dialogue-replacement files in `tools/dark_story/` (including the intentionally comment-only `phase74` stub), comprising **4,235 replacement rows**, including a small number of names/labels and fragment-style messages that correctly have no `{end_wait}` tag.

## Checks performed

A complete programmatic pass over every TSV file checked tabular row structure, message endings, maximum three display lines per page, conservative 27-character line budgets, suspicious repeated words, common English misspellings, and conspicuous grammar patterns. All rows were read from the active `dark-story-rewrite` branch. The line-budget check used *Alexander* as a deliberately longer-than-usual hypothetical actor name; a few existing lines were 28 columns under that nine-character substitution but are inside the project's eight-character variable-name budget. Named enemy/class/Djinn labels and concatenated examination fragments were exempted from end-tag requirements. No structural defects or three-line page violations were found.

In addition, narrative source files and chronological ledger material were used to check the principal path and major choices: Vale and the first Sol Sanctum visit, Jenna/Felix's reveal, Vault and Ivan, Kolima/Tret, Imil/Mia, Mercury Lighthouse, westward regional progression, Altin and Lamakan, Tolbi/Colosso/Babi, Suhalla, Lalivero, Venus Lighthouse, ship departure, and Jenna/Kraden epilogue. Reviewed the hostile Ash Jenna path and independent Heart and Kegare appearances. This was a **pre-play editorial/static inspection**, not a complete human performance read of every line in context or emulator verification of all conditional events.

## Confirmed issues found and corrected

1. **Vale, message 03868:** After Dora hears the children plan to climb Mt. Aleph with Kraden, a previous rewrite had her reflect that children are still playing and that Vale survived. That line was at odds with Jenna's **immediate** response, “No! It's for our studies. Honest.” The original baseline says “Kids and their games...”. Replaced the off-topic reflection with Dora's natural teasing challenge about climbing for fun. This is an event-sequence dialogue repair, not merely polishing.
2. **Babi audience, 08932:** “thought you Lemurian” omitted the verb **were** and misused the singular when speaking of the party. Corrected to “thought you were Lemurians”; preserved the original Lemuria comparison and page break.
3. **Post-Venus Lalivero, 10353:** “{actor_name:1}, your friends and you have done...” had unnatural English word order. Recast as “You and your friends have done what we couldn't, {actor_name:1}.” The speaker/context remains unchanged.
4. **Optional post-Venus Ash Jenna confrontation, N308:** “He let our world die” lacked a clear immediate antecedent after many lines about the coastline. The accusation now identifies **the Wise One** explicitly. This remains **Ash Jenna's contested accusation**, not confirmed game canon. Removed the line's redundant secondary declaration of wanting him to suffer, allowing N310 to carry her explicit hostility.

## What passed and what remains unverified

- The rewritten story retains original Jenna as the rescue objective; the optional evil Ash Jenna is a distinct unrepentant antagonist, not a redemption route.
- Vale's storm, original prologue chronology, Mercury's beacon, Sol Sanctum, the death/fall events at Venus, first return to Lalivero, and the original post-game Felix/Sheba survival reveal have not been reordered or given newly fabricated results by this editorial pass.
- The original **Yes/No** prompt and branch structure, controls, actors, message IDs, number of pages, and game-source files are unchanged in the four fixes. The new lines preserve each original embedded token multiset.
- Code-level story contracts and full IPS build on this revision still require a successful GitHub workflow run. Story coherence should be evaluated with actual dialogue order, choice branches, visual timing and the original ending during the creator's planned playthrough. The known world-map A-button freeze is a separate potential gameplay blocker, not a prose defect.

**Editorial assessment:** No further *confirmed* blocking dialogue contradiction was found in this broad pass after the four repairs. This does not imply that every possible typo, tonal preference, source speaker discrepancy or conditional-state issue is impossible.
