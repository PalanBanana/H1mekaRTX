#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62R No-Open Provider Match Dry-Run Evidence Matrix Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/build-noopen-provider-match-dryrun-evidence-matrix.py
python3 scripts/check-noopen-provider-match-dryrun-evidence-matrix.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62R verification passed =="
