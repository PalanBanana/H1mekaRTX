#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.combined_entitlement_packaging_gate_summary_check.v1"

REQUIRED_FILES = [
    "scripts/generate-combined-entitlement-packaging-gate-summary.py",
    "scripts/check-combined-entitlement-packaging-gate-summary.py",
    "docs/metal/combined-entitlement-packaging-gate-summary.md",
]

REQUIRED_TERMS = [
    "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY",
    "combined_gate_summary_ready",
    "COMBINED_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
    "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED",
    "GO_COMBINED_MANUAL_REVIEW_NO_RUNTIME",
    "NO_GO_COMBINED_GATE",
    "runtime_allowed_after_combined_gate",
    "combined_gate_only",
    "manual_review_only",
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


def run_summary(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-combined-entitlement-packaging-gate-summary.py"),
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
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-5000:],
        "stderr": proc.stderr[-5000:],
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

    summary_run = run_summary(root, out_dir)
    add_check(checks, "summary_generator_returncode", summary_run["returncode"] == 0, f"returncode={summary_run['returncode']}")

    report_path = out_dir / "combined-entitlement-packaging-gate-summary-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(checks, "summary_schema", report.get("schema") == "h1mekartx.combined_entitlement_packaging_gate_summary.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "summary_decision", report.get("decision") == "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY", f"decision={report.get('decision')!r}")
    add_check(checks, "summary_failed_count_zero", report.get("failed_count") == 0, f"failed_count={report.get('failed_count')!r}")
    add_check(checks, "summary_ready", report.get("combined_gate_summary_ready") is True, f"value={report.get('combined_gate_summary_ready')!r}")
    add_check(checks, "case_count_three", report.get("case_count") == 3, f"value={report.get('case_count')!r}")
    add_check(checks, "combined_gate_only", report.get("combined_gate_only") is True, f"value={report.get('combined_gate_only')!r}")
    add_check(checks, "manual_review_only", report.get("manual_review_only") is True, f"value={report.get('manual_review_only')!r}")
    add_check(checks, "runtime_after_combined_gate_false", report.get("runtime_allowed_after_combined_gate") is False, f"value={report.get('runtime_allowed_after_combined_gate')!r}")
    add_check(checks, "metal_goal_recorded", report.get("metal_injection_goal") is True, f"value={report.get('metal_injection_goal')!r}")
    add_check(checks, "metal_runtime_not_allowed_now", report.get("metal_injection_runtime_allowed_now") is False, f"value={report.get('metal_injection_runtime_allowed_now')!r}")

    cases = report.get("cases", [])
    if not isinstance(cases, list):
        cases = []

    case_by_name = {
        item.get("name"): item
        for item in cases
        if isinstance(item, dict)
    }

    sample = case_by_name.get("sample_incomplete", {})
    ready = case_by_name.get("redacted_ready", {})
    runtime_negative = case_by_name.get("runtime_requested_negative", {})

    add_check(checks, "sample_case_not_ready", sample.get("decision") == "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED", f"decision={sample.get('decision')!r}")
    add_check(checks, "ready_case_manual_review", ready.get("decision") == "COMBINED_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME", f"decision={ready.get('decision')!r}")
    add_check(checks, "ready_case_gate", ready.get("gate") == "GO_COMBINED_MANUAL_REVIEW_NO_RUNTIME", f"gate={ready.get('gate')!r}")
    add_check(checks, "ready_case_runtime_false", ready.get("runtime_allowed_after_combined_gate") is False, f"value={ready.get('runtime_allowed_after_combined_gate')!r}")
    add_check(checks, "runtime_negative_not_ready", runtime_negative.get("decision") == "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED", f"decision={runtime_negative.get('decision')!r}")
    add_check(checks, "runtime_negative_runtime_false", runtime_negative.get("runtime_allowed_after_combined_gate") is False, f"value={runtime_negative.get('runtime_allowed_after_combined_gate')!r}")
    add_check(checks, "runtime_negative_blockers_nonempty", isinstance(runtime_negative.get("blockers"), list) and len(runtime_negative["blockers"]) > 0, f"blockers={runtime_negative.get('blockers')!r}")

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
        "combined_gate_summary_only",
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
        "decision": "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY_READY" if failed_count == 0 else "FAIL_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "summary_run": summary_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "combined_gate_summary_only": True,
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
            "# Combined Entitlement Packaging Gate Summary Check",
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
            "This check validates combined entitlement-plus-packaging gate summary only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check combined entitlement packaging gate summary.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "combined-entitlement-packaging-gate-summary-check.json"
    md_path = out_dir / "combined-entitlement-packaging-gate-summary-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
