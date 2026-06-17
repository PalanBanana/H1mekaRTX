#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62I Sanitized Local Provider Visibility Capture Parser Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh

echo "== Verify default parser refusal =="
unset H1MEKARTX_PARSE_LOCAL_PROVIDER_VISIBILITY_CAPTURE || true
python3 scripts/parse-sanitized-local-provider-visibility-capture.py
python3 scripts/check-sanitized-local-provider-visibility-capture-parser.py

./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62I verification passed =="
