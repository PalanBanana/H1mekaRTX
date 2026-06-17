#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62H Local Read-Only Provider Visibility Capture Wrapper Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh

echo "== Verify default refusal =="
unset H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY || true
python3 scripts/capture-local-readonly-provider-visibility.py
python3 scripts/check-local-readonly-provider-visibility-capture-wrapper.py

./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62H verification passed =="
