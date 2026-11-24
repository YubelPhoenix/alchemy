# Golden Sun: Ashfall — early-game narrative pass (3 November 2026)

**Branch:** `dark-story-rewrite`. **Source head:** `be7bf7107b24a1feacbf9994f0b1d1f1a5db70fa`.

Reviewed the complete major narrative trajectory from the Vale storm and three-year return, through the Sol Sanctum revelation, departure, Vault/Ivan, Bilibin/Kolima/Tret and Imil/Mercury. This follow-up targets actual early-story gaps left outside the preceding mid/end editorial pass.

**Revisions:** 22 existing entries in 10 TSVs, plus this report. No new message IDs, lore arcs, scene code, branching choices, flags, event timing, or battle code. Every edited message retains its exact control-token/placeholder multiset and original message ID/context; edited pages were checked for at most 3 lines per page and 27 visible columns using 9-character name placeholders.

**Concrete continuity repair:** The Vale cottage scene's Kraden message `04017` previously claimed he had *been let inside* Sol Sanctum years before the first visit. That contradicts `sol_sanctum_entrance.c` and his subsequent first-time exploration. This now says he had studied the Sanctum for years but had never been permitted inside. Event branching and message order are untouched.

**Prologue and Vale:** Dora reassures Isaac when he hesitates during the evacuation instead of repeating the same command. Another villager advises the two boys how to stay safe. A village resident expresses relief that children can play again after the storm. The farewell advice emphasizes seeking help, the search for Jenna stays practical, and a resident's comment about Felix does not imply that the real Jenna will become evil. The later evil Ash Jenna remains entirely distinct.

**Sol Sanctum:** Kraden stays genuinely curious at the statue puzzle instead of insulting Isaac; all clues remain present. After the theft and eruption, Garet's Yes/No branches express relief and fear rather than a flippant reaction to the captives being taken.

**Vault, Bilibin, Kolima, Imil:** Ivan's isolation is given distinct human motivations without exposing his full powers prematurely. Vault condemns the thieves for exploiting the inn's hospitality. Bilibin characters take part of the responsibility for logging rather than simply blaming Lady McCoy; residents show self-preserving caution or dry humor alongside grief. Kolima's families remain the immediate reason to help Tret. In Imil, a young healer speaks from practical experience.

**Safety:** Scene-defined player progression and original event speakers are unchanged. The previous final narrative pass and original Jenna/Kraden ending are not altered. Text/source audit is not full gameplay verification. The new commit must pass dialogue/story checks, the ROM compiler and IPS creation before its patch can be treated as playtest-ready.
