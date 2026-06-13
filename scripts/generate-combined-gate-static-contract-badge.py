#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.combined_gate_static_contract_badge_report.v1"
BADGE_SCHEMA = "h1mekartx.combined_gate_status_badge.v1"

SUMMARY_SCRIPT = "scripts/generate-combined-entitlement-packaging-gate-summary.py"
BADGE_TEMPLATE = "gate-summary/combined-gate-status-badge.template.json"


def run_summary(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / SUMMARY_SCRIPT),
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

    report_path = out_dir / "combined-entitlement-packaging-gate-summary-report.json"
    report: dict[str, Any] = {}
    if report_path.exists():
        report = json.loads(report_path.read_text())

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "report": report,
    }


def find_case(report: dict[str, Any], name: str) -> dict[str, Any]:
    cases = report.get("cases", [])
    if not isinstance(cases, list):
        return {}
    for item in cases:
        if isinstance(item, dict) and item.get("name") == name:
            return item
    return {}


def build_badge(summary: dict[str, Any]) -> dict[str, Any]:
    ready_case = find_case(summary, "redacted_ready")
    runtime_negative = find_case(summary, "runtime_requested_negative")

    ready_ok = (
        ready_case.get("decision") == "COMBINED_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME"
        and ready_case.get("gate") == "GO_COMBINED_MANUAL_REVIEW_NO_RUNTIME"
        and ready_case.get("runtime_allowed_after_combined_gate") is False
        and ready_case.get("rtx5070_metal_runtime_allowed") is False
    )

    runtime_negative_ok = (
        runtime_negative.get("decision") == "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED"
        and runtime_negative.get("runtime_allowed_after_combined_gate") is False
        and runtime_negative.get("rtx5070_metal_runtime_allowed") is False
    )

    summary_ok = (
        summary.get("decision") == "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY"
        and summary.get("failed_count") == 0
        and summary.get("combined_gate_summary_ready") is True
        and summary.get("runtime_allowed_after_combined_gate") is False
        and summary.get("rtx5070_metal_runtime_allowed") is False
    )

    if ready_ok and runtime_negative_ok and summary_ok:
        message = "manual-review-only"
        color = "yellow"
        contract_ready = True
    else:
        message = "not-ready"
        color = "red"
        contract_ready = False

    return {
        "schema": BADGE_SCHEMA,
        "label": "combined-gate",
        "message": message,
        "color": color,
        "style": "flat",
        "contract_ready": contract_ready,
        "manual_review_only": True,
        "combined_gate_summary_ready": summary.get("combined_gate_summary_ready") is True,
        "metal_injection_goal": summary.get("metal_injection_goal") is True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_combined_gate": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "source_summary_decision": summary.get("decision"),
        "source_ready_case_decision": ready_case.get("decision"),
        "source_runtime_negative_decision": runtime_negative.get("decision"),
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage76-") as tmp:
        tmp_path = Path(tmp)
        summary_run = run_summary(root, tmp_path)

    summary = summary_run.get("report", {})
    badge = build_badge(summary)

    template_path = root / BADGE_TEMPLATE
    template = json.loads(template_path.read_text()) if template_path.exists() else {}

    template_matches = (
        template.get("schema") == BADGE_SCHEMA
        and template.get("message") == "manual-review-only"
        and template.get("metal_injection_runtime_allowed_now") is False
        and template.get("runtime_allowed_after_combined_gate") is False
        and template.get("rtx5070_metal_runtime_allowed") is False
    )

    checks = [
        {
            "name": "summary_returncode",
            "passed": summary_run["returncode"] == 0,
            "detail": f"returncode={summary_run['returncode']}",
        },
        {
            "name": "summary_decision",
            "passed": summary.get("decision") == "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY",
            "detail": f"decision={summary.get('decision')!r}",
        },
        {
            "name": "badge_contract_ready",
            "passed": badge.get("contract_ready") is True,
            "detail": f"value={badge.get('contract_ready')!r}",
        },
        {
            "name": "badge_message",
            "passed": badge.get("message") == "manual-review-only",
            "detail": f"message={badge.get('message')!r}",
        },
        {
            "name": "badge_runtime_disabled",
            "passed": badge.get("runtime_allowed_after_combined_gate") is False and badge.get("rtx5070_metal_runtime_allowed") is False,
            "detail": f"combined={badge.get('runtime_allowed_after_combined_gate')!r}, rtx={badge.get('rtx5070_metal_runtime_allowed')!r}",
        },
        {
            "name": "template_matches",
            "passed": template_matches,
            "detail": f"value={template_matches!r}",
        },
    ]

    failed_count = sum(1 for item in checks if not item["passed"])
    passed_count = len(checks) - failed_count

    badge_path = out_dir / "combined-gate-status-badge.json"
    badge_md_path = out_dir / "combined-gate-status-badge.md"

    badge_path.write_text(json.dumps(badge, indent=2, sort_keys=True) + "\n")
    badge_md_path.write_text(
        "\n".join(
            [
                "# Combined Gate Status Badge",
                "",
                f"Label: `{badge['label']}`",
                "",
                f"Message: `{badge['message']}`",
                "",
                f"Color: `{badge['color']}`",
                "",
                f"Contract ready: `{badge['contract_ready']}`",
                "",
                f"Manual review only: `{badge['manual_review_only']}`",
                "",
                f"RTX 5070 Metal runtime allowed: `{badge['rtx5070_metal_runtime_allowed']}`",
                "",
            ]
        )
        + "\n"
    )

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_COMBINED_GATE_STATIC_CONTRACT_BADGE" if failed_count == 0 else "FAIL_COMBINED_GATE_STATIC_CONTRACT_BADGE",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "badge": badge,
        "badge_path": str(badge_path),
        "badge_markdown_path": str(badge_md_path),
        "summary_decision": summary.get("decision"),
        "combined_gate_static_contract_badge_ready": failed_count == 0,
        "manual_review_only": True,
        "combined_gate_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_combined_gate": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 77 should add a release-readiness dashboard document that summarizes all no-runtime gates.",
        "safety_boundary": {
            "read_only": True,
            "static_contract_badge_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    badge = report["badge"]

    return "\n".join(
        [
            "# Combined Gate Static Contract Badge Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Badge label: `{badge['label']}`",
            "",
            f"Badge message: `{badge['message']}`",
            "",
            f"Badge color: `{badge['color']}`",
            "",
            f"Contract ready: `{badge['contract_ready']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Runtime allowed after combined gate: `{report['runtime_allowed_after_combined_gate']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This stage adds a static contract badge for the combined entitlement-plus-packaging gate only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate combined gate static contract badge.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "combined-gate-static-contract-badge-report.json"
    md_path = out_dir / "combined-gate-static-contract-badge-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
