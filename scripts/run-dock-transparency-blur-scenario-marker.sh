#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 60W Dock Transparency Blur Scenario Marker Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh

echo "== Verify default refusal =="
set +e
python3 scripts/record-dock-transparency-blur-scenario-marker.py --root "${ROOT_DIR}" >/tmp/h1mekartx-phase60w-default.out 2>/tmp/h1mekartx-phase60w-default.err
RC="$?"
set -e
if [ "${RC}" = "0" ]; then
  echo "ERROR: scenario marker must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase60w-default.out
  cat /tmp/h1mekartx-phase60w-default.err
  exit 1
fi

python3 scripts/summarize-dock-transparency-blur-scenario-marker.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-dock-transparency-blur-scenario-marker.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 60W verification passed =="
