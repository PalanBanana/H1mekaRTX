#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60I Applications Location Activation Remediation Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Verify default refusal =="
set +e
python3 "${ROOT_DIR}/scripts/applications-location-activation-remediation.py" --root "${ROOT_DIR}" >/tmp/h1mekartx-phase60i-default-refusal.out 2>/tmp/h1mekartx-phase60i-default-refusal.err
RC="$?"
set -e
if [ "${RC}" = "0" ]; then
  echo "ERROR: Applications staging script must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase60i-default-refusal.out
  cat /tmp/h1mekartx-phase60i-default-refusal.err
  exit 1
fi

python3 "${ROOT_DIR}/scripts/check-applications-location-activation-remediation.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60I verification passed =="
