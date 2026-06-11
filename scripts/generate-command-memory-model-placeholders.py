#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.command_memory_model_placeholders.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

COMMAND_MODEL = [
    {
        "area": "command submission entrypoint",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "documented queue ownership model",
            "documented command packet format",
            "documented submit doorbell or equivalent mechanism",
            "documented failure and recovery path",
        ],
        "forbidden_currently": [
            "hardware command submission",
            "queue programming",
            "doorbell interaction",
            "device execution experiments",
        ],
        "notes": "Metal command buffers exist at the public app layer, but the RTX 5070 hardware command path is not documented in this project.",
    },
    {
        "area": "queue or ring model",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "queue memory layout",
            "producer and consumer ownership",
            "wraparound semantics",
            "submission ordering rules",
        ],
        "forbidden_currently": [
            "queue allocation on the RTX 5070",
            "ring pointer updates",
            "hardware scheduling experiments",
        ],
        "notes": "No queue or ring role is assigned until BAR roles and execution semantics are known.",
    },
    {
        "area": "fence and completion model",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "fence memory location",
            "completion write semantics",
            "timeout policy",
            "error reporting path",
        ],
        "forbidden_currently": [
            "live fence polling",
            "completion waits on RTX 5070",
            "timeout-triggered reset experiments",
        ],
        "notes": "Completion semantics must be known before any real workload can be considered.",
    },
    {
        "area": "interrupt and event model",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "interrupt source documentation",
            "event mask documentation",
            "safe disable and acknowledge rules",
            "panic and recovery handling",
        ],
        "forbidden_currently": [
            "interrupt enablement",
            "event mask programming",
            "acknowledge path experiments",
        ],
        "notes": "No interrupt path is enabled or requested in this stage.",
    },
]

MEMORY_MODEL = [
    {
        "area": "resource allocation",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "VRAM allocation model",
            "system memory sharing model",
            "alignment requirements",
            "lifetime ownership rules",
        ],
        "forbidden_currently": [
            "RTX 5070 resource allocation",
            "VRAM residency experiments",
            "device-backed buffer placement",
        ],
        "notes": "Public Metal resources are validated only on the existing system Metal device.",
    },
    {
        "area": "buffer residency",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "buffer placement policy",
            "residency tracking",
            "eviction behavior",
            "synchronization with CPU-visible memory",
        ],
        "forbidden_currently": [
            "device residency experiments",
            "manual residency updates",
            "device-backed buffer execution",
        ],
        "notes": "No RTX 5070 buffer residency model exists yet.",
    },
    {
        "area": "texture residency",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "texture layout rules",
            "tiling or swizzle model",
            "format capability matrix",
            "copy and synchronization rules",
        ],
        "forbidden_currently": [
            "RTX 5070 texture allocation",
            "texture layout experiments",
            "device sampling experiments",
        ],
        "notes": "Texture handling remains an app-layer validation topic only until hardware layout is documented.",
    },
    {
        "area": "address translation",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "GPU virtual address model",
            "page table ownership",
            "mapping granularity",
            "fault handling and recovery",
        ],
        "forbidden_currently": [
            "page table creation",
            "device address programming",
            "fault generation experiments",
        ],
        "notes": "Address translation is a hard blocker for real acceleration.",
    },
    {
        "area": "cache and coherency",
        "current_state": "PLACEHOLDER_ONLY",
        "known": False,
        "required_before_implementation": [
            "CPU and GPU coherency rules",
            "flush and invalidate policy",
            "resource hazard tracking",
            "barrier semantics",
        ],
        "forbidden_currently": [
            "cache management experiments",
            "manual coherency operations",
            "device barrier programming",
        ],
        "notes": "Coherency behavior must be documented before shared resource execution.",
    },
]

VALIDATION_GATES = [
    {
        "gate": "CMG-1",
        "name": "public Metal harness remains passing",
        "status": "ALLOWED",
        "description": "Continue validating public Metal workloads only on the existing system Metal device.",
    },
    {
        "gate": "CMG-2",
        "name": "command path documentation",
        "status": "BLOCKED_UNTIL_EVIDENCE",
        "description": "No command submission until command packet, queue, fence, and recovery semantics are documented.",
    },
    {
        "gate": "CMG-3",
        "name": "memory model documentation",
        "status": "BLOCKED_UNTIL_EVIDENCE",
        "description": "No resource residency work until allocation, address translation, and coherency are documented.",
    },
    {
        "gate": "CMG-4",
        "name": "cross-check against BAR role plan",
        "status": "BLOCKED_UNTIL_STAGE17_EVIDENCE",
        "description": "Command and memory placeholders must not assign hardware roles before BAR roles are known.",
    },
    {
        "gate": "CMG-5",
        "name": "implementation decision",
        "status": "FUTURE_STAGE_ONLY",
        "description": "Real acceleration implementation remains blocked until Stage 20 or later.",
    },
]

FORBIDDEN_NOW = [
    "hardware command submission",
    "queue or ring programming",
    "doorbell interaction",
    "fence polling on RTX 5070",
    "interrupt enablement",
    "resource allocation on RTX 5070",
    "VRAM residency experiments",
    "device address programming",
    "page table creation",
    "cache management experiments",
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
    "DriverKit activation",
    "IOPCIDevice ownership request",
    "RTX 5070 Metal acceleration attempt",
]


def build_model() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "COMMAND_MEMORY_MODEL_PLACEHOLDERS_READY",
        "full_metal_goal": True,
        "implementation_started": False,
        "command_submission_allowed": False,
        "resource_residency_work_allowed": False,
        "command_model": COMMAND_MODEL,
        "memory_model": MEMORY_MODEL,
        "validation_gates": VALIDATION_GATES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 19 should add off-device shader and compiler research notes without RTX 5070 execution.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "uses_existing_system_metal_device_only_for_validation": True,
            "hardware_command_submission": False,
            "queue_programming": False,
            "doorbell_interaction": False,
            "fence_polling_on_rtx5070": False,
            "interrupt_enablement": False,
            "resource_allocation_on_rtx5070": False,
            "vram_residency_experiments": False,
            "device_address_programming": False,
            "page_table_creation": False,
            "cache_management_experiments": False,
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
            "iopcidevice_ownership_request": False,
            "rtx5070_metal_acceleration_attempt": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    command_rows = []
    for item in data["command_model"]:
        required = ", ".join(item["required_before_implementation"])
        forbidden = ", ".join(item["forbidden_currently"])
        command_rows.append(
            f"| {item['area']} | `{item['current_state']}` | `{item['known']}` | {required} | {forbidden} | {item['notes']} |"
        )

    memory_rows = []
    for item in data["memory_model"]:
        required = ", ".join(item["required_before_implementation"])
        forbidden = ", ".join(item["forbidden_currently"])
        memory_rows.append(
            f"| {item['area']} | `{item['current_state']}` | `{item['known']}` | {required} | {forbidden} | {item['notes']} |"
        )

    gate_rows = []
    for item in data["validation_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | {item['name']} | `{item['status']}` | {item['description']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Command Processor and Memory Manager Placeholders",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
            "",
            f"Command submission allowed: `{data['command_submission_allowed']}`",
            "",
            f"Resource residency work allowed: `{data['resource_residency_work_allowed']}`",
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
            "## Command Model Placeholders",
            "",
            "| Area | State | Known | Required Before Implementation | Forbidden Currently | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
            *command_rows,
            "",
            "## Memory Model Placeholders",
            "",
            "| Area | State | Known | Required Before Implementation | Forbidden Currently | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
            *memory_rows,
            "",
            "## Validation Gates",
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
            "It does not submit hardware commands, program queues or rings, interact with doorbells, poll RTX 5070 fences, enable interrupts, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, run cache management experiments, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, run GPU reset logic, load firmware, initialize GSP, initialize display engine, initialize framebuffer, activate DriverKit, request IOPCIDevice ownership, or attempt RTX 5070 Metal acceleration.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX command processor and memory manager placeholders."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_model()

    json_path = out_dir / "command-memory-model-placeholders.json"
    md_path = out_dir / "command-memory-model-placeholders.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
