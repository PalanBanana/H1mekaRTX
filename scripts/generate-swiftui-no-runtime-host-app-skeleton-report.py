#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_no_runtime_host_app_skeleton.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

SWIFT_FILES = [
    "tools/host-app-no-runtime-swiftui/Package.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/H1mekaRTXHostApp.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/ContentView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/HeaderView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/StatusCardView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/DisabledActionPanel.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/HostStatusViewModel.swift",
]

UI_COMPONENTS = [
    "H1mekaRTXHostApp",
    "ContentView",
    "HeaderView",
    "StatusCardView",
    "DisabledActionPanel",
    "HostStatusViewModel",
]

DISABLED_ACTIONS = [
    "Activate Driver",
    "Deactivate Driver",
    "Install Driver Extension",
    "Attach Provider",
    "Request Device Ownership",
    "Probe PCI",
    "Map BAR",
    "Run Metal Workload On RTX 5070",
]


def build_report(root: Path) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "target": TARGET,
        "decision": "SWIFTUI_NO_RUNTIME_HOST_APP_SKELETON_READY",
        "plain_answer": "SwiftUI host-app skeleton exists, but all runtime and hardware paths remain disabled.",
        "full_metal_goal": True,
        "research_continues": True,
        "swiftui_skeleton_ready": True,
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
        "swift_package_root": "tools/host-app-no-runtime-swiftui",
        "swift_files": SWIFT_FILES,
        "ui_components": UI_COMPONENTS,
        "disabled_actions": DISABLED_ACTIONS,
        "next_stage_recommendation": "Stage 53 should add a SwiftUI no-runtime skeleton static validator and optional syntax/build probe that keeps activation, DriverKit, provider, PCI, BAR, MMIO, and RTX 5070 acceleration paths disabled.",
        "safety_boundary": {
            "read_only": True,
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
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    file_lines = [f"- `{item}`" for item in data["swift_files"]]
    component_lines = [f"- `{item}`" for item in data["ui_components"]]
    action_lines = [f"- {item}" for item in data["disabled_actions"]]

    return "\n".join(
        [
            "# SwiftUI No-runtime Host-app Skeleton",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"SwiftUI skeleton ready: `{data['swiftui_skeleton_ready']}`",
            "",
            f"Actual app code started: `{data['actual_app_code_started']}`",
            "",
            f"No runtime: `{data['no_runtime']}`",
            "",
            f"Runtime buttons enabled: `{data['runtime_buttons_enabled']}`",
            "",
            f"Live system queries allowed: `{data['live_system_queries_allowed']}`",
            "",
            f"Activation request allowed: `{data['activation_request_allowed']}`",
            "",
            f"Manager submit allowed: `{data['manager_submit_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{data['driverkit_target_creation_allowed']}`",
            "",
            f"Provider attach allowed: `{data['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
            "",
            f"Hardware access allowed: `{data['hardware_access_allowed']}`",
            "",
            "## Target",
            "",
            f"- GPU: `{data['target']['gpu']}`",
            f"- Vendor ID: `{data['target']['vendor_id']}`",
            f"- Device ID: `{data['target']['device_id']}`",
            f"- IOPCIMatch: `{data['target']['iopcimatch']}`",
            f"- Subsystem Vendor ID: `{data['target']['subsystem_vendor_id']}`",
            f"- Subsystem ID: `{data['target']['subsystem_id']}`",
            "",
            "## Swift Package Root",
            "",
            f"`{data['swift_package_root']}`",
            "",
            "## Swift Files",
            "",
            *file_lines,
            "",
            "## UI Components",
            "",
            *component_lines,
            "",
            "## Disabled Actions",
            "",
            *action_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage adds SwiftUI source only.",
            "",
            "It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SwiftUI no-runtime host-app skeleton report.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_report(root)

    json_path = out_dir / "swiftui-no-runtime-host-app-skeleton-report.json"
    md_path = out_dir / "swiftui-no-runtime-host-app-skeleton-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
