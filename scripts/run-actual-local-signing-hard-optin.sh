#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 54 Actual Local Signing Hard Opt-In Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Verify default signer refusal =="
set +e
python3 "${ROOT_DIR}/scripts/actual-local-signing-hard-optin.py" --root "${ROOT_DIR}" >/tmp/h1mekartx-phase54-default-refusal.out 2>/tmp/h1mekartx-phase54-default-refusal.err
SIGNER_RC="$?"
set -e
if [ "${SIGNER_RC}" = "0" ]; then
  echo "ERROR: signer must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase54-default-refusal.out
  cat /tmp/h1mekartx-phase54-default-refusal.err
  exit 1
fi

python3 "${ROOT_DIR}/scripts/check-actual-local-signing-hard-optin.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"

"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 54 verification passed =="
