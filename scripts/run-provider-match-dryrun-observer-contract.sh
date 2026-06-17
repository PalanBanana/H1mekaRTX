#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62E Provider Match Dry-Run Observer Contract Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/check-provider-match-dryrun-observer-contract.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62E verification passed =="
