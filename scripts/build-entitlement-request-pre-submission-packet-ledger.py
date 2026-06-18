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

consistency = read_json("release-readiness/entitlement-request-package-consistency-gate.json")
consistency_check = read_json("release-readiness/entitlement-request-package-consistency-gate-check.json")
skeleton = read_json("release-readiness/entitlement-request-package-skeleton.json")
checklist = read_json("release-readiness/entitlement-request-evidence-checklist.json")
notes = read_text("docs/hackintosh/driverkit-entitlement-request-notes-template.md")

consistency_pass = bool(consistency and consistency.get("decision") == "PASS_ENTITLEMENT_REQUEST_PACKAGE_CONSISTENCY_GATE_READY")
consistency_check_pass = bool(consistency_check and consistency_check.get("decision") == "PASS_ENTITLEMENT_REQUEST_PACKAGE_CONSISTENCY_GATE_READY")
consistency_ready = bool(consistency and consistency.get("entitlement_request_package_consistency_gate_ready") is True)
skeleton_ready = bool(skeleton and skeleton.get("entitlement_request_package_skeleton_ready") is True)
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

inputs_safe = safe(consistency) and safe(consistency_check) and safe(skeleton) and safe(checklist)

packet = [
    {"id": "consistency_gate_passed", "status": "PASS" if consistency_pass else "FAIL"},
    {"id": "consistency_gate_check_passed", "status": "PASS" if consistency_check_pass else "FAIL"},
    {"id": "consistency_gate_ready", "status": "PASS" if consistency_ready else "FAIL"},
    {"id": "package_skeleton_ready", "status": "PASS" if skeleton_ready else "FAIL"},
    {"id": "evidence_checklist_ready", "status": "PASS" if checklist_ready else "FAIL"},
    {"id": "request_notes_template_ready", "status": "PASS" if notes_ready else "FAIL"},
    {"id": "apple_developer_team_placeholder", "status": "PLACEHOLDER"},
    {"id": "app_id_placeholder", "status": "PLACEHOLDER"},
    {"id": "driverkit_base_entitlement_placeholder", "status": "PLACEHOLDER"},
    {"id": "driverkit_pci_entitlement_placeholder", "status": "PLACEHOLDER"},
    {"id": "actual_entitlement_request_not_submitted", "status": "BLOCKED" if consistency and consistency.get("actual_apple_entitlement_request_submitted") is False else "FAIL"},
    {"id": "apple_not_contacted", "status": "BLOCKED" if consistency and consistency.get("contacted_apple_by_this_phase") is False else "FAIL"},
    {"id": "app_id_not_created", "status": "BLOCKED" if consistency and consistency.get("app_id_created_by_this_phase") is False else "FAIL"},
    {"id": "provisioning_profile_not_created", "status": "BLOCKED" if consistency and consistency.get("provisioning_profile_created_by_this_phase") is False else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if consistency and consistency.get("provider_open_attempted") is False and consistency.get("provider_open_ready") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if consistency and consistency.get("bar_mapping_attempted") is False and consistency.get("bar_access_ready") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if consistency and consistency.get("gpu_command_submission_attempted") is False and consistency.get("gpu_command_submission_ready") is False else "FAIL"},
    {"id": "metal_acceleration_not_claimed", "status": "PASS" if consistency and consistency.get("current_rtx5070_metal_acceleration_claimed") is False and consistency.get("metal_acceleration_ready") is False else "FAIL"}
]

fail_count = sum(1 for item in packet if item["status"] == "FAIL")
pass_count = sum(1 for item in packet if item["status"] == "PASS")
blocked_count = sum(1 for item in packet if item["status"] == "BLOCKED")
placeholder_count = sum(1 for item in packet if item["status"] == "PLACEHOLDER")
ready = consistency_pass and consistency_check_pass and consistency_ready and skeleton_ready and checklist_ready and notes_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.entitlement_request_pre_submission_packet_ledger_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_ENTITLEMENT_REQUEST_PRE_SUBMISSION_PACKET_LEDGER_OUTPUT",
    "decision": "PASS_ENTITLEMENT_REQUEST_PRE_SUBMISSION_PACKET_LEDGER_READY" if ready else "FAIL_ENTITLEMENT_REQUEST_PRE_SUBMISSION_PACKET_LEDGER",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "pre_submission_ledger_only": True,
    "input_consistency_gate_present": consistency is not None,
    "input_consistency_gate_check_present": consistency_check is not None,
    "input_package_skeleton_present": skeleton is not None,
    "input_checklist_present": checklist is not None,
    "input_request_notes_template_present": bool(notes),
    "input_consistency_gate_pass": consistency_pass,
    "input_consistency_gate_check_pass": consistency_check_pass,
    "input_consistency_gate_ready": consistency_ready,
    "input_package_skeleton_ready": skeleton_ready,
    "input_checklist_ready": checklist_ready,
    "request_notes_template_ready": notes_ready,
    "inputs_safe": inputs_safe,
    "packet": packet,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "placeholder_count": placeholder_count,
    "fail_count": fail_count,
    "entitlement_request_pre_submission_packet_ledger_ready": ready,
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
    "next_gate": "phase62z-entitlement-request-local-submission-readiness-gate"
}

json_path = OUT / "entitlement-request-pre-submission-packet-ledger.json"
md_path = OUT / "entitlement-request-pre-submission-packet-ledger.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in packet)
md_path.write_text(f"""# Entitlement Request Pre-Submission Packet Ledger

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Pre-Submission Ledger Only: `True`
- Consistency Gate PASS: `{out['input_consistency_gate_pass']}`
- Consistency Gate Check PASS: `{out['input_consistency_gate_check_pass']}`
- Consistency Gate Ready: `{out['input_consistency_gate_ready']}`
- Package Skeleton Ready: `{out['input_package_skeleton_ready']}`
- Evidence Checklist Ready: `{out['input_checklist_ready']}`
- Request Notes Template Ready: `{out['request_notes_template_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- PLACEHOLDER Count: `{out['placeholder_count']}`
- FAIL Count: `{out['fail_count']}`
- Entitlement Request Pre-Submission Packet Ledger Ready: `{out['entitlement_request_pre_submission_packet_ledger_ready']}`
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

## Packet

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
