#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.activation_controller_static_contract.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

EXPECTED_STUB_DECISION = "ACTIVATION_CONTROLLER_DESIGN_STUB_READY_NO_RUNTIME"

SOURCE_FILES = [
    "scripts/generate-activation-controller-design-stub.py",
    "scripts/check-activation-controller-design-stub.py",
    "docs/metal/activation-controller-design-stub.md",
]

FORBIDDEN_SOURCE_TOKENS = [
    "activation" + "Request(forExtensionWithIdentifier",
    "deactivation" + "Request(forExtensionWithIdentifier",
    "." + "submitRequest",
    "OSSystem" + "ExtensionManager.shared",
    "OSSystem" + "ExtensionRequest(",
    "IOPCI" + "Device",
    "Configuration" + "Read",
    "Configuration" + "Write",
    "Memory" + "Read",
    "Memory" + "Write",
    "map" + "DeviceMemory",
    "Create" + "MemoryMap",
    "sub" + "process.run([\"ioreg\"",
    "sub" + "process.run([\"system_profiler\"",
]

REQUIRED_FALSE_TOP_LEVEL = [
    "activation_controller_runtime_allowed",
    "activation_request_allowed",
    "deactivation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
]

REQUIRED_FALSE_SAFETY = [
    "runtime_path_enabled",
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
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    return json.loads(path.read_text())


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def build_report(root: Path, input_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    stub_path = input_dir / "activation-controller-design-stub.json"
    stub = load_json(stub_path)

    add_check(checks, "stub_json_exists", stub_path.exists(), "present" if stub_path.exists() else "missing")
    add_check(checks, "stub_json_loaded", bool(stub), "loaded" if stub else "missing-or-empty")
    add_check(
        checks,
        "stub_schema",
        stub.get("schema") == "h1mekartx.activation_controller_design_stub.v1",
        f"schema={stub.get('schema')!r}",
    )
    add_check(
        checks,
        "stub_decision",
        stub.get("decision") == EXPECTED_STUB_DECISION,
        f"decision={stub.get('decision')!r}",
    )
    add_check(
        checks,
        "stub_ready",
        stub.get("activation_controller_design_stub_ready") is True,
        f"value={stub.get('activation_controller_design_stub_ready')!r}",
    )

    target = stub.get("target", {})
    if not isinstance(target, dict):
        target = {}

    for key, expected in EXPECTED_TARGET.items():
        add_check(checks, f"target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    for key in REQUIRED_FALSE_TOP_LEVEL:
        add_check(checks, f"top_level_false:{key}", stub.get(key) is False, f"value={stub.get(key)!r}")

    states = stub.get("state_machine_stub", [])
    if not isinstance(states, list):
        states = []

    state_map = {
        item.get("state"): item.get("allowed")
        for item in states
        if isinstance(item, dict)
    }

    for state in [
        "activationRuntimeEnabled",
        "providerAttached",
        "hardwareAccessEnabled",
    ]:
        add_check(checks, f"state_blocked:{state}", state_map.get(state) is False, f"value={state_map.get(state)!r}")

    sb = stub.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add_check(checks, "safety_design_stub_only", sb.get("design_stub_only") is True, f"value={sb.get('design_stub_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add_check(checks, f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    for rel in SOURCE_FILES:
        path = root / rel
        source = read_text(path)
        add_check(checks, f"source_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

        for token in FORBIDDEN_SOURCE_TOKENS:
            add_check(
                checks,
                f"source_forbidden_absent:{rel}:{token}",
                token not in source,
                "absent" if token not in source else "present",
            )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "input_dir": str(input_dir),
        "decision": "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT" if failed_count == 0 else "FAIL_ACTIVATION_CONTROLLER_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "source_files": SOURCE_FILES,
        "forbidden_source_tokens": FORBIDDEN_SOURCE_TOKENS,
        "expected_target": EXPECTED_TARGET,
        "activation_controller_runtime_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "safety_boundary": {
            "read_only": True,
            "local_json_validation_only": True,
            "static_source_scan_only": True,
            "activation_contract_only": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "driverkit_activation": False,
            "driverkit_dext_installation": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
            "live_provider_state_query": False,
            "live_extension_status_query": False,
            "live_pci_probing": False,
            "runs_ioreg": False,
            "runs_system_profiler": False,
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

    source_lines = [f"- `{item}`" for item in report["source_files"]]

    return "\n".join(
        [
            "# Activation-controller Static Contract Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Activation-controller runtime allowed: `{report['activation_controller_runtime_allowed']}`",
            "",
            f"Activation request allowed: `{report['activation_request_allowed']}`",
            "",
            f"Deactivation request allowed: `{report['deactivation_request_allowed']}`",
            "",
            f"Manager submit allowed: `{report['manager_submit_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{report['driverkit_target_creation_allowed']}`",
            "",
            f"Provider attach allowed: `{report['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{report['device_ownership_allowed']}`",
            "",
            f"Hardware access allowed: `{report['hardware_access_allowed']}`",
            "",
            "## Source Files Scanned",
            "",
            *source_lines,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This validator performs local JSON validation and static source scanning only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, implement an activation controller runtime path, create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate activation-controller static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--input-dir", default=".", help="Directory containing activation-controller design stub JSON.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")
    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, input_dir)

    json_path = out_dir / "activation-controller-static-contract-report.json"
    md_path = out_dir / "activation-controller-static-contract-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
