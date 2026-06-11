#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.recovery_rollback_runbook.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

RECOVERY_SCENARIOS = [
    {
        "id": "RR-001",
        "scenario": "System Extension activation failure",
        "risk_level": "MEDIUM",
        "current_stage_applicability": "DESIGN_ONLY",
        "symptoms": [
            "activation request rejected",
            "user approval not completed",
            "extension remains inactive",
        ],
        "rollback_strategy": [
            "do not retry repeatedly without reading logs",
            "document activation status",
            "remove or disable the test build in a future approved dry-run stage",
            "return to last known-good main branch",
        ],
        "required_before_hardware_experiment": True,
    },
    {
        "id": "RR-002",
        "scenario": "DriverKit dext load or match failure",
        "risk_level": "HIGH",
        "current_stage_applicability": "FUTURE_ONLY",
        "symptoms": [
            "driver does not match provider",
            "driver fails to start",
            "provider match is incorrect",
        ],
        "rollback_strategy": [
            "keep dext disabled",
            "do not request IOPCIDevice ownership",
            "restore previous signed build",
            "capture logs only after a reviewed dry-run plan exists",
        ],
        "required_before_hardware_experiment": True,
    },
    {
        "id": "RR-003",
        "scenario": "Incorrect PCI provider match",
        "risk_level": "CRITICAL",
        "current_stage_applicability": "FUTURE_ONLY",
        "symptoms": [
            "wrong PCI device matched",
            "unexpected device ownership",
            "driver attaches to non-target hardware",
        ],
        "rollback_strategy": [
            "block activation",
            "require exact vendor and device identity checks",
            "require subsystem identity checks",
            "require a no-attach dry-run review before any matching test",
        ],
        "required_before_hardware_experiment": True,
    },
    {
        "id": "RR-004",
        "scenario": "GPU hang or command timeout",
        "risk_level": "CRITICAL",
        "current_stage_applicability": "FORBIDDEN_CURRENTLY",
        "symptoms": [
            "display freeze",
            "kernel panic",
            "system unresponsive",
            "GPU does not complete work",
        ],
        "rollback_strategy": [
            "do not attempt this scenario in current stages",
            "require command timeout policy before any command submission",
            "require reboot and power-cycle procedure",
            "require safe-mode or recovery boot notes",
        ],
        "required_before_hardware_experiment": True,
    },
    {
        "id": "RR-005",
        "scenario": "BAR or MMIO side effect",
        "risk_level": "CRITICAL",
        "current_stage_applicability": "FORBIDDEN_CURRENTLY",
        "symptoms": [
            "device state changes unexpectedly",
            "system instability",
            "device no longer responds",
        ],
        "rollback_strategy": [
            "do not map BAR memory in current stages",
            "do not perform MMIO reads or writes",
            "require BAR role evidence before any exception proposal",
            "require full recovery checklist before any hardware-facing branch",
        ],
        "required_before_hardware_experiment": True,
    },
    {
        "id": "RR-006",
        "scenario": "Firmware or GSP state failure",
        "risk_level": "CRITICAL",
        "current_stage_applicability": "FORBIDDEN_CURRENTLY",
        "symptoms": [
            "firmware load failure",
            "GSP initialization failure",
            "device becomes unstable",
        ],
        "rollback_strategy": [
            "keep firmware loading forbidden",
            "keep GSP initialization forbidden",
            "do not include firmware blobs",
            "require separate reviewed firmware boundary before any work",
        ],
        "required_before_hardware_experiment": True,
    },
    {
        "id": "RR-007",
        "scenario": "Display or framebuffer disruption",
        "risk_level": "CRITICAL",
        "current_stage_applicability": "FORBIDDEN_CURRENTLY",
        "symptoms": [
            "screen loss",
            "display mode corruption",
            "framebuffer ownership conflict",
        ],
        "rollback_strategy": [
            "keep display engine work out of early Metal research",
            "do not initialize framebuffer",
            "do not perform scanout experiments",
            "separate display bring-up from compute and Metal planning",
        ],
        "required_before_hardware_experiment": True,
    },
]

PREFLIGHT_CHECKLIST = [
    {
        "id": "PF-001",
        "item": "working tree clean",
        "required": True,
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "id": "PF-002",
        "item": "latest main pulled",
        "required": True,
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "id": "PF-003",
        "item": "BAR safety gates passing",
        "required": True,
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "id": "PF-004",
        "item": "forbidden operation audit passing",
        "required": True,
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "id": "PF-005",
        "item": "recovery boot path documented",
        "required": True,
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "id": "PF-006",
        "item": "rollback branch and tag known",
        "required": True,
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "id": "PF-007",
        "item": "no hardware-facing code in current PR",
        "required": True,
        "current_stage_action": "ENFORCED_BY_SCOPE",
    },
]

ROLLBACK_LEVELS = [
    {
        "level": "L0",
        "name": "No-op rollback",
        "trigger": "documentation-only PR has local generated artifacts",
        "actions": [
            "remove generated local reports",
            "remove __pycache__ directories",
            "confirm git status is clean",
        ],
    },
    {
        "level": "L1",
        "name": "Branch rollback",
        "trigger": "bad research branch or failed PR checks",
        "actions": [
            "switch back to main",
            "pull latest origin/main",
            "delete or reset the research branch if needed",
        ],
    },
    {
        "level": "L2",
        "name": "Release tag rollback",
        "trigger": "incorrect stage tag or release metadata",
        "actions": [
            "verify tag target",
            "avoid deleting published tags unless absolutely necessary",
            "create corrected follow-up tag or PR when possible",
        ],
    },
    {
        "level": "L3",
        "name": "System Extension rollback",
        "trigger": "future dry-run activation issue",
        "actions": [
            "do not apply in current stage",
            "requires future reviewed deactivation checklist",
            "requires host app and dext identity tracking",
        ],
    },
    {
        "level": "L4",
        "name": "Hardware experiment rollback",
        "trigger": "future hardware-facing experiment failure",
        "actions": [
            "forbidden in current stage",
            "requires reboot and power-cycle runbook",
            "requires panic/log capture policy",
            "requires documented safe-mode or recovery boot procedure",
        ],
    },
]

FORBIDDEN_NOW = [
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission",
    "queue or ring programming",
    "doorbell interaction",
    "RTX 5070 resource allocation",
    "VRAM residency experiments",
    "device address programming",
    "page table creation",
    "private graphics framework patching",
    "DriverKit activation",
    "System Extension activation request",
    "IOPCIDevice ownership request",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_runbook() -> dict[str, Any]:
    required_scenarios = [
        item for item in RECOVERY_SCENARIOS
        if item["required_before_hardware_experiment"]
    ]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "RECOVERY_ROLLBACK_RUNBOOK_READY",
        "full_metal_goal": True,
        "research_continues": True,
        "implementation_allowed": False,
        "implementation_started": False,
        "hardware_experiment_allowed": False,
        "required_recovery_scenario_count": len(required_scenarios),
        "preflight_checklist": PREFLIGHT_CHECKLIST,
        "recovery_scenarios": RECOVERY_SCENARIOS,
        "rollback_levels": ROLLBACK_LEVELS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 23 should add a DriverKit dry-run checklist without activation.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "uses_existing_system_metal_device_only_for_validation": True,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission": False,
            "queue_programming": False,
            "doorbell_interaction": False,
            "resource_allocation_on_rtx5070": False,
            "vram_residency_experiments": False,
            "device_address_programming": False,
            "page_table_creation": False,
            "private_graphics_framework_patching": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "iopcidevice_ownership_request": False,
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
    preflight_rows = []
    for item in data["preflight_checklist"]:
        preflight_rows.append(
            f"| `{item['id']}` | {item['item']} | `{item['required']}` | `{item['current_stage_action']}` |"
        )

    scenario_rows = []
    for item in data["recovery_scenarios"]:
        symptoms = "<br>".join(item["symptoms"])
        strategy = "<br>".join(item["rollback_strategy"])
        scenario_rows.append(
            f"| `{item['id']}` | {item['scenario']} | `{item['risk_level']}` | `{item['current_stage_applicability']}` | {symptoms} | {strategy} | `{item['required_before_hardware_experiment']}` |"
        )

    rollback_rows = []
    for item in data["rollback_levels"]:
        actions = "<br>".join(item["actions"])
        rollback_rows.append(
            f"| `{item['level']}` | {item['name']} | {item['trigger']} | {actions} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Recovery and Rollback Runbook",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Implementation allowed: `{data['implementation_allowed']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
            "",
            f"Hardware experiment allowed: `{data['hardware_experiment_allowed']}`",
            "",
            f"Required recovery scenario count: `{data['required_recovery_scenario_count']}`",
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
            "## Preflight Checklist",
            "",
            "| ID | Item | Required | Current Stage Action |",
            "| --- | --- | --- | --- |",
            *preflight_rows,
            "",
            "## Recovery Scenarios",
            "",
            "| ID | Scenario | Risk | Applicability | Symptoms | Rollback Strategy | Required Before Hardware Experiment |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *scenario_rows,
            "",
            "## Rollback Levels",
            "",
            "| Level | Name | Trigger | Actions |",
            "| --- | --- | --- | --- |",
            *rollback_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This runbook is documentation-only.",
            "",
            "It does not start RTX 5070 Metal acceleration implementation, execute RTX 5070 shaders, submit hardware commands, program queues or rings, interact with doorbells, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, patch private graphics frameworks, activate DriverKit, submit a System Extension activation request, request IOPCIDevice ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX recovery and rollback runbook."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_runbook()

    json_path = out_dir / "recovery-rollback-runbook.json"
    md_path = out_dir / "recovery-rollback-runbook.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
