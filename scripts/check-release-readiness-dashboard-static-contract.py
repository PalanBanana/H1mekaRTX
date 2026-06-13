#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_dashboard_static_contract_check.v1"

REQUIRED_FILES = [
    "release-readiness/release-readiness-dashboard.snapshot.json",
    "release-readiness/release-readiness-dashboard.snapshot.md",
    "scripts/freeze-release-readiness-dashboard-snapshot.py",
    "scripts/check-release-readiness-dashboard-static-contract.py",
    "docs/metal/release-readiness-dashboard-static-contract.md",
]

REQUIRED_TERMS = [
    "PASS_RELEASE_READINESS_DASHBOARD_SNAPSHOT_FROZEN",
    "PASS_RELEASE_READINESS_DASHBOARD_STATIC_CONTRACT_READY",
    "MANUAL_REVIEW_ONLY_NO_RUNTIME",
    "manual-review-only",
    "NO_RUNTIME",
    "snapshot_ready",
    "manual_review_only",
    "snapshot_only",
    "runtime_allowed_after_release_readiness",
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


def run_freezer(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "freeze-release-readiness-dashboard-snapshot.py"),
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

    report_path = out_dir / "release-readiness-dashboard-snapshot-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-5000:],
        "stderr": proc.stderr[-5000:],
        "report": report,
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    freezer_run = run_freezer(root, out_dir)
    add_check(checks, "freezer_returncode", freezer_run["returncode"] == 0, f"returncode={freezer_run['returncode']}")

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{token}", token not in source, "absent" if token not in source else "present")

    snapshot_path = root / "release-readiness/release-readiness-dashboard.snapshot.json"
    snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {}

    add_check(checks, "snapshot_schema", snapshot.get("schema") == "h1mekartx.release_readiness_dashboard_snapshot.v1", f"schema={snapshot.get('schema')!r}")
    add_check(checks, "snapshot_source_decision", snapshot.get("source_decision") == "PASS_RELEASE_READINESS_DASHBOARD_NO_RUNTIME", f"decision={snapshot.get('source_decision')!r}")
    add_check(checks, "snapshot_status", snapshot.get("status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME", f"status={snapshot.get('status')!r}")
    add_check(checks, "snapshot_ready", snapshot.get("release_readiness_dashboard_ready") is True, f"value={snapshot.get('release_readiness_dashboard_ready')!r}")
    add_check(checks, "snapshot_manual_review_only", snapshot.get("manual_review_only") is True, f"value={snapshot.get('manual_review_only')!r}")
    add_check(checks, "snapshot_dashboard_only", snapshot.get("dashboard_only") is True, f"value={snapshot.get('dashboard_only')!r}")
    add_check(checks, "snapshot_row_count", snapshot.get("dashboard_row_count") == 8, f"count={snapshot.get('dashboard_row_count')!r}")
    add_check(checks, "snapshot_runtime_false", snapshot.get("runtime_allowed_after_release_readiness") is False, f"value={snapshot.get('runtime_allowed_after_release_readiness')!r}")
    add_check(checks, "snapshot_rtx_runtime_false", snapshot.get("rtx5070_metal_runtime_allowed") is False, f"value={snapshot.get('rtx5070_metal_runtime_allowed')!r}")

    badge = snapshot.get("combined_gate_badge", {})
    if not isinstance(badge, dict):
        badge = {}

    add_check(checks, "snapshot_badge_message", badge.get("message") == "manual-review-only", f"message={badge.get('message')!r}")
    add_check(checks, "snapshot_badge_ready", badge.get("contract_ready") is True, f"value={badge.get('contract_ready')!r}")

    frozen = snapshot.get("frozen_contract", {})
    if not isinstance(frozen, dict):
        frozen = {}

    add_check(checks, "frozen_contract_status", frozen.get("release_readiness_status") == "MANUAL_REVIEW_ONLY_NO_RUNTIME", f"value={frozen.get('release_readiness_status')!r}")
    add_check(checks, "frozen_contract_badge", frozen.get("badge_message") == "manual-review-only", f"value={frozen.get('badge_message')!r}")
    add_check(checks, "frozen_contract_runtime_policy", frozen.get("runtime_policy") == "NO_RUNTIME", f"value={frozen.get('runtime_policy')!r}")
    add_check(checks, "manual_review_not_runtime_permission", frozen.get("manual_review_is_runtime_permission") is False, f"value={frozen.get('manual_review_is_runtime_permission')!r}")

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
        add_check(checks, f"blocked:{key}", snapshot.get(key) is False, f"value={snapshot.get(key)!r}")

    sb = snapshot.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "read_only",
        "frozen_snapshot_only",
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

    freeze_report = freezer_run.get("report", {})
    add_check(checks, "freeze_report_decision", freeze_report.get("decision") == "PASS_RELEASE_READINESS_DASHBOARD_SNAPSHOT_FROZEN", f"decision={freeze_report.get('decision')!r}")
    add_check(checks, "freeze_report_ready", freeze_report.get("snapshot_ready") is True, f"value={freeze_report.get('snapshot_ready')!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RELEASE_READINESS_DASHBOARD_STATIC_CONTRACT_READY" if failed_count == 0 else "FAIL_RELEASE_READINESS_DASHBOARD_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "freezer_run": {
            "returncode": freezer_run["returncode"],
            "stdout": freezer_run["stdout"],
            "stderr": freezer_run["stderr"],
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "frozen_snapshot_only": True,
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
            "# Release Readiness Dashboard Static Contract Check",
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
            "This check validates the frozen release-readiness dashboard snapshot only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check release-readiness dashboard static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "release-readiness-dashboard-static-contract-check.json"
    md_path = out_dir / "release-readiness-dashboard-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
