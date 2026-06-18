#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62U No-Open To Entitlement Request Handoff Ledger Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/build-noopen-to-entitlement-request-handoff-ledger.py
python3 scripts/check-noopen-to-entitlement-request-handoff-ledger.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62U verification passed =="
