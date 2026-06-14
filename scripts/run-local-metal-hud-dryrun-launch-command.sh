#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 61B Local Metal HUD Dry-Run Launch Command Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/generate-local-metal-hud-dryrun-launch-command.py --root "${ROOT_DIR}"
python3 scripts/summarize-local-metal-hud-dryrun-launch-command.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-local-metal-hud-dryrun-launch-command.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 61B verification passed =="
