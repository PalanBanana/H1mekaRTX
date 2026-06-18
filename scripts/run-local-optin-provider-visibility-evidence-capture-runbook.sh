#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62K Local Opt-In Provider Visibility Evidence Capture Runbook Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/check-local-optin-provider-visibility-evidence-capture-runbook.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62K verification passed =="
