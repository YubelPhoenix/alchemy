# Ashfall — final dialogue proofread and continuity check

**Date:** 3 November 2026. **Branch:** `dark-story-rewrite`. **Base commit:** `67a0788ca0d699791682373655cd5e33f879c38c`.

## Coverage

Reviewed the 77 dialogue replacement TSV files in batches. Checked TSV structure, message endings, three-row page limits, visible-line widths, common misspellings, repeated words and obvious grammatical constructions. Read representative full narrative passages spanning Vale, Sol Sanctum, Vault, Bilibin, Kolima, Imil/Mercury, Altin, Lamakan, Tolbi, Babi, Venus Lighthouse, Lalivero, and the original ending, and compared major beats with the continuity ledger. This is a static editorial pass; no automated checker can certify all nuance of thousands of dialogue lines.

## Findings and changes

- No widespread obvious spelling or TSV-format errors were found in the dialogue scans.
- The Babi line previously flagged as possibly missing **were** (message `08932`) already reads “I thought you were Lemurians.” It is grammatical, and no change was necessary.
- Venus Lighthouse aftermath messages `10306`, `10308`, and `10310` repeated the same “tell Jenna what Felix did” point. They now distinguish gentle truth-telling, hearing Jenna's possible self-blame, and offering companionship.
- Optional Ash Jenna post-Venus Lalivero message `N313` now says “Go find them, then,” instead of “Go on. Run after them,” since Jenna and Kraden are missing, not visibly fleeing.
- These four messages preserve original message IDs, event context, all control tokens and actor-name placeholders. They were verified for a maximum of three rows and 27 visible columns per page.

## Continuity and scope

The original Jenna remains the goal of Isaac's search; alternate Ash Jenna remains ruthless and distinct. The party does not know Felix and Sheba's fate before the original reveal. Ash Jenna's claim about the Wise One is not objective proof. Optional Heart and Kegare encounters are independent. Kraden's Sol Sanctum first-visit contradiction was corrected in the earlier narrative pass.

## Acceptance limits

**Editorial/static check complete, runtime validation outstanding.** This commit still requires a successful dialogue validation and ROM/IPS build before its patch should be used. The separately reported world-map A-button freeze remains an open gameplay defect, not a grammatical or narrative defect.
