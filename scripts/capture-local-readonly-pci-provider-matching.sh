#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/host-report-bundle/readonly-pci-provider-matching}"

echo "== H1mekaRTX Local Read-Only PCI Provider Matching Capture =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

python3 "${ROOT_DIR}/scripts/check-readonly-pci-provider-matching-gate.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}" \
  --collect-local

echo "== Local read-only PCI provider matching capture complete =="
ls -lh "${OUT_DIR}"/readonly-pci-provider-matching-gate-check.*
