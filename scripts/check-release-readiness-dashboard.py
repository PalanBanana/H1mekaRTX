#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_dashboard_check.v1"

REQUIRED_FILES = [
    "release-readiness/release-readiness-dashboard.template.json",
    "scripts/generate-release-readiness-dashboard.py",
    "scripts/check-release-readiness-dashboard.py",
    "docs/metal/release-readiness-dashboard.md",
]

REQUIRED_TERMS = [
    "PASS_RELEASE_READINESS_DASHBOARD_NO_RUNTIME",
    "release_readiness_dashboard_ready",
    "MANUAL_REVIEW_ONLY_NO_RUNTIME",
    "manual_review_only",
    "dashboard_only",
    "runtime_allowed_after_release_readiness",
    "combined_gate_badge_ready",
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "rtx5070_metal_runtime_allowed",
]

FORBIDDEN_LITERAL_TERMS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submit", "Request"]),
    "".join(["OSSystem", "Extension", "Manager.shared"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["sub", "process.run([\"", "io", "reg", "\""]),
    "".join(["sub", "process.run([\"", "system", "_", "profiler", "\""]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_dashboard(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-release-readiness-dashboard.py"),
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
        "stdout": proc.stdout[-5000:],
        "stderr": proc.stderr[-5000:],
        "report": report,
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{token}", token not in source, "absent" if token not in source else "present")

    template_path = root / "release-readiness/release-readiness-dashboard.template.json"
    template = json.loads(template_path.read_text()) if template_path.exists() else {}

    add_check(checks, "template_schema", template.get("schema") == "h1mekartx.release_readiness_dashboard.v1", f"schema={template.get('schema')!r}")
    add_check(checks, "template_status", template.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME", f"status={template.get('status')!r}")
    add_check(checks, "template_runtime_false", template.get("runtime_allowed_after_release_readiness") is False, f"value={template.get('runtime_allowed_after_release_readiness')!r}")
    add_check(checks, "template_rtx_runtime_false", template.get("rtx5070_metal_runtime_allowed") is False, f"value={template.get('rtx5070_metal_runtime_allowed')!r}")

    rows = template.get("dashboard_rows", [])
    add_check(checks, "template_rows_count", isinstance(rows, list) and len(rows) == 8, f"count={len(rows) if isinstance(rows, list) else None!r}")

    if isinstance(rows, list):
        runtime_rows = [
            item.get("id")
            for item in rows
            if isinstance(item, dict) and item.get("runtime_allowed") is not False
        ]
    else:
        runtime_rows = ["dashboard_rows_not_list"]

    add_check(checks, "template_all_rows_runtime_false", not runtime_rows, f"runtime_rows={runtime_rows!r}")

    dashboard_run = run_dashboard(root, out_dir)
    add_check(checks, "dashboard_generator_returncode", dashboard_run["returncode"] == 0, f"returncode={dashboard_run['returncode']}")

    report = dashboard_run["report"]

    add_check(checks, "report_schema", report.get("schema") == "h1mekartx.release_readiness_dashboard_report.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "report_decision", report.get("decision") == "PASS_RELEASE_READINESS_DASHBOARD_NO_RUNTIME", f"decision={report.get('decision')!r}")
    add_check(checks, "report_ready", report.get("release_readiness_dashboard_ready") is True, f"value={report.get('release_readiness_dashboard_ready')!r}")
    add_check(checks, "report_status", report.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME", f"status={report.get('status')!r}")
    add_check(checks, "report_dashboard_rows_count", report.get("dashboard_row_count") == 8, f"count={report.get('dashboard_row_count')!r}")
    add_check(checks, "report_blockers_empty", isinstance(report.get("blockers"), list) and len(report["blockers"]) == 0, f"blockers={report.get('blockers')!r}")
    add_check(checks, "report_badge_ready", report.get("combined_gate_badge_ready") is True, f"value={report.get('combined_gate_badge_ready')!r}")
    add_check(checks, "report_runtime_false", report.get("runtime_allowed_after_release_readiness") is False, f"value={report.get('runtime_allowed_after_release_readiness')!r}")
    add_check(checks, "report_rtx_runtime_false", report.get("rtx5070_metal_runtime_allowed") is False, f"value={report.get('rtx5070_metal_runtime_allowed')!r}")

    badge = report.get("combined_gate_badge", {})
    if not isinstance(badge, dict):
        badge = {}

    add_check(checks, "badge_message", badge.get("message") == "manual-review-only", f"message={badge.get('message')!r}")
    add_check(checks, "badge_contract_ready", badge.get("contract_ready") is True, f"value={badge.get('contract_ready')!r}")

    for key in [
        "live_system_queries_allowed",
        "runtime_buttons_enabled",
        "driver_runtime_allowed",
        "driver_installation_allowed",
        "driver_activation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "low_level_hardware_path_allowed",
        "rtx5070_metal_runtime_allowed",
    ]:
        add_check(checks, f"blocked:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    sb = report.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "read_only",
        "release_readiness_dashboard_only",
        "manual_review_only",
        "no_runtime",
        "no_driver_installation",
        "no_driver_activation",
        "no_provider_attach",
        "no_device_ownership",
        "no_low_level_hardware_path",
        "no_rtx5070_metal_runtime",
    ]:
        add_check(checks, f"safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RELEASE_READINESS_DASHBOARD_READY" if failed_count == 0 else "FAIL_RELEASE_READINESS_DASHBOARD",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "dashboard_run": {
            "returncode": dashboard_run["returncode"],
            "stdout": dashboard_run["stdout"],
            "stderr": dashboard_run["stderr"],
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "release_readiness_dashboard_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# Release Readiness Dashboard Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates the release-readiness dashboard only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check release-readiness dashboard.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "release-readiness-dashboard-check.json"
    md_path = out_dir / "release-readiness-dashboard-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
