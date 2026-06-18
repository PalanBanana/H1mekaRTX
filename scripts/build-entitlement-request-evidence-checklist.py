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

skeleton = read_json("release-readiness/entitlement-request-package-skeleton.json")
skeleton_check = read_json("release-readiness/entitlement-request-package-skeleton-check.json")
handoff = read_json("release-readiness/noopen-to-entitlement-request-handoff-ledger.json")
notes = read_text("docs/hackintosh/driverkit-entitlement-request-notes-template.md")

skeleton_pass = bool(skeleton and skeleton.get("decision") == "PASS_ENTITLEMENT_REQUEST_PACKAGE_SKELETON_READY")
skeleton_check_pass = bool(skeleton_check and skeleton_check.get("decision") == "PASS_ENTITLEMENT_REQUEST_PACKAGE_SKELETON_READY")
skeleton_ready = bool(skeleton and skeleton.get("entitlement_request_package_skeleton_ready") is True)
handoff_ready = bool(handoff and handoff.get("noopen_to_entitlement_request_handoff_ready") is True)
notes_ready = all(token in notes for token in [
    "DriverKit Entitlement Request Notes Template",
    "dev.h1meka.H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXHost",
    "0x2f0410de",
    "No provider open has been performed",
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

inputs_safe = safe(skeleton) and safe(skeleton_check) and safe(handoff)

checklist = [
    {"id": "apple_developer_team_placeholder", "status": "PLACEHOLDER"},
    {"id": "app_id_placeholder", "status": "PLACEHOLDER"},
    {"id": "host_app_bundle_identifier", "status": "PASS" if skeleton and skeleton.get("expected_host_app_bundle_identifier") == "dev.h1meka.H1mekaRTXHost" else "FAIL"},
    {"id": "driverkit_bundle_identifier", "status": "PASS" if skeleton and skeleton.get("expected_driverkit_bundle_identifier") == "dev.h1meka.H1mekaRTXDriver" else "FAIL"},
    {"id": "driverkit_base_entitlement_placeholder", "status": "PLACEHOLDER"},
    {"id": "driverkit_pci_entitlement_placeholder", "status": "PLACEHOLDER"},
    {"id": "vendor_device_identity", "status": "PASS" if skeleton and skeleton.get("expected_vendor_id") == "0x10de" and skeleton.get("expected_device_id") == "0x2f04" else "FAIL"},
    {"id": "iopcimatch_identity", "status": "PASS" if skeleton and skeleton.get("expected_iopcimatch") == "0x2f0410de" else "FAIL"},
    {"id": "noopen_handoff_ready", "status": "PASS" if handoff_ready else "FAIL"},
    {"id": "package_skeleton_ready", "status": "PASS" if skeleton_ready else "FAIL"},
    {"id": "request_notes_template_ready", "status": "PASS" if notes_ready else "FAIL"},
    {"id": "actual_entitlement_request_not_submitted", "status": "BLOCKED" if skeleton and skeleton.get("actual_apple_entitlement_request_submitted") is False else "FAIL"},
    {"id": "driverkit_entitlement_not_requested_by_this_phase", "status": "BLOCKED" if skeleton and skeleton.get("driverkit_entitlement_requested_by_this_phase") is False else "FAIL"},
    {"id": "provisioning_profile_not_created_by_this_phase", "status": "BLOCKED" if skeleton and skeleton.get("provisioning_profile_created_by_this_phase") is False else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if skeleton and skeleton.get("provider_open_attempted") is False and skeleton.get("provider_open_ready") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if skeleton and skeleton.get("bar_mapping_attempted") is False and skeleton.get("bar_access_ready") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if skeleton and skeleton.get("gpu_command_submission_attempted") is False and skeleton.get("gpu_command_submission_ready") is False else "FAIL"},
    {"id": "metal_acceleration_not_claimed", "status": "PASS" if skeleton and skeleton.get("current_rtx5070_metal_acceleration_claimed") is False and skeleton.get("metal_acceleration_ready") is False else "FAIL"}
]

fail_count = sum(1 for item in checklist if item["status"] == "FAIL")
pass_count = sum(1 for item in checklist if item["status"] == "PASS")
blocked_count = sum(1 for item in checklist if item["status"] == "BLOCKED")
placeholder_count = sum(1 for item in checklist if item["status"] == "PLACEHOLDER")
ready = skeleton_pass and skeleton_check_pass and skeleton_ready and handoff_ready and notes_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.entitlement_request_evidence_checklist_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_ENTITLEMENT_REQUEST_EVIDENCE_CHECKLIST_OUTPUT",
    "decision": "PASS_ENTITLEMENT_REQUEST_EVIDENCE_CHECKLIST_READY" if ready else "FAIL_ENTITLEMENT_REQUEST_EVIDENCE_CHECKLIST",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "evidence_checklist_only": True,
    "input_package_skeleton_present": skeleton is not None,
    "input_package_skeleton_check_present": skeleton_check is not None,
    "input_handoff_ledger_present": handoff is not None,
    "input_request_notes_template_present": bool(notes),
    "input_package_skeleton_pass": skeleton_pass,
    "input_package_skeleton_check_pass": skeleton_check_pass,
    "input_package_skeleton_ready": skeleton_ready,
    "input_handoff_ready": handoff_ready,
    "request_notes_template_ready": notes_ready,
    "inputs_safe": inputs_safe,
    "checklist": checklist,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "placeholder_count": placeholder_count,
    "fail_count": fail_count,
    "entitlement_request_evidence_checklist_ready": ready,
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
    "next_gate": "phase62x-entitlement-request-package-consistency-gate"
}

json_path = OUT / "entitlement-request-evidence-checklist.json"
md_path = OUT / "entitlement-request-evidence-checklist.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in checklist)
md_path.write_text(f"""# Entitlement Request Evidence Checklist

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Evidence Checklist Only: `True`
- Input Package Skeleton PASS: `{out['input_package_skeleton_pass']}`
- Input Package Skeleton Check PASS: `{out['input_package_skeleton_check_pass']}`
- Input Package Skeleton Ready: `{out['input_package_skeleton_ready']}`
- Input Handoff Ready: `{out['input_handoff_ready']}`
- Request Notes Template Ready: `{out['request_notes_template_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- PLACEHOLDER Count: `{out['placeholder_count']}`
- FAIL Count: `{out['fail_count']}`
- Entitlement Request Evidence Checklist Ready: `{out['entitlement_request_evidence_checklist_ready']}`
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

## Checklist

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
