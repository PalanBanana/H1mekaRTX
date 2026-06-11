#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.research_only_roadmap_refresh.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

PRODUCTION_STATUS = {
    "app_level_metal_development": "STARTED",
    "host_side_tooling_development": "STARTED",
    "rtx5070_real_acceleration_driver_development": "NOT_APPROVED",
    "plain_answer": "Production has started for safe app-layer and host-side tooling. Real RTX 5070 Metal acceleration driver production is blocked until required evidence gates close.",
}

ROADMAP_TRACKS = [
    {
        "track": "public_metal_workloads",
        "status": "ACTIVE",
        "allowed": True,
        "purpose": "Grow deterministic Metal workloads on the existing system Metal device.",
        "near_term_stages": [
            "Stage 32: workload result schema",
            "Stage 33: workload regression manifest",
            "Stage 34: compute workload expansion plan",
        ],
        "blocked_by": [],
    },
    {
        "track": "host_side_no_activation_tooling",
        "status": "ACTIVE",
        "allowed": True,
        "purpose": "Grow local host status/report tools without System Extension requests.",
        "near_term_stages": [
            "Stage 35: host report bundle format",
            "Stage 36: local diagnostics index",
            "Stage 37: no-activation host UX notes",
        ],
        "blocked_by": [],
    },
    {
        "track": "driverkit_evidence",
        "status": "RESEARCH_ONLY",
        "allowed": True,
        "purpose": "Collect entitlement, signing, provisioning, and provider-match evidence without activation.",
        "near_term_stages": [
            "Stage 38: entitlement evidence checklist",
            "Stage 39: provider-match dry-run spec",
            "Stage 40: no-hardware activation readiness review",
        ],
        "blocked_by": [
            "approved DriverKit entitlement evidence missing",
            "PCI transport entitlement evidence missing",
            "host app signing/provisioning not verified",
        ],
    },
    {
        "track": "bar_evidence",
        "status": "RESEARCH_ONLY",
        "allowed": True,
        "purpose": "Improve non-invasive BAR evidence without live probing, BAR mapping, or MMIO.",
        "near_term_stages": [
            "Stage 41: BAR evidence confidence model",
            "Stage 42: BAR role hypothesis ledger",
            "Stage 43: BAR exception review template",
        ],
        "blocked_by": [
            "BAR roles unknown",
            "safe access policy not defined",
            "hardware recovery procedure not approved for BAR experiments",
        ],
    },
    {
        "track": "command_memory_research",
        "status": "RESEARCH_ONLY",
        "allowed": True,
        "purpose": "Document command submission, queue, fence, interrupt, memory, residency, address, and coherency models.",
        "near_term_stages": [
            "Stage 44: command model evidence ledger",
            "Stage 45: memory model evidence ledger",
            "Stage 46: command-memory NO-GO review",
        ],
        "blocked_by": [
            "queue model unknown",
            "doorbell model unknown",
            "fence and completion model unknown",
            "GPU virtual address model unknown",
            "resource residency model unknown",
        ],
    },
    {
        "track": "shader_compiler_research",
        "status": "RESEARCH_ONLY",
        "allowed": True,
        "purpose": "Keep shader/compiler work off-device until execution path evidence exists.",
        "near_term_stages": [
            "Stage 47: shader subset matrix",
            "Stage 48: IR strategy comparison",
            "Stage 49: off-device shader validation spec",
        ],
        "blocked_by": [
            "target executable strategy unknown",
            "pipeline metadata model unknown",
            "command and memory models not ready",
        ],
    },
    {
        "track": "real_rtx5070_metal_acceleration",
        "status": "BLOCKED",
        "allowed": False,
        "purpose": "Actual RTX 5070 Metal acceleration implementation.",
        "near_term_stages": [
            "Stage 50: full GO/NO-GO review"
        ],
        "blocked_by": [
            "macOS Metal device exposure path unresolved",
            "DriverKit activation blocked",
            "device ownership blocked",
            "BAR roles unknown",
            "MMIO/BAR access denied",
            "command processor model unknown",
            "memory manager model unknown",
            "shader/compiler execution path unknown",
            "firmware and GSP boundary forbidden",
            "display and framebuffer boundary forbidden",
        ],
    },
]

MILESTONES = [
    {
        "milestone": "M1",
        "name": "safe production foundation",
        "status": "IN_PROGRESS",
        "definition": "Metal app-level workloads, host-side skeletons, and local report tooling exist and keep passing safety gates.",
        "production_impact": "This is already being produced.",
    },
    {
        "milestone": "M2",
        "name": "activation evidence readiness",
        "status": "NOT_READY",
        "definition": "Entitlement, signing, provisioning, rollback, and provider-match evidence exist without activation.",
        "production_impact": "Needed before any DriverKit activation implementation.",
    },
    {
        "milestone": "M3",
        "name": "hardware evidence readiness",
        "status": "NOT_READY",
        "definition": "BAR roles, command model, memory model, shader path, and recovery policies are evidence-backed.",
        "production_impact": "Needed before any hardware-facing branch.",
    },
    {
        "milestone": "M4",
        "name": "real implementation gate",
        "status": "BLOCKED",
        "definition": "All required NO-GO gates become PASS.",
        "production_impact": "Only after this can real RTX 5070 Metal acceleration production start.",
    },
]

FORBIDDEN_NOW = [
    "real RTX 5070 Metal acceleration implementation branch",
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
    "device ownership request",
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


def build_roadmap() -> dict[str, Any]:
    active_tracks = [item for item in ROADMAP_TRACKS if item["allowed"]]
    blocked_tracks = [item for item in ROADMAP_TRACKS if not item["allowed"]]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "RESEARCH_ONLY_ROADMAP_REFRESH_READY",
        "full_metal_goal": True,
        "research_continues": True,
        "safe_production_started": True,
        "real_acceleration_production_started": False,
        "real_acceleration_production_allowed": False,
        "production_status": PRODUCTION_STATUS,
        "active_track_count": len(active_tracks),
        "blocked_track_count": len(blocked_tracks),
        "roadmap_tracks": ROADMAP_TRACKS,
        "milestones": MILESTONES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 32 should add a workload result schema for the public Metal reference suite.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "research_only": True,
            "safe_app_level_production_allowed": True,
            "host_side_tooling_allowed": True,
            "real_acceleration_implementation_allowed": False,
            "real_acceleration_implementation_started": False,
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
            "device_ownership_request": False,
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
    track_rows = []
    for item in data["roadmap_tracks"]:
        stages = "<br>".join(item["near_term_stages"])
        blockers = "<br>".join(item["blocked_by"]) if item["blocked_by"] else "—"
        track_rows.append(
            f"| `{item['track']}` | `{item['status']}` | `{item['allowed']}` | {item['purpose']} | {stages} | {blockers} |"
        )

    milestone_rows = []
    for item in data["milestones"]:
        milestone_rows.append(
            f"| `{item['milestone']}` | {item['name']} | `{item['status']}` | {item['definition']} | {item['production_impact']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Research-only Roadmap Refresh",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Safe production started: `{data['safe_production_started']}`",
            "",
            f"Real acceleration production started: `{data['real_acceleration_production_started']}`",
            "",
            f"Real acceleration production allowed: `{data['real_acceleration_production_allowed']}`",
            "",
            "## Production Status",
            "",
            f"- App-level Metal development: `{data['production_status']['app_level_metal_development']}`",
            f"- Host-side tooling development: `{data['production_status']['host_side_tooling_development']}`",
            f"- RTX 5070 real acceleration driver development: `{data['production_status']['rtx5070_real_acceleration_driver_development']}`",
            f"- Plain answer: {data['production_status']['plain_answer']}",
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
            "## Roadmap Tracks",
            "",
            "| Track | Status | Allowed | Purpose | Near-term Stages | Blocked By |",
            "| --- | --- | --- | --- | --- | --- |",
            *track_rows,
            "",
            "## Milestones",
            "",
            "| Milestone | Name | Status | Definition | Production Impact |",
            "| --- | --- | --- | --- | --- |",
            *milestone_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This roadmap refresh is documentation-only and research-only.",
            "",
            "It confirms that safe app-level Metal workload development and host-side local tooling production have started.",
            "",
            "It does not approve real RTX 5070 Metal acceleration implementation, execute RTX 5070 shaders, submit hardware commands, program queues or rings, interact with doorbells, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, patch private graphics frameworks, activate DriverKit, submit System Extension requests, request device ownership, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX research-only roadmap refresh."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_roadmap()

    json_path = out_dir / "research-only-roadmap-refresh.json"
    md_path = out_dir / "research-only-roadmap-refresh.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
