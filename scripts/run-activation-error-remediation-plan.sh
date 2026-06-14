#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60G Activation Error Remediation Plan Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh
python3 "${ROOT_DIR}/scripts/check-activation-error-remediation-plan.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60G verification passed =="
