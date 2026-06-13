#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_dashboard_diff_guard.v1"

DASHBOARD_SCRIPT = "scripts/generate-release-readiness-dashboard.py"
SNAPSHOT_JSON = "release-readiness/release-readiness-dashboard.snapshot.json"

COMPARE_KEYS = [
    "source_decision",
    "status",
    "release_readiness_dashboard_ready",
    "manual_review_only",
    "dashboard_only",
    "dashboard_row_count",
    "dashboard_rows",
    "combined_gate_badge",
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "runtime_allowed_after_release_readiness",
    "live_system_queries_allowed",
    "runtime_buttons_enabled",
    "driver_runtime_allowed",
    "driver_installation_allowed",
    "driver_activation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "low_level_hardware_path_allowed",
    "rtx5070_metal_runtime_allowed",
    "frozen_contract",
    "safety_boundary",
]


def run_dashboard(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / DASHBOARD_SCRIPT),
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    report_path = out_dir / "release-readiness-dashboard-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "report": report,
    }


def normalized_snapshot_from_report(report: dict[str, Any]) -> dict[str, Any]:
    badge = report.get("combined_gate_badge", {})
    if not isinstance(badge, dict):
        badge = {}

    rows = report.get("dashboard_rows", [])
    if not isinstance(rows, list):
        rows = []

    return {
        "schema": "h1mekartx.release_readiness_dashboard_snapshot.v1",
        "snapshot_version": 1,
        "source_schema": report.get("schema"),
        "source_decision": report.get("decision"),
        "status": report.get("status"),
        "release_readiness_dashboard_ready": report.get("release_readiness_dashboard_ready") is True,
        "manual_review_only": True,
        "dashboard_only": True,
        "dashboard_row_count": len(rows),
        "dashboard_rows": rows,
        "combined_gate_badge": {
            "schema": badge.get("schema"),
            "label": badge.get("label"),
            "message": badge.get("message"),
            "color": badge.get("color"),
            "contract_ready": badge.get("contract_ready") is True,
            "runtime_allowed_after_combined_gate": False,
            "rtx5070_metal_runtime_allowed": False,
        },
        "metal_injection_goal": report.get("metal_injection_goal") is True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_release_readiness": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "frozen_contract": {
            "release_readiness_status": "MANUAL_REVIEW_ONLY_NO_RUNTIME",
            "badge_message": "manual-review-only",
            "runtime_policy": "NO_RUNTIME",
            "manual_review_is_runtime_permission": False
        },
        "safety_boundary": {
            "read_only": True,
            "frozen_snapshot_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        }
    }


def values_equal(a: Any, b: Any) -> bool:
    return a == b


def build_report(root: Path) -> dict[str, Any]:
    snapshot_path = root / SNAPSHOT_JSON
    frozen = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {}

    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage79-") as tmp:
        run = run_dashboard(root, Path(tmp))

    generated = normalized_snapshot_from_report(run.get("report", {}))

    diffs = []
    for key in COMPARE_KEYS:
        frozen_value = frozen.get(key)
        generated_value = generated.get(key)
        if not values_equal(frozen_value, generated_value):
            diffs.append(
                {
                    "key": key,
                    "frozen": frozen_value,
                    "generated": generated_value,
                }
            )

    runtime_flags = {
        "generated_runtime_allowed_after_release_readiness": generated.get("runtime_allowed_after_release_readiness"),
        "generated_rtx5070_metal_runtime_allowed": generated.get("rtx5070_metal_runtime_allowed"),
        "frozen_runtime_allowed_after_release_readiness": frozen.get("runtime_allowed_after_release_readiness"),
        "frozen_rtx5070_metal_runtime_allowed": frozen.get("rtx5070_metal_runtime_allowed"),
    }

    runtime_disabled = all(value is False for value in runtime_flags.values())

    frozen_contract_ok = (
        frozen.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME"
        and frozen.get("combined_gate_badge", {}).get("message") == "manual-review-only"
        and frozen.get("frozen_contract", {}).get("runtime_policy") == "NO_RUNTIME"
        and frozen.get("frozen_contract", {}).get("manual_review_is_runtime_permission") is False
    )

    generated_contract_ok = (
        generated.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME"
        and generated.get("combined_gate_badge", {}).get("message") == "manual-review-only"
        and generated.get("frozen_contract", {}).get("runtime_policy") == "NO_RUNTIME"
        and generated.get("frozen_contract", {}).get("manual_review_is_runtime_permission") is False
    )

    guard_ready = (
        run.get("returncode") == 0
        and not diffs
        and runtime_disabled
        and frozen_contract_ok
        and generated_contract_ok
    )

    blockers = []
    if run.get("returncode") != 0:
        blockers.append("dashboard_generator_failed")
    if diffs:
        blockers.append("snapshot_diff_detected")
    if not runtime_disabled:
        blockers.append("runtime_policy_not_disabled")
    if not frozen_contract_ok:
        blockers.append("frozen_contract_invalid")
    if not generated_contract_ok:
        blockers.append("generated_contract_invalid")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "snapshot_path": SNAPSHOT_JSON,
        "decision": "PASS_RELEASE_READINESS_DASHBOARD_DIFF_GUARD" if guard_ready else "FAIL_RELEASE_READINESS_DASHBOARD_DIFF_GUARD",
        "diff_guard_ready": guard_ready,
        "dashboard_generator_returncode": run.get("returncode"),
        "diff_count": len(diffs),
        "diffs": diffs,
        "blockers": blockers,
        "runtime_flags": runtime_flags,
        "frozen_contract_ok": frozen_contract_ok,
        "generated_contract_ok": generated_contract_ok,
        "manual_review_only": True,
        "diff_guard_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_release_readiness": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 80 should add a release-readiness dashboard CI entrypoint script that runs all release-readiness checks without enabling runtime.",
        "safety_boundary": {
            "read_only": True,
            "diff_guard_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        }
    }


def markdown_report(report: dict[str, Any]) -> str:
    blocker_rows = [f"- `{item}`" for item in report["blockers"]] or ["- none"]

    diff_rows = []
    for item in report["diffs"]:
        diff_rows.append(f"| `{item['key']}` | changed |")

    if not diff_rows:
        diff_rows = ["| none | no diff |"]

    return "\n".join(
        [
            "# Release Readiness Dashboard Diff Guard Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Diff guard ready: `{report['diff_guard_ready']}`",
            "",
            f"Snapshot path: `{report['snapshot_path']}`",
            "",
            f"Diff count: `{report['diff_count']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Diff guard only: `{report['diff_guard_only']}`",
            "",
            f"Runtime allowed after release readiness: `{report['runtime_allowed_after_release_readiness']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Runtime Flags",
            "",
            f"- Generated release readiness runtime: `{report['runtime_flags']['generated_runtime_allowed_after_release_readiness']}`",
            f"- Generated RTX 5070 Metal runtime: `{report['runtime_flags']['generated_rtx5070_metal_runtime_allowed']}`",
            f"- Frozen release readiness runtime: `{report['runtime_flags']['frozen_runtime_allowed_after_release_readiness']}`",
            f"- Frozen RTX 5070 Metal runtime: `{report['runtime_flags']['frozen_rtx5070_metal_runtime_allowed']}`",
            "",
            "## Diffs",
            "",
            "| Key | Status |",
            "| --- | --- |",
            *diff_rows,
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage compares the generated release-readiness dashboard to the frozen snapshot only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare generated release-readiness dashboard to frozen snapshot.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "release-readiness-dashboard-diff-guard-report.json"
    md_path = out_dir / "release-readiness-dashboard-diff-guard-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["diff_guard_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
