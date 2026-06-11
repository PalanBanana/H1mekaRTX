#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_feasibility_boundary.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

PUBLIC_APP_LAYER = [
    {
        "area": "Metal app API",
        "status": "PUBLIC_DOCUMENTED",
        "meaning": "Apps can use Metal through MTLDevice, command queues, command buffers, render encoders, compute encoders, buffers, textures, and shaders.",
        "impact": "Useful for test apps and validation harnesses, but it does not by itself make an RTX 5070 appear as a macOS Metal device.",
    },
    {
        "area": "Metal sample apps",
        "status": "PUBLIC_DOCUMENTED",
        "meaning": "Metal sample code can be used to build validation workloads.",
        "impact": "Useful after a GPU is visible to Metal, not sufficient for driver bring-up.",
    },
    {
        "area": "Metal developer tools",
        "status": "PUBLIC_DOCUMENTED",
        "meaning": "Xcode Metal tools can inspect shaders, captures, and performance when a Metal device exists.",
        "impact": "Useful later for validation, not a hardware enablement path.",
    },
]

DRIVER_LAYER_BLOCKERS = [
    {
        "area": "Metal GPU driver registration",
        "status": "BLOCKED_UNKNOWN_PRIVATE",
        "risk": "No public project-local proof that a third-party PCI GPU can be registered as a full macOS Metal device using public APIs only.",
        "required_before_work": "Document whether any public DriverKit, IOKit, or user-space extension path can expose a new Metal-capable GPU.",
    },
    {
        "area": "IOAccelerator / graphics stack integration",
        "status": "BLOCKED_UNKNOWN_PRIVATE",
        "risk": "Metal acceleration depends on macOS graphics stack integration beyond PCI enumeration.",
        "required_before_work": "Create a graphics stack architecture map and mark private or unsupported interfaces as off-limits.",
    },
    {
        "area": "Command processor",
        "status": "BLOCKED_UNDOCUMENTED_FOR_TARGET",
        "risk": "Submitting commands without a documented queue/ring/fence model can hang or wedge the GPU.",
        "required_before_work": "Document a read-only command submission model before any command processor interaction.",
    },
    {
        "area": "VRAM memory manager",
        "status": "BLOCKED_UNDOCUMENTED_FOR_TARGET",
        "risk": "Metal requires buffer/texture memory allocation, residency, synchronization, and lifetime management.",
        "required_before_work": "Document memory domains, page tables, BAR roles, and synchronization primitives.",
    },
    {
        "area": "Firmware / GSP",
        "status": "BLOCKED_FORBIDDEN",
        "risk": "Incorrect firmware or GSP initialization can destabilize the device or system.",
        "required_before_work": "Keep firmware loading and GSP initialization forbidden until a separate reviewed stage.",
    },
    {
        "area": "Display engine",
        "status": "BLOCKED_FORBIDDEN",
        "risk": "Display initialization can affect outputs, scanout, framebuffer ownership, and system display state.",
        "required_before_work": "Keep display engine work separate from compute/Metal planning.",
    },
    {
        "area": "Shader compiler / ISA",
        "status": "BLOCKED_UNDOCUMENTED_FOR_TARGET",
        "risk": "Metal shaders must ultimately map to hardware-specific execution code.",
        "required_before_work": "Document whether translation, compiler, or intermediate representation strategy is possible.",
    },
    {
        "area": "Synchronization",
        "status": "BLOCKED_UNDOCUMENTED_FOR_TARGET",
        "risk": "Fences, interrupts, events, and completion semantics are required for safe GPU command execution.",
        "required_before_work": "Document interrupt and fence model before command execution.",
    },
]

RESEARCH_SEQUENCE = [
    "Stage 13: Metal feasibility boundary",
    "Stage 14: macOS graphics stack architecture map",
    "Stage 15: Metal validation app skeleton using existing system Metal device only",
    "Stage 16: DriverKit entitlement and activation design review",
    "Stage 17: BAR role research plan, still no access",
    "Stage 18: command processor and memory manager documentation placeholder",
    "Stage 19: off-device shader/compiler research notes",
    "Stage 20: decide whether real Metal acceleration implementation is feasible",
]

FORBIDDEN_NOW = [
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "GPU reset logic",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "Metal acceleration attempts",
    "DriverKit activation",
    "IOAccelerator private interface usage",
    "private macOS graphics framework patching",
]


def build_boundary() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "NOT_READY_FOR_FULL_METAL_ACCELERATION",
        "metal_acceleration_start_gate": {
            "planning_started": True,
            "implementation_started": False,
            "earliest_implementation_stage": "Stage 20",
            "reason": "The project has not yet documented a public, safe, and complete path from PCI visibility to macOS Metal GPU registration, command submission, memory management, firmware state, synchronization, shader execution, and graphics stack integration.",
        },
        "public_app_layer": PUBLIC_APP_LAYER,
        "driver_layer_blockers": DRIVER_LAYER_BLOCKERS,
        "research_sequence": RESEARCH_SEQUENCE,
        "forbidden_now": FORBIDDEN_NOW,
        "safety_boundary": {
            "read_only": True,
            "calls_github_api": False,
            "creates_github_release": False,
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
            "metal_acceleration_attempt": False,
            "driverkit_activation": False,
        },
    }


def markdown_report(boundary: dict[str, Any]) -> str:
    public_rows = []
    for item in boundary["public_app_layer"]:
        public_rows.append(
            f"| {item['area']} | {item['status']} | {item['meaning']} | {item['impact']} |"
        )

    blocker_rows = []
    for item in boundary["driver_layer_blockers"]:
        blocker_rows.append(
            f"| {item['area']} | {item['status']} | {item['risk']} | {item['required_before_work']} |"
        )

    sequence_lines = [f"- {item}" for item in boundary["research_sequence"]]
    forbidden_lines = [f"- {item}" for item in boundary["forbidden_now"]]

    gate = boundary["metal_acceleration_start_gate"]

    return "\n".join(
        [
            "# Metal Acceleration Feasibility Boundary",
            "",
            f"Generated UTC: `{boundary['generated_at_utc']}`",
            "",
            f"Decision: `{boundary['decision']}`",
            "",
            "## Target",
            "",
            f"- GPU: `{boundary['target']['gpu']}`",
            f"- Vendor ID: `{boundary['target']['vendor_id']}`",
            f"- Device ID: `{boundary['target']['device_id']}`",
            f"- IOPCIMatch: `{boundary['target']['iopcimatch']}`",
            f"- Subsystem Vendor ID: `{boundary['target']['subsystem_vendor_id']}`",
            f"- Subsystem ID: `{boundary['target']['subsystem_id']}`",
            "",
            "## Metal Acceleration Start Gate",
            "",
            f"- Planning started: `{gate['planning_started']}`",
            f"- Implementation started: `{gate['implementation_started']}`",
            f"- Earliest implementation stage: `{gate['earliest_implementation_stage']}`",
            f"- Reason: {gate['reason']}",
            "",
            "## Public App Layer",
            "",
            "| Area | Status | Meaning | Impact |",
            "| --- | --- | --- | --- |",
            *public_rows,
            "",
            "## Driver Layer Blockers",
            "",
            "| Area | Status | Risk | Required Before Work |",
            "| --- | --- | --- | --- |",
            *blocker_rows,
            "",
            "## Research Sequence",
            "",
            *sequence_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This feasibility boundary is read-only.",
            "",
            "It does not run ioreg, system_profiler, PCI config-space reads, PCI config-space writes, MMIO reads, MMIO writes, BAR memory mapping, BAR memory poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, DriverKit activation, private graphics framework patching, or IOAccelerator private interface usage.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the H1mekaRTX Metal acceleration feasibility boundary."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    boundary = build_boundary()

    json_path = out_dir / "metal-feasibility-boundary.json"
    md_path = out_dir / "metal-feasibility-boundary.md"

    json_path.write_text(json.dumps(boundary, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(boundary) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {boundary['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
