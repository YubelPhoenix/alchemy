# Aster V14 — local smoke-test handoff (no GitHub Actions)

The staged Map180 and Aster scene are now real source files on
experiment/aster-v14-native-map-staging. They have passed source-level
validation, **not** a C compile or emulator test.

## Safety rules

- Work from a disposable local checkout of this isolated branch.
- Do not merge or push to main, dark-story-rewrite, or
  experiment/aster-convergence-town until a real playtest passes.
- Do not invoke GitHub Actions, paid runners, Codespaces, or cloud builds.
- Building a ROM **locally** on your own computer does not consume GitHub
  Actions minutes. Local computing and download requirements still apply.
- Back up any existing .sav files; use a separate experimental save slot.

## First run locally

Run from the project root with the toolchain described in INSTALL.md:

```bash
git switch experiment/aster-v14-native-map-staging
python3 tools/check_aster_v14.py
python3 tools/aster_dev_entry.py --check
```

The old `tools/aster_layout.py` is deliberately guarded against
overwriting the migrated map. Do not run it or the old
`tools/check_aster.py` as if they validate V14.

## Development entry (local changes only)

In a **disposable working tree**, after confirming
`tools/aster_dev_entry.py --check` passes:

```bash
python3 tools/aster_dev_entry.py --apply
# Follow INSTALL.md prerequisites for local toolchains, then:
make tbs-en
# Whatever the build outcome, before committing:
python3 tools/aster_dev_entry.py --restore
git status --short
```

The development shortcut was already present in the prototype, not
introduced in V14. Start a field scene, hold B+L+R and press Start to enter
Aster scene 201. If you cannot build from source, no genuine game QA can be
claimed from these instructions.

## Emulator QA checklist

1. Enter with the development shortcut, verify sprite priority and player
   position at tile (32,61). No black screen.
2. Walk the southern road and inspect all four natural borders.
   Only the south edge (32,63) should be accessible.
3. Visit the eight event tile approaches:
   e1 (32,36), e2 (29,20), e3 (18,22), e4 (16,35),
   e5 (17,47), e6 (41,48), e7 (48,35), e8 (45,22).
4. Talk to all seven NPCs; test Mind Read on the three scripted targets.
   Check the 27-character-per-line display rule visually.
5. Inspect water and cliff seams. The current native open-water cells are
   provisional and native bridge/shore materials are still incomplete.
6. Try the southern exit. **Expected unsafe prototype behavior:** it
   returns near Vault via WORLD_MAP_FROM_VAULT_SOUTH. Do not treat this as
   a correct Aster reciprocal world connection.
7. Test re-entry, save/load in an experimental slot, menus, Djinn and
   party state. Stop immediately if anything corrupts.

## Remaining launch blockers

- Register a safe, reciprocal world-map contact/arrival for Aster.
- Complete compatible shoreline/cliff/bridge graphics and collision QA.
- Create and wire native Sanctum and additional-home exteriors/interiors.
- Finish the well/memorial registered visual props.
- Replace the old generator and extend the full source contract.
- Compile and inspect real emulator screenshots before any merge.

The source branch is a meaningful integration step, **not a release build**.
