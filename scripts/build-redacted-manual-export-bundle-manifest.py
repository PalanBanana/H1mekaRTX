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

export_checklist = read_json("release-readiness/manual-entitlement-request-packet-export-checklist.json")
export_check = read_json("release-readiness/manual-entitlement-request-packet-export-checklist-check.json")
local_gate = read_json("release-readiness/entitlement-request-local-submission-readiness-gate.json")
packet = read_json("release-readiness/entitlement-request-pre-submission-packet-ledger.json")
evidence = read_json("release-readiness/entitlement-request-evidence-checklist.json")
notes = read_text("docs/hackintosh/driverkit-entitlement-request-notes-template.md")

export_pass = bool(export_checklist and export_checklist.get("decision") == "PASS_MANUAL_ENTITLEMENT_REQUEST_PACKET_EXPORT_CHECKLIST_READY")
export_check_pass = bool(export_check and export_check.get("decision") == "PASS_MANUAL_ENTITLEMENT_REQUEST_PACKET_EXPORT_CHECKLIST_READY")
export_ready = bool(export_checklist and export_checklist.get("manual_entitlement_request_packet_export_checklist_ready") is True)
local_ready = bool(local_gate and local_gate.get("entitlement_request_local_submission_readiness_gate_ready") is True)
packet_ready = bool(packet and packet.get("entitlement_request_pre_submission_packet_ledger_ready") is True)
evidence_ready = bool(evidence and evidence.get("entitlement_request_evidence_checklist_ready") is True)
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

inputs_safe = safe(export_checklist) and safe(export_check) and safe(local_gate) and safe(packet) and safe(evidence)

included_files = [
    "docs/hackintosh/driverkit-entitlement-request-notes-template.md",
    "release-readiness/entitlement-request-package-skeleton.md",
    "release-readiness/entitlement-request-evidence-checklist.md",
    "release-readiness/entitlement-request-package-consistency-gate.md",
    "release-readiness/entitlement-request-pre-submission-packet-ledger.md",
    "release-readiness/entitlement-request-local-submission-readiness-gate.md",
    "release-readiness/manual-entitlement-request-packet-export-checklist.md"
]

excluded_patterns = [
    "HOST_REPORT_BUNDLE_TOKEN",
    "raw stdout",
    "raw stderr",
    "IORegistry raw",
    "private key",
    "certificate",
    "provisioning profile",
    "PRIVATE_HOME_PATH_TOKEN",
    "PRIVATE_VAR_FOLDERS_TOKEN",
    "VAR_FOLDERS_TOKEN",
    "provider handle",
    "BAR dump",
    "MMIO dump"
]

items = [
    {"id": "manual_export_checklist_passed", "status": "PASS" if export_pass else "FAIL"},
    {"id": "manual_export_check_passed", "status": "PASS" if export_check_pass else "FAIL"},
    {"id": "manual_export_checklist_ready", "status": "PASS" if export_ready else "FAIL"},
    {"id": "local_submission_readiness_gate_ready", "status": "PASS" if local_ready else "FAIL"},
    {"id": "pre_submission_packet_ready", "status": "PASS" if packet_ready else "FAIL"},
    {"id": "evidence_checklist_ready", "status": "PASS" if evidence_ready else "FAIL"},
    {"id": "request_notes_template_ready", "status": "PASS" if notes_ready else "FAIL"},
    {"id": "future_manual_redaction_required", "status": "PLACEHOLDER"},
    {"id": "future_manual_bundle_creation_required", "status": "PLACEHOLDER"},
    {"id": "bundle_archive_not_created_by_this_phase", "status": "BLOCKED"},
    {"id": "certificates_not_exported", "status": "BLOCKED"},
    {"id": "private_keys_not_exported", "status": "BLOCKED"},
    {"id": "provisioning_assets_not_exported", "status": "BLOCKED"},
    {"id": "raw_ioregistry_not_exported", "status": "BLOCKED"},
    {"id": "actual_apple_submission_not_performed", "status": "BLOCKED" if export_checklist and export_checklist.get("actual_apple_entitlement_request_submitted") is False else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if export_checklist and export_checklist.get("provider_open_attempted") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if export_checklist and export_checklist.get("bar_mapping_attempted") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if export_checklist and export_checklist.get("gpu_command_submission_attempted") is False else "FAIL"},
    {"id": "metal_acceleration_not_claimed", "status": "PASS" if export_checklist and export_checklist.get("current_rtx5070_metal_acceleration_claimed") is False else "FAIL"}
]

fail_count = sum(1 for item in items if item["status"] == "FAIL")
pass_count = sum(1 for item in items if item["status"] == "PASS")
blocked_count = sum(1 for item in items if item["status"] == "BLOCKED")
placeholder_count = sum(1 for item in items if item["status"] == "PLACEHOLDER")
ready = export_pass and export_check_pass and export_ready and local_ready and packet_ready and evidence_ready and notes_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.redacted_manual_export_bundle_manifest_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_OUTPUT",
    "decision": "PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY" if ready else "FAIL_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "redacted_manifest_only": True,
    "input_manual_export_checklist_present": export_checklist is not None,
    "input_manual_export_check_present": export_check is not None,
    "input_local_submission_readiness_gate_present": local_gate is not None,
    "input_pre_submission_packet_present": packet is not None,
    "input_evidence_checklist_present": evidence is not None,
    "input_request_notes_template_present": bool(notes),
    "input_manual_export_checklist_pass": export_pass,
    "input_manual_export_check_pass": export_check_pass,
    "input_manual_export_checklist_ready": export_ready,
    "input_local_submission_readiness_ready": local_ready,
    "input_pre_submission_packet_ready": packet_ready,
    "input_evidence_checklist_ready": evidence_ready,
    "request_notes_template_ready": notes_ready,
    "inputs_safe": inputs_safe,
    "included_files": included_files,
    "excluded_patterns": excluded_patterns,
    "items": items,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "placeholder_count": placeholder_count,
    "fail_count": fail_count,
    "redacted_manual_export_bundle_manifest_ready": ready,
    "bundle_archive_created_by_this_phase": False,
    "certificates_exported": False,
    "private_keys_exported": False,
    "provisioning_assets_exported": False,
    "raw_ioregistry_exported": False,
    "provider_handles_exported": False,
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
    "next_gate": "phase63c-redacted-bundle-manifest-consistency-gate"
}

json_path = OUT / "redacted-manual-export-bundle-manifest.json"
md_path = OUT / "redacted-manual-export-bundle-manifest.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

included_rows = "\n".join(f"| `{p}` |" for p in included_files)
excluded_rows = "\n".join(f"| `{p}` |" for p in excluded_patterns)
item_rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in items)
md_path.write_text(f"""# Redacted Manual Export Bundle Manifest

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Redacted Manifest Only: `True`
- Manual Export Checklist PASS: `{out['input_manual_export_checklist_pass']}`
- Manual Export Check PASS: `{out['input_manual_export_check_pass']}`
- Manual Export Checklist Ready: `{out['input_manual_export_checklist_ready']}`
- Local Submission Readiness Ready: `{out['input_local_submission_readiness_ready']}`
- Pre-Submission Packet Ready: `{out['input_pre_submission_packet_ready']}`
- Evidence Checklist Ready: `{out['input_evidence_checklist_ready']}`
- Request Notes Template Ready: `{out['request_notes_template_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- PLACEHOLDER Count: `{out['placeholder_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Manual Export Bundle Manifest Ready: `{out['redacted_manual_export_bundle_manifest_ready']}`
- Bundle Archive Created By This Phase: `False`
- Certificates Exported: `False`
- Private Keys Exported: `False`
- Provisioning Assets Exported: `False`
- Raw IORegistry Exported: `False`
- Provider Handles Exported: `False`
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

## Included Files

| File |
| --- |
{included_rows}

## Excluded Patterns

| Excluded |
| --- |
{excluded_rows}

## Items

| Item | Status |
| --- | --- |
{item_rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
