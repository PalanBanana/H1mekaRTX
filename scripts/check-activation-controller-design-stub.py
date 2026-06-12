#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.activation_controller_design_stub_check.v1"

REQUIRED_FILES = [
    "scripts/generate-activation-controller-design-stub.py",
    "scripts/check-activation-controller-design-stub.py",
    "docs/metal/activation-controller-design-stub.md",
]

REQUIRED_TERMS = [
    "ACTIVATION_CONTROLLER_DESIGN_STUB_READY_NO_RUNTIME",
    "activation_controller_runtime_allowed",
    "activation_request_allowed",
    "deactivation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
    "design_stub_only",
    "runtime_path_enabled",
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


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_generator(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["python3", str(root / "scripts" / "generate-activation-controller-design-stub.py"), "--out-dir", str(out_dir)],
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

    source = "\n".join(
        [
            read_text(root / "scripts" / "generate-activation-controller-design-stub.py"),
            read_text(root / "scripts" / "check-activation-controller-design-stub.py"),
            read_text(root / "docs" / "metal" / "activation-controller-design-stub.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add_check(checks, "generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    stub_path = out_dir / "activation-controller-design-stub.json"
    data = json.loads(stub_path.read_text()) if stub_path.exists() else {}

    add_check(
        checks,
        "stub_schema",
        data.get("schema") == "h1mekartx.activation_controller_design_stub.v1",
        f"schema={data.get('schema')!r}",
    )
    add_check(
        checks,
        "stub_decision",
        data.get("decision") == "ACTIVATION_CONTROLLER_DESIGN_STUB_READY_NO_RUNTIME",
        f"decision={data.get('decision')!r}",
    )
    add_check(
        checks,
        "stub_ready",
        data.get("activation_controller_design_stub_ready") is True,
        f"value={data.get('activation_controller_design_stub_ready')!r}",
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
        add_check(checks, f"blocked:{key}", data.get(key) is False, f"value={data.get(key)!r}")

    target = data.get("target", {})
    expected_target = {
        "vendor_id": "0x10de",
        "device_id": "0x2f04",
        "iopcimatch": "0x2f0410de",
        "subsystem_vendor_id": "0x1458",
        "subsystem_id": "0x417e",
    }
    for key, expected in expected_target.items():
        add_check(checks, f"target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    add_check(
        checks,
        "design_components_present",
        isinstance(data.get("design_components"), list) and len(data.get("design_components", [])) >= 5,
        f"count={len(data.get('design_components', [])) if isinstance(data.get('design_components'), list) else 'not-list'}",
    )
    add_check(
        checks,
        "state_machine_stub_present",
        isinstance(data.get("state_machine_stub"), list) and len(data.get("state_machine_stub", [])) >= 6,
        f"count={len(data.get('state_machine_stub', [])) if isinstance(data.get('state_machine_stub'), list) else 'not-list'}",
    )
    add_check(
        checks,
        "blocking_preconditions_present",
        data.get("blocking_precondition_gate_count", 0) > 0,
        f"value={data.get('blocking_precondition_gate_count')!r}",
    )

    states = data.get("state_machine_stub", [])
    add_check(
        checks,
        "runtime_state_blocked",
        any(isinstance(item, dict) and item.get("state") == "activationRuntimeEnabled" and item.get("allowed") is False for item in states),
        "activationRuntimeEnabled blocked",
    )
    add_check(
        checks,
        "provider_state_blocked",
        any(isinstance(item, dict) and item.get("state") == "providerAttached" and item.get("allowed") is False for item in states),
        "providerAttached blocked",
    )
    add_check(
        checks,
        "hardware_state_blocked",
        any(isinstance(item, dict) and item.get("state") == "hardwareAccessEnabled" and item.get("allowed") is False for item in states),
        "hardwareAccessEnabled blocked",
    )

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add_check(checks, "safety_design_stub_only", sb.get("design_stub_only") is True, f"value={sb.get('design_stub_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add_check(checks, f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_ACTIVATION_CONTROLLER_DESIGN_STUB_READY" if failed_count == 0 else "FAIL_ACTIVATION_CONTROLLER_DESIGN_STUB",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "design_stub_only": True,
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
            "# Activation-controller Design Stub Check",
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
            "This check validates the activation-controller design stub using local generated JSON only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, request device ownership, attach to PCI providers, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX activation-controller design stub.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "activation-controller-design-stub-check.json"
    md_path = out_dir / "activation-controller-design-stub-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
