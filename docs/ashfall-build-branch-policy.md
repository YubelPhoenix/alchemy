# Ashfall: authoritative build and integration notes

**Authoritative build branch:** `dark-story-rewrite`.

The branch was consolidated from `mia-exit-smoothing` (its two tested Mercury
Aerie scene commits) and Heart's `games/tbs/src/battle/battle/background.c`
from `heart-backdrop-calm`. The resulting ROM workflow is intentionally
restricted to the authoritative branch.

## Gameplay changes integrated from Claude's tested branches

- `boss-ai-experiment` (source revision `190aa3aefd3a`): tactical AI for
  optional Kegare, Vale Ash Jenna and Heart, with their different round logic,
  target selection, cooldowns and rush safeguards.
- Optional superboss balancing from the same branch: Ash Jenna 9000 HP / 90
  Defense, Heart 9500 HP / 100 Defense, Kegare 8000 HP / 80 Defense.
  The ordinary Suhalla Gate Ash Jenna encounter remains separate.
- `boss-flip-fix` (source revision `7cf3e6e2d065`): boss sprite-facing fixes
  during applicable volcano/plasma camera moves.
- These source commits passed their own GitHub builds before integration.
  The primary build must also pass, and gameplay balance still requires
  emulator testing.

## What stays separate

- `boss-ai-experiment` and `boss-flip-fix`: their tested battle source changes
  are now integrated into the primary build, but retain these branches as
  recovery references until in-game stress testing is complete.
- `experiment/aster-*`: preserve until the latest coherent Aster design is
  selected and validated against map collision and exit requirements.
- Other historical branches remain intact as recovery points. Do not delete
  any branch or force-update `main` simply to reduce the branch count.

## Editing and testing discipline

1. Make story edits in `dark-story-rewrite`, not in a new gameplay branch.
2. Batch corrections, run local/static checks before each push, and avoid
   repeated GitHub Actions runs for every individual dialogue line.
3. The full build runs only for pushes on `dark-story-rewrite` or manual
   workflow dispatch; GitHub Actions concurrency cancels superseded builds
   on the same branch.
4. Confirm the `Golden-Sun-Ashfall-<SHA>` artifact contains exactly the expected
   source commit, and test the generated patch in the emulator.
5. Before integrating a separate feature, compare both refs, preserve unique
   files, and re-run the source/scene checks.
6. Mercury Aerie dialogue IDs 05532-05587 must match the event speaker calls.
   `MsgDarkDuelMiaStops` through `MsgDarkDuelSaturosResumes` must remain in
   the game catalogue. Do not treat a successful build on another branch as
   a tested story patch.

These are source and workflow controls. In-game sequence validation still
requires a playthrough of the resulting ROM.
