#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.implementation_blocker_register.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

BLOCKERS = [
    {
        "id": "IB-001",
        "area": "Metal device exposure",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "MISSING",
        "problem": "No verified public path exists in this repository to expose RTX 5070 as an app-visible macOS Metal device.",
        "required_evidence": [
            "public API or documented architecture path",
            "clear distinction between app-visible Metal device and PCI device ownership",
            "proof that the path does not rely on private framework patching",
        ],
        "next_action": "Continue graphics stack integration research.",
    },
    {
        "id": "IB-002",
        "area": "DriverKit activation",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "DESIGN_ONLY",
        "problem": "DriverKit activation is still design-only and no host app, dext target, provisioning profile, or activation request exists.",
        "required_evidence": [
            "approved entitlement evidence",
            "host app design",
            "driver extension design",
            "signing and provisioning plan",
            "user approval flow",
        ],
        "next_action": "Stage 23 should create a DriverKit dry-run checklist without activation.",
    },
    {
        "id": "IB-003",
        "area": "BAR role evidence",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "UNKNOWN",
        "problem": "BAR0 through BAR5 and ROM roles remain unknown.",
        "required_evidence": [
            "non-invasive BAR role evidence",
            "BAR pairing hypotheses",
            "clear confidence levels",
            "no live BAR mapping",
        ],
        "next_action": "Stage 24 should create a BAR evidence ledger using existing artifacts only.",
    },
    {
        "id": "IB-004",
        "area": "Command processor model",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "PLACEHOLDER_ONLY",
        "problem": "Queue, ring, doorbell, fence, interrupt, completion, and recovery semantics are not documented.",
        "required_evidence": [
            "command submission entrypoint",
            "queue or ring model",
            "fence and completion model",
            "interrupt and event model",
            "timeout and recovery model",
        ],
        "next_action": "Continue documentation-only command processor research.",
    },
    {
        "id": "IB-005",
        "area": "Memory manager model",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "PLACEHOLDER_ONLY",
        "problem": "Resource allocation, residency, address translation, page tables, and coherency remain undocumented for RTX 5070.",
        "required_evidence": [
            "allocation model",
            "buffer residency model",
            "texture residency model",
            "address translation model",
            "cache and coherency model",
        ],
        "next_action": "Continue documentation-only memory manager research.",
    },
    {
        "id": "IB-006",
        "area": "Shader and compiler path",
        "severity": "HIGH",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "RESEARCH_ONLY",
        "problem": "No RTX 5070 executable shader strategy exists.",
        "required_evidence": [
            "source language boundary",
            "intermediate representation strategy",
            "target instruction strategy",
            "pipeline metadata strategy",
            "validation strategy",
        ],
        "next_action": "Keep shader/compiler research off-device.",
    },
    {
        "id": "IB-007",
        "area": "Firmware and GSP boundary",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "FORBIDDEN",
        "problem": "Firmware loading and GSP initialization remain forbidden and unplanned.",
        "required_evidence": [
            "separate reviewed firmware boundary",
            "safe source provenance policy",
            "rollback and recovery plan",
            "no firmware loading in current track",
        ],
        "next_action": "Do not start firmware work in this track.",
    },
    {
        "id": "IB-008",
        "area": "Display and framebuffer boundary",
        "severity": "HIGH",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "FORBIDDEN",
        "problem": "Display engine and framebuffer initialization remain forbidden.",
        "required_evidence": [
            "separate display boundary",
            "scanout ownership model",
            "framebuffer safety model",
            "rollback plan",
        ],
        "next_action": "Keep display work separate from early Metal research.",
    },
    {
        "id": "IB-009",
        "area": "Recovery and rollback",
        "severity": "CRITICAL",
        "status": "OPEN",
        "blocks_implementation": True,
        "evidence_state": "MISSING",
        "problem": "No approved recovery runbook exists for failed hardware experiments.",
        "required_evidence": [
            "panic capture procedure",
            "reboot and power-cycle procedure",
            "driver unload or disable procedure",
            "safe-mode recovery procedure",
            "rollback checklist",
        ],
        "next_action": "Stage 22 should create a recovery and rollback runbook.",
    },
    {
        "id": "IB-010",
        "area": "Public Metal reference workloads",
        "severity": "MEDIUM",
        "status": "OPEN",
        "blocks_implementation": False,
        "evidence_state": "PARTIAL",
        "problem": "Only a minimal vector-add Metal validation harness exists.",
        "required_evidence": [
            "more compute workloads",
            "basic render workload",
            "deterministic expected outputs",
            "JSON result schema",
        ],
        "next_action": "Stage 25 should expand public Metal reference workloads on the existing system Metal device.",
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


def build_register() -> dict[str, Any]:
    blocking_open = [
        item for item in BLOCKERS
        if item["blocks_implementation"] and item["status"] != "CLOSED"
    ]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "IMPLEMENTATION_BLOCKERS_REGISTERED",
        "full_metal_goal": True,
        "research_continues": True,
        "implementation_allowed": False,
        "implementation_started": False,
        "total_blocker_count": len(BLOCKERS),
        "open_required_blocker_count": len(blocking_open),
        "blockers": BLOCKERS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 22 should add a recovery and rollback runbook before any future hardware experiment.",
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
    rows = []
    for item in data["blockers"]:
        required = "<br>".join(item["required_evidence"])
        rows.append(
            f"| `{item['id']}` | {item['area']} | `{item['severity']}` | `{item['status']}` | `{item['blocks_implementation']}` | `{item['evidence_state']}` | {item['problem']} | {required} | {item['next_action']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Implementation Blocker Register",
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
            f"Total blocker count: `{data['total_blocker_count']}`",
            "",
            f"Open required blocker count: `{data['open_required_blocker_count']}`",
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
            "## Blockers",
            "",
            "| ID | Area | Severity | Status | Blocks Implementation | Evidence State | Problem | Required Evidence | Next Action |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This register is documentation-only.",
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
        description="Generate H1mekaRTX implementation blocker register."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_register()

    json_path = out_dir / "implementation-blocker-register.json"
    md_path = out_dir / "implementation-blocker-register.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
