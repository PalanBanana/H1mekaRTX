#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_dashboard_diff_guard_check.v1"

REQUIRED_FILES = [
    "release-readiness/release-readiness-dashboard.snapshot.json",
    "release-readiness/release-readiness-dashboard.snapshot.md",
    "scripts/compare-release-readiness-dashboard-snapshot.py",
    "scripts/check-release-readiness-dashboard-diff-guard.py",
    "docs/metal/release-readiness-dashboard-diff-guard.md",
]

REQUIRED_TERMS = [
    "PASS_RELEASE_READINESS_DASHBOARD_DIFF_GUARD",
    "PASS_RELEASE_READINESS_DASHBOARD_DIFF_GUARD_READY",
    "diff_guard_ready",
    "MANUAL_REVIEW_ONLY_NO_RUNTIME",
    "manual-review-only",
    "NO_RUNTIME",
    "manual_review_only",
    "diff_guard_only",
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


def run_guard(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "compare-release-readiness-dashboard-snapshot.py"),
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

    report_path = out_dir / "release-readiness-dashboard-diff-guard-report.json"
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

    guard_run = run_guard(root, out_dir)
    add_check(checks, "guard_returncode", guard_run["returncode"] == 0, f"returncode={guard_run['returncode']}")

    report = guard_run["report"]

    add_check(checks, "guard_schema", report.get("schema") == "h1mekartx.release_readiness_dashboard_diff_guard.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "guard_decision", report.get("decision") == "PASS_RELEASE_READINESS_DASHBOARD_DIFF_GUARD", f"decision={report.get('decision')!r}")
    add_check(checks, "guard_ready", report.get("diff_guard_ready") is True, f"value={report.get('diff_guard_ready')!r}")
    add_check(checks, "diff_count_zero", report.get("diff_count") == 0, f"diff_count={report.get('diff_count')!r}")
    add_check(checks, "blockers_empty", isinstance(report.get("blockers"), list) and len(report["blockers"]) == 0, f"blockers={report.get('blockers')!r}")
    add_check(checks, "frozen_contract_ok", report.get("frozen_contract_ok") is True, f"value={report.get('frozen_contract_ok')!r}")
    add_check(checks, "generated_contract_ok", report.get("generated_contract_ok") is True, f"value={report.get('generated_contract_ok')!r}")
    add_check(checks, "manual_review_only", report.get("manual_review_only") is True, f"value={report.get('manual_review_only')!r}")
    add_check(checks, "diff_guard_only", report.get("diff_guard_only") is True, f"value={report.get('diff_guard_only')!r}")
    add_check(checks, "runtime_false", report.get("runtime_allowed_after_release_readiness") is False, f"value={report.get('runtime_allowed_after_release_readiness')!r}")
    add_check(checks, "rtx_runtime_false", report.get("rtx5070_metal_runtime_allowed") is False, f"value={report.get('rtx5070_metal_runtime_allowed')!r}")

    runtime_flags = report.get("runtime_flags", {})
    if not isinstance(runtime_flags, dict):
        runtime_flags = {}

    for key in [
        "generated_runtime_allowed_after_release_readiness",
        "generated_rtx5070_metal_runtime_allowed",
        "frozen_runtime_allowed_after_release_readiness",
        "frozen_rtx5070_metal_runtime_allowed",
    ]:
        add_check(checks, f"runtime_flag_false:{key}", runtime_flags.get(key) is False, f"value={runtime_flags.get(key)!r}")

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
        "diff_guard_only",
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
        "decision": "PASS_RELEASE_READINESS_DASHBOARD_DIFF_GUARD_READY" if failed_count == 0 else "FAIL_RELEASE_READINESS_DASHBOARD_DIFF_GUARD",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "guard_run": {
            "returncode": guard_run["returncode"],
            "stdout": guard_run["stdout"],
            "stderr": guard_run["stderr"],
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "diff_guard_only": True,
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
            "# Release Readiness Dashboard Diff Guard Check",
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
            "This check validates the release-readiness dashboard diff guard only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check release-readiness dashboard diff guard.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "release-readiness-dashboard-diff-guard-check.json"
    md_path = out_dir / "release-readiness-dashboard-diff-guard-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
