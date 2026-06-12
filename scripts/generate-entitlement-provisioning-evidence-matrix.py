#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_provisioning_evidence_matrix.v1"

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
        "id": "apple_developer_program_membership",
        "label": "Apple Developer Program membership",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "Required before relying on Apple-issued signing and profile workflows for driver work."
    },
    {
        "id": "driverkit_entitlement_request",
        "label": "DriverKit entitlement request evidence",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "Apple-granted DriverKit entitlement evidence is required before real driver runtime work."
    },
    {
        "id": "device_interface_entitlement_scope",
        "label": "Device interface entitlement scope",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "The target device/interface entitlement scope must be explicit before any provider/device transition is considered."
    },
    {
        "id": "extension_install_entitlement",
        "label": "Extension install entitlement evidence",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "Host app install entitlement evidence is required before real extension install workflow."
    },
    {
        "id": "bundle_id_pairing",
        "label": "Host app and extension bundle ID pairing",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "Bundle IDs must be planned and matched to the entitlement and profile workflow."
    },
    {
        "id": "driverkit_development_profile",
        "label": "DriverKit development provisioning profile",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "A DriverKit development profile requires the relevant entitlement to be enabled on the Bundle ID."
    },
    {
        "id": "developer_id_distribution_profile",
        "label": "Distribution signing and notarization path",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "NOT_PROVIDED",
        "blocking": True,
        "notes": "Distribution is separate from local UI validation and must not be assumed."
    },
    {
        "id": "local_research_scope_statement",
        "label": "Local research scope statement",
        "required_for_distribution_or_regular_driver_work": False,
        "required_for_local_ui_research": True,
        "current_status": "PRESENT_IN_PROJECT_POLICY",
        "blocking": False,
        "notes": "Current project scope allows UI, reports, local validation, and architecture planning only."
    },
    {
        "id": "metal_injection_runtime_gate",
        "label": "RTX 5070 Metal runtime gate",
        "required_for_distribution_or_regular_driver_work": True,
        "required_for_local_ui_research": False,
        "current_status": "CLOSED",
        "blocking": True,
        "notes": "The Metal runtime gate remains closed until entitlement, profile, provider, device, and hardware-path evidence gates pass."
    }
]


def build_report(root: Path) -> dict[str, Any]:
    blocking_missing = [
        item["id"]
        for item in EVIDENCE_ITEMS
        if item["blocking"] and item["current_status"] != "PROVIDED"
    ]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "target": TARGET,
        "decision": "NOT_READY_ENTITLEMENT_PROVISIONING_EVIDENCE_REQUIRED",
        "plain_answer": "RTX 5070 Metal runtime work cannot start until entitlement and provisioning evidence is provided and validated.",
        "goal": "RTX 5070 Metal full graphics acceleration research path",
        "actual_app_code_continues": False,
        "evidence_matrix_ready": True,
        "blocking_missing_count": len(blocking_missing),
        "blocking_missing": blocking_missing,
        "evidence_items": EVIDENCE_ITEMS,
        "free_account_scope": {
            "local_ui_research": True,
            "static_reports": True,
            "local_json_validation": True,
            "architecture_docs": True,
            "driver_runtime": False,
            "extension_install": False,
            "provider_transition": False,
            "device_ownership_transition": False,
            "metal_runtime": False
        },
        "paid_or_approved_scope_required": {
            "apple_developer_program_membership": True,
            "driverkit_entitlement": True,
            "device_interface_entitlement_scope": True,
            "driverkit_development_profile": True,
            "distribution_profile_or_notarization_path": True
        },
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 67 should add a static contract checker for the entitlement and provisioning evidence matrix. Keep it evidence-only and no-runtime.",
        "safety_boundary": {
            "read_only": True,
            "evidence_matrix_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    rows = []
    for item in data["evidence_items"]:
        rows.append(
            "| `{id}` | {status} | {blocking} | {notes} |".format(
                id=item["id"],
                status=item["current_status"],
                blocking=item["blocking"],
                notes=item["notes"].replace("|", "\\|"),
            )
        )

    return "\n".join(
        [
            "# Entitlement and Provisioning Evidence Matrix",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Goal: {data['goal']}",
            "",
            f"Evidence matrix ready: `{data['evidence_matrix_ready']}`",
            "",
            f"Blocking missing count: `{data['blocking_missing_count']}`",
            "",
            "## Evidence Items",
            "",
            "| ID | Status | Blocking | Notes |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Free Account Scope",
            "",
            f"- Local UI research: `{data['free_account_scope']['local_ui_research']}`",
            f"- Static reports: `{data['free_account_scope']['static_reports']}`",
            f"- Local JSON validation: `{data['free_account_scope']['local_json_validation']}`",
            f"- Architecture docs: `{data['free_account_scope']['architecture_docs']}`",
            f"- Driver runtime: `{data['free_account_scope']['driver_runtime']}`",
            f"- Extension install: `{data['free_account_scope']['extension_install']}`",
            f"- Provider transition: `{data['free_account_scope']['provider_transition']}`",
            f"- Device ownership transition: `{data['free_account_scope']['device_ownership_transition']}`",
            f"- Metal runtime: `{data['free_account_scope']['metal_runtime']}`",
            "",
            "## Paid or Approved Scope Required",
            "",
            f"- Apple Developer Program membership: `{data['paid_or_approved_scope_required']['apple_developer_program_membership']}`",
            f"- DriverKit entitlement: `{data['paid_or_approved_scope_required']['driverkit_entitlement']}`",
            f"- Device interface entitlement scope: `{data['paid_or_approved_scope_required']['device_interface_entitlement_scope']}`",
            f"- DriverKit development profile: `{data['paid_or_approved_scope_required']['driverkit_development_profile']}`",
            f"- Distribution profile or notarization path: `{data['paid_or_approved_scope_required']['distribution_profile_or_notarization_path']}`",
            "",
            "## Metal Goal Tracking",
            "",
            f"- metal_injection_goal: `{data['metal_injection_goal']}`",
            f"- metal_injection_runtime_allowed_now: `{data['metal_injection_runtime_allowed_now']}`",
            f"- rtx5070_metal_runtime_allowed: `{data['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Safety Boundary",
            "",
            "This stage adds an entitlement and provisioning evidence matrix only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate entitlement and provisioning evidence matrix.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_report(root)

    json_path = out_dir / "entitlement-provisioning-evidence-matrix-report.json"
    md_path = out_dir / "entitlement-provisioning-evidence-matrix-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
