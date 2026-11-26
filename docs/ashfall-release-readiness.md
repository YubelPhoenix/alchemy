# Ashfall — first-release readiness

Status: development / release candidate. The planned first public release is `v0.9.0-rc.1`. This document is a proposed release-note summary and a checklist, not a certification that gameplay testing or distribution clearance is complete.

## Planned release notes (spoiler-free)

Golden Sun: Ashfall reimagines the original GBA adventure while retaining the original campaign's foundation.

- Rewritten campaign dialogue and additional character encounters.
- Optional superbosses and custom battle artwork and animations.
- Expanded Psynergy and tactical combat mechanics.
- The Umbral Rift, an additional area built around familiar places made unfamiliar.
- Narrative continuity, dialogue and encounter refinements during development.

These are project features, not changes since a previous public release. Update the notes with the exact fixes and known issues for the tested candidate before publication.

## Test and packaging checklist

- [ ] Identify the exact candidate source commit and successful workflow run. Record both here or in the draft release.
- [ ] Download and preserve the corresponding versioned patch artifact before it expires. The package includes `Golden-Sun-Ashfall.ips` and `ashfall-build.txt`.
- [ ] Verify the clean English Golden Sun base ROM against SHA-1 `5c4695205413df7db52b9a184815a07783999971` (see [rom.sha1](../rom.sha1)).
- [ ] Apply the patch to a copy of that ROM, verify it launches, and start a fresh save.
- [ ] Play the main campaign from Vale through the original ending; verify choices, dialogue, portraits, event sequencing, travel and save/load.
- [ ] Test optional encounters independently, including losses, retries and revisits where supported; do not assume an enforced boss defeat order.
- [ ] Test Umbral Rift entrances, exits, optional paths, collision, battle triggers and return travel.
- [ ] Test custom Psynergy, battle effects, resource costs and animations; record reproducible problems.
- [ ] Resolve release-blocking bugs and retest the exact patched build; don't mark untested paths as passed.
- [ ] Capture genuine, spoiler-free gameplay: exploration, dialogue, battles and custom mechanics. Do not use simulated gameplay images.
- [ ] Record any known limitations and supported save compatibility in the release notes.
- [ ] Review upstream permissions, third-party artwork/music credits, and distribution rights; patch-only distribution does not by itself establish permission.
- [ ] Package the tested IPS, source/build record, installation instructions and SHA-256 checksum of the distributed patch. Do not include a complete ROM.
- [ ] Pin the release tag to the tested source commit, not an untested newer branch head.
- [ ] Review the draft and its attachments, then publish only with the author's approval.

## Candidate record

| Field | Value |
| --- | --- |
| Version | Planned v0.9.0-rc.1 |
| Source commit | Pending selection |
| Workflow run | Pending selection |
| IPS SHA-256 | Pending calculation |
| Emulator / hardware | Pending testing |
| Save compatibility | Not yet established |
| Gameplay acceptance | Pending |
| Distribution review | Pending |

The [official build workflow](../.github/workflows/build-ashfall.yml) creates a versioned IPS artifact; an automated build is not a complete gameplay test. The [release page](https://github.com/YubelPhoenix/alchemy/releases) is the intended location for public downloads after approval.

Do not trigger or modify builds solely for documentation changes.
