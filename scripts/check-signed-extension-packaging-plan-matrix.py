#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.signed_extension_packaging_plan_matrix_check.v1"

REQUIRED_FILES = [
    "packaging-plan/signed-extension-packaging-plan.sample.json",
    "scripts/generate-signed-extension-packaging-plan-matrix.py",
    "scripts/check-signed-extension-packaging-plan-matrix.py",
    "docs/metal/signed-extension-packaging-plan-matrix.md",
]

REQUIRED_TERMS = [
    "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED",
    "packaging_plan_matrix_ready",
    "packaging_ready_for_review",
    "runtime_allowed_after_packaging_plan",
    "host_app_bundle_id_status",
    "driver_extension_bundle_id_status",
    "driverkit_entitlement_status",
    "driverkit_development_profile_status",
    "extension_install_permission_status",
    "developer_certificate_status",
    "distribution_signing_status",
    "notarization_status",
    "manual_review_status",
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


def run_report(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-signed-extension-packaging-plan-matrix.py"),
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
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
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

    plan_path = root / "packaging-plan/signed-extension-packaging-plan.sample.json"
    plan = json.loads(plan_path.read_text()) if plan_path.exists() else {}
    packaging_plan = plan.get("packaging_plan", {}) if isinstance(plan, dict) else {}
    runtime_policy = plan.get("runtime_policy", {}) if isinstance(plan, dict) else {}
    if not isinstance(packaging_plan, dict):
        packaging_plan = {}
    if not isinstance(runtime_policy, dict):
        runtime_policy = {}

    add_check(checks, "plan_schema", plan.get("schema") == "h1mekartx.signed_extension_packaging_plan.v1", f"schema={plan.get('schema')!r}")
    add_check(checks, "plan_runtime_goal_true", runtime_policy.get("metal_injection_goal") is True, f"value={runtime_policy.get('metal_injection_goal')!r}")
    add_check(checks, "plan_metal_runtime_false", runtime_policy.get("metal_injection_runtime_allowed_now") is False, f"value={runtime_policy.get('metal_injection_runtime_allowed_now')!r}")
    add_check(checks, "plan_rtx_runtime_false", runtime_policy.get("rtx5070_metal_runtime_allowed") is False, f"value={runtime_policy.get('rtx5070_metal_runtime_allowed')!r}")

    for key in [
        "host_app_bundle_id_status",
        "driver_extension_bundle_id_status",
        "bundle_id_pairing_status",
        "driverkit_entitlement_status",
        "driverkit_development_profile_status",
        "extension_install_permission_status",
        "developer_certificate_status",
        "distribution_signing_status",
        "notarization_status",
    ]:
        add_check(checks, f"plan_default_not_provided:{key}", packaging_plan.get(key) == "NOT_PROVIDED", f"value={packaging_plan.get(key)!r}")

    add_check(checks, "plan_manual_review_not_ready", packaging_plan.get("manual_review_status") == "NOT_READY", f"value={packaging_plan.get('manual_review_status')!r}")

    report_run = run_report(root, out_dir)
    add_check(checks, "report_generator_returncode", report_run["returncode"] == 0, f"returncode={report_run['returncode']}")

    report_path = out_dir / "signed-extension-packaging-plan-matrix-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(checks, "report_schema", report.get("schema") == "h1mekartx.signed_extension_packaging_plan_matrix.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "report_decision", report.get("decision") == "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED", f"decision={report.get('decision')!r}")
    add_check(checks, "matrix_ready", report.get("packaging_plan_matrix_ready") is True, f"value={report.get('packaging_plan_matrix_ready')!r}")
    add_check(checks, "packaging_not_ready_for_review", report.get("packaging_ready_for_review") is False, f"value={report.get('packaging_ready_for_review')!r}")
    add_check(checks, "blockers_nonempty", isinstance(report.get("blockers"), list) and len(report["blockers"]) > 0, f"count={len(report.get('blockers', [])) if isinstance(report.get('blockers'), list) else None!r}")
    add_check(checks, "matrix_rows_count", isinstance(report.get("matrix_rows"), list) and len(report["matrix_rows"]) == 10, f"count={len(report.get('matrix_rows', [])) if isinstance(report.get('matrix_rows'), list) else None!r}")
    add_check(checks, "runtime_after_plan_false", report.get("runtime_allowed_after_packaging_plan") is False, f"value={report.get('runtime_allowed_after_packaging_plan')!r}")
    add_check(checks, "metal_goal_recorded", report.get("metal_injection_goal") is True, f"value={report.get('metal_injection_goal')!r}")
    add_check(checks, "metal_runtime_not_allowed_now", report.get("metal_injection_runtime_allowed_now") is False, f"value={report.get('metal_injection_runtime_allowed_now')!r}")

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
        "packaging_plan_only",
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
        "decision": "PASS_SIGNED_EXTENSION_PACKAGING_PLAN_MATRIX_READY" if failed_count == 0 else "FAIL_SIGNED_EXTENSION_PACKAGING_PLAN_MATRIX",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "report_run": report_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "packaging_plan_only": True,
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
            "# Signed Extension Packaging Plan Matrix Check",
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
            "This check validates signed-extension packaging plan requirements only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check signed extension packaging plan matrix.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "signed-extension-packaging-plan-matrix-check.json"
    md_path = out_dir / "signed-extension-packaging-plan-matrix-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
