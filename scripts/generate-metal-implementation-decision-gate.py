#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_implementation_decision_gate.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

INPUT_STAGES = [
    {
        "stage": "Stage 13",
        "name": "Metal feasibility boundary",
        "state": "COMPLETE",
        "result": "Planning started, implementation not started.",
    },
    {
        "stage": "Stage 14",
        "name": "macOS graphics stack architecture map",
        "state": "COMPLETE",
        "result": "Architecture layers mapped; implementation still blocked.",
    },
    {
        "stage": "Stage 15",
        "name": "Metal validation harness skeleton",
        "state": "COMPLETE",
        "result": "Public Metal app-layer harness exists for the existing system Metal device only.",
    },
    {
        "stage": "Stage 16",
        "name": "DriverKit activation design review",
        "state": "COMPLETE",
        "result": "Design only; no activation, no host app target, no dext target.",
    },
    {
        "stage": "Stage 17",
        "name": "BAR role research plan",
        "state": "COMPLETE",
        "result": "BAR roles remain UNKNOWN; no BAR access allowed.",
    },
    {
        "stage": "Stage 18",
        "name": "Command and memory model placeholders",
        "state": "COMPLETE",
        "result": "Command and memory models are placeholders only.",
    },
    {
        "stage": "Stage 19",
        "name": "Shader and compiler research notes",
        "state": "COMPLETE",
        "result": "Shader/compiler notes exist; no RTX 5070 execution allowed.",
    },
]

READINESS_CHECKS = [
    {
        "area": "Metal device exposure path",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "No verified public path in this repository for exposing RTX 5070 as a macOS Metal device.",
        "next_action": "Continue graphics stack integration research.",
    },
    {
        "area": "DriverKit activation",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Stage 16 is design-only and does not add a host app, dext, provisioning profile, activation request, or device ownership.",
        "next_action": "Create a later dry-run design only after entitlement/provisioning evidence exists.",
    },
    {
        "area": "BAR roles",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Stage 17 keeps BAR0 through BAR5 and ROM as UNKNOWN.",
        "next_action": "Collect non-invasive evidence and keep BAR access denied.",
    },
    {
        "area": "Command submission",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Stage 18 defines placeholders only; no queue, ring, doorbell, fence, interrupt, or recovery semantics are known.",
        "next_action": "Continue command processor documentation without hardware submission.",
    },
    {
        "area": "Memory manager",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Stage 18 defines placeholders only; no resource allocation, residency, address translation, or coherency model exists.",
        "next_action": "Continue memory model documentation without RTX 5070 resource work.",
    },
    {
        "area": "Shader/compiler path",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Stage 19 documents research notes only; no RTX 5070 executable shader strategy exists.",
        "next_action": "Keep shader work off-device and public-system-Metal-only.",
    },
    {
        "area": "Firmware and GSP boundary",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Firmware loading and GSP initialization remain forbidden.",
        "next_action": "Do not start firmware work until a separate reviewed stage.",
    },
    {
        "area": "Display and framebuffer boundary",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "Display engine and framebuffer initialization remain forbidden.",
        "next_action": "Keep display bring-up separate from early Metal research.",
    },
    {
        "area": "Recovery plan",
        "status": "BLOCKED",
        "required_for_implementation": True,
        "evidence": "No approved recovery plan exists for failed hardware experiments.",
        "next_action": "Document rollback, reboot, panic capture, power-cycle, and safety procedures.",
    },
    {
        "area": "Public Metal validation harness",
        "status": "PASS",
        "required_for_implementation": False,
        "evidence": "Stage 15 public Metal validation harness exists for the existing system Metal device only.",
        "next_action": "Continue using it as a reference test harness.",
    },
]

NEXT_RESEARCH_TRACK = [
    {
        "stage": "Stage 21",
        "name": "Implementation blocker register",
        "purpose": "Create a tracked register of remaining blockers and required evidence.",
    },
    {
        "stage": "Stage 22",
        "name": "Recovery and rollback runbook",
        "purpose": "Document safety procedures before any future hardware experiment.",
    },
    {
        "stage": "Stage 23",
        "name": "DriverKit dry-run checklist",
        "purpose": "Design-only checklist for host app, dext, provisioning, signing, and user approval.",
    },
    {
        "stage": "Stage 24",
        "name": "BAR evidence ledger",
        "purpose": "Collect non-invasive evidence for BAR roles without mapping or probing.",
    },
    {
        "stage": "Stage 25",
        "name": "Metal reference workload suite",
        "purpose": "Expand public Metal validation workloads on existing system Metal devices.",
    },
]

FORBIDDEN_NOW = [
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission",
    "queue or ring programming",
    "doorbell interaction",
    "resource allocation on RTX 5070",
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


def build_gate() -> dict[str, Any]:
    blocked_required = [
        item for item in READINESS_CHECKS
        if item["required_for_implementation"] and item["status"] != "PASS"
    ]

    decision = "IMPLEMENTATION_NOT_READY_RESEARCH_CONTINUES"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": decision,
        "full_metal_goal": True,
        "research_track_started": True,
        "implementation_started": False,
        "implementation_allowed": False,
        "required_blocker_count": len(blocked_required),
        "input_stages": INPUT_STAGES,
        "readiness_checks": READINESS_CHECKS,
        "next_research_track": NEXT_RESEARCH_TRACK,
        "forbidden_now": FORBIDDEN_NOW,
        "summary": {
            "plain_answer": "Do not start real RTX 5070 Metal acceleration implementation yet. Continue the full Metal graphics acceleration research track.",
            "why": "Required driver, BAR, command, memory, shader, firmware, display, and recovery evidence is still missing.",
            "what_is_allowed": "Public Metal validation on the existing system Metal device and documentation-only research.",
        },
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
    input_rows = []
    for item in data["input_stages"]:
        input_rows.append(
            f"| {item['stage']} | {item['name']} | `{item['state']}` | {item['result']} |"
        )

    check_rows = []
    for item in data["readiness_checks"]:
        check_rows.append(
            f"| {item['area']} | `{item['status']}` | `{item['required_for_implementation']}` | {item['evidence']} | {item['next_action']} |"
        )

    next_rows = []
    for item in data["next_research_track"]:
        next_rows.append(
            f"| {item['stage']} | {item['name']} | {item['purpose']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Metal Implementation Decision Gate",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research track started: `{data['research_track_started']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
            "",
            f"Implementation allowed: `{data['implementation_allowed']}`",
            "",
            f"Required blocker count: `{data['required_blocker_count']}`",
            "",
            "## Plain Answer",
            "",
            data["summary"]["plain_answer"],
            "",
            "## Why",
            "",
            data["summary"]["why"],
            "",
            "## Allowed Now",
            "",
            data["summary"]["what_is_allowed"],
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
            "## Input Stages",
            "",
            "| Stage | Name | State | Result |",
            "| --- | --- | --- | --- |",
            *input_rows,
            "",
            "## Readiness Checks",
            "",
            "| Area | Status | Required For Implementation | Evidence | Next Action |",
            "| --- | --- | --- | --- | --- |",
            *check_rows,
            "",
            "## Next Research Track",
            "",
            "| Stage | Name | Purpose |",
            "| --- | --- | --- |",
            *next_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is documentation-only.",
            "",
            "It does not start RTX 5070 Metal acceleration implementation, execute RTX 5070 shaders, submit hardware commands, program queues or rings, interact with doorbells, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, patch private graphics frameworks, activate DriverKit, submit a System Extension activation request, request IOPCIDevice ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX Metal implementation decision gate."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_gate()

    json_path = out_dir / "metal-implementation-decision-gate.json"
    md_path = out_dir / "metal-implementation-decision-gate.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
