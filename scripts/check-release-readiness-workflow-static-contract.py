#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_workflow_static_contract_check.v1"

WORKFLOW = ".github/workflows/release-readiness.yml"
WRAPPER = "scripts/run-release-readiness-ci.sh"
INTENT = "release-readiness/rtx5070-metal-runtime-request.intent.json"

REQUIRED_FILES = [
    WORKFLOW,
    WRAPPER,
    INTENT,
    "scripts/check-release-readiness-workflow-static-contract.py",
    "docs/metal/release-readiness-workflow-static-contract.md",
]

REQUIRED_TERMS = [
    "PASS_RELEASE_READINESS_WORKFLOW_STATIC_CONTRACT_READY",
    "rtx5070_metal_runtime_request_intent",
    "metal_full_graphics_acceleration_requested",
    "desired_rtx5070_metal_runtime_state",
    "runtime_allowed_after_workflow_static_contract",
    "requested_metal_runtime_true_recorded",
    "effective_rtx5070_metal_runtime_allowed",
    "manual_review_only",
    "workflow_static_contract_only"
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


def run_wrapper_check(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "check-release-readiness-ci-wrapper.py"),
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

    report_path = out_dir / "release-readiness-ci-wrapper-check.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
        "report": report,
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    workflow_text = read_text(root / WORKFLOW)
    wrapper_text = read_text(root / WRAPPER)
    intent_text = read_text(root / INTENT)
    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{token}", token not in source, "absent" if token not in source else "present")

    add_check(checks, "workflow_calls_wrapper", "bash scripts/run-release-readiness-ci.sh" in workflow_text, "wrapper command present")
    add_check(checks, "workflow_no_secrets", "secrets." not in workflow_text, "no secrets reference")
    add_check(checks, "workflow_no_sudo", "sudo " not in workflow_text, "no sudo")
    add_check(checks, "workflow_no_runtime_enabled_marker", "runtime-enabled" not in workflow_text, "no runtime-enabled marker")
    add_check(checks, "wrapper_no_sudo", "sudo " not in wrapper_text, "no sudo")
    add_check(checks, "wrapper_calls_dashboard_ci", "run-release-readiness-dashboard-ci.sh" in wrapper_text, "dashboard CI call present")
    add_check(checks, "wrapper_calls_safety_gates", "run-bar-safety-gates.sh" in wrapper_text, "safety gate call present")

    intent = json.loads(intent_text) if intent_text.strip() else {}
    intent_block = intent.get("intent", {}) if isinstance(intent, dict) else {}
    effective = intent.get("effective_policy", {}) if isinstance(intent, dict) else {}
    boundary = intent.get("safety_boundary", {}) if isinstance(intent, dict) else {}

    if not isinstance(intent_block, dict):
        intent_block = {}
    if not isinstance(effective, dict):
        effective = {}
    if not isinstance(boundary, dict):
        boundary = {}

    add_check(checks, "intent_schema", intent.get("schema") == "h1mekartx.rtx5070_metal_runtime_request_intent.v1", f"schema={intent.get('schema')!r}")
    add_check(checks, "intent_requested_true", intent_block.get("metal_full_graphics_acceleration_requested") is True, f"value={intent_block.get('metal_full_graphics_acceleration_requested')!r}")
    add_check(checks, "intent_desired_runtime_true", intent_block.get("desired_rtx5070_metal_runtime_state") is True, f"value={intent_block.get('desired_rtx5070_metal_runtime_state')!r}")
    add_check(checks, "effective_runtime_false", effective.get("rtx5070_metal_runtime_allowed") is False, f"value={effective.get('rtx5070_metal_runtime_allowed')!r}")
    add_check(checks, "effective_metal_runtime_false", effective.get("metal_injection_runtime_allowed_now") is False, f"value={effective.get('metal_injection_runtime_allowed_now')!r}")
    add_check(checks, "effective_after_contract_false", effective.get("runtime_allowed_after_workflow_static_contract") is False, f"value={effective.get('runtime_allowed_after_workflow_static_contract')!r}")

    for key in [
        "driver_runtime_allowed",
        "driver_installation_allowed",
        "driver_activation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "low_level_hardware_path_allowed",
    ]:
        add_check(checks, f"effective_blocked:{key}", effective.get(key) is False, f"value={effective.get(key)!r}")

    for key in [
        "read_only",
        "intent_record_only",
        "manual_review_only",
        "no_runtime",
        "no_driver_installation",
        "no_driver_activation",
        "no_provider_attach",
        "no_device_ownership",
        "no_low_level_hardware_path",
        "no_rtx5070_metal_runtime",
    ]:
        add_check(checks, f"intent_safety_true:{key}", boundary.get(key) is True, f"value={boundary.get(key)!r}")

    bash_check = subprocess.run(
        ["bash", "-n", str(root / WRAPPER)],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    add_check(checks, "wrapper_bash_syntax", bash_check.returncode == 0, f"returncode={bash_check.returncode}, stderr={bash_check.stderr[-1000:]!r}")

    wrapper_run = run_wrapper_check(root, out_dir)
    add_check(checks, "wrapper_check_returncode", wrapper_run["returncode"] == 0, f"returncode={wrapper_run['returncode']}")

    wrapper_report = wrapper_run["report"]
    add_check(checks, "wrapper_check_decision", wrapper_report.get("decision") == "PASS_RELEASE_READINESS_CI_WRAPPER_READY", f"decision={wrapper_report.get('decision')!r}")
    add_check(checks, "wrapper_check_failed_count_zero", wrapper_report.get("failed_count") == 0, f"failed_count={wrapper_report.get('failed_count')!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RELEASE_READINESS_WORKFLOW_STATIC_CONTRACT_READY" if failed_count == 0 else "FAIL_RELEASE_READINESS_WORKFLOW_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "requested_metal_runtime_true_recorded": intent_block.get("desired_rtx5070_metal_runtime_state") is True,
        "effective_rtx5070_metal_runtime_allowed": False,
        "metal_full_graphics_acceleration_requested": intent_block.get("metal_full_graphics_acceleration_requested") is True,
        "workflow_static_contract_ready": failed_count == 0,
        "manual_review_only": True,
        "workflow_static_contract_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_workflow_static_contract": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 83 should add a runtime milestone map that separates requested RTX 5070 Metal runtime from effective runtime permission.",
        "wrapper_check_run": {
            "returncode": wrapper_run["returncode"],
            "stdout": wrapper_run["stdout"],
            "stderr": wrapper_run["stderr"],
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "workflow_static_contract_only": True,
            "intent_record_only": True,
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
            "# Release Readiness Workflow Static Contract Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Requested Metal runtime true recorded: `{report['requested_metal_runtime_true_recorded']}`",
            "",
            f"Effective RTX 5070 Metal runtime allowed: `{report['effective_rtx5070_metal_runtime_allowed']}`",
            "",
            f"Metal full graphics acceleration requested: `{report['metal_full_graphics_acceleration_requested']}`",
            "",
            f"Runtime allowed after workflow static contract: `{report['runtime_allowed_after_workflow_static_contract']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates workflow wiring and runtime intent recording only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check release-readiness workflow static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "release-readiness-workflow-static-contract-check.json"
    md_path = out_dir / "release-readiness-workflow-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
