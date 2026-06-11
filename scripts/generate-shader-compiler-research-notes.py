#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.shader_compiler_research_notes.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

PUBLIC_METAL_SHADER_LAYER = [
    {
        "area": "Metal Shading Language source",
        "status": "PUBLIC_APP_LAYER",
        "current_use": "Stage 15 validation harness shader source",
        "research_value": "Defines the app-facing shader input language used by public Metal workflows.",
        "rtx5070_execution": False,
    },
    {
        "area": "Metal shader library",
        "status": "PUBLIC_APP_LAYER",
        "current_use": "Default library or precompiled library for existing system Metal devices",
        "research_value": "Documents how public Metal apps package shader functions.",
        "rtx5070_execution": False,
    },
    {
        "area": "Metal function lookup",
        "status": "PUBLIC_APP_LAYER",
        "current_use": "Lookup validation kernel by name",
        "research_value": "Documents the public app-layer function selection point.",
        "rtx5070_execution": False,
    },
    {
        "area": "Compute pipeline creation",
        "status": "PUBLIC_APP_LAYER",
        "current_use": "Create pipeline against existing system Metal device",
        "research_value": "Separates app-layer pipeline validation from hardware compiler strategy.",
        "rtx5070_execution": False,
    },
]

COMPILER_RESEARCH_AREAS = [
    {
        "area": "source language boundary",
        "state": "RESEARCH_NOTE_ONLY",
        "known": True,
        "description": "MSL is the public shader authoring layer used by Metal apps.",
        "required_before_implementation": [
            "define which shader subset the project can validate",
            "define compute-only versus graphics shader scope",
            "define unsupported language features for early research",
        ],
    },
    {
        "area": "intermediate representation strategy",
        "state": "UNKNOWN_FOR_RTX5070_PATH",
        "known": False,
        "description": "The project has not defined an IR path from MSL or another representation to RTX 5070 execution.",
        "required_before_implementation": [
            "document candidate IR layers",
            "document legal and technical constraints",
            "keep all translation off-device until reviewed",
        ],
    },
    {
        "area": "target instruction strategy",
        "state": "UNKNOWN_FOR_TARGET",
        "known": False,
        "description": "No RTX 5070 executable shader instruction strategy exists in this repository.",
        "required_before_implementation": [
            "document target ISA research boundaries",
            "document what must remain out of scope",
            "avoid hardware execution until command and memory models exist",
        ],
    },
    {
        "area": "pipeline metadata strategy",
        "state": "PLACEHOLDER_ONLY",
        "known": False,
        "description": "Real Metal pipelines require more than shader code, including resource binding and capability metadata.",
        "required_before_implementation": [
            "define resource binding model",
            "define pipeline state metadata model",
            "cross-check with memory manager placeholder",
        ],
    },
    {
        "area": "validation strategy",
        "state": "PUBLIC_DEVICE_ONLY",
        "known": True,
        "description": "Validation can run on the existing system Metal device through Stage 15 harnesses.",
        "required_before_implementation": [
            "keep reference outputs deterministic",
            "record shader inputs and outputs",
            "avoid RTX 5070 execution claims",
        ],
    },
]

SHADER_RESEARCH_GATES = [
    {
        "gate": "SCG-1",
        "name": "public MSL validation harness",
        "status": "ALLOWED",
        "description": "Continue testing small shaders on the existing system Metal device only.",
    },
    {
        "gate": "SCG-2",
        "name": "shader subset definition",
        "status": "ALLOWED_DOCUMENTATION_ONLY",
        "description": "Document a small shader subset for future research.",
    },
    {
        "gate": "SCG-3",
        "name": "IR strategy notes",
        "status": "RESEARCH_ONLY",
        "description": "Document possible intermediate representation approaches without implementation claims.",
    },
    {
        "gate": "SCG-4",
        "name": "target executable strategy",
        "status": "BLOCKED_UNTIL_COMMAND_MEMORY_MODELS",
        "description": "No target execution strategy until command processor and memory manager research is mature.",
    },
    {
        "gate": "SCG-5",
        "name": "RTX 5070 shader execution",
        "status": "FORBIDDEN_CURRENTLY",
        "description": "No RTX 5070 shader execution in this stage.",
    },
]

FORBIDDEN_NOW = [
    "RTX 5070 shader execution",
    "RTX 5070 Metal acceleration attempt",
    "hardware command submission",
    "queue or ring programming",
    "doorbell interaction",
    "resource allocation on RTX 5070",
    "VRAM residency experiments",
    "device address programming",
    "page table creation",
    "private graphics framework patching",
    "DriverKit activation",
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
]


def build_notes() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "SHADER_COMPILER_RESEARCH_NOTES_READY",
        "full_metal_goal": True,
        "implementation_started": False,
        "rtx5070_shader_execution_allowed": False,
        "public_system_metal_shader_validation_allowed": True,
        "public_metal_shader_layer": PUBLIC_METAL_SHADER_LAYER,
        "compiler_research_areas": COMPILER_RESEARCH_AREAS,
        "shader_research_gates": SHADER_RESEARCH_GATES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 20 should evaluate whether the project is ready for a real implementation decision or must remain in research-only mode.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "uses_existing_system_metal_device_only_for_validation": True,
            "rtx5070_shader_execution": False,
            "rtx5070_metal_acceleration_attempt": False,
            "hardware_command_submission": False,
            "queue_programming": False,
            "doorbell_interaction": False,
            "resource_allocation_on_rtx5070": False,
            "vram_residency_experiments": False,
            "device_address_programming": False,
            "page_table_creation": False,
            "private_graphics_framework_patching": False,
            "driverkit_activation": False,
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
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    public_rows = []
    for item in data["public_metal_shader_layer"]:
        public_rows.append(
            f"| {item['area']} | `{item['status']}` | {item['current_use']} | {item['research_value']} | `{item['rtx5070_execution']}` |"
        )

    research_rows = []
    for item in data["compiler_research_areas"]:
        required = ", ".join(item["required_before_implementation"])
        research_rows.append(
            f"| {item['area']} | `{item['state']}` | `{item['known']}` | {item['description']} | {required} |"
        )

    gate_rows = []
    for item in data["shader_research_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | {item['name']} | `{item['status']}` | {item['description']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Off-device Shader and Compiler Research Notes",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
            "",
            f"RTX 5070 shader execution allowed: `{data['rtx5070_shader_execution_allowed']}`",
            "",
            f"Public system Metal shader validation allowed: `{data['public_system_metal_shader_validation_allowed']}`",
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
            "## Public Metal Shader Layer",
            "",
            "| Area | Status | Current Use | Research Value | RTX 5070 Execution |",
            "| --- | --- | --- | --- | --- |",
            *public_rows,
            "",
            "## Compiler Research Areas",
            "",
            "| Area | State | Known | Description | Required Before Implementation |",
            "| --- | --- | --- | --- | --- |",
            *research_rows,
            "",
            "## Shader Research Gates",
            "",
            "| Gate | Name | Status | Description |",
            "| --- | --- | --- | --- |",
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
            "It allows shader validation only on the existing system Metal device through public Metal app-layer APIs.",
            "",
            "It does not execute shaders on RTX 5070, attempt RTX 5070 Metal acceleration, submit hardware commands, program queues or rings, interact with doorbells, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, patch private graphics frameworks, activate DriverKit, request IOPCIDevice ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, load firmware, initialize GSP, initialize display engine, or initialize framebuffer.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX off-device shader and compiler research notes."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_notes()

    json_path = out_dir / "shader-compiler-research-notes.json"
    md_path = out_dir / "shader-compiler-research-notes.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
