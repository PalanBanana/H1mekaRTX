#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_evidence_ledger.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

SOURCE_ARTIFACTS = [
    {
        "artifact": "provider-match-dry-run-spec",
        "path": "docs/metal/provider-match-dry-run-spec.md",
        "status": "SPEC_READY",
        "required_for_transition": True,
        "purpose": "Defines exact target identity, rejection rules, and local dry-run cases.",
    },
    {
        "artifact": "entitlement-evidence-checklist",
        "path": "docs/metal/entitlement-evidence-checklist.md",
        "status": "NEEDS_USER_EVIDENCE",
        "required_for_transition": True,
        "purpose": "Tracks DriverKit, PCI transport, signing, provisioning, and private evidence requirements.",
    },
    {
        "artifact": "no-hardware-activation-readiness-review",
        "path": "docs/metal/no-hardware-activation-readiness-review.md",
        "status": "NO_GO",
        "required_for_transition": True,
        "purpose": "Keeps activation and device ownership blocked until evidence is complete.",
    },
    {
        "artifact": "local-diagnostics-index",
        "path": "docs/metal/local-diagnostics-index.md",
        "status": "LOCAL_TOOLING_READY",
        "required_for_transition": False,
        "purpose": "Indexes generated local diagnostics artifacts without live queries.",
    },
]

EVIDENCE_LEDGER = [
    {
        "id": "PMEL-001",
        "category": "target_identity",
        "evidence": "vendor ID exact match",
        "expected_value": "0x10de",
        "current_status": "SPEC_READY",
        "required_for_provider_transition": True,
        "blocking": False,
        "source_artifact": "provider-match-dry-run-spec",
        "acceptance_rule": "candidate vendor_id must equal 0x10de",
    },
    {
        "id": "PMEL-002",
        "category": "target_identity",
        "evidence": "device ID exact match",
        "expected_value": "0x2f04",
        "current_status": "SPEC_READY",
        "required_for_provider_transition": True,
        "blocking": False,
        "source_artifact": "provider-match-dry-run-spec",
        "acceptance_rule": "candidate device_id must equal 0x2f04",
    },
    {
        "id": "PMEL-003",
        "category": "target_identity",
        "evidence": "IOPCIMatch exact match",
        "expected_value": "0x2f0410de",
        "current_status": "SPEC_READY",
        "required_for_provider_transition": True,
        "blocking": False,
        "source_artifact": "provider-match-dry-run-spec",
        "acceptance_rule": "candidate iopcimatch must equal 0x2f0410de",
    },
    {
        "id": "PMEL-004",
        "category": "target_identity",
        "evidence": "subsystem vendor ID exact match",
        "expected_value": "0x1458",
        "current_status": "SPEC_READY",
        "required_for_provider_transition": True,
        "blocking": False,
        "source_artifact": "provider-match-dry-run-spec",
        "acceptance_rule": "candidate subsystem_vendor_id must equal 0x1458",
    },
    {
        "id": "PMEL-005",
        "category": "target_identity",
        "evidence": "subsystem ID exact match",
        "expected_value": "0x417e",
        "current_status": "SPEC_READY",
        "required_for_provider_transition": True,
        "blocking": False,
        "source_artifact": "provider-match-dry-run-spec",
        "acceptance_rule": "candidate subsystem_id must equal 0x417e",
    },
    {
        "id": "PMEL-006",
        "category": "entitlement",
        "evidence": "DriverKit entitlement approval",
        "expected_value": "user-private approved status",
        "current_status": "NEEDS_USER_EVIDENCE",
        "required_for_provider_transition": True,
        "blocking": True,
        "source_artifact": "entitlement-evidence-checklist",
        "acceptance_rule": "user records approval outside repository before any provider transition",
    },
    {
        "id": "PMEL-007",
        "category": "entitlement",
        "evidence": "PCI transport entitlement approval",
        "expected_value": "user-private approved status",
        "current_status": "NEEDS_USER_EVIDENCE",
        "required_for_provider_transition": True,
        "blocking": True,
        "source_artifact": "entitlement-evidence-checklist",
        "acceptance_rule": "user records PCI transport approval outside repository before any provider transition",
    },
    {
        "id": "PMEL-008",
        "category": "bundle_identity",
        "evidence": "host app and dext bundle identity plan",
        "expected_value": "user-private bundle identity evidence",
        "current_status": "NEEDS_USER_EVIDENCE",
        "required_for_provider_transition": True,
        "blocking": True,
        "source_artifact": "entitlement-evidence-checklist",
        "acceptance_rule": "bundle identity evidence exists outside repository without signed artifacts committed",
    },
    {
        "id": "PMEL-009",
        "category": "wrong_device_prevention",
        "evidence": "reject vendor-only, device-only, incomplete, wildcard, and wrong-subsystem matches",
        "expected_value": "all rejection rules present",
        "current_status": "SPEC_READY",
        "required_for_provider_transition": True,
        "blocking": False,
        "source_artifact": "provider-match-dry-run-spec",
        "acceptance_rule": "all non-exact dry-run cases reject",
    },
    {
        "id": "PMEL-010",
        "category": "activation_boundary",
        "evidence": "activation remains blocked",
        "expected_value": "NO_GO",
        "current_status": "NO_GO",
        "required_for_provider_transition": True,
        "blocking": True,
        "source_artifact": "no-hardware-activation-readiness-review",
        "acceptance_rule": "no activation request or manager submit exists",
    },
    {
        "id": "PMEL-011",
        "category": "device_ownership_boundary",
        "evidence": "device ownership remains blocked",
        "expected_value": "NO_GO",
        "current_status": "NO_GO",
        "required_for_provider_transition": True,
        "blocking": True,
        "source_artifact": "no-hardware-activation-readiness-review",
        "acceptance_rule": "no device ownership request or provider attach exists",
    },
    {
        "id": "PMEL-012",
        "category": "hardware_access_boundary",
        "evidence": "PCI/BAR/MMIO access remains blocked",
        "expected_value": "NO_GO",
        "current_status": "NO_GO",
        "required_for_provider_transition": True,
        "blocking": True,
        "source_artifact": "no-hardware-activation-readiness-review",
        "acceptance_rule": "no PCI config access, BAR mapping, MMIO access, firmware loading, or reset logic exists",
    },
]

TRANSITION_GATES = [
    {
        "gate": "PMTG-001",
        "name": "all exact identity fields are specified",
        "status": "PASS",
        "blocking": False,
    },
    {
        "gate": "PMTG-002",
        "name": "wrong-device rejection rules exist",
        "status": "PASS",
        "blocking": False,
    },
    {
        "gate": "PMTG-003",
        "name": "DriverKit entitlement evidence exists outside repository",
        "status": "NO_GO",
        "blocking": True,
    },
    {
        "gate": "PMTG-004",
        "name": "PCI transport entitlement evidence exists outside repository",
        "status": "NO_GO",
        "blocking": True,
    },
    {
        "gate": "PMTG-005",
        "name": "host app and dext bundle identity evidence exists outside repository",
        "status": "NO_GO",
        "blocking": True,
    },
    {
        "gate": "PMTG-006",
        "name": "activation request code remains absent",
        "status": "PASS",
        "blocking": False,
    },
    {
        "gate": "PMTG-007",
        "name": "provider attach and device ownership code remain absent",
        "status": "PASS",
        "blocking": False,
    },
    {
        "gate": "PMTG-008",
        "name": "PCI/BAR/MMIO hardware access remains absent",
        "status": "PASS",
        "blocking": False,
    },
]

FORBIDDEN_NOW = [
    "creating DriverKit target",
    "adding dext provider class",
    "adding Info.plist provider match dictionary",
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
    "installing DriverKit dext",
    "activating DriverKit",
    "requesting device ownership",
    "attaching to PCI provider",
    "querying live provider state",
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


def build_ledger() -> dict[str, Any]:
    blocking_items = [item for item in EVIDENCE_LEDGER if item["blocking"]]
    blocking_gates = [item for item in TRANSITION_GATES if item["blocking"]]
    pass_gates = [item for item in TRANSITION_GATES if item["status"] == "PASS"]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "PROVIDER_MATCH_EVIDENCE_LEDGER_READY_BLOCKED_ON_USER_EVIDENCE",
        "plain_answer": "Provider-match evidence is now tracked, but transition to DriverKit/provider work remains blocked.",
        "full_metal_goal": True,
        "research_continues": True,
        "provider_match_evidence_ledger_ready": True,
        "provider_match_transition_allowed": False,
        "driverkit_target_creation_allowed": False,
        "activation_request_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "source_artifacts": SOURCE_ARTIFACTS,
        "ledger_item_count": len(EVIDENCE_LEDGER),
        "blocking_ledger_item_count": len(blocking_items),
        "transition_gate_count": len(TRANSITION_GATES),
        "blocking_transition_gate_count": len(blocking_gates),
        "pass_transition_gate_count": len(pass_gates),
        "evidence_ledger": EVIDENCE_LEDGER,
        "transition_gates": TRANSITION_GATES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 44 should add a provider-match ledger validator that can consume local generated JSON reports without live provider attachment, device ownership requests, PCI config access, BAR mapping, or MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "ledger_only": True,
            "local_report_reference_only": True,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
            "driverkit_activation": False,
            "driverkit_dext_installation": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
            "live_provider_state_query": False,
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
    source_rows = []
    for item in data["source_artifacts"]:
        source_rows.append(
            f"| `{item['artifact']}` | `{item['path']}` | `{item['status']}` | `{item['required_for_transition']}` | {item['purpose']} |"
        )

    ledger_rows = []
    for item in data["evidence_ledger"]:
        ledger_rows.append(
            f"| `{item['id']}` | `{item['category']}` | {item['evidence']} | `{item['expected_value']}` | `{item['current_status']}` | `{item['blocking']}` | `{item['source_artifact']}` | {item['acceptance_rule']} |"
        )

    gate_rows = []
    for item in data["transition_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | {item['name']} | `{item['status']}` | `{item['blocking']}` |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Provider-match Evidence Ledger",
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
            f"Provider-match evidence ledger ready: `{data['provider_match_evidence_ledger_ready']}`",
            "",
            f"Provider-match transition allowed: `{data['provider_match_transition_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{data['driverkit_target_creation_allowed']}`",
            "",
            f"Activation request allowed: `{data['activation_request_allowed']}`",
            "",
            f"Provider attach allowed: `{data['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
            "",
            f"Hardware access allowed: `{data['hardware_access_allowed']}`",
            "",
            f"Ledger item count: `{data['ledger_item_count']}`",
            "",
            f"Blocking ledger item count: `{data['blocking_ledger_item_count']}`",
            "",
            f"Transition gate count: `{data['transition_gate_count']}`",
            "",
            f"Blocking transition gate count: `{data['blocking_transition_gate_count']}`",
            "",
            f"PASS transition gate count: `{data['pass_transition_gate_count']}`",
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
            "## Source Artifacts",
            "",
            "| Artifact | Path | Status | Required For Transition | Purpose |",
            "| --- | --- | --- | --- | --- |",
            *source_rows,
            "",
            "## Evidence Ledger",
            "",
            "| ID | Category | Evidence | Expected Value | Current Status | Blocking | Source Artifact | Acceptance Rule |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
            *ledger_rows,
            "",
            "## Transition Gates",
            "",
            "| Gate | Name | Status | Blocking |",
            "| --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is ledger-only and documentation-only.",
            "",
            "It links existing specs and checklists into a provider-match evidence ledger. It does not create a DriverKit target, add a dext provider class, add an Info.plist provider-match dictionary, create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, activate DriverKit, install a DriverKit dext, request device ownership, attach to a PCI provider, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX provider-match evidence ledger."
    )
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_ledger()

    json_path = out_dir / "provider-match-evidence-ledger.json"
    md_path = out_dir / "provider-match-evidence-ledger.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
