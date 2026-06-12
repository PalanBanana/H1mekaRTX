#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_status_schema.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

STATUS_FIELDS = [
    {
        "field": "project_status",
        "type": "string",
        "required": True,
        "default": "RESEARCH_ONLY",
        "allowed_values": ["RESEARCH_ONLY", "NO_GO", "READY_FOR_REVIEW"],
        "ui_purpose": "Top-level project state.",
    },
    {
        "field": "provider_match_status",
        "type": "string",
        "required": True,
        "default": "NO_GO",
        "allowed_values": ["NO_GO", "PASS", "READY_FOR_REVIEW"],
        "ui_purpose": "Provider-match transition status from local reports.",
    },
    {
        "field": "activation_status",
        "type": "string",
        "required": True,
        "default": "NO_GO",
        "allowed_values": ["NO_GO", "DESIGN_ONLY", "READY_FOR_REVIEW"],
        "ui_purpose": "Activation-controller transition status from local reports.",
    },
    {
        "field": "entitlement_evidence_status",
        "type": "string",
        "required": True,
        "default": "NEEDS_USER_EVIDENCE",
        "allowed_values": ["NEEDS_USER_EVIDENCE", "USER_PRIVATE_RECORDED", "READY_FOR_REVIEW"],
        "ui_purpose": "User-private entitlement evidence status.",
    },
    {
        "field": "bundle_identity_status",
        "type": "string",
        "required": True,
        "default": "NEEDS_USER_EVIDENCE",
        "allowed_values": ["NEEDS_USER_EVIDENCE", "USER_PRIVATE_RECORDED", "READY_FOR_REVIEW"],
        "ui_purpose": "Host app and dext bundle identity evidence status.",
    },
    {
        "field": "hardware_access_status",
        "type": "string",
        "required": True,
        "default": "BLOCKED",
        "allowed_values": ["BLOCKED", "NO_GO", "READY_FOR_REVIEW"],
        "ui_purpose": "PCI, BAR, MMIO, firmware, command submission, and Metal runtime access status.",
    },
    {
        "field": "last_local_report_generated_at_utc",
        "type": "string",
        "required": False,
        "default": None,
        "allowed_values": [],
        "ui_purpose": "Optional timestamp copied from local generated reports.",
    },
    {
        "field": "status_source",
        "type": "string",
        "required": True,
        "default": "LOCAL_GENERATED_REPORTS_ONLY",
        "allowed_values": ["LOCAL_GENERATED_REPORTS_ONLY"],
        "ui_purpose": "Declares that status comes from local generated JSON only.",
    },
]

STATUS_EXAMPLE = {
    "project_status": "RESEARCH_ONLY",
    "provider_match_status": "NO_GO",
    "activation_status": "NO_GO",
    "entitlement_evidence_status": "NEEDS_USER_EVIDENCE",
    "bundle_identity_status": "NEEDS_USER_EVIDENCE",
    "hardware_access_status": "BLOCKED",
    "last_local_report_generated_at_utc": None,
    "status_source": "LOCAL_GENERATED_REPORTS_ONLY",
}

INPUT_REPORTS = [
    "host-app-activation-ui-plan.json",
    "activation-controller-transition-gate-report.json",
    "activation-controller-static-contract-report.json",
    "provider-match-transition-gate-report.json",
    "provider-match-ledger-validator-report.json",
    "provider-match-evidence-ledger.json",
    "provider-match-dry-run-spec.json",
    "entitlement-evidence-checklist.json",
    "no-hardware-activation-readiness-review.json",
]

FORBIDDEN_NOW = [
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
    "creating DriverKit target",
    "adding dext provider class",
    "adding Info.plist provider match dictionary",
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


def build_schema() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "HOST_APP_STATUS_SCHEMA_READY_LOCAL_REPORT_ONLY",
        "plain_answer": "Host-app status schema can be defined, but it must be populated only from local generated reports.",
        "full_metal_goal": True,
        "research_continues": True,
        "host_app_status_schema_ready": True,
        "local_report_only": True,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "activation_runtime_transition_allowed": False,
        "activation_controller_runtime_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "status_fields": STATUS_FIELDS,
        "status_example": STATUS_EXAMPLE,
        "input_reports": INPUT_REPORTS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 51 should add a host-app status schema validator that checks local report status fields and keeps all runtime, activation, DriverKit, provider, PCI, BAR, MMIO, and RTX 5070 acceleration paths disabled.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "schema_only": True,
            "local_report_only": True,
            "runtime_buttons_enabled": False,
            "live_system_queries": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
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
    field_rows = [
        f"| `{item['field']}` | `{item['type']}` | `{item['required']}` | `{item['default']}` | {', '.join(item['allowed_values']) if item['allowed_values'] else 'freeform or null'} | {item['ui_purpose']} |"
        for item in data["status_fields"]
    ]
    report_lines = [f"- `{item}`" for item in data["input_reports"]]
    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Host-app Status Schema",
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
            f"Host-app status schema ready: `{data['host_app_status_schema_ready']}`",
            "",
            f"Local report only: `{data['local_report_only']}`",
            "",
            f"Live system queries allowed: `{data['live_system_queries_allowed']}`",
            "",
            f"Runtime buttons enabled: `{data['runtime_buttons_enabled']}`",
            "",
            f"Activation runtime transition allowed: `{data['activation_runtime_transition_allowed']}`",
            "",
            f"Activation request allowed: `{data['activation_request_allowed']}`",
            "",
            f"Manager submit allowed: `{data['manager_submit_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{data['driverkit_target_creation_allowed']}`",
            "",
            f"Provider attach allowed: `{data['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
            "",
            f"Hardware access allowed: `{data['hardware_access_allowed']}`",
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
            "## Status Fields",
            "",
            "| Field | Type | Required | Default | Allowed Values | UI Purpose |",
            "| --- | --- | --- | --- | --- | --- |",
            *field_rows,
            "",
            "## Status Example",
            "",
            "```json",
            json.dumps(data["status_example"], indent=2, sort_keys=True),
            "```",
            "",
            "## Local Input Reports",
            "",
            *report_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is schema-only, local-report-only, and documentation-only.",
            "",
            "It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX host-app status schema.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_schema()

    json_path = out_dir / "host-app-status-schema.json"
    md_path = out_dir / "host-app-status-schema.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
