#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.rtx5070_metal_runtime_milestone_map_static_contract_check.v1"

SNAPSHOT_JSON = "release-readiness/rtx5070-metal-runtime-milestone-map.snapshot.json"
SNAPSHOT_MD = "release-readiness/rtx5070-metal-runtime-milestone-map.snapshot.md"

REQUIRED_FILES = [
    SNAPSHOT_JSON,
    SNAPSHOT_MD,
    "scripts/freeze-rtx5070-metal-runtime-milestone-map-snapshot.py",
    "scripts/check-rtx5070-metal-runtime-milestone-map-static-contract.py",
    "docs/metal/rtx5070-metal-runtime-milestone-map-static-contract.md",
]

REQUIRED_TERMS = [
    "PASS_RTX5070_METAL_RUNTIME_MILESTONE_MAP_SNAPSHOT_FROZEN",
    "PASS_RTX5070_METAL_RUNTIME_MILESTONE_MAP_STATIC_CONTRACT_READY",
    "REQUESTED_TRUE_EFFECTIVE_FALSE",
    "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE",
    "requested_runtime_state",
    "effective_runtime_permission",
    "effective_true_allowed_in_this_snapshot",
    "runtime_allowed_after_milestone_snapshot",
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
            str(root / "scripts" / "freeze-rtx5070-metal-runtime-milestone-map-snapshot.py"),
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

    report_path = out_dir / "rtx5070-metal-runtime-milestone-map-snapshot-report.json"
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

    snapshot = json.loads((root / SNAPSHOT_JSON).read_text()) if (root / SNAPSHOT_JSON).exists() else {}

    requested = snapshot.get("requested_state", {})
    effective = snapshot.get("effective_state", {})
    frozen = snapshot.get("frozen_contract", {})
    milestones = snapshot.get("milestones", [])
    boundary = snapshot.get("safety_boundary", {})

    if not isinstance(requested, dict):
        requested = {}
    if not isinstance(effective, dict):
        effective = {}
    if not isinstance(frozen, dict):
        frozen = {}
    if not isinstance(milestones, list):
        milestones = []
    if not isinstance(boundary, dict):
        boundary = {}

    add_check(checks, "snapshot_schema", snapshot.get("schema") == "h1mekartx.rtx5070_metal_runtime_milestone_map_snapshot.v1", f"schema={snapshot.get('schema')!r}")
    add_check(checks, "snapshot_source_decision", snapshot.get("source_decision") == "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE", f"decision={snapshot.get('source_decision')!r}")
    add_check(checks, "snapshot_decision", snapshot.get("decision") == "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE", f"decision={snapshot.get('decision')!r}")

    add_check(checks, "requested_full_accel_true", requested.get("metal_full_graphics_acceleration_requested") is True, f"value={requested.get('metal_full_graphics_acceleration_requested')!r}")
    add_check(checks, "requested_runtime_true", requested.get("desired_rtx5070_metal_runtime_state") is True, f"value={requested.get('desired_rtx5070_metal_runtime_state')!r}")

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

    add_check(checks, "frozen_requested_true", frozen.get("requested_runtime_state") is True, f"value={frozen.get('requested_runtime_state')!r}")
    add_check(checks, "frozen_effective_false", frozen.get("effective_runtime_permission") is False, f"value={frozen.get('effective_runtime_permission')!r}")
    add_check(checks, "frozen_policy", frozen.get("runtime_policy") == "REQUESTED_TRUE_EFFECTIVE_FALSE", f"value={frozen.get('runtime_policy')!r}")
    add_check(checks, "frozen_effective_true_not_allowed", frozen.get("effective_true_allowed_in_this_snapshot") is False, f"value={frozen.get('effective_true_allowed_in_this_snapshot')!r}")
    add_check(checks, "manual_review_not_runtime", frozen.get("manual_review_is_runtime_permission") is False, f"value={frozen.get('manual_review_is_runtime_permission')!r}")

    add_check(checks, "milestone_count", len(milestones) == 6, f"count={len(milestones)!r}")

    for item in milestones:
        if not isinstance(item, dict):
            add_check(checks, "milestone_dict", False, f"value={item!r}")
            continue
        add_check(checks, f"milestone_requested_true:{item.get('id')}", item.get("requested_true") is True, f"value={item.get('requested_true')!r}")
        add_check(checks, f"milestone_effective_false:{item.get('id')}", item.get("effective_runtime_allowed") is False, f"value={item.get('effective_runtime_allowed')!r}")

    for key in [
        "read_only",
        "milestone_snapshot_only",
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

    freeze_report = freezer_run.get("report", {})
    add_check(checks, "freeze_report_decision", freeze_report.get("decision") == "PASS_RTX5070_METAL_RUNTIME_MILESTONE_MAP_SNAPSHOT_FROZEN", f"decision={freeze_report.get('decision')!r}")
    add_check(checks, "freeze_report_ready", freeze_report.get("snapshot_ready") is True, f"value={freeze_report.get('snapshot_ready')!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RTX5070_METAL_RUNTIME_MILESTONE_MAP_STATIC_CONTRACT_READY" if failed_count == 0 else "FAIL_RTX5070_METAL_RUNTIME_MILESTONE_MAP_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "requested_metal_runtime_true_recorded": True,
        "effective_rtx5070_metal_runtime_allowed": False,
        "runtime_allowed_after_milestone_snapshot": False,
        "snapshot_only": True,
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
        "next_stage_recommendation": "Stage 85 should add a milestone-map diff guard that compares generated milestone data to the frozen snapshot.",
        "freezer_run": {
            "returncode": freezer_run["returncode"],
            "stdout": freezer_run["stdout"],
            "stderr": freezer_run["stderr"],
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "milestone_snapshot_only": True,
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
            "# RTX 5070 Metal Runtime Milestone Map Static Contract Check",
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
            f"Runtime allowed after milestone snapshot: `{report['runtime_allowed_after_milestone_snapshot']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates the frozen runtime milestone snapshot only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check RTX 5070 Metal runtime milestone map static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "rtx5070-metal-runtime-milestone-map-static-contract-check.json"
    md_path = out_dir / "rtx5070-metal-runtime-milestone-map-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
