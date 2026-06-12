#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_activation_ui_plan.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

UI_SECTIONS = [
    {
        "id": "HAUI-001",
        "name": "StatusOverview",
        "purpose": "Show current project status as UI-only state.",
        "default_state": "NO_GO",
        "interactive_runtime_enabled": False,
    },
    {
        "id": "HAUI-002",
        "name": "EvidenceChecklistView",
        "purpose": "Show entitlement, signing, bundle identity, provider-match, and rollback evidence requirements.",
        "default_state": "NEEDS_USER_EVIDENCE",
        "interactive_runtime_enabled": False,
    },
    {
        "id": "HAUI-003",
        "name": "ActivationGateView",
        "purpose": "Show activation runtime transition decision from local reports.",
        "default_state": "ACTIVATION_CONTROLLER_TRANSITION_GATE_NO_GO",
        "interactive_runtime_enabled": False,
    },
    {
        "id": "HAUI-004",
        "name": "SafetyBoundaryPanel",
        "purpose": "Show forbidden runtime paths and hardware safety boundaries.",
        "default_state": "LOCKED",
        "interactive_runtime_enabled": False,
    },
    {
        "id": "HAUI-005",
        "name": "LocalReportImportPlaceholder",
        "purpose": "Future UI placeholder for loading local generated JSON reports without live system queries.",
        "default_state": "LOCAL_ONLY",
        "interactive_runtime_enabled": False,
    },
    {
        "id": "HAUI-006",
        "name": "DisabledActionArea",
        "purpose": "Reserve disabled UI controls for future activation actions while keeping all controls non-functional.",
        "default_state": "DISABLED",
        "interactive_runtime_enabled": False,
    },
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

FORBIDDEN_NOW = [
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
    "creating DriverKit target",
    "adding dext provider class",
    "adding Info.plist provider match dictionary",
    "installing DriverKit dext",
    "activating DriverKit",
    "requesting device ownership",
    "attaching to PCI provider",
    "querying live provider state",
    "live extension status query",
    "live PCI probing",
    "ioreg collection",
    "system_profiler collection",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission to RTX 5070",
    "RTX 5070 resource allocation",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_plan() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "HOST_APP_ACTIVATION_UI_PLAN_READY_UI_ONLY",
        "plain_answer": "Host-app activation UI planning can start, but all activation and hardware runtime actions remain disabled.",
        "full_metal_goal": True,
        "research_continues": True,
        "host_app_activation_ui_plan_ready": True,
        "ui_only": True,
        "runtime_buttons_enabled": False,
        "activation_runtime_transition_allowed": False,
        "activation_controller_runtime_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "ui_sections": UI_SECTIONS,
        "disabled_actions": DISABLED_ACTIONS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 50 should add a host-app status schema for the UI plan. It must remain local-report-only and must not create activation requests, submit manager requests, create DriverKit targets, attach providers, request device ownership, access PCI config space, map BAR memory, or perform MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "ui_plan_only": True,
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
    section_rows = [
        f"| `{item['id']}` | `{item['name']}` | `{item['default_state']}` | `{item['interactive_runtime_enabled']}` | {item['purpose']} |"
        for item in data["ui_sections"]
    ]
    disabled_lines = [f"- {item}" for item in data["disabled_actions"]]
    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Host-app Activation UI Plan",
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
            f"Host-app activation UI plan ready: `{data['host_app_activation_ui_plan_ready']}`",
            "",
            f"UI only: `{data['ui_only']}`",
            "",
            f"Runtime buttons enabled: `{data['runtime_buttons_enabled']}`",
            "",
            f"Activation runtime transition allowed: `{data['activation_runtime_transition_allowed']}`",
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
            "## UI Sections",
            "",
            "| ID | Name | Default State | Interactive Runtime Enabled | Purpose |",
            "| --- | --- | --- | --- | --- |",
            *section_rows,
            "",
            "## Disabled UI Actions",
            "",
            *disabled_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is UI-plan-only and documentation-only.",
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
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX host-app activation UI plan.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_plan()

    json_path = out_dir / "host-app-activation-ui-plan.json"
    md_path = out_dir / "host-app-activation-ui-plan.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
