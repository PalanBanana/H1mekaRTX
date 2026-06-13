#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_dashboard_report.v1"

TEMPLATE_PATH = "release-readiness/release-readiness-dashboard.template.json"
BADGE_SCRIPT = "scripts/generate-combined-gate-static-contract-badge.py"

REQUIRED_ROWS = [
    "swiftui_host_app",
    "local_report_import",
    "entitlement_evidence",
    "packaging_plan",
    "combined_gate",
    "combined_gate_badge",
    "safety_gates",
    "rtx5070_metal_runtime",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def run_badge(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / BADGE_SCRIPT),
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

    badge_path = out_dir / "combined-gate-status-badge.json"
    report_path = out_dir / "combined-gate-static-contract-badge-report.json"

    badge = json.loads(badge_path.read_text()) if badge_path.exists() else {}
    badge_report = json.loads(report_path.read_text()) if report_path.exists() else {}

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "badge": badge,
        "badge_report": badge_report,
    }


def build_report(root: Path) -> dict[str, Any]:
    template = load_json(root / TEMPLATE_PATH)
    rows = template.get("dashboard_rows", [])
    if not isinstance(rows, list):
        rows = []

    row_ids = [
        item.get("id")
        for item in rows
        if isinstance(item, dict)
    ]

    missing_rows = [
        row_id for row_id in REQUIRED_ROWS
        if row_id not in row_ids
    ]

    runtime_enabled_rows = [
        item.get("id")
        for item in rows
        if isinstance(item, dict) and item.get("runtime_allowed") is not False
    ]

    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage77-") as tmp:
        badge_run = run_badge(root, Path(tmp))

    badge = badge_run.get("badge", {})
    badge_report = badge_run.get("badge_report", {})

    badge_ok = (
        badge_run.get("returncode") == 0
        and badge.get("schema") == "h1mekartx.combined_gate_status_badge.v1"
        and badge.get("message") == "manual-review-only"
        and badge.get("contract_ready") is True
        and badge.get("runtime_allowed_after_combined_gate") is False
        and badge.get("rtx5070_metal_runtime_allowed") is False
    )

    badge_report_ok = (
        badge_report.get("decision") == "PASS_COMBINED_GATE_STATIC_CONTRACT_BADGE"
        and badge_report.get("failed_count") == 0
        and badge_report.get("combined_gate_static_contract_badge_ready") is True
        and badge_report.get("runtime_allowed_after_combined_gate") is False
        and badge_report.get("rtx5070_metal_runtime_allowed") is False
    )

    template_runtime_ok = (
        template.get("metal_injection_goal") is True
        and template.get("metal_injection_runtime_allowed_now") is False
        and template.get("runtime_allowed_after_release_readiness") is False
        and template.get("rtx5070_metal_runtime_allowed") is False
        and template.get("driver_runtime_allowed") is False
        and template.get("driver_installation_allowed") is False
        and template.get("driver_activation_allowed") is False
        and template.get("provider_attach_allowed") is False
        and template.get("device_ownership_allowed") is False
        and template.get("low_level_hardware_path_allowed") is False
    )

    dashboard_ready = (
        template.get("schema") == "h1mekartx.release_readiness_dashboard.v1"
        and template.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME"
        and not missing_rows
        and not runtime_enabled_rows
        and badge_ok
        and badge_report_ok
        and template_runtime_ok
    )

    blockers = []
    blockers.extend(f"missing_dashboard_row:{item}" for item in missing_rows)
    blockers.extend(f"runtime_enabled_row:{item}" for item in runtime_enabled_rows)

    if not badge_ok:
        blockers.append("combined_gate_badge_not_ready")

    if not badge_report_ok:
        blockers.append("combined_gate_badge_report_not_ready")

    if not template_runtime_ok:
        blockers.append("dashboard_template_runtime_policy_invalid")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "template_path": TEMPLATE_PATH,
        "template_schema": template.get("schema"),
        "decision": "PASS_RELEASE_READINESS_DASHBOARD_NO_RUNTIME" if dashboard_ready else "FAIL_RELEASE_READINESS_DASHBOARD",
        "plain_answer": "Release-readiness dashboard is present and remains manual-review-only with runtime disabled." if dashboard_ready else "Release-readiness dashboard is not ready.",
        "release_readiness_dashboard_ready": dashboard_ready,
        "status": template.get("status"),
        "dashboard_rows": rows,
        "dashboard_row_count": len(rows),
        "required_rows": REQUIRED_ROWS,
        "missing_rows": missing_rows,
        "runtime_enabled_rows": runtime_enabled_rows,
        "blockers": blockers,
        "combined_gate_badge": badge,
        "combined_gate_badge_decision": badge_report.get("decision"),
        "combined_gate_badge_ready": badge_ok and badge_report_ok,
        "manual_review_only": True,
        "dashboard_only": True,
        "metal_injection_goal": template.get("metal_injection_goal") is True,
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
        "next_stage_recommendation": "Stage 78 should add a release-readiness dashboard static contract checker and frozen dashboard snapshot.",
        "safety_boundary": {
            "read_only": True,
            "release_readiness_dashboard_only": True,
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
    rows = []
    for item in report["dashboard_rows"]:
        if not isinstance(item, dict):
            continue
        rows.append(
            "| `{id}` | {label} | `{status}` | `{runtime}` |".format(
                id=item.get("id"),
                label=item.get("label"),
                status=item.get("status"),
                runtime=item.get("runtime_allowed"),
            )
        )

    blocker_rows = [f"- `{item}`" for item in report["blockers"]] or ["- none"]

    badge = report["combined_gate_badge"]

    return "\n".join(
        [
            "# Release Readiness Dashboard",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Plain answer: {report['plain_answer']}",
            "",
            f"Status: `{report['status']}`",
            "",
            f"Dashboard ready: `{report['release_readiness_dashboard_ready']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Dashboard only: `{report['dashboard_only']}`",
            "",
            f"Runtime allowed after release readiness: `{report['runtime_allowed_after_release_readiness']}`",
            "",
            f"Metal injection goal: `{report['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{report['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Combined Gate Badge",
            "",
            f"- Label: `{badge.get('label')}`",
            f"- Message: `{badge.get('message')}`",
            f"- Color: `{badge.get('color')}`",
            f"- Ready: `{badge.get('contract_ready')}`",
            "",
            "## Dashboard Rows",
            "",
            "| ID | Label | Status | Runtime Allowed |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage adds a release-readiness dashboard only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release-readiness dashboard.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "release-readiness-dashboard-report.json"
    md_path = out_dir / "release-readiness-dashboard-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["release_readiness_dashboard_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
