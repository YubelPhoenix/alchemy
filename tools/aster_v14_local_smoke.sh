#!/usr/bin/env bash
# Aster V14 - local experimental ROM build. No GitHub Actions or uploads.
set -Eeuo pipefail

EXPECTED_BRANCH='experiment/aster-v14-native-map-staging'
CHECK_ONLY=0
SKIP_BOOTSTRAP=0
SKIP_ASSETS=0
MAP_ONLY=0
WORLD_PROBE=0

usage() {
  cat <<'EOF'
Usage: bash tools/aster_v14_local_smoke.sh [--check-only] [--skip-bootstrap] [--skip-assets] [--map-only] [--probe-world]
  --check-only      Run source checks; do not build or patch any game source.
  --skip-bootstrap  Use an already built local pinned compiler toolchain.
  --skip-assets     Skip Ashfall art/text preparation (only for already prepared checkouts).
  --map-only        Build only the native map encoder and encode Aster Map180.
  --probe-world     Temporarily route Aster's exit to unused world entrance 98
                    at UNVERIFIED world position (5696,1536), south of icon (5696,1504).
This script never pushes, invokes GitHub Actions, uses Codespaces or uploads a ROM.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --check-only) CHECK_ONLY=1 ;;
    --skip-bootstrap) SKIP_BOOTSTRAP=1 ;;
    --skip-assets) SKIP_ASSETS=1 ;;
    --map-only) MAP_ONLY=1 ;;
    --probe-world) WORLD_PROBE=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unrecognized option: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

if (( WORLD_PROBE && (CHECK_ONLY || MAP_ONLY) )); then
  echo 'STOP: --probe-world is only useful for a full ROM build.' >&2
  exit 2
fi

if ! command -v git >/dev/null || ! command -v python3 >/dev/null || ! command -v make >/dev/null; then
  echo 'STOP: git, python3 and make are required.' >&2
  exit 1
fi

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" || ! -d "$ROOT/.git" ]]; then
  echo 'STOP: run from a real, disposable alchemy Git checkout.' >&2
  exit 1
fi
cd "$ROOT"
branch="$(git branch --show-current)"
if [[ "$branch" != "$EXPECTED_BRANCH" ]]; then
  echo "STOP: refusing to build branch '$branch'; expected '$EXPECTED_BRANCH'." >&2
  exit 1
fi

# No automatic reset/clean/merge; all tracked edits must be resolved first.
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo 'STOP: tracked working tree is dirty. Review and preserve local edits first.' >&2
  exit 1
fi

printf 'Checking isolated Aster source, without network or paid services...\n'
python3 tools/aster_v14_preflight.py

if (( CHECK_ONLY )); then
  echo 'CHECK-ONLY PASS: no ROM built and no game code modified.'
  exit 0
fi
if (( MAP_ONLY )); then
  mkdir -p out/aster-v14-smoke
  echo 'Building Alchemy native map encoder locally (no ARM compiler)...'
  make -f tools/Makefile tools/out/ags-graphics
  result='out/aster-v14-smoke/aster-map.grid.lz'
  tools/out/ags-graphics games/tbs/src/map/map_180/map.txt "$result"
  if [[ ! -s "$result" ]]; then
    echo "STOP: map encoder produced no output: $result" >&2
    exit 1
  fi
  echo "MAP ENCODE PASS: $result"
  wc -c < "$result" | awk '{printf "Encoded map bytes: %s\n", $1}'
  echo 'This verifies native map encoding, NOT ROM compilation or emulator behavior.'
  exit 0
fi

mkdir -p out/aster-v14-smoke
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
log="$ROOT/out/aster-v14-smoke/$stamp.log"
exec > >(tee -a "$log") 2>&1

echo "Aster isolated local build: $stamp"
echo "Branch: $branch"
echo 'Cost: local machine only; this script has no Actions, Codespaces or paid-runner calls.'
echo "Log: $log"

if [[ ! -f alchemy-gcc/Makefile ]]; then
  echo 'Initializing pinned public compiler submodule (git download, no push)...'
  git submodule update --init --recursive alchemy-gcc
fi

if (( ! SKIP_ASSETS )); then
  echo 'Preparing Ashfall text and custom graphics in this disposable checkout...'
  python3 tools/aster_prepare_messages.py
  python3 tools/dark_story_rewrite.py
  python3 tools/aster_polish_dialogue.py --apply
  python3 tools/aster_prepare_messages.py --verify
  venv="$ROOT/out/aster-v14-smoke/.venv"
  if [[ ! -x "$venv/bin/python" ]]; then
    python3 -m venv "$venv" || {
      echo 'STOP: Python venv setup failed; install python3-venv.' >&2
      exit 1
    }
  fi
  "$venv/bin/python" -m pip install --disable-pip-version-check \
    Pillow numpy opencv-python-headless
  for tool in \
    build_heart_art.py build_ash_jenna_art.py build_kegare_art.py \
    build_sarah_art.py build_sarah_overworld.py; do
    "$venv/bin/python" "tools/dark_story/$tool"
  done
  python3 tools/check_aster.py
else
  echo 'SKIP: generated Ashfall assets and message preparation; build may fail.'
fi

if (( ! SKIP_BOOTSTRAP )); then
  echo 'Building pinned Alchemy compiler tools and native asset encoders locally...'
  make -j2 bootstrap CARGO=false
else
  [[ -x tools/out/compilers/xgcc && -x tools/out/ags-graphics && -x tools/out/compilers/as ]] || {
    echo 'STOP: --skip-bootstrap chosen but required local tools are missing.' >&2
    exit 1
  }
fi

# Patch only the disposable test worktree; restore on every exit path.
PATCH_APPLIED=0
PROBE_APPLIED=0
cleanup() {
  code=$?
  trap - EXIT
  if (( PROBE_APPLIED )); then
    echo 'Restoring experimental overworld route probe in tracked source...'
    if ! python3 tools/aster_world_route_probe.py --restore; then
      echo 'WARNING: world-probe source restoration failed; inspect git diff!' >&2
      code=1
    fi
  fi
  if (( PATCH_APPLIED )); then
    echo 'Restoring development-only Aster shortcut in tracked source...'
    if ! python3 tools/aster_dev_entry.py --restore; then
      echo 'WARNING: restoration failed; inspect git diff before leaving this checkout!' >&2
      code=1
    fi
  fi
  if (( code )); then
    echo "BUILD FAILED; inspect log: $log" >&2
  fi
  exit "$code"
}
trap cleanup EXIT

python3 tools/aster_dev_entry.py --apply
PATCH_APPLIED=1
if (( WORLD_PROBE )); then
  PROBE_APPLIED=1
  python3 tools/aster_world_route_probe.py --apply
  echo 'WORLD PROBE: Aster south gate now returns to (5696,1536); icon at (5696,1504).'
fi

echo 'Compiling English experimental Golden Sun ROM locally...'
make -j2 tbs-en CARGO=false
rom='out/tbs-en/tbs-en.gba'
if [[ ! -s "$rom" ]]; then
  echo "STOP: compilation did not produce $rom" >&2
  exit 1
fi

# The temporary test-entry patch is intentionally included in the compiled ROM.
# Do not distribute this ROM or use real Ashfall saves for testing.
echo "LOCAL COMPILE PASS: $rom"
wc -c < "$rom" | awk '{printf "Compiled ROM bytes: %s\n", $1}'
sha256sum "$rom"
echo 'The compiled ROM contains the experimental B+L+R+Start Aster field shortcut.'
if (( WORLD_PROBE )); then
  echo 'WORLD PROBE TEST: Exit Aster, walk to Vault, then approach the new Aster icon.'
  echo 'Do NOT use existing saves. The overworld coordinate is NOT VERIFIED safe.'
else
  echo 'Test using a separate .sav file; world-map return is still a temporary Vault placeholder.'
fi
echo 'No ROM is uploaded or redistributed by this script.'
