#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.real_implementation_readiness_review.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

INPUT_STAGE_SUMMARY = [
    {
        "stage": "Stage 13",
        "name": "Metal feasibility boundary",
        "result": "Research boundary exists; implementation not started.",
        "supports_go": False,
    },
    {
        "stage": "Stage 14",
        "name": "macOS graphics stack architecture map",
        "result": "Architecture layers mapped; macOS Metal device exposure remains unresolved.",
        "supports_go": False,
    },
    {
        "stage": "Stage 15",
        "name": "Metal validation harness skeleton",
        "result": "Public Metal app-layer validation exists for the existing system Metal device only.",
        "supports_go": True,
    },
    {
        "stage": "Stage 16",
        "name": "DriverKit activation design review",
        "result": "Design-only; no activation implementation, host app target, or dext target.",
        "supports_go": False,
    },
    {
        "stage": "Stage 17",
        "name": "BAR role research plan",
        "result": "BAR roles remain UNKNOWN and BAR access remains denied.",
        "supports_go": False,
    },
    {
        "stage": "Stage 18",
        "name": "Command and memory model placeholders",
        "result": "Command processor and memory manager are placeholder-only.",
        "supports_go": False,
    },
    {
        "stage": "Stage 19",
        "name": "Shader and compiler research notes",
        "result": "Shader/compiler path remains off-device and research-only.",
        "supports_go": False,
    },
    {
        "stage": "Stage 20",
        "name": "Metal implementation decision gate",
        "result": "Implementation explicitly marked not ready.",
        "supports_go": False,
    },
    {
        "stage": "Stage 21",
        "name": "Implementation blocker register",
        "result": "Critical blockers are open.",
        "supports_go": False,
    },
    {
        "stage": "Stage 22",
        "name": "Recovery and rollback runbook",
        "result": "Recovery planning exists; hardware experiments still not allowed.",
        "supports_go": True,
    },
    {
        "stage": "Stage 23",
        "name": "DriverKit dry-run checklist",
        "result": "Activation decision remains NO-GO.",
        "supports_go": False,
    },
    {
        "stage": "Stage 24",
        "name": "BAR evidence ledger",
        "result": "BAR evidence tracking exists; roles remain UNKNOWN.",
        "supports_go": False,
    },
    {
        "stage": "Stage 25",
        "name": "Metal reference workload suite",
        "result": "Public Metal workload suite exists on the existing system Metal device only.",
        "supports_go": True,
    },
    {
        "stage": "Stage 26",
        "name": "Host app scaffold plan",
        "result": "Host app plan exists; no host target or activation code.",
        "supports_go": False,
    },
    {
        "stage": "Stage 27",
        "name": "No-activation host app skeleton",
        "result": "Host-side Swift skeleton exists with no activation path.",
        "supports_go": True,
    },
    {
        "stage": "Stage 28",
        "name": "Host status schema and viewer plan",
        "result": "Local status schema and viewer plan exist.",
        "supports_go": True,
    },
    {
        "stage": "Stage 29",
        "name": "Local host report renderer",
        "result": "Local JSON-to-Markdown renderer exists; no live extension or hardware access.",
        "supports_go": True,
    },
]

READINESS_GATES = [
    {
        "gate": "RIR-001",
        "area": "macOS Metal device exposure",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "No verified path exists in this repository to expose RTX 5070 as an app-visible macOS Metal device.",
        "required_to_close": [
            "documented public or approved architecture path",
            "clear separation from private framework patching",
            "proof that app-visible Metal device creation is feasible",
        ],
    },
    {
        "gate": "RIR-002",
        "area": "DriverKit activation",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "DriverKit remains design-only and dry-run-only. No activation request code exists.",
        "required_to_close": [
            "approved entitlement evidence",
            "signed host app plan",
            "signed dext plan",
            "reviewed no-hardware activation dry-run",
        ],
    },
    {
        "gate": "RIR-003",
        "area": "PCI provider ownership",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "No IOPCIDevice ownership request is implemented or allowed.",
        "required_to_close": [
            "exact provider match proof",
            "wrong-device attach prevention",
            "rollback plan",
            "no-BAR no-MMIO attach-only dry-run review",
        ],
    },
    {
        "gate": "RIR-004",
        "area": "BAR role evidence",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "BAR0 through BAR5 and ROM remain UNKNOWN.",
        "required_to_close": [
            "slot-specific non-invasive evidence",
            "confidence level assignment",
            "reviewed BAR access exception proposal",
        ],
    },
    {
        "gate": "RIR-005",
        "area": "MMIO/BAR safety",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "Default-deny policy still blocks MMIO reads, MMIO writes, and BAR mapping.",
        "required_to_close": [
            "documented safe read policy",
            "documented forbidden offset list",
            "panic and recovery runbook",
            "explicit reviewed exception stage",
        ],
    },
    {
        "gate": "RIR-006",
        "area": "Command processor model",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "Queue, ring, doorbell, fence, interrupt, timeout, and recovery semantics remain unknown.",
        "required_to_close": [
            "command packet model",
            "queue or ring model",
            "doorbell or submit model",
            "completion and timeout model",
            "recovery model",
        ],
    },
    {
        "gate": "RIR-007",
        "area": "Memory manager model",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "VRAM allocation, resource residency, address translation, page tables, and coherency are not implemented.",
        "required_to_close": [
            "allocation model",
            "buffer residency model",
            "texture layout model",
            "GPU virtual address model",
            "cache and coherency model",
        ],
    },
    {
        "gate": "RIR-008",
        "area": "Shader and compiler execution path",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "Only public system Metal validation exists. No RTX 5070 executable shader path exists.",
        "required_to_close": [
            "shader subset definition",
            "IR strategy",
            "target instruction strategy",
            "pipeline metadata model",
            "off-device validation strategy",
        ],
    },
    {
        "gate": "RIR-009",
        "area": "Firmware and GSP boundary",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "Firmware loading and GSP initialization remain forbidden.",
        "required_to_close": [
            "separate firmware boundary review",
            "source provenance policy",
            "no-blob policy or approved artifact policy",
            "rollback policy",
        ],
    },
    {
        "gate": "RIR-010",
        "area": "Display and framebuffer boundary",
        "required_for_real_implementation": True,
        "status": "NO_GO",
        "evidence": "Display engine and framebuffer initialization remain forbidden.",
        "required_to_close": [
            "separate display bring-up plan",
            "scanout ownership policy",
            "framebuffer rollback plan",
        ],
    },
    {
        "gate": "RIR-011",
        "area": "Public Metal workload suite",
        "required_for_real_implementation": False,
        "status": "PASS",
        "evidence": "Stage 25 provides deterministic public Metal reference workloads on the existing system Metal device.",
        "required_to_close": [
            "continue expanding reference workloads",
        ],
    },
    {
        "gate": "RIR-012",
        "area": "Host-side local tooling",
        "required_for_real_implementation": False,
        "status": "PASS",
        "evidence": "Stages 27 through 29 provide no-activation host skeleton and local report rendering.",
        "required_to_close": [
            "continue local-only status/report tooling",
        ],
    },
]

NEXT_ALLOWED_TRACKS = [
    {
        "track": "research-only",
        "allowed": True,
        "description": "Continue docs, schemas, local renderers, workload tests, and evidence ledgers.",
    },
    {
        "track": "public Metal app-layer workloads",
        "allowed": True,
        "description": "Continue expanding workloads on the existing system Metal device only.",
    },
    {
        "track": "host-side no-activation tooling",
        "allowed": True,
        "description": "Continue local-only host/status/report tooling with no System Extension requests.",
    },
    {
        "track": "DriverKit activation implementation",
        "allowed": False,
        "description": "Blocked until entitlement, signing, provisioning, rollback, and dry-run gates are closed.",
    },
    {
        "track": "PCI/BAR/MMIO hardware work",
        "allowed": False,
        "description": "Blocked until BAR roles, access policy, and recovery evidence are complete.",
    },
    {
        "track": "RTX 5070 Metal acceleration implementation",
        "allowed": False,
        "description": "Blocked until all required NO-GO gates are closed.",
    },
]

FORBIDDEN_NOW = [
    "RTX 5070 Metal acceleration implementation branch",
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
    "System Extension deactivation request",
    "extension manager submit request",
    "IOPCIDevice ownership request",
    "live PCI probing",
    "ioreg collection",
    "system_profiler collection",
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


def build_review() -> dict[str, Any]:
    required_gates = [
        item for item in READINESS_GATES
        if item["required_for_real_implementation"]
    ]
    required_no_go = [
        item for item in required_gates
        if item["status"] != "PASS"
    ]
    optional_pass = [
        item for item in READINESS_GATES
        if not item["required_for_real_implementation"] and item["status"] == "PASS"
    ]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "REAL_IMPLEMENTATION_NOT_APPROVED_RESEARCH_ONLY_CONTINUES",
        "plain_answer": "Do not open a real RTX 5070 Metal acceleration implementation branch yet.",
        "full_metal_goal": True,
        "research_continues": True,
        "real_implementation_allowed": False,
        "real_implementation_started": False,
        "implementation_branch_allowed": False,
        "required_gate_count": len(required_gates),
        "required_no_go_count": len(required_no_go),
        "optional_pass_count": len(optional_pass),
        "input_stage_summary": INPUT_STAGE_SUMMARY,
        "readiness_gates": READINESS_GATES,
        "next_allowed_tracks": NEXT_ALLOWED_TRACKS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 31 should add a research-only roadmap refresh that groups remaining work into public Metal workloads, host tooling, DriverKit evidence, BAR evidence, command/memory research, and shader/compiler research.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "real_implementation_allowed": False,
            "implementation_branch_allowed": False,
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
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
            "iopcidevice_ownership_request": False,
            "live_pci_probing": False,
            "runs_ioreg": False,
            "runs_system_profiler": False,
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
    stage_rows = []
    for item in data["input_stage_summary"]:
        stage_rows.append(
            f"| {item['stage']} | {item['name']} | `{item['supports_go']}` | {item['result']} |"
        )

    gate_rows = []
    for item in data["readiness_gates"]:
        required = "<br>".join(item["required_to_close"])
        gate_rows.append(
            f"| `{item['gate']}` | {item['area']} | `{item['required_for_real_implementation']}` | `{item['status']}` | {item['evidence']} | {required} |"
        )

    track_rows = []
    for item in data["next_allowed_tracks"]:
        track_rows.append(
            f"| {item['track']} | `{item['allowed']}` | {item['description']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Real Implementation Readiness Review",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Real implementation allowed: `{data['real_implementation_allowed']}`",
            "",
            f"Real implementation started: `{data['real_implementation_started']}`",
            "",
            f"Implementation branch allowed: `{data['implementation_branch_allowed']}`",
            "",
            f"Required gate count: `{data['required_gate_count']}`",
            "",
            f"Required NO-GO count: `{data['required_no_go_count']}`",
            "",
            f"Optional PASS count: `{data['optional_pass_count']}`",
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
            "## Input Stage Summary",
            "",
            "| Stage | Name | Supports GO | Result |",
            "| --- | --- | --- | --- |",
            *stage_rows,
            "",
            "## Readiness Gates",
            "",
            "| Gate | Area | Required | Status | Evidence | Required To Close |",
            "| --- | --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Next Allowed Tracks",
            "",
            "| Track | Allowed | Description |",
            "| --- | --- | --- |",
            *track_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This review is documentation-only.",
            "",
            "It does not approve a real implementation branch, start RTX 5070 Metal acceleration implementation, execute RTX 5070 shaders, submit hardware commands, program queues or rings, interact with doorbells, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, patch private graphics frameworks, activate DriverKit, submit System Extension requests, request IOPCIDevice ownership, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX real implementation readiness review."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_review()

    json_path = out_dir / "real-implementation-readiness-review.json"
    md_path = out_dir / "real-implementation-readiness-review.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
