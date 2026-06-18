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

packet = read_json("release-readiness/entitlement-request-pre-submission-packet-ledger.json")
packet_check = read_json("release-readiness/entitlement-request-pre-submission-packet-ledger-check.json")
consistency = read_json("release-readiness/entitlement-request-package-consistency-gate.json")
checklist = read_json("release-readiness/entitlement-request-evidence-checklist.json")
notes = read_text("docs/hackintosh/driverkit-entitlement-request-notes-template.md")

packet_pass = bool(packet and packet.get("decision") == "PASS_ENTITLEMENT_REQUEST_PRE_SUBMISSION_PACKET_LEDGER_READY")
packet_check_pass = bool(packet_check and packet_check.get("decision") == "PASS_ENTITLEMENT_REQUEST_PRE_SUBMISSION_PACKET_LEDGER_READY")
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

inputs_safe = safe(packet) and safe(packet_check) and safe(consistency) and safe(checklist)

gate = [
    {"id": "pre_submission_packet_ledger_passed", "status": "PASS" if packet_pass else "FAIL"},
    {"id": "pre_submission_packet_ledger_check_passed", "status": "PASS" if packet_check_pass else "FAIL"},
    {"id": "pre_submission_packet_ledger_ready", "status": "PASS" if packet_ready else "FAIL"},
    {"id": "consistency_gate_ready", "status": "PASS" if consistency_ready else "FAIL"},
    {"id": "evidence_checklist_ready", "status": "PASS" if checklist_ready else "FAIL"},
    {"id": "request_notes_template_ready", "status": "PASS" if notes_ready else "FAIL"},
    {"id": "manual_team_review_required", "status": "PLACEHOLDER"},
    {"id": "manual_app_id_review_required", "status": "PLACEHOLDER"},
    {"id": "manual_entitlement_scope_review_required", "status": "PLACEHOLDER"},
    {"id": "apple_submission_not_performed", "status": "BLOCKED" if packet and packet.get("actual_apple_entitlement_request_submitted") is False else "FAIL"},
    {"id": "apple_contact_not_performed", "status": "BLOCKED" if packet and packet.get("contacted_apple_by_this_phase") is False else "FAIL"},
    {"id": "app_id_creation_not_performed", "status": "BLOCKED" if packet and packet.get("app_id_created_by_this_phase") is False else "FAIL"},
    {"id": "provisioning_profile_not_created", "status": "BLOCKED" if packet and packet.get("provisioning_profile_created_by_this_phase") is False else "FAIL"},
    {"id": "driverkit_extension_not_loaded", "status": "BLOCKED" if packet and packet.get("driverkit_extension_loaded") is False and packet.get("driverkit_extension_activated") is False else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if packet and packet.get("provider_open_attempted") is False and packet.get("provider_open_ready") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if packet and packet.get("bar_mapping_attempted") is False and packet.get("bar_access_ready") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if packet and packet.get("gpu_command_submission_attempted") is False and packet.get("gpu_command_submission_ready") is False else "FAIL"},
    {"id": "metal_acceleration_not_claimed", "status": "PASS" if packet and packet.get("current_rtx5070_metal_acceleration_claimed") is False and packet.get("metal_acceleration_ready") is False else "FAIL"}
]

fail_count = sum(1 for item in gate if item["status"] == "FAIL")
pass_count = sum(1 for item in gate if item["status"] == "PASS")
blocked_count = sum(1 for item in gate if item["status"] == "BLOCKED")
placeholder_count = sum(1 for item in gate if item["status"] == "PLACEHOLDER")
ready = packet_pass and packet_check_pass and packet_ready and consistency_ready and checklist_ready and notes_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.entitlement_request_local_submission_readiness_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_ENTITLEMENT_REQUEST_LOCAL_SUBMISSION_READINESS_GATE_OUTPUT",
    "decision": "PASS_ENTITLEMENT_REQUEST_LOCAL_SUBMISSION_READINESS_GATE_READY" if ready else "FAIL_ENTITLEMENT_REQUEST_LOCAL_SUBMISSION_READINESS_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "local_readiness_gate_only": True,
    "input_pre_submission_packet_ledger_present": packet is not None,
    "input_pre_submission_packet_ledger_check_present": packet_check is not None,
    "input_consistency_gate_present": consistency is not None,
    "input_checklist_present": checklist is not None,
    "input_request_notes_template_present": bool(notes),
    "input_pre_submission_packet_ledger_pass": packet_pass,
    "input_pre_submission_packet_ledger_check_pass": packet_check_pass,
    "input_pre_submission_packet_ledger_ready": packet_ready,
    "input_consistency_gate_ready": consistency_ready,
    "input_checklist_ready": checklist_ready,
    "request_notes_template_ready": notes_ready,
    "inputs_safe": inputs_safe,
    "gate": gate,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "placeholder_count": placeholder_count,
    "fail_count": fail_count,
    "entitlement_request_local_submission_readiness_gate_ready": ready,
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
    "next_gate": "phase63a-manual-entitlement-request-packet-export-checklist"
}

json_path = OUT / "entitlement-request-local-submission-readiness-gate.json"
md_path = OUT / "entitlement-request-local-submission-readiness-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in gate)
md_path.write_text(f"""# Entitlement Request Local Submission Readiness Gate

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Local Readiness Gate Only: `True`
- Pre-Submission Packet Ledger PASS: `{out['input_pre_submission_packet_ledger_pass']}`
- Pre-Submission Packet Ledger Check PASS: `{out['input_pre_submission_packet_ledger_check_pass']}`
- Pre-Submission Packet Ledger Ready: `{out['input_pre_submission_packet_ledger_ready']}`
- Consistency Gate Ready: `{out['input_consistency_gate_ready']}`
- Evidence Checklist Ready: `{out['input_checklist_ready']}`
- Request Notes Template Ready: `{out['request_notes_template_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- PLACEHOLDER Count: `{out['placeholder_count']}`
- FAIL Count: `{out['fail_count']}`
- Entitlement Request Local Submission Readiness Gate Ready: `{out['entitlement_request_local_submission_readiness_gate_ready']}`
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
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Gate

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
