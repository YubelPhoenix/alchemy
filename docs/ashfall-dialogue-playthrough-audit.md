# Golden Sun: Ashfall — Dialogue Test Playthrough Audit

This document tracks issues found during the in-game test. **A logged issue is not yet a change to the game's dialogue text.** Proposed replacements must be verified against scene context, character continuity, and the Alchemy text/event system before implementation.

## Outstanding issues

| ID | Location / event | Reported original dialogue | Problem | Status |
| --- | --- | --- | --- | --- |
| AFD-001 | Vale prologue — Dora waking Isaac | "wake him up quickly" | Tone and urgency do not fit the scene | Reported; exact text/context to verify |
| AFD-002 | Vale prologue — Dora and Kyle | "No... Kyle... Please, get up..." | Awkward given Kyle, Felix, and Felix's parents have been washed away | Reported; context to verify |
| AFD-003 | Prologue — Saturos | "it's a miracle we two walked out of it alive" | Unnatural phrasing | Reported; context to verify |
| AFD-004 | Prologue — Jenna | "Thanks for asking But. My family isn't coming back." | Unnatural wording and response contradicts Garet's preceding question | Reported; context to verify |
| AFD-005 | Vale — Dora | "You remind of Kyle, Isaac. More every day." | Missing word and awkward cadence | Reported; context to verify |
| AFD-006 | Vale — Dora | "you're nearly seventeen. You have Kyle's eyes. Some days its' hard." | Apostrophe, punctuation, and cadence problems | Reported; context to verify |
| AFD-007 | Prologue — Saturos | "he knows the mountain we should speak with him" | They have just spoken with Kraden; continuity error | Reported; context to verify |
| AFD-009 | Vault inn — Garet Yes/No choice | "They run whenever we get ne4ar. What now?" (playthrough transcription) | "What now?" cannot be answered with Yes or No; check player-choice branches before replacing | Reported; verify exact text and scene |
| AFD-008 | Vault — Hammet's caravan departure / destroyed bridge | "Master Hammet! This is terrible! The bridge has been destryed..." (transcribed during test; original spelling should be checked) | Entire scene appears unchanged from vanilla Golden Sun; needs Ashfall-specific editorial review without breaking the bridge/Lunpa event | Reported; no in-game text modified |
| AFD-010 | Vault inn — thieves discovered upstairs | "So you found us. Hammet's boy brought company. You should have stayed downstairs." (playthrough transcription) | Continuity error: Ivan is at the mayor's house, not accompanying Isaac and Garet; thieves should not refer to Ivan bringing anyone | Reported; proposed: "So, you found us. You two should have stayed downstairs." Verify occupants/choice branches before implementation |
| AFD-011 | Vault inn — Ivan reads Isaac's mind after thieves fight | Original live Ashfall rewrite at `04850`: "So this is where they hid everything." | This is a story continuity error; Ivan learns of Isaac's journey and the Elemental Stars. Earlier correction was incorrectly committed directly to pristine `main` `en.po`, causing the default CI's ROM SHA-1 comparison to fail. | **Fixed in the actual Ashfall TSV** on `dark-story-rewrite`: `tools/dark_story/phase5_vault_c.tsv` ID `04850`, text "I see... So you're / trying to recover the / Elemental Stars." Commit `304132c`. Restored `main` `en.po` byte-for-byte to baseline (blob `af39490`, commit `1fb8e20`). Both workflows need to finish and in-game behavior still needs verification. |
| AFD-012 | Custom world-map interlude: Mia vs hired thieves on snowy road south of Imil, immediately after Vault Inn | Opening: "Another quiet day in Imil" and 21 additional lines across two battles and interrogation | Existing scene was rewritten end-to-end for Mia's healer voice, her duty to Imil, the chief's failed attack, and the red-haired girl mystery. Verified mapping in `world_map.c`; original 22 N15–N36 messages retained with same contexts and ending/control tokens | **Source revised** in `tools/dark_story/phase7_mia_thieves.tsv` on `dark-story-rewrite`, commit `9281acef`; the full scene is on `dark-story-rewrite` (commit `9281acef`); follow-up N23/N31/N32 wording refinement committed as `b38655f` (burnt clothes and one glowing eye); checked line widths; fresh ROM build and in-game verification still pending |
| AFD-013 | Goma Cave Entrance — Ivan rejoins after the Vault thieves are jailed | The original reunion dialogue still plays, including Ivan's return from Lunpa and request to join Isaac's quest (IDs `05007`–`05024`) | Only Garet's opening line `05007` was covered by the dark-story TSV; all 17 follow-up entries were missing from rewrite coverage. Event traced in `games/tbs/src/scene/goma_cave_entrance.c`. | **Implemented in Ashfall source:** `tools/dark_story/phase_goma_ivan_rejoin.tsv`, `dark-story-rewrite` commit `45a3bd1`. IDs `05008`–`05024`; max 25 visible chars per line, <=3 lines per page; original message contexts, end controls, and runtime-name placeholders retained. Game build and playthrough verification pending. |

### AFD-008 editorial direction (not implemented)

Keep Hammet cautious, pragmatic, and politically aware. Preserve the bridge's destruction and the caravan's need to reroute via Lunpa. Avoid claiming Ash Jenna caused the destruction or implying Hammet knows about her. The sample wording discussed in chat is **provisional**, not verified against the complete scene, and must not be pasted directly into the event script.

## Implementation checklist

- Locate the precise dialogue contexts and IDs in `games/tbs/text/en.po`.
- Read each full scene, including preceding and following lines and original control tokens.
- Implement the approved revised text without altering message IDs or event control commands.
- Build the game, re-test the scene, and update each row's status from **Reported** to **Implemented / Verified** only after confirmation.

## Dialogue change acceptance rule (27-character limit)

Before approving Ashfall dialogue, check every display line in the complete event, not only changed words:

- At most **27 visible characters per ordinary dialogue line**, **3 lines per page**. Literal `\n` starts a line and `{page_break}` starts a new page.
- Preserve original message ID/context, ending and formatting control tokens, and runtime placeholders. Dynamic names must reserve enough display width.
- The existing build workflow runs `python3 tools/dark_story_rewrite.py`, rejecting overflow, invalid page counts, duplicate IDs, context mismatches, and altered control tokens **before compilation**. The game still needs in-engine visual verification.

**Mia scene acceptance:** Entries N15–N36 in `tools/dark_story/phase7_mia_thieves.tsv`, branch `dark-story-rewrite`, commit `b38655f`, have no width or page-count violations. Longest line: 27 characters in N19. Commit `9281acef` passed the full workflow; the later wording changes need their own completed build.

**Known unrelated failures:** Nov 6 GCC 2.95.2 download failed due to a connection reset; older artwork jobs failed for missing `cv2`. Neither is a dialogue-length violation.


### CI incident 2026-11-06: run 42291464940
`main` run `42291464940` failed at `make compare-tbs-en` with `/usr/bin/sha1sum: WARNING: 1 computed checksum did NOT match`. This workflow compares a pristine English ROM build against the published original checksum, so custom dialogue must never be written to `main` `games/tbs/text/en.po`. A previous AFD-011 change did precisely that. Corrective actions: restore original English `.po` on main (commit `1fb8e20`, original blob `af39490` verified identical), move the intended Ivan correction into the `dark-story-rewrite` dialogue-source TSV (commit `304132c`). This incident was not a 27-character dialogue violation. Reverify post-fix CI before marking passed.