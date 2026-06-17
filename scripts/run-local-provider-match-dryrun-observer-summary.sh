#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62F Local Provider Match Dry-Run Observer Summary Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/summarize-local-provider-match-dryrun-observer.py
python3 scripts/check-local-provider-match-dryrun-observer-summary.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62F verification passed =="
