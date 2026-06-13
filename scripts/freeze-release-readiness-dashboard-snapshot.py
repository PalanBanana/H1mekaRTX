#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_dashboard_snapshot_report.v1"
SNAPSHOT_SCHEMA = "h1mekartx.release_readiness_dashboard_snapshot.v1"

DASHBOARD_SCRIPT = "scripts/generate-release-readiness-dashboard.py"

SNAPSHOT_JSON = "release-readiness/release-readiness-dashboard.snapshot.json"
SNAPSHOT_MD = "release-readiness/release-readiness-dashboard.snapshot.md"


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


def build_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    badge = report.get("combined_gate_badge", {})
    if not isinstance(badge, dict):
        badge = {}

    rows = report.get("dashboard_rows", [])
    if not isinstance(rows, list):
        rows = []

    return {
        "schema": SNAPSHOT_SCHEMA,
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


def snapshot_markdown(snapshot: dict[str, Any]) -> str:
    rows = []
    for row in snapshot["dashboard_rows"]:
        if not isinstance(row, dict):
            continue
        rows.append(
            "| `{id}` | {label} | `{status}` | `{runtime}` |".format(
                id=row.get("id"),
                label=row.get("label"),
                status=row.get("status"),
                runtime=row.get("runtime_allowed"),
            )
        )

    badge = snapshot["combined_gate_badge"]

    return "\n".join(
        [
            "# Release Readiness Dashboard Snapshot",
            "",
            f"Snapshot schema: `{snapshot['schema']}`",
            "",
            f"Snapshot version: `{snapshot['snapshot_version']}`",
            "",
            f"Source decision: `{snapshot['source_decision']}`",
            "",
            f"Status: `{snapshot['status']}`",
            "",
            f"Dashboard ready: `{snapshot['release_readiness_dashboard_ready']}`",
            "",
            f"Manual review only: `{snapshot['manual_review_only']}`",
            "",
            f"Runtime allowed after release readiness: `{snapshot['runtime_allowed_after_release_readiness']}`",
            "",
            f"Metal injection goal: `{snapshot['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{snapshot['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{snapshot['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Combined Gate Badge",
            "",
            f"- Label: `{badge.get('label')}`",
            f"- Message: `{badge.get('message')}`",
            f"- Color: `{badge.get('color')}`",
            f"- Contract ready: `{badge.get('contract_ready')}`",
            "",
            "## Dashboard Rows",
            "",
            "| ID | Label | Status | Runtime Allowed |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Frozen Contract",
            "",
            "- Release readiness status: `MANUAL_REVIEW_ONLY_NO_RUNTIME`",
            "- Badge message: `manual-review-only`",
            "- Runtime policy: `NO_RUNTIME`",
            "- Manual review is runtime permission: `false`",
            "",
            "## Safety Boundary",
            "",
            "This snapshot freezes the release-readiness dashboard state only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def build_report(root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage78-") as tmp:
        run = run_dashboard(root, Path(tmp))

    dashboard_report = run.get("report", {})
    snapshot = build_snapshot(dashboard_report)

    snapshot_ready = (
        run.get("returncode") == 0
        and snapshot.get("source_decision") == "PASS_RELEASE_READINESS_DASHBOARD_NO_RUNTIME"
        and snapshot.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME"
        and snapshot.get("release_readiness_dashboard_ready") is True
        and snapshot.get("manual_review_only") is True
        and snapshot.get("runtime_allowed_after_release_readiness") is False
        and snapshot.get("rtx5070_metal_runtime_allowed") is False
        and snapshot.get("combined_gate_badge", {}).get("message") == "manual-review-only"
        and snapshot.get("combined_gate_badge", {}).get("contract_ready") is True
    )

    blockers = []

    if run.get("returncode") != 0:
        blockers.append("dashboard_generator_failed")

    if snapshot.get("source_decision") != "PASS_RELEASE_READINESS_DASHBOARD_NO_RUNTIME":
        blockers.append("source_dashboard_not_passed")

    if snapshot.get("runtime_allowed_after_release_readiness") is not False:
        blockers.append("snapshot_runtime_not_disabled")

    if snapshot.get("rtx5070_metal_runtime_allowed") is not False:
        blockers.append("snapshot_rtx_runtime_not_disabled")

    snapshot_json_path = root / SNAPSHOT_JSON
    snapshot_md_path = root / SNAPSHOT_MD

    snapshot_json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    snapshot_md_path.write_text(snapshot_markdown(snapshot) + "\n")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RELEASE_READINESS_DASHBOARD_SNAPSHOT_FROZEN" if snapshot_ready else "FAIL_RELEASE_READINESS_DASHBOARD_SNAPSHOT",
        "snapshot_ready": snapshot_ready,
        "blockers": blockers,
        "snapshot_json_path": SNAPSHOT_JSON,
        "snapshot_markdown_path": SNAPSHOT_MD,
        "source_dashboard_decision": dashboard_report.get("decision"),
        "snapshot": snapshot,
        "manual_review_only": True,
        "snapshot_only": True,
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
        "next_stage_recommendation": "Stage 79 should add a release-readiness dashboard diff guard that compares generated output to the frozen snapshot.",
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


def markdown_report(report: dict[str, Any]) -> str:
    blocker_rows = [f"- `{item}`" for item in report["blockers"]] or ["- none"]

    return "\n".join(
        [
            "# Release Readiness Dashboard Snapshot Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Snapshot ready: `{report['snapshot_ready']}`",
            "",
            f"Source dashboard decision: `{report['source_dashboard_decision']}`",
            "",
            f"Snapshot JSON: `{report['snapshot_json_path']}`",
            "",
            f"Snapshot Markdown: `{report['snapshot_markdown_path']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Snapshot only: `{report['snapshot_only']}`",
            "",
            f"Runtime allowed after release readiness: `{report['runtime_allowed_after_release_readiness']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage freezes the release-readiness dashboard snapshot only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze release-readiness dashboard snapshot.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "release-readiness-dashboard-snapshot-report.json"
    md_path = out_dir / "release-readiness-dashboard-snapshot-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["snapshot_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
