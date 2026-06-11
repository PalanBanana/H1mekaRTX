#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.driverkit_dry_run_checklist.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

DRY_RUN_PHASES = [
    {
        "phase": "DRY-001",
        "name": "Entitlement evidence check",
        "status": "REQUIRED_BEFORE_ACTIVATION",
        "current_stage_action": "DOCUMENT_ONLY",
        "checks": [
            "DriverKit entitlement evidence recorded",
            "PCI transport entitlement evidence recorded",
            "host app system extension install entitlement evidence recorded",
            "no entitlement values committed from private profiles",
        ],
    },
    {
        "phase": "DRY-002",
        "name": "Bundle identity check",
        "status": "REQUIRED_BEFORE_ACTIVATION",
        "current_stage_action": "DOCUMENT_ONLY",
        "checks": [
            "host app bundle identifier planned",
            "driver extension bundle identifier planned",
            "bundle identifier relationship documented",
            "no real host app target added in this stage",
            "no real dext target added in this stage",
        ],
    },
    {
        "phase": "DRY-003",
        "name": "Provisioning and signing check",
        "status": "REQUIRED_BEFORE_ACTIVATION",
        "current_stage_action": "DOCUMENT_ONLY",
        "checks": [
            "host app provisioning profile plan documented",
            "driver extension provisioning profile plan documented",
            "signing identity plan documented",
            "no provisioning profile committed",
            "no certificates committed",
        ],
    },
    {
        "phase": "DRY-004",
        "name": "Provider match check",
        "status": "REQUIRED_BEFORE_ACTIVATION",
        "current_stage_action": "DOCUMENT_ONLY",
        "checks": [
            "vendor ID target documented",
            "device ID target documented",
            "subsystem vendor ID target documented",
            "subsystem ID target documented",
            "wrong-device attach risk documented",
            "no IOPCIDevice ownership request made",
        ],
    },
    {
        "phase": "DRY-005",
        "name": "System Extension request check",
        "status": "FUTURE_ONLY",
        "current_stage_action": "DOCUMENT_ONLY_NO_REQUEST_CODE",
        "checks": [
            "activation request flow documented",
            "deactivation request flow documented",
            "user approval requirement documented",
            "restart requirement risk documented",
            "no OSSystemExtensionRequest code added",
            "no OSSystemExtensionManager submit call added",
        ],
    },
    {
        "phase": "DRY-006",
        "name": "Rollback readiness check",
        "status": "REQUIRED_BEFORE_ACTIVATION",
        "current_stage_action": "DOCUMENT_ONLY",
        "checks": [
            "Stage 22 recovery runbook exists",
            "branch rollback documented",
            "activation failure rollback documented",
            "deactivation/restart risk documented",
            "no hardware experiment allowed",
        ],
    },
    {
        "phase": "DRY-007",
        "name": "Safety gate check",
        "status": "REQUIRED_BEFORE_ACTIVATION",
        "current_stage_action": "DOCUMENT_ONLY",
        "checks": [
            "BAR safety gates passing",
            "forbidden operation audit passing",
            "release readiness check passing",
            "Metal validation harness check passing",
            "no BAR mapping",
            "no MMIO access",
            "no RTX 5070 acceleration attempt",
        ],
    },
]

GO_NO_GO_CRITERIA = [
    {
        "criterion": "Entitlements approved",
        "required_for_activation": True,
        "current_result": "UNKNOWN",
        "decision": "NO_GO",
    },
    {
        "criterion": "Host app target exists",
        "required_for_activation": True,
        "current_result": "ABSENT_BY_DESIGN",
        "decision": "NO_GO",
    },
    {
        "criterion": "DriverKit dext target exists",
        "required_for_activation": True,
        "current_result": "ABSENT_BY_DESIGN",
        "decision": "NO_GO",
    },
    {
        "criterion": "Provisioning and signing verified",
        "required_for_activation": True,
        "current_result": "UNKNOWN",
        "decision": "NO_GO",
    },
    {
        "criterion": "Provider match reviewed",
        "required_for_activation": True,
        "current_result": "DOCUMENTATION_ONLY",
        "decision": "NO_GO",
    },
    {
        "criterion": "Rollback runbook exists",
        "required_for_activation": True,
        "current_result": "PRESENT",
        "decision": "PARTIAL",
    },
    {
        "criterion": "Hardware access remains denied",
        "required_for_activation": True,
        "current_result": "DENIED",
        "decision": "PASS_FOR_CURRENT_STAGE",
    },
]

FORBIDDEN_NOW = [
    "DriverKit activation",
    "System Extension activation request",
    "System Extension deactivation request",
    "OSSystemExtensionManager submit request",
    "host app target creation",
    "DriverKit dext target creation",
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
    "queue or ring programming",
    "doorbell interaction",
    "RTX 5070 resource allocation",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_checklist() -> dict[str, Any]:
    no_go_count = sum(1 for item in GO_NO_GO_CRITERIA if item["decision"] == "NO_GO")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "DRIVERKIT_DRY_RUN_CHECKLIST_READY_NO_ACTIVATION",
        "full_metal_goal": True,
        "research_continues": True,
        "dry_run_checklist_ready": True,
        "driverkit_activation_allowed": False,
        "system_extension_request_allowed": False,
        "implementation_allowed": False,
        "implementation_started": False,
        "no_go_count": no_go_count,
        "dry_run_phases": DRY_RUN_PHASES,
        "go_no_go_criteria": GO_NO_GO_CRITERIA,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 24 should add a BAR evidence ledger using existing artifacts only.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "adds_host_app_target": False,
            "adds_driverkit_dext_target": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "ossystemextensionmanager_submit_request": False,
            "iopcidevice_ownership_request": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission": False,
            "queue_programming": False,
            "doorbell_interaction": False,
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
    phase_rows = []
    for item in data["dry_run_phases"]:
        checks = "<br>".join(item["checks"])
        phase_rows.append(
            f"| `{item['phase']}` | {item['name']} | `{item['status']}` | `{item['current_stage_action']}` | {checks} |"
        )

    criteria_rows = []
    for item in data["go_no_go_criteria"]:
        criteria_rows.append(
            f"| {item['criterion']} | `{item['required_for_activation']}` | `{item['current_result']}` | `{item['decision']}` |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# DriverKit Dry-run Checklist",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Dry-run checklist ready: `{data['dry_run_checklist_ready']}`",
            "",
            f"DriverKit activation allowed: `{data['driverkit_activation_allowed']}`",
            "",
            f"System Extension request allowed: `{data['system_extension_request_allowed']}`",
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
            "## Dry-run Phases",
            "",
            "| Phase | Name | Status | Current Stage Action | Checks |",
            "| --- | --- | --- | --- | --- |",
            *phase_rows,
            "",
            "## Go / No-go Criteria",
            "",
            "| Criterion | Required For Activation | Current Result | Decision |",
            "| --- | --- | --- | --- |",
            *criteria_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This checklist is documentation-only.",
            "",
            "It does not add a host app target, add a DriverKit dext target, activate DriverKit, submit a System Extension activation request, submit a System Extension deactivation request, call OSSystemExtensionManager submit, request IOPCIDevice ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, run GPU reset logic, or start RTX 5070 Metal acceleration implementation.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX DriverKit dry-run checklist."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_checklist()

    json_path = out_dir / "driverkit-dry-run-checklist.json"
    md_path = out_dir / "driverkit-dry-run-checklist.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
