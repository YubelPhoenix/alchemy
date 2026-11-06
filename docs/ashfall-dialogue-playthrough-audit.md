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
| AFD-008 | Vault — Hammet's caravan departure / destroyed bridge | "Master Hammet! This is terrible! The bridge has been destryed..." (transcribed during test; original spelling should be checked) | Entire scene appears unchanged from vanilla Golden Sun; needs Ashfall-specific editorial review without breaking the bridge/Lunpa event | Reported; no in-game text modified |

### AFD-008 editorial direction (not implemented)

Keep Hammet cautious, pragmatic, and politically aware. Preserve the bridge's destruction and the caravan's need to reroute via Lunpa. Avoid claiming Ash Jenna caused the destruction or implying Hammet knows about her. The sample wording discussed in chat is **provisional**, not verified against the complete scene, and must not be pasted directly into the event script.

## Implementation checklist

- Locate the precise dialogue contexts and IDs in `games/tbs/text/en.po`.
- Read each full scene, including preceding and following lines and original control tokens.
- Implement the approved revised text without altering message IDs or event control commands.
- Build the game, re-test the scene, and update each row's status from **Reported** to **Implemented / Verified** only after confirmation.
