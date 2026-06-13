#!/usr/bin/env bash
set -euo pipefail

ROOT="."
OUT_DIR="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      ROOT="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

ROOT="$(cd "$ROOT" && pwd)"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "== H1mekaRTX release-readiness dashboard CI =="
echo "Root: $ROOT"
echo "Temp: $TMP_DIR"
echo "Out:  $OUT_DIR"

cd "$ROOT"

echo "== Python syntax =="
python3 -m py_compile \
  scripts/compare-release-readiness-dashboard-snapshot.py \
  scripts/check-release-readiness-dashboard-diff-guard.py \
  scripts/check-release-readiness-dashboard-static-contract.py \
  scripts/check-release-readiness-dashboard.py \
  scripts/generate-release-readiness-dashboard.py \
  scripts/generate-combined-gate-static-contract-badge.py \
  scripts/generate-combined-entitlement-packaging-gate-summary.py \
  scripts/resolve-entitlement-evidence.py \
  scripts/resolve-signed-extension-packaging-plan.py

echo "== Release readiness checks =="
./scripts/check-release-readiness-dashboard-diff-guard.py --root "$ROOT" --out-dir "$TMP_DIR/diff-guard"
./scripts/check-release-readiness-dashboard-static-contract.py --root "$ROOT" --out-dir "$TMP_DIR/static-contract"
./scripts/check-release-readiness-dashboard.py --root "$ROOT" --out-dir "$TMP_DIR/dashboard"
./scripts/check-combined-gate-static-contract-badge.py --root "$ROOT" --out-dir "$TMP_DIR/badge"
./scripts/check-combined-entitlement-packaging-gate-summary.py --root "$ROOT" --out-dir "$TMP_DIR/combined-gate"

python3 - "$ROOT" "$TMP_DIR" "$OUT_DIR" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


root = Path(sys.argv[1])
tmp = Path(sys.argv[2])
out_dir = Path(sys.argv[3])

schema = "h1mekartx.release_readiness_dashboard_ci_report.v1"

inputs = [
    {
        "id": "diff_guard",
        "path": tmp / "diff-guard" / "release-readiness-dashboard-diff-guard-check.json",
        "expected": "PASS_RELEASE_READINESS_DASHBOARD_DIFF_GUARD_READY",
        "runtime_key": None,
    },
    {
        "id": "static_contract",
        "path": tmp / "static-contract" / "release-readiness-dashboard-static-contract-check.json",
        "expected": "PASS_RELEASE_READINESS_DASHBOARD_STATIC_CONTRACT_READY",
        "runtime_key": None,
    },
    {
        "id": "dashboard",
        "path": tmp / "dashboard" / "release-readiness-dashboard-check.json",
        "expected": "PASS_RELEASE_READINESS_DASHBOARD_READY",
        "runtime_key": None,
    },
    {
        "id": "badge",
        "path": tmp / "badge" / "combined-gate-static-contract-badge-check.json",
        "expected": "PASS_COMBINED_GATE_STATIC_CONTRACT_BADGE_READY",
        "runtime_key": None,
    },
    {
        "id": "combined_gate",
        "path": tmp / "combined-gate" / "combined-entitlement-packaging-gate-summary-check.json",
        "expected": "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY_READY",
        "runtime_key": None,
    },
]

checks: list[dict[str, Any]] = []
rows: list[dict[str, Any]] = []

for item in inputs:
    path = item["path"]
    exists = path.exists()
    checks.append(
        {
            "name": f"{item['id']}:report_exists",
            "passed": exists,
            "detail": str(path),
        }
    )

    data: dict[str, Any] = {}
    if exists:
        data = json.loads(path.read_text())

    decision = data.get("decision")
    failed_count = data.get("failed_count")

    checks.append(
        {
            "name": f"{item['id']}:decision",
            "passed": decision == item["expected"],
            "detail": f"actual={decision!r}, expected={item['expected']!r}",
        }
    )

    checks.append(
        {
            "name": f"{item['id']}:failed_count_zero",
            "passed": failed_count == 0,
            "detail": f"failed_count={failed_count!r}",
        }
    )

    rows.append(
        {
            "id": item["id"],
            "decision": decision,
            "expected": item["expected"],
            "failed_count": failed_count,
            "passed": decision == item["expected"] and failed_count == 0,
        }
    )

passed_count = sum(1 for item in checks if item["passed"])
failed_count = len(checks) - passed_count

report = {
    "schema": schema,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "repo_root": str(root),
    "decision": "PASS_RELEASE_READINESS_DASHBOARD_CI" if failed_count == 0 else "FAIL_RELEASE_READINESS_DASHBOARD_CI",
    "ci_entrypoint_ready": failed_count == 0,
    "passed_count": passed_count,
    "failed_count": failed_count,
    "checks": checks,
    "rows": rows,
    "manual_review_only": True,
    "ci_entrypoint_only": True,
    "metal_injection_goal": True,
    "metal_injection_runtime_allowed_now": False,
    "runtime_allowed_after_release_readiness_ci": False,
    "live_system_queries_allowed": False,
    "runtime_buttons_enabled": False,
    "driver_runtime_allowed": False,
    "driver_installation_allowed": False,
    "driver_activation_allowed": False,
    "provider_attach_allowed": False,
    "device_ownership_allowed": False,
    "low_level_hardware_path_allowed": False,
    "rtx5070_metal_runtime_allowed": False,
    "next_stage_recommendation": "Stage 81 should add a top-level release-readiness CI wrapper that can be called from GitHub Actions while keeping runtime disabled.",
    "safety_boundary": {
        "read_only": True,
        "ci_entrypoint_only": True,
        "manual_review_only": True,
        "no_runtime": True,
        "no_driver_installation": True,
        "no_driver_activation": True,
        "no_provider_attach": True,
        "no_device_ownership": True,
        "no_low_level_hardware_path": True,
        "no_rtx5070_metal_runtime": True,
    },
}

json_path = out_dir / "release-readiness-dashboard-ci-report.json"
md_path = out_dir / "release-readiness-dashboard-ci-report.md"

json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

row_lines = [
    f"| `{row['id']}` | `{row['decision']}` | `{row['expected']}` | `{row['failed_count']}` | `{row['passed']}` |"
    for row in rows
]

check_lines = [
    f"| `{item['name']}` | {'PASS' if item['passed'] else 'FAIL'} | {str(item['detail']).replace('|', '\\|')} |"
    for item in checks
]

md_path.write_text(
    "\n".join(
        [
            "# Release Readiness Dashboard CI Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"CI entrypoint ready: `{report['ci_entrypoint_ready']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"CI entrypoint only: `{report['ci_entrypoint_only']}`",
            "",
            f"Runtime allowed after release readiness CI: `{report['runtime_allowed_after_release_readiness_ci']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Rows",
            "",
            "| ID | Decision | Expected | Failed Count | Passed |",
            "| --- | --- | --- | --- | --- |",
            *row_lines,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *check_lines,
            "",
            "## Safety Boundary",
            "",
            "This CI entrypoint runs release-readiness dashboard checks only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )
    + "\n"
)

print(f"Wrote: {json_path}")
print(f"Wrote: {md_path}")
print(f"Decision: {report['decision']}")

if failed_count:
    raise SystemExit(1)
PY
