# Ashfall: authoritative build and integration notes

**Authoritative build branch:** `dark-story-rewrite`.

The branch was consolidated from `mia-exit-smoothing` (its two tested Mercury
Aerie scene commits) and Heart's `games/tbs/src/battle/battle/background.c`
from `heart-backdrop-calm`. The resulting ROM workflow is intentionally
restricted to the authoritative branch.

## What stays separate

- `boss-ai-experiment`: keep intact until stress testing and gameplay balance
  are complete. Do not replace current battle files without a targeted review.
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
4. Confirm the `ashfall-ips-<SHA>` artifact contains exactly the expected
   source commit, and test the generated patch in the emulator.
5. Before integrating a separate feature, compare both refs, preserve unique
   files, and re-run the source/scene checks.
6. Mercury Aerie dialogue IDs 05532-05587 must match the event speaker calls.
   `MsgDarkDuelMiaStops` through `MsgDarkDuelSaturosResumes` must remain in
   the game catalogue. Do not treat a successful build on another branch as
   a tested story patch.

These are source and workflow controls. In-game sequence validation still
requires a playthrough of the resulting ROM.
