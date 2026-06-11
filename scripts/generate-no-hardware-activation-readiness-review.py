#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.no_hardware_activation_readiness_review.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

EVIDENCE_GATES = [
    {
        "gate": "NHAR-001",
        "area": "Apple Developer account and signing identity",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "Developer Team ID recorded privately by user",
            "Developer ID Application signing identity available",
            "Developer ID Installer or packaging plan documented",
            "certificate expiration and revocation risk noted",
        ],
    },
    {
        "gate": "NHAR-002",
        "area": "DriverKit entitlement evidence",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "approved DriverKit entitlement evidence",
            "approved PCI transport entitlement evidence if applicable",
            "entitlement ownership and scope documented",
            "no private entitlement assumptions",
        ],
    },
    {
        "gate": "NHAR-003",
        "area": "Host app bundle architecture",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "host app bundle identifier reserved",
            "dext bundle identifier reserved",
            "embedding and packaging plan documented",
            "activation controller remains disabled by default",
        ],
    },
    {
        "gate": "NHAR-004",
        "area": "System Extension request boundary",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "activation request code review plan",
            "deactivation request code review plan",
            "manager submit call prohibited until explicit GO",
            "user approval and restart behavior documented",
        ],
    },
    {
        "gate": "NHAR-005",
        "area": "Provider matching and wrong-device prevention",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "exact vendor/device/subsystem matching plan",
            "wrong-device attach denial plan",
            "dry-run provider identity report",
            "no live device ownership request",
        ],
    },
    {
        "gate": "NHAR-006",
        "area": "Rollback and recovery",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "deactivation and cleanup runbook",
            "safe mode or recovery workflow",
            "panic collection plan",
            "known-good boot recovery notes",
        ],
    },
    {
        "gate": "NHAR-007",
        "area": "No-hardware dry-run boundary",
        "status": "NO_GO",
        "required": True,
        "evidence_required": [
            "dry-run does not request device ownership",
            "dry-run does not access PCI config space",
            "dry-run does not map BAR memory",
            "dry-run does not perform MMIO access",
        ],
    },
    {
        "gate": "NHAR-008",
        "area": "Safety gates and audit coverage",
        "status": "PASS",
        "required": False,
        "evidence_required": [
            "BAR safety gates exist",
            "forbidden operation audit exists",
            "local diagnostics index exists",
            "host-side local tooling exists",
        ],
    },
]

ALLOWED_NEXT = [
    {
        "track": "entitlement evidence checklist",
        "allowed": True,
        "description": "Document what entitlement/signing evidence is needed before any activation code exists.",
    },
    {
        "track": "provider-match dry-run spec",
        "allowed": True,
        "description": "Specify provider matching rules without device ownership or hardware access.",
    },
    {
        "track": "activation controller design",
        "allowed": True,
        "description": "Design only; no request object creation and no manager submit.",
    },
    {
        "track": "real activation implementation",
        "allowed": False,
        "description": "Blocked until all required no-hardware activation gates pass.",
    },
    {
        "track": "PCI/BAR/MMIO hardware work",
        "allowed": False,
        "description": "Blocked until separate hardware evidence gates pass.",
    },
    {
        "track": "RTX 5070 Metal acceleration implementation",
        "allowed": False,
        "description": "Blocked until full implementation GO/NO-GO turns GO.",
    },
]

FORBIDDEN_NOW = [
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
    "activating DriverKit",
    "installing a DriverKit dext",
    "requesting device ownership",
    "attaching to IOPCIDevice provider",
    "live extension status query",
    "live PCI probing",
    "ioreg collection",
    "system_profiler collection",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission to RTX 5070",
    "RTX 5070 resource allocation",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_review() -> dict[str, Any]:
    required = [gate for gate in EVIDENCE_GATES if gate["required"]]
    required_no_go = [gate for gate in required if gate["status"] != "PASS"]
    optional_pass = [gate for gate in EVIDENCE_GATES if not gate["required"] and gate["status"] == "PASS"]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "NO_HARDWARE_ACTIVATION_NOT_READY_EVIDENCE_REQUIRED",
        "plain_answer": "Do not implement or submit DriverKit/System Extension activation yet.",
        "full_metal_goal": True,
        "research_continues": True,
        "host_side_tooling_started": True,
        "no_hardware_activation_review_ready": True,
        "activation_implementation_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_activation_allowed": False,
        "device_ownership_allowed": False,
        "required_gate_count": len(required),
        "required_no_go_count": len(required_no_go),
        "optional_pass_count": len(optional_pass),
        "evidence_gates": EVIDENCE_GATES,
        "allowed_next": ALLOWED_NEXT,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 41 should add an entitlement evidence checklist without creating activation requests, DriverKit targets, provider ownership, PCI config access, BAR mapping, or MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "review_only": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
            "driverkit_activation": False,
            "driverkit_dext_installation": False,
            "device_ownership_request": False,
            "iopcidevice_provider_attach": False,
            "live_extension_status_query": False,
            "live_pci_probing": False,
            "runs_ioreg": False,
            "runs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    gate_rows = []
    for gate in data["evidence_gates"]:
        evidence = "<br>".join(gate["evidence_required"])
        gate_rows.append(
            f"| `{gate['gate']}` | {gate['area']} | `{gate['required']}` | `{gate['status']}` | {evidence} |"
        )

    next_rows = []
    for item in data["allowed_next"]:
        next_rows.append(
            f"| {item['track']} | `{item['allowed']}` | {item['description']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# No-hardware Activation Readiness Review",
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
            f"Host-side tooling started: `{data['host_side_tooling_started']}`",
            "",
            f"No-hardware activation review ready: `{data['no_hardware_activation_review_ready']}`",
            "",
            f"Activation implementation allowed: `{data['activation_implementation_allowed']}`",
            "",
            f"Activation request allowed: `{data['activation_request_allowed']}`",
            "",
            f"Deactivation request allowed: `{data['deactivation_request_allowed']}`",
            "",
            f"Manager submit allowed: `{data['manager_submit_allowed']}`",
            "",
            f"DriverKit activation allowed: `{data['driverkit_activation_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
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
            "## Evidence Gates",
            "",
            "| Gate | Area | Required | Status | Evidence Required |",
            "| --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Allowed Next Tracks",
            "",
            "| Track | Allowed | Description |",
            "| --- | --- | --- |",
            *next_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is review-only and documentation-only.",
            "",
            "It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, activate DriverKit, install a DriverKit dext, request device ownership, attach to an IOPCIDevice provider, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX no-hardware activation readiness review."
    )
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_review()

    json_path = out_dir / "no-hardware-activation-readiness-review.json"
    md_path = out_dir / "no-hardware-activation-readiness-review.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
