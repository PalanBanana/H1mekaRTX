#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62Z Entitlement Request Local Submission Readiness Gate Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/build-entitlement-request-local-submission-readiness-gate.py
python3 scripts/check-entitlement-request-local-submission-readiness-gate.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62Z verification passed =="
