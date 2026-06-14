#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60L Real DriverKit Dext Build Gate Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Verify default refusal =="
set +e
python3 "${ROOT_DIR}/scripts/real-driverkit-dext-build-gate.py" --root "${ROOT_DIR}" >/tmp/h1mekartx-phase60l-default-refusal.out 2>/tmp/h1mekartx-phase60l-default-refusal.err
RC="$?"
set -e
if [ "${RC}" = "0" ]; then
  echo "ERROR: real DriverKit build gate must refuse without hard opt-in flags"
  cat /tmp/h1mekartx-phase60l-default-refusal.out
  cat /tmp/h1mekartx-phase60l-default-refusal.err
  exit 1
fi

python3 "${ROOT_DIR}/scripts/summarize-real-driverkit-dext-build-gate.py" --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 "${ROOT_DIR}/scripts/check-real-driverkit-dext-build-gate.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60L verification passed =="
