#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 63A Manual Entitlement Request Packet Export Checklist Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/build-manual-entitlement-request-packet-export-checklist.py
python3 scripts/check-manual-entitlement-request-packet-export-checklist.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 63A verification passed =="
