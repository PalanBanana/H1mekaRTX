#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.activation_controller_design_stub.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

DESIGN_COMPONENTS = [
    {
        "component": "ActivationController",
        "kind": "design_stub",
        "status": "DESIGN_ONLY",
        "runtime_enabled": False,
        "responsibility": "Own future activation-controller state machine design notes without creating request objects.",
    },
    {
        "component": "ActivationState",
        "kind": "enum_spec",
        "status": "DESIGN_ONLY",
        "runtime_enabled": False,
        "responsibility": "Describe planned states such as idle, evidenceBlocked, userApprovalRequired, restartRequired, completed, and failed.",
    },
    {
        "component": "ActivationPreflight",
        "kind": "gate_spec",
        "status": "DESIGN_ONLY",
        "runtime_enabled": False,
        "responsibility": "Require provider-match transition gate GO before any future activation path can exist.",
    },
    {
        "component": "ActivationEventLog",
        "kind": "local_model_spec",
        "status": "DESIGN_ONLY",
        "runtime_enabled": False,
        "responsibility": "Describe local event names for a future UI without querying live extension state.",
    },
    {
        "component": "RollbackNotice",
        "kind": "runbook_link_spec",
        "status": "DESIGN_ONLY",
        "runtime_enabled": False,
        "responsibility": "Require rollback/recovery docs before future activation implementation.",
    },
]

STATE_MACHINE_STUB = [
    {
        "state": "idle",
        "allowed": True,
        "description": "Design-only default state.",
    },
    {
        "state": "evidenceBlocked",
        "allowed": True,
        "description": "Current expected state while entitlement, signing, bundle identity, and provider transition evidence remain incomplete.",
    },
    {
        "state": "activationDesignReviewed",
        "allowed": True,
        "description": "Future design-review state only; still no request object or manager submit.",
    },
    {
        "state": "activationRuntimeEnabled",
        "allowed": False,
        "description": "Blocked until separate GO decision exists.",
    },
    {
        "state": "providerAttached",
        "allowed": False,
        "description": "Blocked; no provider attach or device ownership in this stage.",
    },
    {
        "state": "hardwareAccessEnabled",
        "allowed": False,
        "description": "Blocked; no PCI config, BAR, MMIO, firmware, display, framebuffer, or reset path.",
    },
]

PRECONDITION_GATES = [
    {
        "gate": "ACD-001",
        "name": "provider-match transition gate",
        "required_status": "GO",
        "current_status": "NO_GO",
        "blocking": True,
    },
    {
        "gate": "ACD-002",
        "name": "DriverKit entitlement evidence",
        "required_status": "USER_PRIVATE_APPROVED",
        "current_status": "MISSING",
        "blocking": True,
    },
    {
        "gate": "ACD-003",
        "name": "PCI transport entitlement evidence",
        "required_status": "USER_PRIVATE_APPROVED",
        "current_status": "MISSING",
        "blocking": True,
    },
    {
        "gate": "ACD-004",
        "name": "host app and dext bundle identity evidence",
        "required_status": "USER_PRIVATE_RECORDED",
        "current_status": "MISSING",
        "blocking": True,
    },
    {
        "gate": "ACD-005",
        "name": "rollback and recovery runbook",
        "required_status": "REVIEWED",
        "current_status": "NEEDS_REVIEW",
        "blocking": True,
    },
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


def build_stub() -> dict[str, Any]:
    blocking_gates = [gate for gate in PRECONDITION_GATES if gate["blocking"]]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "ACTIVATION_CONTROLLER_DESIGN_STUB_READY_NO_RUNTIME",
        "plain_answer": "Activation-controller design notes can exist, but activation runtime remains blocked.",
        "full_metal_goal": True,
        "research_continues": True,
        "activation_controller_design_stub_ready": True,
        "activation_controller_runtime_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "design_components": DESIGN_COMPONENTS,
        "state_machine_stub": STATE_MACHINE_STUB,
        "precondition_gates": PRECONDITION_GATES,
        "blocking_precondition_gate_count": len(blocking_gates),
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 47 should add an activation-controller static contract validator that proves the design stub contains no activation request creation, manager submit, DriverKit target creation, provider attach, device ownership, PCI config access, BAR mapping, or MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "design_stub_only": True,
            "runtime_path_enabled": False,
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
    component_rows = [
        f"| `{item['component']}` | `{item['kind']}` | `{item['status']}` | `{item['runtime_enabled']}` | {item['responsibility']} |"
        for item in data["design_components"]
    ]

    state_rows = [
        f"| `{item['state']}` | `{item['allowed']}` | {item['description']} |"
        for item in data["state_machine_stub"]
    ]

    gate_rows = [
        f"| `{item['gate']}` | {item['name']} | `{item['required_status']}` | `{item['current_status']}` | `{item['blocking']}` |"
        for item in data["precondition_gates"]
    ]

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Activation-controller Design Stub",
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
            f"Activation-controller design stub ready: `{data['activation_controller_design_stub_ready']}`",
            "",
            f"Activation-controller runtime allowed: `{data['activation_controller_runtime_allowed']}`",
            "",
            f"Activation request allowed: `{data['activation_request_allowed']}`",
            "",
            f"Deactivation request allowed: `{data['deactivation_request_allowed']}`",
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
            f"Blocking precondition gate count: `{data['blocking_precondition_gate_count']}`",
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
            "## Design Components",
            "",
            "| Component | Kind | Status | Runtime Enabled | Responsibility |",
            "| --- | --- | --- | --- | --- |",
            *component_rows,
            "",
            "## State Machine Stub",
            "",
            "| State | Allowed | Description |",
            "| --- | --- | --- |",
            *state_rows,
            "",
            "## Preconditions",
            "",
            "| Gate | Name | Required Status | Current Status | Blocking |",
            "| --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is design-stub-only and documentation-only.",
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
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX activation-controller design stub.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_stub()

    json_path = out_dir / "activation-controller-design-stub.json"
    md_path = out_dir / "activation-controller-design-stub.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
