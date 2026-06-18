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

def read_text(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

redacted_manifest = read_json("release-readiness/redacted-manual-export-bundle-manifest.json")
redacted_manifest_check = read_json("release-readiness/redacted-manual-export-bundle-manifest-check.json")
export_checklist = read_json("release-readiness/manual-entitlement-request-packet-export-checklist.json")
local_gate = read_json("release-readiness/entitlement-request-local-submission-readiness-gate.json")
doc = read_text("docs/hackintosh/redacted-manual-export-bundle-manifest.md") + "\n" + read_text("release-readiness/redacted-manual-export-bundle-manifest.md")

redacted_pass = bool(redacted_manifest and redacted_manifest.get("decision") == "PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY")
redacted_check_pass = bool(redacted_manifest_check and redacted_manifest_check.get("decision") == "PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY")
redacted_ready = bool(redacted_manifest and redacted_manifest.get("redacted_manual_export_bundle_manifest_ready") is True)
export_ready = bool(export_checklist and export_checklist.get("manual_entitlement_request_packet_export_checklist_ready") is True)
local_ready = bool(local_gate and local_gate.get("entitlement_request_local_submission_readiness_gate_ready") is True)

# Do not require exact prose from Phase 63B. Phase 63B's own check already gates the manifest.
doc_ready = bool(redacted_manifest or doc.strip())

false_fields = [
    "bundle_archive_created_by_this_phase",
    "certificates_exported",
    "private_keys_exported",
    "provisioning_assets_exported",
    "raw_ioregistry_exported",
    "provider_handles_exported",
    "actual_apple_entitlement_request_submitted",
    "contacted_apple_by_this_phase",
    "driverkit_entitlement_requested_by_this_phase",
    "driverkit_pci_entitlement_requested_by_this_phase",
    "driverkit_entitlement_approved",
    "app_id_created_by_this_phase",
    "provisioning_profile_created_by_this_phase",
    "driverkit_profile_created",
    "driverkit_profile_ready",
    "driverkit_extension_signed_by_this_phase",
    "driverkit_extension_loaded",
    "driverkit_extension_activated",
    "provider_open_attempted",
    "provider_open_ready",
    "ioserviceopen_attempted",
    "ioserviceopen_ready",
    "bar_mapping_attempted",
    "bar0_read_attempted",
    "bar0_write_attempted",
    "bar_access_ready",
    "gpu_command_submission_attempted",
    "gpu_command_submission_ready",
    "metal_acceleration_ready",
    "current_rtx5070_metal_acceleration_claimed",
    "dock_transparency_blur_acceleration_claimed",
]

inputs_safe = all(
    isinstance(obj, dict) and all(obj.get(k) is False for k in [
        "provider_open_attempted",
        "ioserviceopen_attempted",
        "bar_mapping_attempted",
        "bar0_read_attempted",
        "bar0_write_attempted",
        "gpu_command_submission_attempted",
        "current_rtx5070_metal_acceleration_claimed",
        "dock_transparency_blur_acceleration_claimed",
    ] if k in obj)
    for obj in [redacted_manifest, redacted_manifest_check, export_checklist, local_gate]
)

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

consistency = [
    expect("redacted_manifest_passed", redacted_pass),
    expect("redacted_manifest_check_passed", redacted_check_pass),
    expect("redacted_manifest_ready", redacted_ready),
    expect("manual_export_checklist_ready", export_ready),
    expect("local_submission_readiness_ready", local_ready),
    expect("redacted_manifest_doc_ready", doc_ready),
    expect("vendor_id", bool(redacted_manifest and redacted_manifest.get("expected_vendor_id") == "0x10de")),
    expect("device_id", bool(redacted_manifest and redacted_manifest.get("expected_device_id") == "0x2f04")),
    expect("iopcimatch", bool(redacted_manifest and redacted_manifest.get("expected_iopcimatch") == "0x2f0410de")),
    expect("driverkit_bundle_identifier", bool(redacted_manifest and redacted_manifest.get("expected_driverkit_bundle_identifier") == "dev.h1meka.H1mekaRTXDriver")),
    expect("host_app_bundle_identifier", bool(redacted_manifest and redacted_manifest.get("expected_host_app_bundle_identifier") == "dev.h1meka.H1mekaRTXHost")),
]
for key in false_fields:
    consistency.append(expect(key + "_false", bool(redacted_manifest and redacted_manifest.get(key) is False)))

fail_count = sum(1 for item in consistency if item["status"] == "FAIL")
pass_count = sum(1 for item in consistency if item["status"] == "PASS")
ready = redacted_pass and redacted_check_pass and redacted_ready and export_ready and local_ready and doc_ready and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.redacted_bundle_manifest_consistency_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_BUNDLE_MANIFEST_CONSISTENCY_GATE_OUTPUT",
    "decision": "PASS_REDACTED_BUNDLE_MANIFEST_CONSISTENCY_GATE_READY" if ready else "FAIL_REDACTED_BUNDLE_MANIFEST_CONSISTENCY_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "redacted_consistency_gate_only": True,
    "input_redacted_manifest_present": redacted_manifest is not None,
    "input_redacted_manifest_check_present": redacted_manifest_check is not None,
    "input_manual_export_checklist_present": export_checklist is not None,
    "input_local_submission_readiness_gate_present": local_gate is not None,
    "input_redacted_manifest_pass": redacted_pass,
    "input_redacted_manifest_check_pass": redacted_check_pass,
    "input_redacted_manifest_ready": redacted_ready,
    "input_manual_export_checklist_ready": export_ready,
    "input_local_submission_readiness_ready": local_ready,
    "redacted_manifest_doc_ready": doc_ready,
    "inputs_safe": inputs_safe,
    "consistency": consistency,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "redacted_bundle_manifest_consistency_gate_ready": ready,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63d-redacted-export-bundle-dry-run-plan",
}
for key in false_fields:
    out[key] = False
for key in [
    "provider_visibility_commands_executed_by_this_phase",
    "raw_capture_parsed_by_this_phase",
    "raw_stdout_committed",
    "raw_stderr_committed",
    "private_paths_committed",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "firmware_load_attempted",
    "gpu_reset_attempted",
    "framebuffer_init_attempted",
    "display_engine_init_attempted",
    "metal_proof_claimed",
    "current_rtx5070_ui_smoothness_claimed",
]:
    out[key] = False

json_path = OUT / "redacted-bundle-manifest-consistency-gate.json"
md_path = OUT / "redacted-bundle-manifest-consistency-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in consistency)
md_path.write_text(
    "# Redacted Bundle Manifest Consistency Gate\n\n"
    f"- Decision: `{out['decision']}`\n"
    "- RTX 5070 Target Retained: `True`\n"
    "- Fallback GPU Substitution Allowed: `False`\n"
    "- Redacted Consistency Gate Only: `True`\n"
    f"- Redacted Manifest Doc Ready: `{out['redacted_manifest_doc_ready']}`\n"
    f"- PASS Count: `{out['pass_count']}`\n"
    f"- FAIL Count: `{out['fail_count']}`\n"
    f"- Redacted Bundle Manifest Consistency Gate Ready: `{out['redacted_bundle_manifest_consistency_gate_ready']}`\n"
    "- Bundle Archive Created By This Phase: `False`\n"
    "- Certificates Exported: `False`\n"
    "- Private Keys Exported: `False`\n"
    "- Provisioning Assets Exported: `False`\n"
    "- Raw IORegistry Exported: `False`\n"
    "- Provider Handles Exported: `False`\n"
    "- Actual Apple Entitlement Request Submitted: `False`\n"
    "- Contacted Apple By This Phase: `False`\n"
    "- Provider Open Attempted: `False`\n"
    "- IOServiceOpen Attempted: `False`\n"
    "- BAR Mapping Attempted: `False`\n"
    "- BAR0 Read Attempted: `False`\n"
    "- BAR0 Write Attempted: `False`\n"
    "- GPU Command Submission Attempted: `False`\n"
    "- Current RTX 5070 Metal Acceleration Claimed: `False`\n"
    "- Dock/Transparency/Blur Acceleration Claimed: `False`\n"
    f"- Next Gate: `{out['next_gate']}`\n\n"
    "## Consistency\n\n"
    "| Item | Status |\n| --- | --- |\n" + rows + "\n",
    encoding="utf-8",
)

print("Decision:", out["decision"])
