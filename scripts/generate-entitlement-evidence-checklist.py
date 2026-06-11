#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_evidence_checklist.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

EVIDENCE_ITEMS = [
    {
        "id": "EEC-001",
        "area": "Apple Developer identity",
        "status": "NEEDS_USER_EVIDENCE",
        "required": True,
        "private_data_policy": "Do not commit Team ID, certificate serials, account emails, private keys, or provisioning profile contents.",
        "evidence_to_collect": [
            "Developer account membership status confirmed by the user",
            "team role that can request needed entitlements confirmed by the user",
            "private Team ID stored outside the repository",
            "account expiration risk noted outside the repository",
        ],
    },
    {
        "id": "EEC-002",
        "area": "DriverKit entitlement approval",
        "status": "NEEDS_USER_EVIDENCE",
        "required": True,
        "private_data_policy": "Do not commit entitlement approval emails or portal screenshots containing account identifiers.",
        "evidence_to_collect": [
            "DriverKit entitlement request status",
            "approved bundle scope if approval exists",
            "rejection or pending status if approval does not exist",
            "date of last entitlement review by the user",
        ],
    },
    {
        "id": "EEC-003",
        "area": "PCI transport entitlement approval",
        "status": "NEEDS_USER_EVIDENCE",
        "required": True,
        "private_data_policy": "Do not commit signed entitlement files or provisioning payloads.",
        "evidence_to_collect": [
            "PCI transport entitlement availability",
            "vendor/device/subsystem matching plan",
            "exact RTX 5070 identity values",
            "wrong-device match denial rule",
        ],
    },
    {
        "id": "EEC-004",
        "area": "Host app bundle identity",
        "status": "NEEDS_USER_EVIDENCE",
        "required": True,
        "private_data_policy": "Do not commit personal developer identifiers.",
        "evidence_to_collect": [
            "host app bundle identifier reserved",
            "host app signing team selected outside repository",
            "host app distribution mode documented",
            "no activation runtime path by default",
        ],
    },
    {
        "id": "EEC-005",
        "area": "Driver extension bundle identity",
        "status": "NEEDS_USER_EVIDENCE",
        "required": True,
        "private_data_policy": "Do not commit signed dext artifacts.",
        "evidence_to_collect": [
            "dext bundle identifier reserved",
            "dext embedding plan documented",
            "dext signing plan documented",
            "activation request still prohibited",
        ],
    },
    {
        "id": "EEC-006",
        "area": "Signing certificate and provisioning evidence",
        "status": "NEEDS_USER_EVIDENCE",
        "required": True,
        "private_data_policy": "Do not commit certificates, private keys, provisioning profiles, or account screenshots.",
        "evidence_to_collect": [
            "Developer ID Application signing path documented",
            "provisioning profile strategy documented",
            "certificate expiration tracked outside repository",
            "notarization requirement noted",
        ],
    },
    {
        "id": "EEC-007",
        "area": "System Extension request boundary",
        "status": "BLOCKED_BY_POLICY",
        "required": True,
        "private_data_policy": "No request or submit code belongs in this stage.",
        "evidence_to_collect": [
            "activation request object creation remains forbidden",
            "deactivation request object creation remains forbidden",
            "manager submit call remains forbidden",
            "user approval behavior documented later, not implemented now",
        ],
    },
    {
        "id": "EEC-008",
        "area": "Provider matching and device ownership boundary",
        "status": "BLOCKED_BY_POLICY",
        "required": True,
        "private_data_policy": "No live provider ownership data belongs in this stage.",
        "evidence_to_collect": [
            "provider match plan only",
            "no device ownership request",
            "no provider attach",
            "no live PCI probing",
        ],
    },
    {
        "id": "EEC-009",
        "area": "Hardware access boundary",
        "status": "BLOCKED_BY_POLICY",
        "required": True,
        "private_data_policy": "No hardware dump or MMIO/BAR data belongs in this stage.",
        "evidence_to_collect": [
            "no PCI config-space reads",
            "no PCI config-space writes",
            "no MMIO reads",
            "no MMIO writes",
            "no BAR mapping",
        ],
    },
    {
        "id": "EEC-010",
        "area": "Repository hygiene",
        "status": "PASS",
        "required": False,
        "private_data_policy": "Generated local checklists may be committed; private evidence must not be committed.",
        "evidence_to_collect": [
            "checklist generator exists",
            "checklist checker exists",
            "private data policy exists",
            "activation and hardware paths remain forbidden",
        ],
    },
]

PRIVATE_DATA_FORBIDDEN_IN_REPO = [
    "Apple Developer account email",
    "Team ID",
    "certificate private key",
    "certificate serial number",
    "provisioning profile contents",
    "signed app bundle",
    "signed driver extension bundle",
    "notarization ticket",
    "entitlement approval screenshot with account identity",
    "Apple portal screenshot with private identifiers",
]

FORBIDDEN_NOW = [
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
    "creating DriverKit target",
    "installing DriverKit dext",
    "activating DriverKit",
    "requesting device ownership",
    "attaching to PCI provider",
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


def build_checklist() -> dict[str, Any]:
    required_items = [item for item in EVIDENCE_ITEMS if item["required"]]
    missing_or_blocked = [
        item for item in required_items
        if item["status"] != "PASS"
    ]
    optional_pass = [
        item for item in EVIDENCE_ITEMS
        if not item["required"] and item["status"] == "PASS"
    ]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "ENTITLEMENT_EVIDENCE_CHECKLIST_READY_NEEDS_USER_EVIDENCE",
        "plain_answer": "Collect entitlement and signing evidence next; do not create activation code yet.",
        "full_metal_goal": True,
        "research_continues": True,
        "host_side_tooling_started": True,
        "entitlement_evidence_checklist_ready": True,
        "required_item_count": len(required_items),
        "required_missing_or_blocked_count": len(missing_or_blocked),
        "optional_pass_count": len(optional_pass),
        "activation_implementation_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "driverkit_activation_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "evidence_items": EVIDENCE_ITEMS,
        "private_data_forbidden_in_repo": PRIVATE_DATA_FORBIDDEN_IN_REPO,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 42 should add a provider-match dry-run spec without creating DriverKit targets, activation requests, device ownership requests, PCI config access, BAR mapping, or MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "checklist_only": True,
            "collects_private_evidence": False,
            "stores_private_evidence_in_repo": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
            "creates_driverkit_target": False,
            "driverkit_activation": False,
            "driverkit_dext_installation": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
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
    evidence_rows = []
    for item in data["evidence_items"]:
        evidence = "<br>".join(item["evidence_to_collect"])
        evidence_rows.append(
            f"| `{item['id']}` | {item['area']} | `{item['required']}` | `{item['status']}` | {evidence} | {item['private_data_policy']} |"
        )

    private_lines = [f"- {item}" for item in data["private_data_forbidden_in_repo"]]
    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Entitlement Evidence Checklist",
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
            f"Checklist ready: `{data['entitlement_evidence_checklist_ready']}`",
            "",
            f"Required item count: `{data['required_item_count']}`",
            "",
            f"Required missing or blocked count: `{data['required_missing_or_blocked_count']}`",
            "",
            f"Optional pass count: `{data['optional_pass_count']}`",
            "",
            f"Activation implementation allowed: `{data['activation_implementation_allowed']}`",
            "",
            f"Activation request allowed: `{data['activation_request_allowed']}`",
            "",
            f"Manager submit allowed: `{data['manager_submit_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{data['driverkit_target_creation_allowed']}`",
            "",
            f"DriverKit activation allowed: `{data['driverkit_activation_allowed']}`",
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
            "## Evidence Items",
            "",
            "| ID | Area | Required | Status | Evidence To Collect | Private Data Policy |",
            "| --- | --- | --- | --- | --- | --- |",
            *evidence_rows,
            "",
            "## Private Data Forbidden In Repository",
            "",
            *private_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is checklist-only and documentation-only.",
            "",
            "It does not collect private Apple Developer evidence into the repository. It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, create a DriverKit target, activate DriverKit, install a DriverKit dext, request device ownership, attach to a PCI provider, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX entitlement evidence checklist."
    )
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_checklist()

    json_path = out_dir / "entitlement-evidence-checklist.json"
    md_path = out_dir / "entitlement-evidence-checklist.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
