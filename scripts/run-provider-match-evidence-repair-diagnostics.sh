#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60A Provider Match Evidence Repair Diagnostics Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh
python3 "${ROOT_DIR}/scripts/collect-provider-match-evidence-repair-diagnostics.py" --root "${ROOT_DIR}" --out-dir "host-report-bundle/provider-match-evidence-repair"
python3 "${ROOT_DIR}/scripts/summarize-provider-match-evidence-repair-diagnostics.py" --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 "${ROOT_DIR}/scripts/check-provider-match-evidence-repair-diagnostics.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60A verification passed =="
