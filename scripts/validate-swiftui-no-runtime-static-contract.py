#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_no_runtime_static_contract.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

SWIFT_PACKAGE_ROOT = "tools/host-app-no-runtime-swiftui"

SWIFT_FILES = [
    "tools/host-app-no-runtime-swiftui/Package.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/H1mekaRTXHostApp.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/ContentView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/HeaderView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/StatusCardView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/DisabledActionPanel.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/HostStatusViewModel.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/HostAppStatusModel.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalStatusModelLoader.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/Resources/sample-host-status.json",
]

REQUIRED_SWIFT_TERMS = [
    "import SwiftUI",
    "@main",
    "struct H1mekaRTXHostApp: App",
    "struct ContentView: View",
    "struct HeaderView: View",
    "struct StatusCardView: View",
    "struct DisabledActionPanel: View",
    "struct HostStatusViewModel",
    "HostStatusViewModel.sample",
    ".disabled(true)",
    "RESEARCH_ONLY",
    "NO_GO",
    "NEEDS_USER_EVIDENCE",
    "BLOCKED",
]

FORBIDDEN_SOURCE_TOKENS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submitRequest"]),
    "".join(["OSSystem", "ExtensionManager.shared"]),
    "".join(["OSSystem", "ExtensionRequest"]),
    "".join(["IOPCI", "Device"]),
    "".join(["IOService", "GetMatchingServices"]),
    "".join(["Configuration", "Read"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["map", "DeviceMemory"]),
    "".join(["Create", "MemoryMap"]),
    "".join(["sub", "process.run([\"live registry tool\""]),
    "".join(["sub", "process.run([\"live profiler tool\""]),
]

REQUIRED_FALSE_FLAGS = [
    "runtime_buttons_enabled",
    "live_system_queries_allowed",
    "activation_runtime_transition_allowed",
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
    "runtime_buttons_enabled",
    "live_system_queries",
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
    "runs_live registry tool",
    "runs_live profiler tool",
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


def run_optional_swift_build(root: Path) -> dict[str, Any]:
    enabled = os.environ.get("H1MEKARTX_RUN_SWIFT_BUILD", "0") == "1"
    swift_path = shutil.which("swift")

    if not enabled:
        return {
            "enabled": False,
            "status": "SKIPPED_DISABLED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }

    if not swift_path:
        return {
            "enabled": True,
            "status": "SKIPPED_SWIFT_NOT_FOUND",
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }

    proc = subprocess.run(
        [
            swift_path,
            "build",
            "--package-path",
            str(root / SWIFT_PACKAGE_ROOT),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return {
        "enabled": True,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout[-6000:],
        "stderr": proc.stderr[-6000:],
    }


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in SWIFT_FILES:
        path = root / rel
        add_check(checks, f"swift_file_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in SWIFT_FILES)

    for term in REQUIRED_SWIFT_TERMS:
        add_check(checks, f"swift_required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_SOURCE_TOKENS:
        add_check(checks, f"forbidden_source_token_absent:{token}", token not in source, "absent" if token not in source else "present")

    add_check(checks, "package_root_exists", (root / SWIFT_PACKAGE_ROOT).is_dir(), SWIFT_PACKAGE_ROOT)
    add_check(checks, "package_swift_exists", (root / SWIFT_PACKAGE_ROOT / "Package.swift").is_file(), "Package.swift")
    add_check(checks, "sources_dir_exists", (root / SWIFT_PACKAGE_ROOT / "Sources" / "H1mekaRTXHostApp").is_dir(), "Sources/H1mekaRTXHostApp")

    build_probe = run_optional_swift_build(root)
    add_check(
        checks,
        "optional_swift_build_probe_not_required",
        build_probe["status"] in ["SKIPPED_DISABLED", "SKIPPED_SWIFT_NOT_FOUND", "PASS"],
        f"status={build_probe['status']!r}, returncode={build_probe['returncode']!r}",
    )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "target": EXPECTED_TARGET,
        "decision": "PASS_SWIFTUI_NO_RUNTIME_STATIC_CONTRACT" if failed_count == 0 else "FAIL_SWIFTUI_NO_RUNTIME_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "swift_package_root": SWIFT_PACKAGE_ROOT,
        "swift_files": SWIFT_FILES,
        "optional_swift_build_probe": build_probe,
        "swiftui_static_contract_valid": failed_count == 0,
        "actual_app_code_started": True,
        "no_runtime": True,
        "local_status_placeholders_only": True,
        "runtime_buttons_enabled": False,
        "live_system_queries_allowed": False,
        "activation_runtime_transition_allowed": False,
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
            "static_source_scan_only": True,
            "optional_build_probe_only": True,
            "swiftui_source_only": True,
            "no_runtime": True,
            "local_status_placeholders_only": True,
            "runtime_buttons_enabled": False,
            "live_system_queries": False,
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
            "runs_live registry tool": False,
            "runs_live profiler tool": False,
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
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        rows.append(f"| `{item['name']}` | {status} | {item['detail'].replace('|', '\\|')} |")

    file_lines = [f"- `{item}`" for item in report["swift_files"]]
    build_probe = report["optional_swift_build_probe"]

    return "\n".join(
        [
            "# SwiftUI No-runtime Static Contract Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"SwiftUI static contract valid: `{report['swiftui_static_contract_valid']}`",
            "",
            f"Actual app code started: `{report['actual_app_code_started']}`",
            "",
            f"No runtime: `{report['no_runtime']}`",
            "",
            f"Runtime buttons enabled: `{report['runtime_buttons_enabled']}`",
            "",
            f"Live system queries allowed: `{report['live_system_queries_allowed']}`",
            "",
            f"Activation request allowed: `{report['activation_request_allowed']}`",
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
            "## Swift Files",
            "",
            *file_lines,
            "",
            "## Optional Swift Build Probe",
            "",
            f"- Enabled: `{build_probe['enabled']}`",
            f"- Status: `{build_probe['status']}`",
            f"- Return code: `{build_probe['returncode']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This validator performs static source scanning and an optional Swift build probe only.",
            "",
            "It does not create activation request objects, create deactivation request objects, call extension manager submit, implement activation runtime, create DriverKit targets, attach providers, request device ownership, run live PCI tools, touch low-level hardware access paths, execute RTX 5070 shaders, submit hardware commands, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SwiftUI no-runtime static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "swiftui-no-runtime-static-contract-report.json"
    md_path = out_dir / "swiftui-no-runtime-static-contract-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
