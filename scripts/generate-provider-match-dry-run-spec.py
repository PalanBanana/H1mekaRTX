#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_dry_run_spec.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

MATCH_FIELDS = [
    {
        "field": "vendor_id",
        "expected": "0x10de",
        "required": True,
        "match_policy": "exact",
        "reject_if_missing": True,
        "reject_if_different": True,
    },
    {
        "field": "device_id",
        "expected": "0x2f04",
        "required": True,
        "match_policy": "exact",
        "reject_if_missing": True,
        "reject_if_different": True,
    },
    {
        "field": "iopcimatch",
        "expected": "0x2f0410de",
        "required": True,
        "match_policy": "exact",
        "reject_if_missing": True,
        "reject_if_different": True,
    },
    {
        "field": "subsystem_vendor_id",
        "expected": "0x1458",
        "required": True,
        "match_policy": "exact",
        "reject_if_missing": True,
        "reject_if_different": True,
    },
    {
        "field": "subsystem_id",
        "expected": "0x417e",
        "required": True,
        "match_policy": "exact",
        "reject_if_missing": True,
        "reject_if_different": True,
    },
]

DRY_RUN_CASES = [
    {
        "case_id": "PMD-001",
        "name": "exact target match",
        "input": {
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "iopcimatch": "0x2f0410de",
            "subsystem_vendor_id": "0x1458",
            "subsystem_id": "0x417e",
        },
        "expected_decision": "MATCH_TARGET_SPEC_ONLY",
        "reason": "All identity fields match the RTX 5070 target exactly.",
    },
    {
        "case_id": "PMD-002",
        "name": "wrong NVIDIA device",
        "input": {
            "vendor_id": "0x10de",
            "device_id": "0x0000",
            "iopcimatch": "0x000010de",
            "subsystem_vendor_id": "0x1458",
            "subsystem_id": "0x417e",
        },
        "expected_decision": "REJECT_WRONG_DEVICE",
        "reason": "Vendor alone is not enough. Device ID and IOPCIMatch must match exactly.",
    },
    {
        "case_id": "PMD-003",
        "name": "wrong subsystem",
        "input": {
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "iopcimatch": "0x2f0410de",
            "subsystem_vendor_id": "0x0000",
            "subsystem_id": "0x0000",
        },
        "expected_decision": "REJECT_WRONG_SUBSYSTEM",
        "reason": "Subsystem identity must match exactly before any future provider path can be considered.",
    },
    {
        "case_id": "PMD-004",
        "name": "missing subsystem",
        "input": {
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "iopcimatch": "0x2f0410de",
        },
        "expected_decision": "REJECT_INCOMPLETE_IDENTITY",
        "reason": "Missing required identity fields must default to deny.",
    },
    {
        "case_id": "PMD-005",
        "name": "non NVIDIA device",
        "input": {
            "vendor_id": "0xffff",
            "device_id": "0xffff",
            "iopcimatch": "0xffffffff",
            "subsystem_vendor_id": "0xffff",
            "subsystem_id": "0xffff",
        },
        "expected_decision": "REJECT_WRONG_VENDOR",
        "reason": "Non-target vendor must be rejected.",
    },
]

REJECTION_RULES = [
    "Reject vendor-only matches.",
    "Reject device-only matches.",
    "Reject IOPCIMatch-only matches.",
    "Reject missing subsystem identity.",
    "Reject broad wildcard matching.",
    "Reject masked matching until explicit evidence review approves it.",
    "Reject multiple-target matching in this stage.",
    "Reject any path that would request device ownership.",
    "Reject any path that would attach to a live provider.",
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


def classify_candidate(candidate: dict[str, str]) -> str:
    vendor = candidate.get("vendor_id")
    device = candidate.get("device_id")
    match = candidate.get("iopcimatch")
    subvendor = candidate.get("subsystem_vendor_id")
    subid = candidate.get("subsystem_id")

    required_keys = [
        "vendor_id",
        "device_id",
        "iopcimatch",
        "subsystem_vendor_id",
        "subsystem_id",
    ]

    if any(key not in candidate for key in required_keys):
        return "REJECT_INCOMPLETE_IDENTITY"

    if vendor != TARGET["vendor_id"]:
        return "REJECT_WRONG_VENDOR"

    if device != TARGET["device_id"] or match != TARGET["iopcimatch"]:
        return "REJECT_WRONG_DEVICE"

    if subvendor != TARGET["subsystem_vendor_id"] or subid != TARGET["subsystem_id"]:
        return "REJECT_WRONG_SUBSYSTEM"

    return "MATCH_TARGET_SPEC_ONLY"


def build_spec() -> dict[str, Any]:
    evaluated_cases = []
    passed_case_count = 0

    for case in DRY_RUN_CASES:
        actual = classify_candidate(case["input"])
        passed = actual == case["expected_decision"]
        passed_case_count += 1 if passed else 0
        evaluated_cases.append(
            {
                **case,
                "actual_decision": actual,
                "passed": passed,
            }
        )

    failed_case_count = len(evaluated_cases) - passed_case_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "PROVIDER_MATCH_DRY_RUN_SPEC_READY",
        "plain_answer": "Provider matching can be specified, but no DriverKit target, activation, provider attach, device ownership, PCI config access, BAR mapping, or MMIO access is allowed.",
        "full_metal_goal": True,
        "research_continues": True,
        "provider_match_spec_ready": True,
        "dry_run_only": True,
        "case_count": len(evaluated_cases),
        "passed_case_count": passed_case_count,
        "failed_case_count": failed_case_count,
        "match_fields": MATCH_FIELDS,
        "dry_run_cases": evaluated_cases,
        "rejection_rules": REJECTION_RULES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 43 should add a provider-match evidence ledger without creating DriverKit targets, activation requests, provider attachment, device ownership requests, PCI config access, BAR mapping, or MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "spec_only": True,
            "local_dry_run_only": True,
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
    field_rows = []
    for item in data["match_fields"]:
        field_rows.append(
            f"| `{item['field']}` | `{item['expected']}` | `{item['required']}` | `{item['match_policy']}` | `{item['reject_if_missing']}` | `{item['reject_if_different']}` |"
        )

    case_rows = []
    for item in data["dry_run_cases"]:
        case_rows.append(
            f"| `{item['case_id']}` | {item['name']} | `{item['expected_decision']}` | `{item['actual_decision']}` | `{item['passed']}` | {item['reason']} |"
        )

    rejection_lines = [f"- {item}" for item in data["rejection_rules"]]
    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Provider-match Dry-run Spec",
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
            f"Provider match spec ready: `{data['provider_match_spec_ready']}`",
            "",
            f"Dry-run only: `{data['dry_run_only']}`",
            "",
            f"Case count: `{data['case_count']}`",
            "",
            f"Passed case count: `{data['passed_case_count']}`",
            "",
            f"Failed case count: `{data['failed_case_count']}`",
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
            "## Required Match Fields",
            "",
            "| Field | Expected | Required | Match Policy | Reject If Missing | Reject If Different |",
            "| --- | --- | --- | --- | --- | --- |",
            *field_rows,
            "",
            "## Dry-run Cases",
            "",
            "| Case | Name | Expected | Actual | Passed | Reason |",
            "| --- | --- | --- | --- | --- | --- |",
            *case_rows,
            "",
            "## Rejection Rules",
            "",
            *rejection_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is spec-only and documentation-only.",
            "",
            "It does not create a DriverKit target, add a dext provider class, add an Info.plist provider-match dictionary, create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, activate DriverKit, install a DriverKit dext, request device ownership, attach to a PCI provider, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX provider-match dry-run spec."
    )
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_spec()

    json_path = out_dir / "provider-match-dry-run-spec.json"
    md_path = out_dir / "provider-match-dry-run-spec.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    return 0 if data["failed_case_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
