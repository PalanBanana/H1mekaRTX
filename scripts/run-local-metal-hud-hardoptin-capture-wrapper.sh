#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 61C Local Metal HUD Hard-Opt-In Capture Wrapper Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh

echo "== Verify default refusal =="
set +e
python3 scripts/local-metal-hud-hardoptin-capture-wrapper.py --root "${ROOT_DIR}" >/tmp/h1mekartx-phase61c-refuse.out 2>/tmp/h1mekartx-phase61c-refuse.err
RC="$?"
set -e
if [ "${RC}" = "0" ]; then
  echo "ERROR: wrapper must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase61c-refuse.out
  cat /tmp/h1mekartx-phase61c-refuse.err
  exit 1
fi

python3 scripts/summarize-local-metal-hud-hardoptin-capture.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-local-metal-hud-hardoptin-capture-wrapper.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 61C verification passed =="
