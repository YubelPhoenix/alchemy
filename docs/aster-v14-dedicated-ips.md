# Aster V14 — dedicated IPS test build (not yet compiled)

The user-requested delivery artifact is **Aster_V14_Overworld_Test.ips**,
a completely separate patch for the original **Golden Sun: The Broken Seal
(USA/Europe, English)** game. It must NOT be applied on top of the existing
Ashfall IPS, because it is already a full-ROM differential patch.

## Contents of the planned IPS

- Source-native Aster Map180 and its provisional woods, paths and collision
- Seven Aster NPCs and nine native entrance/interaction markers
- Native dedicated Aster overworld icon, sprite 505
- B+L+R+Start experimental field shortcut into Aster
- Test-only two-way map connection using original dormant signpost slot 39:
  Aster icon at (5696,1504) and return at (5696,1536)
- Existing Ashfall story/asset preparations required to compile this branch

This is a **temporary test patch**, not a production release. Riverbanks,
cliffs and bridge seams, sanctum and extra-house interiors, overworld
walkability and save compatibility need emulator inspection.

## Generate only the IPS, locally and without GitHub Actions

After the WSL prerequisites described in
`docs/aster-v14-windows-local-build.md` are installed, in a separate
checkout of `experiment/aster-v14-native-map-staging`, run:

```bash
bash tools/aster_v14_build_ips.sh "/mnt/c/Users/YOUR-PC/your-clean-Golden-Sun.gba"
```

The script refuses any base whose SHA-1 differs from the repository's
canonical clean English game, `5c4695205413df7db52b9a184815a07783999971`.
It verifies the clean ROM **before** compiling, runs the existing local
Aster `--probe-world` build, then creates the IPS by comparing the local
compiled output to the clean base ROM.

Only the following two new outputs are intended for sharing:

- `out/aster-v14-smoke/Aster_V14_Overworld_Test.ips`
- `out/aster-v14-smoke/Aster_V14_Overworld_Test.manifest.json`

The generator applies the IPS in memory and **requires a byte-for-byte match**
to the compiled experimental ROM before writing the patch. The manifest
contains clean-ROM SHA-1, compiled-ROM SHA-256, IPS SHA-256, source commit,
changed-byte count and IPS record count. The game ROM is never uploaded.

## Applying and testing

Use a clean, unmodified English Golden Sun ROM with the exact checksum above.
Apply the IPS through Floating IPS or another trusted IPS patcher to a
**copy** of the original game. Open that copy in mGBA with a **new save**.
Do not reuse existing Ashfall saves: modified overlay addresses may differ.

Check the Aster woods, northern houses, all NPCs, southern exit, approach
to Vault, Aster icon entry and return. If any route is blocked or the
world map softlocks, report it; do not enable the overworld contact in
production yet.

## Status and billing

**No real V14 ROM or IPS has been compiled in this environment.**
The scripts and IPS-format test are prepared; this document is NOT the patch.
Older Aster workflow artifacts do NOT contain the current V14 two-way link.

The local scripts use local Python, local Git and local Make. They do not
start GitHub Actions, Codespaces, paid runners, or separate OpenAI API usage.
GitHub account fees and ChatGPT invoices must still be verified in each
service's private billing dashboard.
