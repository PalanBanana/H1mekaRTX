#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62P No-Open Provider Match Dry-Run Hard-Opt-In Wrapper Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh

echo "== Verify default refusal =="
unset H1MEKARTX_ALLOW_NOOPEN_PROVIDER_MATCH_DRYRUN || true
python3 scripts/run-noopen-provider-match-dryrun-hardoptin-wrapper.py
python3 scripts/check-noopen-provider-match-dryrun-hardoptin-wrapper.py

./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62P verification passed =="
