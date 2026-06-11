#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.bar_role_research_plan.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

BAR_SLOTS = [
    {
        "slot": "BAR0",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "Stage 3 OS-visible PCI inventory",
            "Stage 4 normalized summary",
            "public vendor-independent PCI documentation",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "live BAR mapping",
            "device register probing",
            "write-based size probing",
            "GPU reset experiments",
        ],
        "research_question": "Is this control/register aperture, VRAM aperture, doorbell aperture, or unused/reserved?",
        "next_action": "Collect only documented or already-existing inventory evidence.",
    },
    {
        "slot": "BAR1",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "Stage 3 OS-visible PCI inventory",
            "Stage 4 normalized summary",
            "public vendor-independent PCI documentation",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "live BAR mapping",
            "device register probing",
            "write-based size probing",
            "GPU reset experiments",
        ],
        "research_question": "Is this aperture paired with BAR0, an address extension, or unused/reserved?",
        "next_action": "Document possible 64-bit pairing hypotheses without touching hardware.",
    },
    {
        "slot": "BAR2",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "Stage 3 OS-visible PCI inventory",
            "Stage 4 normalized summary",
            "public vendor-independent PCI documentation",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "live BAR mapping",
            "device register probing",
            "write-based size probing",
            "GPU reset experiments",
        ],
        "research_question": "Is this a large memory aperture, control aperture, or unused/reserved?",
        "next_action": "Compare only OS-visible address hints and external documentation notes.",
    },
    {
        "slot": "BAR3",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "Stage 3 OS-visible PCI inventory",
            "Stage 4 normalized summary",
            "public vendor-independent PCI documentation",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "live BAR mapping",
            "device register probing",
            "write-based size probing",
            "GPU reset experiments",
        ],
        "research_question": "Is this paired with BAR2, an address extension, or unused/reserved?",
        "next_action": "Keep as unknown until non-invasive evidence exists.",
    },
    {
        "slot": "BAR4",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "Stage 3 OS-visible PCI inventory",
            "Stage 4 normalized summary",
            "public vendor-independent PCI documentation",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "live BAR mapping",
            "device register probing",
            "write-based size probing",
            "GPU reset experiments",
        ],
        "research_question": "Is this a small control aperture, doorbell aperture, or unused/reserved?",
        "next_action": "Record only safe inventory hints.",
    },
    {
        "slot": "BAR5",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "Stage 3 OS-visible PCI inventory",
            "Stage 4 normalized summary",
            "public vendor-independent PCI documentation",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "live BAR mapping",
            "device register probing",
            "write-based size probing",
            "GPU reset experiments",
        ],
        "research_question": "Is this paired with BAR4, an address extension, or unused/reserved?",
        "next_action": "Keep as unknown until documented evidence exists.",
    },
    {
        "slot": "ROM",
        "current_role": "UNKNOWN",
        "confidence": "NONE",
        "allowed_evidence": [
            "OS-visible ROM presence hints",
            "public documentation notes",
            "safe project-local notes",
        ],
        "forbidden_evidence": [
            "firmware extraction from hardware",
            "firmware loading",
            "firmware modification",
            "GPU reset experiments",
        ],
        "research_question": "Is an expansion ROM exposed to macOS, and is it relevant to this project?",
        "next_action": "Document presence only if already visible through safe inventory.",
    },
]

RESEARCH_GATES = [
    {
        "gate": "BRG-1",
        "name": "Inventory evidence consolidation",
        "status": "ALLOWED",
        "description": "Use existing Stage 3 and Stage 4 artifacts to list OS-visible BAR hints.",
    },
    {
        "gate": "BRG-2",
        "name": "BAR pairing hypothesis",
        "status": "ALLOWED_DOCUMENTATION_ONLY",
        "description": "Record possible 64-bit BAR pairings as hypotheses only.",
    },
    {
        "gate": "BRG-3",
        "name": "Role confidence assignment",
        "status": "BLOCKED_UNTIL_EVIDENCE",
        "description": "Do not assign roles above UNKNOWN until non-invasive evidence exists.",
    },
    {
        "gate": "BRG-4",
        "name": "Register map placeholder",
        "status": "FUTURE_STAGE_ONLY",
        "description": "A later stage may create a register map placeholder without offsets being accessed.",
    },
    {
        "gate": "BRG-5",
        "name": "BAR access exception proposal",
        "status": "FORBIDDEN_CURRENTLY",
        "description": "No exception proposal is allowed until role evidence and recovery plans are complete.",
    },
]

FORBIDDEN_NOW = [
    "PCI config-space writes",
    "PCI config-space reads for live probing",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "BAR size probing by writes",
    "register offset probing",
    "GPU reset logic",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "DriverKit activation",
    "IOPCIDevice ownership request",
    "RTX 5070 Metal acceleration attempt",
]


def build_plan() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "BAR_ROLE_RESEARCH_PLAN_READY",
        "full_metal_goal": True,
        "bar_access_allowed": False,
        "implementation_started": False,
        "bar_slots": BAR_SLOTS,
        "research_gates": RESEARCH_GATES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 18 should add command processor and memory manager placeholders without command submission or BAR access.",
        "safety_boundary": {
            "read_only": True,
            "uses_existing_artifacts_only": True,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "bar_size_probing": False,
            "register_offset_probing": False,
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
    bar_rows = []
    for item in data["bar_slots"]:
        allowed = ", ".join(item["allowed_evidence"])
        forbidden = ", ".join(item["forbidden_evidence"])
        bar_rows.append(
            f"| `{item['slot']}` | `{item['current_role']}` | `{item['confidence']}` | {item['research_question']} | {item['next_action']} | {allowed} | {forbidden} |"
        )

    gate_rows = []
    for item in data["research_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | {item['name']} | `{item['status']}` | {item['description']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# BAR Role Research Plan",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"BAR access allowed: `{data['bar_access_allowed']}`",
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
            "## BAR Slot Plan",
            "",
            "| Slot | Current Role | Confidence | Research Question | Next Action | Allowed Evidence | Forbidden Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *bar_rows,
            "",
            "## Research Gates",
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
            "This stage is read-only and uses existing artifacts only.",
            "",
            "It does not run ioreg, run system_profiler, perform live PCI probing, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, probe BAR sizes, probe register offsets, run GPU reset logic, load firmware, initialize GSP, initialize display engine, initialize framebuffer, activate DriverKit, request IOPCIDevice ownership, or attempt RTX 5070 Metal acceleration.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the H1mekaRTX BAR role research plan."
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

    json_path = out_dir / "bar-role-research-plan.json"
    md_path = out_dir / "bar-role-research-plan.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
