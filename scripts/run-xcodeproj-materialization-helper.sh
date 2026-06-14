#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60N XcodeProj Materialization Helper Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Verify default refusal =="
set +e
python3 "${ROOT_DIR}/scripts/xcodeproj-materialization-helper.py" --root "${ROOT_DIR}" >/tmp/h1mekartx-phase60n-default-refusal.out 2>/tmp/h1mekartx-phase60n-default-refusal.err
RC="$?"
set -e
if [ "${RC}" = "0" ]; then
  echo "ERROR: xcodeproj materialization helper must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase60n-default-refusal.out
  cat /tmp/h1mekartx-phase60n-default-refusal.err
  exit 1
fi

python3 "${ROOT_DIR}/scripts/summarize-xcodeproj-materialization-helper.py" --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 "${ROOT_DIR}/scripts/check-xcodeproj-materialization-helper.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60N verification passed =="
