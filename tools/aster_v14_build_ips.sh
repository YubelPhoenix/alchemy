#!/usr/bin/env bash
# Create an experimental IPS for Aster V14 entirely on the user's PC.
set -Eeuo pipefail
if [[ $# -ne 1 ]]; then
  echo 'Usage: bash tools/aster_v14_build_ips.sh "/path/to/clean Golden Sun (USA, Europe).gba"' >&2
  exit 2
fi
if [[ ! -f "$1" ]]; then
  echo 'The supplied clean Golden Sun ROM was not found' >&2
  exit 2
fi
BASE=$(realpath "$1")
echo 'ASTER V14 EXPERIMENTAL FULL-ROM PATCH (not Aster-only).'
echo 'This patch contains every change in the V14 test build, and may lack'
echo 'newer dark-story-rewrite boss AI/balance. Do NOT stack patches.'
echo 'Use only a copy of the exact clean English Golden Sun ROM.'
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
if [[ $(git branch --show-current) != 'experiment/aster-v14-native-map-staging' ]]; then
  echo 'STOP: this builder only supports the isolated V14 staging branch' >&2
  exit 1
fi
if [[ -n $(git status --porcelain --untracked-files=no) ]]; then
  echo 'STOP: tracked files have edits; preserve them before building' >&2
  exit 1
fi
python3 - "$BASE" <<'PY'
import sys,hashlib
from pathlib import Path
expected="5c4695205413df7db52b9a184815a07783999971"
actual=hashlib.sha1(Path(sys.argv[1]).read_bytes()).hexdigest()
if actual!=expected:
    raise SystemExit("Wrong original English Golden Sun ROM: "+actual+"; expected "+expected)
print("PASS verified clean TBS English ROM")
PY
python3 tools/aster_v14_make_ips.py --self-test
bash tools/aster_v14_local_smoke.sh --probe-world
python3 tools/aster_v14_make_ips.py --clean "$BASE" \
  --modified out/tbs-en/tbs-en.gba \
  --out out/aster-v14-smoke/Aster_V14_Overworld_Test.ips
echo 'IPS ready at out/aster-v14-smoke/Aster_V14_Overworld_Test.ips'
echo 'Apply to a COPY of the clean ROM, not your existing Ashfall patched ROM.'
echo 'No GitHub Actions, Codespaces, paid runners, API calls, or ROM uploads.'
