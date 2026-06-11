#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.macos_graphics_stack_map.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

LAYERS = [
    {
        "layer": "Application validation layer",
        "public_status": "PUBLIC",
        "examples": [
            "Metal sample app",
            "MTLDevice enumeration",
            "command queue validation",
            "buffer and texture validation",
            "shader compilation validation",
        ],
        "role": "Build test workloads against an existing system Metal device.",
        "rtx5070_impact": "Does not expose RTX 5070 as a Metal device.",
        "stage": "Stage 15",
    },
    {
        "layer": "Metal API layer",
        "public_status": "PUBLIC",
        "examples": [
            "MTLDevice",
            "MTLCommandQueue",
            "MTLCommandBuffer",
            "MTLBuffer",
            "MTLTexture",
            "MTLLibrary",
        ],
        "role": "Public app-facing graphics and compute API.",
        "rtx5070_impact": "Can validate app-side Metal harnesses only after a Metal device exists.",
        "stage": "Stage 15+",
    },
    {
        "layer": "macOS graphics integration layer",
        "public_status": "UNKNOWN_OR_PRIVATE_FOR_THIRD_PARTY_GPU_ENABLEMENT",
        "examples": [
            "Metal device exposure",
            "graphics accelerator registration",
            "display and framebuffer ownership",
            "GPU capability publication",
        ],
        "role": "Bridge between hardware-backed graphics drivers and app-visible Metal devices.",
        "rtx5070_impact": "Major blocker for RTX 5070 Metal acceleration research.",
        "stage": "Stage 16+",
    },
    {
        "layer": "DriverKit PCI layer",
        "public_status": "PUBLIC_DRIVERKIT_BUT_NOT_METAL_ENABLEMENT",
        "examples": [
            "IOPCIDevice provider",
            "PCI configuration inventory",
            "PCI identity matching",
            "driver activation design",
        ],
        "role": "Public driver framework for PCI device management.",
        "rtx5070_impact": "Useful for PCI research, but does not by itself create a Metal GPU.",
        "stage": "Stage 16+",
    },
    {
        "layer": "BAR and aperture layer",
        "public_status": "BLOCKED_BY_DEFAULT_DENY_POLICY",
        "examples": [
            "BAR identity",
            "BAR size semantics",
            "aperture role mapping",
            "register offset inventory",
        ],
        "role": "Low-level device memory and register access area.",
        "rtx5070_impact": "Forbidden until BAR roles and register side effects are documented.",
        "stage": "Stage 17+",
    },
    {
        "layer": "GPU execution layer",
        "public_status": "UNDOCUMENTED_FOR_TARGET",
        "examples": [
            "command processor",
            "rings or queues",
            "fences",
            "interrupts",
            "completion events",
        ],
        "role": "Hardware command submission and synchronization.",
        "rtx5070_impact": "Required before any real acceleration attempt.",
        "stage": "Stage 18+",
    },
    {
        "layer": "Memory manager layer",
        "public_status": "UNDOCUMENTED_FOR_TARGET",
        "examples": [
            "VRAM allocation",
            "buffer residency",
            "texture residency",
            "page tables",
            "cache coherency",
        ],
        "role": "Resource allocation and residency for graphics and compute workloads.",
        "rtx5070_impact": "Required before Metal buffers and textures can map to RTX 5070 hardware.",
        "stage": "Stage 18+",
    },
    {
        "layer": "Shader and compiler layer",
        "public_status": "UNDOCUMENTED_FOR_TARGET",
        "examples": [
            "Metal shading language input",
            "intermediate representation",
            "target ISA strategy",
            "offline compiler research",
        ],
        "role": "Translate Metal workloads into hardware-executable code.",
        "rtx5070_impact": "Required before real Metal shader execution on RTX 5070.",
        "stage": "Stage 19+",
    },
    {
        "layer": "Firmware and GSP layer",
        "public_status": "FORBIDDEN_CURRENTLY",
        "examples": [
            "firmware loading",
            "GSP initialization",
            "firmware state validation",
        ],
        "role": "Device firmware state and management processor path.",
        "rtx5070_impact": "Forbidden until separately reviewed.",
        "stage": "Future separate track",
    },
    {
        "layer": "Display and framebuffer layer",
        "public_status": "FORBIDDEN_CURRENTLY",
        "examples": [
            "display engine",
            "scanout",
            "framebuffer ownership",
            "display mode setting",
        ],
        "role": "Display output and framebuffer presentation.",
        "rtx5070_impact": "Out of scope for early Metal research.",
        "stage": "Future separate track",
    },
]

HANDOFFS = [
    {
        "from": "Application validation layer",
        "to": "Metal API layer",
        "status": "SAFE_PUBLIC",
        "meaning": "A test app can exercise public Metal APIs on an existing system Metal device.",
    },
    {
        "from": "Metal API layer",
        "to": "macOS graphics integration layer",
        "status": "BLOCKED_RESEARCH_REQUIRED",
        "meaning": "No project-local proof that RTX 5070 can be exposed as an app-visible macOS Metal device.",
    },
    {
        "from": "macOS graphics integration layer",
        "to": "DriverKit PCI layer",
        "status": "BLOCKED_ARCHITECTURE_UNKNOWN",
        "meaning": "PCI driver ownership and app-visible Metal device exposure are not the same problem.",
    },
    {
        "from": "DriverKit PCI layer",
        "to": "BAR and aperture layer",
        "status": "BLOCKED_BY_DEFAULT_DENY_POLICY",
        "meaning": "BAR access remains denied until documented and reviewed.",
    },
    {
        "from": "BAR and aperture layer",
        "to": "GPU execution layer",
        "status": "BLOCKED_UNDOCUMENTED_TARGET",
        "meaning": "Command submission cannot start without queue, ring, fence, and recovery documentation.",
    },
    {
        "from": "GPU execution layer",
        "to": "Memory manager layer",
        "status": "BLOCKED_UNDOCUMENTED_TARGET",
        "meaning": "Buffers, textures, and residency require a documented memory model.",
    },
    {
        "from": "Memory manager layer",
        "to": "Shader and compiler layer",
        "status": "BLOCKED_UNDOCUMENTED_TARGET",
        "meaning": "Metal workloads need a safe shader and execution strategy.",
    },
]

RESEARCH_GATES = [
    {
        "gate": "G1",
        "name": "Public Metal validation harness",
        "earliest_stage": "Stage 15",
        "allowed": True,
        "description": "Build app-side tests using the existing system Metal device only.",
    },
    {
        "gate": "G2",
        "name": "DriverKit activation design",
        "earliest_stage": "Stage 16",
        "allowed": False,
        "description": "Design only; no activation until separately reviewed.",
    },
    {
        "gate": "G3",
        "name": "BAR role research",
        "earliest_stage": "Stage 17",
        "allowed": False,
        "description": "Research plan only; no BAR mapping or MMIO access.",
    },
    {
        "gate": "G4",
        "name": "Command processor and memory model",
        "earliest_stage": "Stage 18",
        "allowed": False,
        "description": "Documentation only; no command submission.",
    },
    {
        "gate": "G5",
        "name": "Shader/compiler research",
        "earliest_stage": "Stage 19",
        "allowed": False,
        "description": "Off-device notes only; no RTX 5070 execution.",
    },
    {
        "gate": "G6",
        "name": "Full Metal acceleration implementation decision",
        "earliest_stage": "Stage 20",
        "allowed": False,
        "description": "Decision gate for whether real implementation work can begin.",
    },
]


def build_map() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "GRAPHICS_STACK_RESEARCH_MAP_READY",
        "full_metal_goal": True,
        "implementation_started": False,
        "layers": LAYERS,
        "handoffs": HANDOFFS,
        "research_gates": RESEARCH_GATES,
        "safety_boundary": {
            "read_only": True,
            "metal_app_validation_allowed_on_existing_system_device": True,
            "rtx5070_metal_acceleration_attempt": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "driverkit_activation": False,
            "private_graphics_framework_patching": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    layer_rows = []
    for item in data["layers"]:
        examples = ", ".join(f"`{example}`" for example in item["examples"])
        layer_rows.append(
            f"| {item['layer']} | {item['public_status']} | {item['stage']} | {item['role']} | {item['rtx5070_impact']} | {examples} |"
        )

    handoff_rows = []
    for item in data["handoffs"]:
        handoff_rows.append(
            f"| {item['from']} | {item['to']} | {item['status']} | {item['meaning']} |"
        )

    gate_rows = []
    for item in data["research_gates"]:
        gate_rows.append(
            f"| {item['gate']} | {item['name']} | {item['earliest_stage']} | {item['allowed']} | {item['description']} |"
        )

    return "\n".join(
        [
            "# macOS Graphics Stack Architecture Map",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
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
            "## Layer Map",
            "",
            "| Layer | Public Status | Stage | Role | RTX 5070 Impact | Examples |",
            "| --- | --- | --- | --- | --- | --- |",
            *layer_rows,
            "",
            "## Handoff Map",
            "",
            "| From | To | Status | Meaning |",
            "| --- | --- | --- | --- |",
            *handoff_rows,
            "",
            "## Research Gates",
            "",
            "| Gate | Name | Earliest Stage | Currently Allowed | Description |",
            "| --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Safety Boundary",
            "",
            "This architecture map is read-only.",
            "",
            "It allows public Metal app validation only on an existing system Metal device.",
            "",
            "It does not attempt RTX 5070 Metal acceleration, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, run GPU reset logic, load firmware, initialize GSP, initialize display engine, initialize framebuffer, activate DriverKit, or patch private graphics frameworks.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the H1mekaRTX macOS graphics stack architecture map."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_map()

    json_path = out_dir / "macos-graphics-stack-map.json"
    md_path = out_dir / "macos-graphics-stack-map.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
