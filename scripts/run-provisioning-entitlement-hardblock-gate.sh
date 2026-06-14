#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60Q Provisioning Entitlement Hardblock Gate Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh
python3 "${ROOT_DIR}/scripts/check-provisioning-entitlement-hardblock-gate.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60Q verification passed =="
