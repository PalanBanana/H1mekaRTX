#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/host-report-bundle/reversible-driverkit-activation-dryrun}"

echo "== H1mekaRTX Local Reversible DriverKit Activation Dry-Run Status Capture =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

python3 "${ROOT_DIR}/scripts/check-reversible-driverkit-activation-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}" \
  --collect-local

echo "== Local reversible DriverKit activation dry-run status capture complete =="
ls -lh "${OUT_DIR}"/reversible-driverkit-activation-dryrun-check.*
