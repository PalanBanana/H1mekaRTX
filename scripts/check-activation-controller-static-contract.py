#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.activation_controller_static_contract_check.v1"

REQUIRED_FILES = [
    "scripts/validate-activation-controller-static-contract.py",
    "scripts/check-activation-controller-static-contract.py",
    "docs/metal/activation-controller-static-contract-validator.md",
]

REQUIRED_TERMS = [
    "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT",
    "activation-controller-design-stub.json",
    "activation_controller_runtime_allowed",
    "activation_request_allowed",
    "deactivation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
    "static_source_scan_only",
    "activation_contract_only",
]

FORBIDDEN_LITERAL_TERMS = [
    "activation" + "Request(forExtensionWithIdentifier",
    "deactivation" + "Request(forExtensionWithIdentifier",
    "." + "submitRequest",
    "OSSystem" + "ExtensionManager.shared",
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
            read_text(root / "scripts" / "validate-activation-controller-static-contract.py"),
            read_text(root / "scripts" / "check-activation-controller-static-contract.py"),
            read_text(root / "docs" / "metal" / "activation-controller-static-contract-validator.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "activation-controller-static-contract"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    generator_run = run_command(
        [
            "python3",
            str(root / "scripts" / "generate-activation-controller-design-stub.py"),
            "--out-dir",
            str(fixture_dir),
        ],
        root,
    )
    add_check(checks, "design_stub_generator_returncode", generator_run["returncode"] == 0, f"returncode={generator_run['returncode']}")

    validator_run = run_command(
        [
            "python3",
            str(root / "scripts" / "validate-activation-controller-static-contract.py"),
            "--root",
            str(root),
            "--input-dir",
            str(fixture_dir),
            "--out-dir",
            str(fixture_dir),
        ],
        root,
    )
    add_check(checks, "static_contract_validator_returncode", validator_run["returncode"] == 0, f"returncode={validator_run['returncode']}")

    report_path = fixture_dir / "activation-controller-static-contract-report.json"
    contract = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(
        checks,
        "contract_schema",
        contract.get("schema") == "h1mekartx.activation_controller_static_contract.v1",
        f"schema={contract.get('schema')!r}",
    )
    add_check(
        checks,
        "contract_decision",
        contract.get("decision") == "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT",
        f"decision={contract.get('decision')!r}",
    )
    add_check(
        checks,
        "contract_failed_count_zero",
        contract.get("failed_count") == 0,
        f"failed_count={contract.get('failed_count')!r}",
    )

    for key in [
        "activation_controller_runtime_allowed",
        "activation_request_allowed",
        "deactivation_request_allowed",
        "manager_submit_allowed",
        "driverkit_target_creation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add_check(checks, f"contract_blocks:{key}", contract.get(key) is False, f"value={contract.get(key)!r}")

    target = contract.get("expected_target", {})
    expected_target = {
        "vendor_id": "0x10de",
        "device_id": "0x2f04",
        "iopcimatch": "0x2f0410de",
        "subsystem_vendor_id": "0x1458",
        "subsystem_id": "0x417e",
    }
    for key, expected in expected_target.items():
        add_check(checks, f"contract_target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    sb = contract.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "contract_safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "contract_safety_local_json_validation_only", sb.get("local_json_validation_only") is True, f"value={sb.get('local_json_validation_only')!r}")
    add_check(checks, "contract_safety_static_source_scan_only", sb.get("static_source_scan_only") is True, f"value={sb.get('static_source_scan_only')!r}")
    add_check(checks, "contract_safety_activation_contract_only", sb.get("activation_contract_only") is True, f"value={sb.get('activation_contract_only')!r}")

    for key in [
        "creates_activation_request_objects",
        "creates_deactivation_request_objects",
        "calls_extension_manager_submit",
        "implements_activation_controller_runtime_path",
        "creates_driverkit_target",
        "adds_dext_provider_class",
        "adds_info_plist_provider_match",
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
        add_check(checks, f"contract_safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "fixture_dir": str(fixture_dir),
        "decision": "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT_VALIDATOR_READY" if failed_count == 0 else "FAIL_ACTIVATION_CONTROLLER_STATIC_CONTRACT_VALIDATOR",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator_run": generator_run,
        "validator_run": validator_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "local_json_validation_only": True,
            "static_source_scan_only": True,
            "activation_contract_only": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "creates_driverkit_target": False,
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
            "# Activation-controller Static Contract Check",
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
            "This check validates the activation-controller static contract validator using local fixture JSON only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, request device ownership, attach to PCI providers, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check activation-controller static contract validator.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "activation-controller-static-contract-check.json"
    md_path = out_dir / "activation-controller-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
