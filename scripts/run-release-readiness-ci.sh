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

echo "== H1mekaRTX top-level release-readiness CI =="
echo "Root: $ROOT"
echo "Temp: $TMP_DIR"
echo "Out:  $OUT_DIR"

cd "$ROOT"

echo "== Release-readiness dashboard CI =="
bash scripts/run-release-readiness-dashboard-ci.sh --root "$ROOT" --out-dir "$TMP_DIR/release-dashboard-ci"

echo "== Repository safety gates =="
bash scripts/run-bar-safety-gates.sh

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

dashboard_ci_path = tmp / "release-dashboard-ci" / "release-readiness-dashboard-ci-report.json"
dashboard_ci = json.loads(dashboard_ci_path.read_text()) if dashboard_ci_path.exists() else {}

checks: list[dict[str, Any]] = []

def add_check(name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})

add_check("dashboard_ci_report_exists", dashboard_ci_path.exists(), str(dashboard_ci_path))
add_check(
    "dashboard_ci_decision",
    dashboard_ci.get("decision") == "PASS_RELEASE_READINESS_DASHBOARD_CI",
    f"decision={dashboard_ci.get('decision')!r}",
)
add_check(
    "dashboard_ci_ready",
    dashboard_ci.get("ci_entrypoint_ready") is True,
    f"value={dashboard_ci.get('ci_entrypoint_ready')!r}",
)
add_check(
    "dashboard_ci_failed_count_zero",
    dashboard_ci.get("failed_count") == 0,
    f"failed_count={dashboard_ci.get('failed_count')!r}",
)
add_check(
    "dashboard_ci_runtime_false",
    dashboard_ci.get("runtime_allowed_after_release_readiness_ci") is False,
    f"value={dashboard_ci.get('runtime_allowed_after_release_readiness_ci')!r}",
)
add_check(
    "dashboard_ci_rtx_runtime_false",
    dashboard_ci.get("rtx5070_metal_runtime_allowed") is False,
    f"value={dashboard_ci.get('rtx5070_metal_runtime_allowed')!r}",
)

rows = dashboard_ci.get("rows", [])
if not isinstance(rows, list):
    rows = []

add_check("dashboard_ci_rows_count", len(rows) == 5, f"count={len(rows)!r}")
add_check("dashboard_ci_rows_pass", all(isinstance(row, dict) and row.get("passed") is True for row in rows), f"rows={rows!r}")

passed_count = sum(1 for item in checks if item["passed"])
failed_count = len(checks) - passed_count

report = {
    "schema": "h1mekartx.release_readiness_ci_wrapper_report.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "repo_root": str(root),
    "decision": "PASS_RELEASE_READINESS_CI_WRAPPER" if failed_count == 0 else "FAIL_RELEASE_READINESS_CI_WRAPPER",
    "ci_wrapper_ready": failed_count == 0,
    "passed_count": passed_count,
    "failed_count": failed_count,
    "checks": checks,
    "dashboard_ci_decision": dashboard_ci.get("decision"),
    "dashboard_ci_ready": dashboard_ci.get("ci_entrypoint_ready"),
    "manual_review_only": True,
    "ci_wrapper_only": True,
    "metal_injection_goal": True,
    "metal_injection_runtime_allowed_now": False,
    "runtime_allowed_after_release_readiness_ci_wrapper": False,
    "live_system_queries_allowed": False,
    "runtime_buttons_enabled": False,
    "driver_runtime_allowed": False,
    "driver_installation_allowed": False,
    "driver_activation_allowed": False,
    "provider_attach_allowed": False,
    "device_ownership_allowed": False,
    "low_level_hardware_path_allowed": False,
    "rtx5070_metal_runtime_allowed": False,
    "next_stage_recommendation": "Stage 82 should add a GitHub Actions workflow static contract for the top-level release-readiness CI wrapper while keeping runtime disabled.",
    "safety_boundary": {
        "read_only": True,
        "ci_wrapper_only": True,
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

json_path = out_dir / "release-readiness-ci-wrapper-report.json"
md_path = out_dir / "release-readiness-ci-wrapper-report.md"

json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

check_lines = [
    f"| `{item['name']}` | {'PASS' if item['passed'] else 'FAIL'} | {str(item['detail']).replace('|', '\\|')} |"
    for item in checks
]

md_path.write_text(
    "\n".join(
        [
            "# Release Readiness CI Wrapper Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"CI wrapper ready: `{report['ci_wrapper_ready']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"CI wrapper only: `{report['ci_wrapper_only']}`",
            "",
            f"Runtime allowed after release readiness CI wrapper: `{report['runtime_allowed_after_release_readiness_ci_wrapper']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *check_lines,
            "",
            "## Safety Boundary",
            "",
            "This CI wrapper runs release-readiness checks and repository safety gates only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
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
