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
checklist = read_json("release-readiness/entitlement-request-evidence-checklist.json")
checklist_check = read_json("release-readiness/entitlement-request-evidence-checklist-check.json")
notes = read_text("docs/hackintosh/driverkit-entitlement-request-notes-template.md")

skeleton_pass = bool(skeleton and skeleton.get("decision") == "PASS_ENTITLEMENT_REQUEST_PACKAGE_SKELETON_READY")
checklist_pass = bool(checklist and checklist.get("decision") == "PASS_ENTITLEMENT_REQUEST_EVIDENCE_CHECKLIST_READY")
checklist_check_pass = bool(checklist_check and checklist_check.get("decision") == "PASS_ENTITLEMENT_REQUEST_EVIDENCE_CHECKLIST_READY")

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

inputs_safe = safe(skeleton) and safe(checklist) and safe(checklist_check)
notes_ready = all(token in notes for token in [
    "DriverKit Entitlement Request Notes Template",
    "dev.h1meka.H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXHost",
    "0x2f0410de",
])

def eq(name, a, b):
    return {
        "id": name,
        "status": "PASS" if a == b else "FAIL",
        "skeleton": a,
        "checklist": b
    }

consistency = [
    {"id": "skeleton_pass", "status": "PASS" if skeleton_pass else "FAIL"},
    {"id": "checklist_pass", "status": "PASS" if checklist_pass else "FAIL"},
    {"id": "checklist_check_pass", "status": "PASS" if checklist_check_pass else "FAIL"},
    {"id": "request_notes_template_ready", "status": "PASS" if notes_ready else "FAIL"},
    eq("vendor_id", skeleton.get("expected_vendor_id") if skeleton else None, checklist.get("expected_vendor_id") if checklist else None),
    eq("device_id", skeleton.get("expected_device_id") if skeleton else None, checklist.get("expected_device_id") if checklist else None),
    eq("iopcimatch", skeleton.get("expected_iopcimatch") if skeleton else None, checklist.get("expected_iopcimatch") if checklist else None),
    eq("driverkit_bundle_identifier", skeleton.get("expected_driverkit_bundle_identifier") if skeleton else None, checklist.get("expected_driverkit_bundle_identifier") if checklist else None),
    eq("host_app_bundle_identifier", skeleton.get("expected_host_app_bundle_identifier") if skeleton else None, checklist.get("expected_host_app_bundle_identifier") if checklist else None),
    eq("actual_entitlement_request_not_submitted", skeleton.get("actual_apple_entitlement_request_submitted") if skeleton else None, checklist.get("actual_apple_entitlement_request_submitted") if checklist else None),
    eq("driverkit_entitlement_not_requested", skeleton.get("driverkit_entitlement_requested_by_this_phase") if skeleton else None, checklist.get("driverkit_entitlement_requested_by_this_phase") if checklist else None),
    eq("driverkit_profile_not_ready", skeleton.get("driverkit_profile_ready") if skeleton else None, checklist.get("driverkit_profile_ready") if checklist else None),
    eq("provider_open_blocked", skeleton.get("provider_open_ready") if skeleton else None, checklist.get("provider_open_ready") if checklist else None),
    eq("ioserviceopen_blocked", skeleton.get("ioserviceopen_ready") if skeleton else None, checklist.get("ioserviceopen_ready") if checklist else None),
    eq("bar_access_blocked", skeleton.get("bar_access_ready") if skeleton else None, checklist.get("bar_access_ready") if checklist else None),
    eq("gpu_command_submission_blocked", skeleton.get("gpu_command_submission_ready") if skeleton else None, checklist.get("gpu_command_submission_ready") if checklist else None),
    eq("metal_acceleration_not_ready", skeleton.get("metal_acceleration_ready") if skeleton else None, checklist.get("metal_acceleration_ready") if checklist else None),
]

fail_count = sum(1 for item in consistency if item["status"] == "FAIL")
pass_count = sum(1 for item in consistency if item["status"] == "PASS")
ready = skeleton_pass and checklist_pass and checklist_check_pass and notes_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.entitlement_request_package_consistency_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_ENTITLEMENT_REQUEST_PACKAGE_CONSISTENCY_GATE_OUTPUT",
    "decision": "PASS_ENTITLEMENT_REQUEST_PACKAGE_CONSISTENCY_GATE_READY" if ready else "FAIL_ENTITLEMENT_REQUEST_PACKAGE_CONSISTENCY_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "consistency_gate_only": True,
    "input_package_skeleton_present": skeleton is not None,
    "input_checklist_present": checklist is not None,
    "input_checklist_check_present": checklist_check is not None,
    "input_request_notes_template_present": bool(notes),
    "input_package_skeleton_pass": skeleton_pass,
    "input_checklist_pass": checklist_pass,
    "input_checklist_check_pass": checklist_check_pass,
    "request_notes_template_ready": notes_ready,
    "inputs_safe": inputs_safe,
    "consistency": consistency,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "entitlement_request_package_consistency_gate_ready": ready,
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
    "next_gate": "phase62y-entitlement-request-pre-submission-packet-ledger"
}

json_path = OUT / "entitlement-request-package-consistency-gate.json"
md_path = OUT / "entitlement-request-package-consistency-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in consistency)
md_path.write_text(f"""# Entitlement Request Package Consistency Gate

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Consistency Gate Only: `True`
- Package Skeleton PASS: `{out['input_package_skeleton_pass']}`
- Checklist PASS: `{out['input_checklist_pass']}`
- Checklist Check PASS: `{out['input_checklist_check_pass']}`
- Request Notes Template Ready: `{out['request_notes_template_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Entitlement Request Package Consistency Gate Ready: `{out['entitlement_request_package_consistency_gate_ready']}`
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

## Consistency

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
