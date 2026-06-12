#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_no_runtime_host_app_skeleton_check.v1"

REQUIRED_FILES = [
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
    "scripts/generate-swiftui-no-runtime-host-app-skeleton-report.py",
    "scripts/check-swiftui-no-runtime-host-app-skeleton.py",
    "docs/metal/swiftui-no-runtime-host-app-skeleton.md",
]

REQUIRED_TERMS = [
    "SWIFTUI_NO_RUNTIME_HOST_APP_SKELETON_READY",
    "swiftui_skeleton_ready",
    "actual_app_code_started",
    "no_runtime",
    "local_status_placeholders_only",
    "runtime_buttons_enabled",
    "live_system_queries_allowed",
    "activation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
]

FORBIDDEN_LITERAL_TERMS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submitRequest"]),
    "".join(["OSSystem", "ExtensionManager.shared"]),
    "".join(["Configuration", "Read"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["IOPCI", "Device"]),
    "".join(["map", "DeviceMemory"]),
    "".join(["Create", "MemoryMap"]),
    "".join(["sub", "process.run([\"ioreg\""]),
    "".join(["sub", "process.run([\"system_profiler\""]),
]

REQUIRED_FALSE_KEYS = [
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


def run_report(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-swiftui-no-runtime-host-app-skeleton-report.py"),
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
        ],
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

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    swift_source = "\n".join(
        read_text(root / rel)
        for rel in REQUIRED_FILES
        if rel.endswith(".swift")
    )

    for term in [
        "import SwiftUI",
        "@main",
        "struct H1mekaRTXHostApp: App",
        "struct ContentView: View",
        "struct DisabledActionPanel: View",
        "HostStatusViewModel.sample",
        ".disabled(true)",
        "RESEARCH_ONLY",
        "NO_GO",
        "BLOCKED",
        "NEEDS_USER_EVIDENCE",
    ]:
        add_check(checks, f"swift_required_term:{term}", term in swift_source, "found" if term in swift_source else "missing")

    report_run = run_report(root, out_dir)
    add_check(checks, "report_generator_returncode", report_run["returncode"] == 0, f"returncode={report_run['returncode']}")

    report_path = out_dir / "swiftui-no-runtime-host-app-skeleton-report.json"
    data = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(checks, "report_schema", data.get("schema") == "h1mekartx.swiftui_no_runtime_host_app_skeleton.v1", f"schema={data.get('schema')!r}")
    add_check(checks, "report_decision", data.get("decision") == "SWIFTUI_NO_RUNTIME_HOST_APP_SKELETON_READY", f"decision={data.get('decision')!r}")
    add_check(checks, "skeleton_ready", data.get("swiftui_skeleton_ready") is True, f"value={data.get('swiftui_skeleton_ready')!r}")
    add_check(checks, "actual_app_code_started", data.get("actual_app_code_started") is True, f"value={data.get('actual_app_code_started')!r}")
    add_check(checks, "no_runtime", data.get("no_runtime") is True, f"value={data.get('no_runtime')!r}")

    for key in REQUIRED_FALSE_KEYS:
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

    swift_files = data.get("swift_files", [])
    ui_components = data.get("ui_components", [])
    disabled_actions = data.get("disabled_actions", [])

    add_check(checks, "swift_files_present", isinstance(swift_files, list) and len(swift_files) >= 7, f"count={len(swift_files) if isinstance(swift_files, list) else 'not-list'}")
    add_check(checks, "ui_components_present", isinstance(ui_components, list) and len(ui_components) >= 6, f"count={len(ui_components) if isinstance(ui_components, list) else 'not-list'}")
    add_check(checks, "disabled_actions_present", isinstance(disabled_actions, list) and len(disabled_actions) >= 8, f"count={len(disabled_actions) if isinstance(disabled_actions, list) else 'not-list'}")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "safety_swiftui_source_only", sb.get("swiftui_source_only") is True, f"value={sb.get('swiftui_source_only')!r}")
    add_check(checks, "safety_no_runtime", sb.get("no_runtime") is True, f"value={sb.get('no_runtime')!r}")
    add_check(checks, "safety_local_status_placeholders_only", sb.get("local_status_placeholders_only") is True, f"value={sb.get('local_status_placeholders_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add_check(checks, f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_SWIFTUI_NO_RUNTIME_HOST_APP_SKELETON_READY" if failed_count == 0 else "FAIL_SWIFTUI_NO_RUNTIME_HOST_APP_SKELETON",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "report_run": report_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "swiftui_source_only": True,
            "no_runtime": True,
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
            "# SwiftUI No-runtime Host-app Skeleton Check",
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
            "This check validates SwiftUI source and local report metadata only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, request device ownership, attach to PCI providers, run live PCI tools, access PCI config space, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SwiftUI no-runtime host-app skeleton.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "swiftui-no-runtime-host-app-skeleton-check.json"
    md_path = out_dir / "swiftui-no-runtime-host-app-skeleton-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
