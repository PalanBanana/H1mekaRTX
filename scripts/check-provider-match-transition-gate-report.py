#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_transition_gate_check.v1"

REQUIRED_FILES = [
    "scripts/generate-provider-match-transition-gate-report.py",
    "scripts/check-provider-match-transition-gate-report.py",
    "docs/metal/provider-match-transition-gate-report.md",
]

GENERATOR_SCRIPTS = [
    "generate-provider-match-dry-run-spec.py",
    "generate-entitlement-evidence-checklist.py",
    "generate-no-hardware-activation-readiness-review.py",
    "generate-provider-match-evidence-ledger.py",
]

REQUIRED_TERMS = [
    "PROVIDER_MATCH_TRANSITION_GATE_NO_GO",
    "provider_work_transition_allowed",
    "driverkit_target_creation_allowed",
    "activation_request_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
    "transition_report_only",
    "local_json_validation_only",
    "provider-match-ledger-validator-report.json",
    "provider-match-evidence-ledger.json",
    "provider-match-dry-run-spec.json",
    "entitlement-evidence-checklist.json",
    "no-hardware-activation-readiness-review.json",
]

FORBIDDEN_LITERAL_TERMS = [
    "activation" + "Request(forExtensionWithIdentifier",
    "deactivation" + "Request(forExtensionWithIdentifier",
    "." + "submitRequest",
    "Configuration" + "Write",
    "Memory" + "Read",
    "Memory" + "Write",
    "sub" + "process.run([\"ioreg\"",
    "sub" + "process.run([\"system_profiler\"",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_command(args: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(
        [
            read_text(root / "scripts" / "generate-provider-match-transition-gate-report.py"),
            read_text(root / "scripts" / "check-provider-match-transition-gate-report.py"),
            read_text(root / "docs" / "metal" / "provider-match-transition-gate-report.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "provider-match-transition-gate"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    generator_runs = []
    for script in GENERATOR_SCRIPTS:
        run = run_command(["python3", str(root / "scripts" / script), "--out-dir", str(fixture_dir)], root)
        generator_runs.append(run)
        add_check(checks, f"generator_returncode:{script}", run["returncode"] == 0, f"returncode={run['returncode']}")

    validator_run = run_command(
        [
            "python3",
            str(root / "scripts" / "validate-provider-match-evidence-ledger.py"),
            "--input-dir",
            str(fixture_dir),
            "--out-dir",
            str(fixture_dir),
        ],
        root,
    )
    add_check(checks, "ledger_validator_returncode", validator_run["returncode"] == 0, f"returncode={validator_run['returncode']}")

    gate_run = run_command(
        [
            "python3",
            str(root / "scripts" / "generate-provider-match-transition-gate-report.py"),
            "--input-dir",
            str(fixture_dir),
            "--out-dir",
            str(fixture_dir),
        ],
        root,
    )
    add_check(checks, "transition_gate_generator_returncode", gate_run["returncode"] == 0, f"returncode={gate_run['returncode']}")

    gate_path = fixture_dir / "provider-match-transition-gate-report.json"
    gate = json.loads(gate_path.read_text()) if gate_path.exists() else {}

    add_check(
        checks,
        "gate_schema",
        gate.get("schema") == "h1mekartx.provider_match_transition_gate_report.v1",
        f"schema={gate.get('schema')!r}",
    )
    add_check(
        checks,
        "gate_decision",
        gate.get("decision") == "PROVIDER_MATCH_TRANSITION_GATE_NO_GO",
        f"decision={gate.get('decision')!r}",
    )
    add_check(
        checks,
        "gate_validation_zero_failed",
        gate.get("failed_validation_count") == 0,
        f"failed_validation_count={gate.get('failed_validation_count')!r}",
    )
    add_check(
        checks,
        "gate_failed_gate_zero",
        gate.get("failed_gate_count") == 0,
        f"failed_gate_count={gate.get('failed_gate_count')!r}",
    )
    add_check(
        checks,
        "gate_has_no_go",
        gate.get("no_go_gate_count", 0) > 0,
        f"no_go_gate_count={gate.get('no_go_gate_count')!r}",
    )
    add_check(
        checks,
        "gate_has_blocking",
        gate.get("blocking_gate_count", 0) > 0,
        f"blocking_gate_count={gate.get('blocking_gate_count')!r}",
    )

    for key in [
        "provider_work_transition_allowed",
        "driverkit_target_creation_allowed",
        "activation_request_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add_check(checks, f"gate_blocks:{key}", gate.get(key) is False, f"value={gate.get(key)!r}")

    sb = gate.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "gate_safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "gate_safety_local_json_only", sb.get("local_json_validation_only") is True, f"value={sb.get('local_json_validation_only')!r}")
    add_check(checks, "gate_safety_transition_report_only", sb.get("transition_report_only") is True, f"value={sb.get('transition_report_only')!r}")

    for key in [
        "creates_driverkit_target",
        "adds_dext_provider_class",
        "adds_info_plist_provider_match",
        "creates_activation_request_objects",
        "creates_deactivation_request_objects",
        "calls_extension_manager_submit",
        "driverkit_activation",
        "driverkit_dext_installation",
        "device_ownership_request",
        "pci_provider_attach",
        "live_provider_state_query",
        "live_extension_status_query",
        "live_pci_probing",
        "runs_ioreg",
        "runs_system_profiler",
        "performs_pci_config_reads",
        "performs_pci_config_writes",
        "performs_mmio_reads",
        "performs_mmio_writes",
        "maps_bar_memory",
        "bar_poking",
        "rtx5070_metal_acceleration_implementation",
        "rtx5070_shader_execution",
        "hardware_command_submission_to_rtx5070",
        "resource_allocation_on_rtx5070",
    ]:
        add_check(checks, f"gate_safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "fixture_dir": str(fixture_dir),
        "decision": "PASS_PROVIDER_MATCH_TRANSITION_GATE_REPORT_READY" if failed_count == 0 else "FAIL_PROVIDER_MATCH_TRANSITION_GATE_REPORT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator_runs": generator_runs,
        "validator_run": validator_run,
        "gate_run": gate_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "local_json_validation_only": True,
            "transition_report_only": True,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "driverkit_activation": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
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
            "# Provider-match Transition Gate Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Fixture directory: `{report['fixture_dir']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates the provider-match transition gate report using local fixture JSON only.",
            "",
            "It does not create DriverKit targets, add provider classes, add provider-match dictionaries, create activation requests, create deactivation requests, call extension manager submit, activate DriverKit, request device ownership, attach to PCI providers, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX provider-match transition gate report.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "provider-match-transition-gate-check.json"
    md_path = out_dir / "provider-match-transition-gate-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
