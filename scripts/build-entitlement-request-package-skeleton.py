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

handoff = read_json("release-readiness/noopen-to-entitlement-request-handoff-ledger.json")
handoff_check = read_json("release-readiness/noopen-to-entitlement-request-handoff-ledger-check.json")

handoff_pass = bool(handoff and handoff.get("decision") == "PASS_NOOPEN_TO_ENTITLEMENT_REQUEST_HANDOFF_LEDGER_READY")
handoff_check_pass = bool(handoff_check and handoff_check.get("decision") == "PASS_NOOPEN_TO_ENTITLEMENT_REQUEST_HANDOFF_LEDGER_READY")
handoff_ready = bool(handoff and handoff.get("noopen_to_entitlement_request_handoff_ready") is True)

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

inputs_safe = safe(handoff) and safe(handoff_check)
skeleton_ready = handoff_pass and handoff_check_pass and handoff_ready and inputs_safe

package_fields = {
    "account_holder_placeholder": "PENDING_NOT_COLLECTED_BY_THIS_PHASE",
    "team_id_placeholder": "PENDING_NOT_COLLECTED_BY_THIS_PHASE",
    "app_id_placeholder": "PENDING_NOT_CREATED_BY_THIS_PHASE",
    "host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "driverkit_base_entitlement_placeholder": "PENDING_NOT_REQUESTED_BY_THIS_PHASE",
    "driverkit_pci_transport_entitlement_placeholder": "PENDING_NOT_REQUESTED_BY_THIS_PHASE",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
}

out = {
    "schema": "h1mekartx.entitlement_request_package_skeleton_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_ENTITLEMENT_REQUEST_PACKAGE_SKELETON_OUTPUT",
    "decision": "PASS_ENTITLEMENT_REQUEST_PACKAGE_SKELETON_READY" if skeleton_ready else "FAIL_ENTITLEMENT_REQUEST_PACKAGE_SKELETON",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "package_skeleton_only": True,
    "input_handoff_ledger_present": handoff is not None,
    "input_handoff_ledger_check_present": handoff_check is not None,
    "input_handoff_ledger_pass": handoff_pass,
    "input_handoff_ledger_check_pass": handoff_check_pass,
    "input_handoff_ready": handoff_ready,
    "inputs_safe": inputs_safe,
    "entitlement_request_package_skeleton_ready": skeleton_ready,
    "package_fields": package_fields,
    "actual_apple_entitlement_request_submitted": False,
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
    "next_gate": "phase62w-entitlement-request-evidence-checklist"
}

json_path = OUT / "entitlement-request-package-skeleton.json"
md_path = OUT / "entitlement-request-package-skeleton.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

field_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in package_fields.items())
md_path.write_text(f"""# Entitlement Request Package Skeleton

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Package Skeleton Only: `True`
- Input Handoff Ledger PASS: `{out['input_handoff_ledger_pass']}`
- Input Handoff Ledger Check PASS: `{out['input_handoff_ledger_check_pass']}`
- Input Handoff Ready: `{out['input_handoff_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- Entitlement Request Package Skeleton Ready: `{out['entitlement_request_package_skeleton_ready']}`
- Actual Apple Entitlement Request Submitted: `False`
- DriverKit Entitlement Requested By This Phase: `False`
- DriverKit PCI Entitlement Requested By This Phase: `False`
- DriverKit Entitlement Approved: `False`
- App ID Created By This Phase: `False`
- Provisioning Profile Created By This Phase: `False`
- DriverKit Profile Created: `False`
- DriverKit Profile Ready: `False`
- DriverKit Extension Signed By This Phase: `False`
- DriverKit Extension Loaded: `False`
- DriverKit Extension Activated: `False`
- Provider Open Ready: `False`
- IOServiceOpen Ready: `False`
- BAR Access Ready: `False`
- GPU Command Submission Ready: `False`
- Metal Acceleration Ready: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Package Fields

| Field | Value |
| --- | --- |
{field_rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
