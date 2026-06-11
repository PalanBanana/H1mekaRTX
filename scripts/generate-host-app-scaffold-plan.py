#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_scaffold_plan.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

HOST_APP_COMPONENTS = [
    {
        "component": "host_app_shell",
        "status": "PLANNED_ONLY",
        "future_role": "Container app that would package and manage the DriverKit system extension.",
        "current_stage_action": "DOCUMENT_ONLY_NO_TARGET",
        "required_before_scaffold": [
            "bundle identifier policy",
            "signing identity policy",
            "provisioning profile policy",
            "entitlement evidence",
        ],
    },
    {
        "component": "activation_controller",
        "status": "PLANNED_ONLY",
        "future_role": "Future object responsible for activation/deactivation request orchestration.",
        "current_stage_action": "DOCUMENT_ONLY_NO_REQUEST_CODE",
        "required_before_scaffold": [
            "System Extension request dry-run checklist",
            "rollback procedure",
            "user approval UI copy",
            "log capture plan",
        ],
    },
    {
        "component": "driver_status_view",
        "status": "PLANNED_ONLY",
        "future_role": "Future UI surface for showing inactive, pending approval, active, failed, or disabled states.",
        "current_stage_action": "DOCUMENT_ONLY_NO_UI_TARGET",
        "required_before_scaffold": [
            "state machine definition",
            "error code mapping",
            "non-sensitive diagnostics format",
        ],
    },
    {
        "component": "diagnostics_exporter",
        "status": "PLANNED_ONLY",
        "future_role": "Future user-triggered exporter for safe logs and generated reports.",
        "current_stage_action": "DOCUMENT_ONLY_NO_COLLECTION",
        "required_before_scaffold": [
            "allowed diagnostic file list",
            "privacy boundary",
            "no live hardware probing",
        ],
    },
    {
        "component": "metal_reference_launcher",
        "status": "PLANNED_ONLY",
        "future_role": "Future launcher for public Metal reference workloads on the existing system Metal device.",
        "current_stage_action": "DOCUMENT_ONLY_NO_APP_INTEGRATION",
        "required_before_scaffold": [
            "Stage 25 reference workload suite stability",
            "JSON result import format",
            "no RTX 5070 acceleration claims",
        ],
    },
]

BUNDLE_PLAN = [
    {
        "item": "host_app_bundle_id",
        "placeholder": "com.h1meka.H1mekaRTXHost",
        "status": "PLACEHOLDER_ONLY",
        "committed_to_project": False,
    },
    {
        "item": "driver_extension_bundle_id",
        "placeholder": "com.h1meka.H1mekaRTXDriver",
        "status": "PLACEHOLDER_ONLY",
        "committed_to_project": False,
    },
    {
        "item": "app_group",
        "placeholder": "none-currently",
        "status": "NOT_PLANNED_CURRENTLY",
        "committed_to_project": False,
    },
]

STATE_MACHINE = [
    {
        "state": "NOT_INSTALLED",
        "meaning": "No system extension activation attempt has been made.",
        "allowed_currently": True,
    },
    {
        "state": "PLANNED_ONLY",
        "meaning": "Host app/deext architecture is documented but not implemented.",
        "allowed_currently": True,
    },
    {
        "state": "READY_FOR_DRY_RUN_REVIEW",
        "meaning": "Future stage may review scaffold creation without activation.",
        "allowed_currently": False,
    },
    {
        "state": "PENDING_USER_APPROVAL",
        "meaning": "Future activation request submitted and waiting for approval.",
        "allowed_currently": False,
    },
    {
        "state": "ACTIVE",
        "meaning": "Future system extension activated.",
        "allowed_currently": False,
    },
    {
        "state": "FAILED",
        "meaning": "Future activation or driver state failed.",
        "allowed_currently": False,
    },
    {
        "state": "DISABLED_OR_ROLLED_BACK",
        "meaning": "Future rollback path completed.",
        "allowed_currently": False,
    },
]

SCAFFOLD_GATES = [
    {
        "gate": "HAG-1",
        "name": "Entitlement evidence",
        "status": "NO_GO",
        "required_before_target_creation": True,
        "reason": "DriverKit and PCI transport entitlement evidence is not verified in this repository.",
    },
    {
        "gate": "HAG-2",
        "name": "Bundle identity policy",
        "status": "PARTIAL",
        "required_before_target_creation": True,
        "reason": "Placeholder bundle identifiers exist, but no final identity policy exists.",
    },
    {
        "gate": "HAG-3",
        "name": "Provisioning profile policy",
        "status": "NO_GO",
        "required_before_target_creation": True,
        "reason": "No provisioning profile or signing plan is verified.",
    },
    {
        "gate": "HAG-4",
        "name": "Activation request boundary",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_target_creation": True,
        "reason": "Current stage explicitly forbids activation request code.",
    },
    {
        "gate": "HAG-5",
        "name": "Rollback runbook",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_target_creation": True,
        "reason": "Stage 22 recovery and rollback runbook exists.",
    },
    {
        "gate": "HAG-6",
        "name": "Hardware access boundary",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_target_creation": True,
        "reason": "Current stage forbids PCI, BAR, MMIO, DriverKit activation, and RTX 5070 acceleration.",
    },
]

FORBIDDEN_NOW = [
    "host app target creation",
    "DriverKit dext target creation",
    "System Extension activation request",
    "System Extension deactivation request",
    "OSSystemExtensionManager submit request",
    "DriverKit activation",
    "IOPCIDevice ownership request",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission",
    "RTX 5070 resource allocation",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_plan() -> dict[str, Any]:
    no_go_count = sum(1 for item in SCAFFOLD_GATES if item["status"] == "NO_GO")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "HOST_APP_SCAFFOLD_PLAN_READY_NO_TARGETS",
        "full_metal_goal": True,
        "research_continues": True,
        "host_app_scaffold_plan_ready": True,
        "host_app_target_creation_allowed": False,
        "driverkit_dext_target_creation_allowed": False,
        "system_extension_request_allowed": False,
        "driverkit_activation_allowed": False,
        "implementation_allowed": False,
        "implementation_started": False,
        "no_go_count": no_go_count,
        "host_app_components": HOST_APP_COMPONENTS,
        "bundle_plan": BUNDLE_PLAN,
        "state_machine": STATE_MACHINE,
        "scaffold_gates": SCAFFOLD_GATES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 27 should add a host app skeleton only if it remains no-activation and no-dext, or continue with additional planning if entitlement evidence is still missing.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "adds_host_app_target": False,
            "adds_driverkit_dext_target": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "ossystemextensionmanager_submit_request": False,
            "iopcidevice_ownership_request": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission": False,
            "resource_allocation_on_rtx5070": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    component_rows = []
    for item in data["host_app_components"]:
        required = "<br>".join(item["required_before_scaffold"])
        component_rows.append(
            f"| `{item['component']}` | `{item['status']}` | {item['future_role']} | `{item['current_stage_action']}` | {required} |"
        )

    bundle_rows = []
    for item in data["bundle_plan"]:
        bundle_rows.append(
            f"| `{item['item']}` | `{item['placeholder']}` | `{item['status']}` | `{item['committed_to_project']}` |"
        )

    state_rows = []
    for item in data["state_machine"]:
        state_rows.append(
            f"| `{item['state']}` | {item['meaning']} | `{item['allowed_currently']}` |"
        )

    gate_rows = []
    for item in data["scaffold_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | {item['name']} | `{item['status']}` | `{item['required_before_target_creation']}` | {item['reason']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Host App Scaffold Plan",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Host app scaffold plan ready: `{data['host_app_scaffold_plan_ready']}`",
            "",
            f"Host app target creation allowed: `{data['host_app_target_creation_allowed']}`",
            "",
            f"DriverKit dext target creation allowed: `{data['driverkit_dext_target_creation_allowed']}`",
            "",
            f"System Extension request allowed: `{data['system_extension_request_allowed']}`",
            "",
            f"DriverKit activation allowed: `{data['driverkit_activation_allowed']}`",
            "",
            f"Implementation allowed: `{data['implementation_allowed']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
            "",
            f"No-go count: `{data['no_go_count']}`",
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
            "## Planned Host App Components",
            "",
            "| Component | Status | Future Role | Current Stage Action | Required Before Scaffold |",
            "| --- | --- | --- | --- | --- |",
            *component_rows,
            "",
            "## Bundle Plan",
            "",
            "| Item | Placeholder | Status | Committed To Project |",
            "| --- | --- | --- | --- |",
            *bundle_rows,
            "",
            "## State Machine",
            "",
            "| State | Meaning | Allowed Currently |",
            "| --- | --- | --- |",
            *state_rows,
            "",
            "## Scaffold Gates",
            "",
            "| Gate | Name | Status | Required Before Target Creation | Reason |",
            "| --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is documentation-only.",
            "",
            "It does not add a host app target, add a DriverKit dext target, add System Extension request code, activate DriverKit, submit activation or deactivation requests, call OSSystemExtensionManager submit, request IOPCIDevice ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, run GPU reset logic, or start RTX 5070 Metal acceleration implementation.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX host app scaffold plan."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_plan()

    json_path = out_dir / "host-app-scaffold-plan.json"
    md_path = out_dir / "host-app-scaffold-plan.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
