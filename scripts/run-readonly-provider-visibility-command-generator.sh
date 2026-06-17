#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62G Read-Only Provider Visibility Command Generator Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/generate-readonly-provider-visibility-commands.py
python3 scripts/check-readonly-provider-visibility-command-generator.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62G verification passed =="
