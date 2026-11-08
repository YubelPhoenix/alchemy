# Aster V14 — Windows/WSL local ROM smoke-test guide

**This compiles only on your own computer. It does not invoke GitHub Actions or
paid runners. Do not test against a personal Ashfall save.**

The repository branch is
[experiment/aster-v14-native-map-staging](https://github.com/YubelPhoenix/alchemy/tree/experiment/aster-v14-native-map-staging).
It is separate from `main` and `dark-story-rewrite`.

## One-time Windows setup

Open PowerShell and install the free WSL Ubuntu environment if needed:

```powershell
wsl --install -d Ubuntu
```

Restart Windows if asked. Open the Ubuntu application. From the Ubuntu terminal:

```bash
sudo apt update
sudo apt install -y build-essential git curl patch binutils-arm-none-eabi   pkg-config libpng-dev libutf8proc-dev python3-venv python3-pip

git clone --branch experiment/aster-v14-native-map-staging --single-branch   https://github.com/YubelPhoenix/alchemy.git ~/aster-v14-test

cd ~/aster-v14-test
bash tools/aster_v14_local_smoke.sh --check-only
bash tools/aster_v14_local_smoke.sh --map-only
bash tools/aster_v14_local_smoke.sh
```

**Do not run these commands from an existing working Ashfall checkout.**
The separate `~/aster-v14-test` clone is an experimental disposable worktree.

Run the three commands in order. **`--check-only` is the read-only
source audit. `--map-only` compiles the project's actual host-native
`ags-graphics` encoder and tests the full Map180 without needing the old
ARM compiler.** The final command is the much heavier actual ROM compile,
which depends on downloadable pinned compilers.

The build helper:
1. Verifies the exact branch, clean tracked checkout, native map snapshot,
   all story markers/NPCs, registered original Vale trees and Aster resources.
2. Prepares Ashfall's authored text in the disposable clone, then generates
   Heart, Ash Jenna, Kegare and Sarah graphics with dependencies installed
   into a local Python virtual environment under `out/`.
3. Builds the exact legacy Alchemy toolchain and native asset encoders via
   `make bootstrap` (may download public compiler source).
4. Temporarily installs the existing Aster `B+L+R+Start`
   field-entry shortcut in the disposable clone.
5. Optionally installs a reversible test-only world-map arrival (`--probe-world`).
6. Invokes `make -j2 tbs-en` **locally**.
7. Restores the temporary debug-entry and optional probe patches even when
   compilation fails and writes a local log to `out/aster-v14-smoke/`.

The map-only encoder's expected output is
`out/aster-v14-smoke/aster-map.grid.lz`. A nonempty file proves
the original graphics encoder accepted the native grid; it does **not**
prove that any field renders correctly or that a ROM has been built.

The toolchain sources and assets require local network downloads.
The existing `INSTALL.md` estimates roughly 500 MB for the
compiler tools. The script will not push, create a pull request, upload a ROM,
start an Actions run, or invoke Codespaces. Local package downloads are
separate from GitHub's metered Actions service. Check the private GitHub
billing dashboard for account charges.

## What success means

A successful command prints `LOCAL COMPILE PASS` and
saves the **local-only** modified ROM at:

```text
out/tbs-en/tbs-en.gba
```

Don't upload or redistribute the ROM. In mGBA, use a separate save.
From a normal field, hold B+L+R and press Start to enter experimental Aster.
The south exit currently uses a temporary Vault arrival. Never test with
your real save or assume a successful compile makes Aster release-ready.

## Optional: test Aster's provisional overworld clearing

The native overworld icon `SPRITE_WORLD_MAP_ASTER = 0x1f9` is now a
separate, registered 32×32 indexed icon, but its contact actor is NOT
on the map yet because the candidate location is unverified.

To test whether the area southwest of Vale and west-northwest of Vault
is safe to walk around, run **in the isolated disposable checkout only**:

```bash
bash tools/aster_v14_local_smoke.sh --probe-world
```

The build helper temporarily patches Aster's southern exit to UNUSED
world-map entrance 98 at X=5696, Z=1536 (32 pixels south of icon
X=5696, Z=1504). The probe also uses one unused signpost actor and
world exit kind 115 for icon-to-Aster contact. It restores both patched C
files and the scene exit header
even on compilation failure. This does not register the icon or alter
the main Ashfall branch.

In mGBA with a separate experimental save: enter Aster using B+L+R+Start
from a field, exit through the south, and attempt to walk from the
candidate site to Vault and back. **Then approach the new Aster icon from
outside and confirm that it enters Aster; leave through the southern gate
again.** Check for mountains, invisible walls, water, event collisions,
softlocks, wild encounters, stuck looping on an entrance, and camera issues.
If the site is blocked, do not implement it in production. Move the
candidate and rerun the source and in-emulator checks.

**This is a route test, not an approved overworld entrance.**
We must still register a new world actor/contact, reciprocal Aster
transition and test Isaac approaching the icon from outside.

## If it fails

The build log is saved at `out/aster-v14-smoke/*.log`.
Copy the **last 80–120 lines of that log** into the conversation. A compiler
or graphics encoding failure should be diagnosed before modifying unrelated
Golden Sun files. Avoid repeated Actions workflow runs.

Optional safe-only checks:

```bash
bash tools/aster_v14_local_smoke.sh --check-only
```

For existing local toolchains only, `--skip-bootstrap` avoids
rebuilding the pinned compiler. `--skip-assets` avoids regenerated
Ashfall graphics *only* when the disposable checkout already contains all
needed output.

## Remaining known game integration issues

This first compile is a **smoke test**, not a playable release:
the river/cliff/bridge native art is still provisional; the Sanctum and
additional house are collision-reserved but not implemented as true interiors;
the dry well/memorial art needs visual polish; and Aster's reciprocal overworld
area/contact is not registered. The source has no in-emulator acceptance
evidence for those features yet.
