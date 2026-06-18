#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62Q Sanitized No-Open Provider Match Dry-Run Output Parser Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh

echo "== Verify default parser refusal =="
unset H1MEKARTX_PARSE_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT || true
python3 scripts/parse-sanitized-noopen-provider-match-dryrun-output.py
python3 scripts/check-sanitized-noopen-provider-match-dryrun-output-parser.py

./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62Q verification passed =="
