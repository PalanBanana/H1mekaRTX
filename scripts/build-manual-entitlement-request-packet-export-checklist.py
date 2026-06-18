#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(rel: str):
    p = ROOT / rel
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))

def read_text(rel: str):
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

local_gate = read_json("release-readiness/entitlement-request-local-submission-readiness-gate.json")
local_gate_check = read_json("release-readiness/entitlement-request-local-submission-readiness-gate-check.json")
packet = read_json("release-readiness/entitlement-request-pre-submission-packet-ledger.json")
consistency = read_json("release-readiness/entitlement-request-package-consistency-gate.json")
checklist = read_json("release-readiness/entitlement-request-evidence-checklist.json")
notes = read_text("docs/hackintosh/driverkit-entitlement-request-notes-template.md")

local_pass = bool(local_gate and local_gate.get("decision") == "PASS_ENTITLEMENT_REQUEST_LOCAL_SUBMISSION_READINESS_GATE_READY")
local_check_pass = bool(local_gate_check and local_gate_check.get("decision") == "PASS_ENTITLEMENT_REQUEST_LOCAL_SUBMISSION_READINESS_GATE_READY")
local_ready = bool(local_gate and local_gate.get("entitlement_request_local_submission_readiness_gate_ready") is True)
packet_ready = bool(packet and packet.get("entitlement_request_pre_submission_packet_ledger_ready") is True)
consistency_ready = bool(consistency and consistency.get("entitlement_request_package_consistency_gate_ready") is True)
checklist_ready = bool(checklist and checklist.get("entitlement_request_evidence_checklist_ready") is True)
notes_ready = all(token in notes for token in [
    "DriverKit Entitlement Request Notes Template",
    "dev.h1meka.H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXHost",
    "0x2f0410de",
])

danger_keys = [
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar0_read_attempted",
    "bar0_write_attempted",
    "gpu_command_submission_attempted",
    "current_rtx5070_metal_acceleration_claimed",
    "dock_transparency_blur_acceleration_claimed",
]

def safe(obj):
    return isinstance(obj, dict) and all(obj.get(k) is False for k in danger_keys if k in obj)

inputs_safe = safe(local_gate) and safe(local_gate_check) and safe(packet) and safe(consistency) and safe(checklist)

items = [
    {"id": "local_submission_readiness_gate_passed", "status": "PASS" if local_pass else "FAIL"},
    {"id": "local_submission_readiness_gate_check_passed", "status": "PASS" if local_check_pass else "FAIL"},
    {"id": "local_submission_readiness_ready", "status": "PASS" if local_ready else "FAIL"},
    {"id": "pre_submission_packet_ledger_ready", "status": "PASS" if packet_ready else "FAIL"},
    {"id": "package_consistency_gate_ready", "status": "PASS" if consistency_ready else "FAIL"},
    {"id": "evidence_checklist_ready", "status": "PASS" if checklist_ready else "FAIL"},
    {"id": "request_notes_template_ready", "status": "PASS" if notes_ready else "FAIL"},
    {"id": "manual_export_required", "status": "PLACEHOLDER"},
    {"id": "manual_redaction_required", "status": "PLACEHOLDER"},
    {"id": "manual_team_id_required", "status": "PLACEHOLDER"},
    {"id": "manual_account_holder_required", "status": "PLACEHOLDER"},
    {"id": "actual_apple_submission_not_performed", "status": "BLOCKED" if local_gate and local_gate.get("actual_apple_entitlement_request_submitted") is False else "FAIL"},
    {"id": "apple_contact_not_performed", "status": "BLOCKED" if local_gate and local_gate.get("contacted_apple_by_this_phase") is False else "FAIL"},
    {"id": "app_id_not_created", "status": "BLOCKED" if local_gate and local_gate.get("app_id_created_by_this_phase") is False else "FAIL"},
    {"id": "provisioning_profile_not_created", "status": "BLOCKED" if local_gate and local_gate.get("provisioning_profile_created_by_this_phase") is False else "FAIL"},
    {"id": "driverkit_extension_not_loaded", "status": "BLOCKED" if local_gate and local_gate.get("driverkit_extension_loaded") is False and local_gate.get("driverkit_extension_activated") is False else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if local_gate and local_gate.get("provider_open_attempted") is False and local_gate.get("provider_open_ready") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if local_gate and local_gate.get("bar_mapping_attempted") is False and local_gate.get("bar_access_ready") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if local_gate and local_gate.get("gpu_command_submission_attempted") is False and local_gate.get("gpu_command_submission_ready") is False else "FAIL"},
    {"id": "metal_acceleration_not_claimed", "status": "PASS" if local_gate and local_gate.get("current_rtx5070_metal_acceleration_claimed") is False and local_gate.get("metal_acceleration_ready") is False else "FAIL"}
]

fail_count = sum(1 for item in items if item["status"] == "FAIL")
pass_count = sum(1 for item in items if item["status"] == "PASS")
blocked_count = sum(1 for item in items if item["status"] == "BLOCKED")
placeholder_count = sum(1 for item in items if item["status"] == "PLACEHOLDER")
ready = local_pass and local_check_pass and local_ready and packet_ready and consistency_ready and checklist_ready and notes_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.manual_entitlement_request_packet_export_checklist_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_MANUAL_ENTITLEMENT_REQUEST_PACKET_EXPORT_CHECKLIST_OUTPUT",
    "decision": "PASS_MANUAL_ENTITLEMENT_REQUEST_PACKET_EXPORT_CHECKLIST_READY" if ready else "FAIL_MANUAL_ENTITLEMENT_REQUEST_PACKET_EXPORT_CHECKLIST",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "manual_export_checklist_only": True,
    "input_local_submission_readiness_gate_present": local_gate is not None,
    "input_local_submission_readiness_gate_check_present": local_gate_check is not None,
    "input_pre_submission_packet_ledger_present": packet is not None,
    "input_package_consistency_gate_present": consistency is not None,
    "input_evidence_checklist_present": checklist is not None,
    "input_request_notes_template_present": bool(notes),
    "input_local_submission_readiness_gate_pass": local_pass,
    "input_local_submission_readiness_gate_check_pass": local_check_pass,
    "input_local_submission_readiness_ready": local_ready,
    "input_pre_submission_packet_ledger_ready": packet_ready,
    "input_package_consistency_gate_ready": consistency_ready,
    "input_evidence_checklist_ready": checklist_ready,
    "request_notes_template_ready": notes_ready,
    "inputs_safe": inputs_safe,
    "items": items,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "placeholder_count": placeholder_count,
    "fail_count": fail_count,
    "manual_entitlement_request_packet_export_checklist_ready": ready,
    "actual_apple_entitlement_request_submitted": False,
    "contacted_apple_by_this_phase": False,
    "driverkit_entitlement_requested_by_this_phase": False,
    "driverkit_pci_entitlement_requested_by_this_phase": False,
    "driverkit_entitlement_approved": False,
    "app_id_created_by_this_phase": False,
    "provisioning_profile_created_by_this_phase": False,
    "driverkit_profile_created": False,
    "driverkit_profile_ready": False,
    "driverkit_extension_signed_by_this_phase": False,
    "driverkit_extension_loaded": False,
    "driverkit_extension_activated": False,
    "provisioning_assets_exported": False,
    "private_keys_exported": False,
    "provider_open_ready": False,
    "ioserviceopen_ready": False,
    "bar_access_ready": False,
    "gpu_command_submission_ready": False,
    "metal_acceleration_ready": False,
    "provider_visibility_commands_executed_by_this_phase": False,
    "raw_capture_parsed_by_this_phase": False,
    "raw_stdout_committed": False,
    "raw_stderr_committed": False,
    "private_paths_committed": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "bar_mmio_mutation_attempted": False,
    "configuration_writes_attempted": False,
    "firmware_load_attempted": False,
    "gpu_reset_attempted": False,
    "framebuffer_init_attempted": False,
    "display_engine_init_attempted": False,
    "gpu_command_submission_attempted": False,
    "metal_proof_claimed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63b-redacted-manual-export-bundle-manifest"
}

json_path = OUT / "manual-entitlement-request-packet-export-checklist.json"
md_path = OUT / "manual-entitlement-request-packet-export-checklist.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in items)
md_path.write_text(f"""# Manual Entitlement Request Packet Export Checklist

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Manual Export Checklist Only: `True`
- Local Submission Readiness Gate PASS: `{out['input_local_submission_readiness_gate_pass']}`
- Local Submission Readiness Gate Check PASS: `{out['input_local_submission_readiness_gate_check_pass']}`
- Local Submission Readiness Ready: `{out['input_local_submission_readiness_ready']}`
- Pre-Submission Packet Ledger Ready: `{out['input_pre_submission_packet_ledger_ready']}`
- Package Consistency Gate Ready: `{out['input_package_consistency_gate_ready']}`
- Evidence Checklist Ready: `{out['input_evidence_checklist_ready']}`
- Request Notes Template Ready: `{out['request_notes_template_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- PLACEHOLDER Count: `{out['placeholder_count']}`
- FAIL Count: `{out['fail_count']}`
- Manual Entitlement Request Packet Export Checklist Ready: `{out['manual_entitlement_request_packet_export_checklist_ready']}`
- Actual Apple Entitlement Request Submitted: `False`
- Contacted Apple By This Phase: `False`
- DriverKit Entitlement Requested By This Phase: `False`
- DriverKit PCI Entitlement Requested By This Phase: `False`
- DriverKit Entitlement Approved: `False`
- App ID Created By This Phase: `False`
- Provisioning Profile Created By This Phase: `False`
- DriverKit Profile Created: `False`
- DriverKit Profile Ready: `False`
- DriverKit Extension Signed/Loaded/Activated: `False`
- Provisioning Assets Exported: `False`
- Private Keys Exported: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Checklist Items

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
