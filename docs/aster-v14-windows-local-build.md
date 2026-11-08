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
5. Invokes `make -j2 tbs-en` **locally**.
6. Automatically restores the debug-entry source even when compilation
   fails and writes an internal log to `out/aster-v14-smoke/`.

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
