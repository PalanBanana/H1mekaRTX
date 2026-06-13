#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.rtx5070_metal_runtime_milestone_map_check.v1"

MAP_PATH = "release-readiness/rtx5070-metal-runtime-milestone-map.json"
INTENT_PATH = "release-readiness/rtx5070-metal-runtime-request.intent.json"

REQUIRED_FILES = [
    MAP_PATH,
    INTENT_PATH,
    "scripts/check-rtx5070-metal-runtime-milestone-map.py",
    "docs/metal/rtx5070-metal-runtime-milestone-map.md"
]

REQUIRED_TERMS = [
    "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE",
    "requested_true_is_not_effective_permission",
    "manual_review_is_not_runtime_permission",
    "effective_runtime_true_requires_future_stage",
    "runtime_allowed_after_milestone_map",
    "metal_full_graphics_acceleration_requested",
    "desired_rtx5070_metal_runtime_state",
    "rtx5070_metal_runtime_allowed"
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


def run_workflow_static_contract(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "check-release-readiness-workflow-static-contract.py"),
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

    report_path = out_dir / "release-readiness-workflow-static-contract-check.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-8000:],
        "report": report
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

    milestone_map = json.loads((root / MAP_PATH).read_text())
    intent = json.loads((root / INTENT_PATH).read_text())

    requested = milestone_map.get("requested_state", {})
    effective = milestone_map.get("effective_state", {})
    rules = milestone_map.get("promotion_rules", {})
    milestones = milestone_map.get("milestones", [])
    boundary = milestone_map.get("safety_boundary", {})

    intent_requested = intent.get("intent", {})
    intent_effective = intent.get("effective_policy", {})

    add_check(checks, "map_schema", milestone_map.get("schema") == "h1mekartx.rtx5070_metal_runtime_milestone_map.v1", f"schema={milestone_map.get('schema')!r}")
    add_check(checks, "map_decision", milestone_map.get("decision") == "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE", f"decision={milestone_map.get('decision')!r}")

    add_check(checks, "requested_metal_full_true", requested.get("metal_full_graphics_acceleration_requested") is True, f"value={requested.get('metal_full_graphics_acceleration_requested')!r}")
    add_check(checks, "requested_desired_runtime_true", requested.get("desired_rtx5070_metal_runtime_state") is True, f"value={requested.get('desired_rtx5070_metal_runtime_state')!r}")
    add_check(checks, "intent_requested_matches", intent_requested.get("desired_rtx5070_metal_runtime_state") is True, f"value={intent_requested.get('desired_rtx5070_metal_runtime_state')!r}")

    for key in [
        "metal_injection_runtime_allowed_now",
        "runtime_allowed_after_milestone_map",
        "rtx5070_metal_runtime_allowed",
        "driver_runtime_allowed",
        "driver_installation_allowed",
        "driver_activation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "low_level_hardware_path_allowed",
    ]:
        add_check(checks, f"effective_false:{key}", effective.get(key) is False, f"value={effective.get(key)!r}")

    add_check(checks, "intent_effective_runtime_false", intent_effective.get("rtx5070_metal_runtime_allowed") is False, f"value={intent_effective.get('rtx5070_metal_runtime_allowed')!r}")

    for key in [
        "requested_true_is_not_effective_permission",
        "manual_review_is_not_runtime_permission",
        "effective_runtime_true_requires_future_stage",
        "effective_runtime_true_requires_separate_review",
        "effective_runtime_true_requires_all_safety_gates_to_pass",
        "current_stage_must_keep_runtime_false",
    ]:
        add_check(checks, f"rule_true:{key}", rules.get(key) is True, f"value={rules.get(key)!r}")

    add_check(checks, "milestone_count", isinstance(milestones, list) and len(milestones) == 6, f"count={len(milestones) if isinstance(milestones, list) else None!r}")

    if isinstance(milestones, list):
        for item in milestones:
            if not isinstance(item, dict):
                continue
            add_check(checks, f"milestone_requested_true:{item.get('id')}", item.get("requested_true") is True, f"value={item.get('requested_true')!r}")
            add_check(checks, f"milestone_effective_false:{item.get('id')}", item.get("effective_runtime_allowed") is False, f"value={item.get('effective_runtime_allowed')!r}")

    for key in [
        "read_only",
        "milestone_map_only",
        "manual_review_only",
        "no_runtime",
        "no_driver_installation",
        "no_driver_activation",
        "no_provider_attach",
        "no_device_ownership",
        "no_low_level_hardware_path",
        "no_rtx5070_metal_runtime",
    ]:
        add_check(checks, f"safety_true:{key}", boundary.get(key) is True, f"value={boundary.get(key)!r}")

    workflow_run = run_workflow_static_contract(root, out_dir)
    add_check(checks, "workflow_static_contract_returncode", workflow_run["returncode"] == 0, f"returncode={workflow_run['returncode']}")

    workflow_report = workflow_run["report"]
    add_check(checks, "workflow_static_contract_decision", workflow_report.get("decision") == "PASS_RELEASE_READINESS_WORKFLOW_STATIC_CONTRACT_READY", f"decision={workflow_report.get('decision')!r}")
    add_check(checks, "workflow_effective_runtime_false", workflow_report.get("rtx5070_metal_runtime_allowed") is False, f"value={workflow_report.get('rtx5070_metal_runtime_allowed')!r}")
    add_check(checks, "workflow_requested_true_recorded", workflow_report.get("requested_metal_runtime_true_recorded") is True, f"value={workflow_report.get('requested_metal_runtime_true_recorded')!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RTX5070_METAL_RUNTIME_MILESTONE_MAP_READY" if failed_count == 0 else "FAIL_RTX5070_METAL_RUNTIME_MILESTONE_MAP",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "requested_metal_runtime_true_recorded": True,
        "effective_rtx5070_metal_runtime_allowed": False,
        "runtime_allowed_after_milestone_map": False,
        "milestone_map_only": True,
        "manual_review_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 84 should add a runtime milestone map static contract snapshot while keeping effective runtime disabled.",
        "workflow_static_contract_run": {
            "returncode": workflow_run["returncode"],
            "stdout": workflow_run["stdout"],
            "stderr": workflow_run["stderr"]
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "milestone_map_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        }
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# RTX 5070 Metal Runtime Milestone Map Check",
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
            f"Runtime allowed after milestone map: `{report['runtime_allowed_after_milestone_map']}`",
            "",
            f"Milestone map only: `{report['milestone_map_only']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates requested runtime intent versus effective runtime permission only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check RTX 5070 Metal runtime milestone map.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "rtx5070-metal-runtime-milestone-map-check.json"
    md_path = out_dir / "rtx5070-metal-runtime-milestone-map-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
