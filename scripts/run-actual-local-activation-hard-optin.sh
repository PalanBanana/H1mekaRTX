#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 57B Actual Local Activation Hard Opt-In Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Verify default activation refusal =="
set +e
python3 "${ROOT_DIR}/scripts/actual-local-activation-hard-optin.py" --root "${ROOT_DIR}" >/tmp/h1mekartx-phase57b-default-refusal.out 2>/tmp/h1mekartx-phase57b-default-refusal.err
RC="$?"
set -e
if [ "${RC}" = "0" ]; then
  echo "ERROR: activation script must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase57b-default-refusal.out
  cat /tmp/h1mekartx-phase57b-default-refusal.err
  exit 1
fi

python3 "${ROOT_DIR}/scripts/check-actual-local-activation-hard-optin.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 57B verification passed =="
