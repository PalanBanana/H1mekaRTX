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

plan = read_json("release-readiness/redacted-export-bundle-dry-run-plan.json")
plan_check = read_json("release-readiness/redacted-export-bundle-dry-run-plan-check.json")
consistency_gate = read_json("release-readiness/redacted-bundle-manifest-consistency-gate.json")
manifest = read_json("release-readiness/redacted-manual-export-bundle-manifest.json")

plan_pass = bool(plan and plan.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_PLAN_READY")
plan_check_pass = bool(plan_check and plan_check.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_PLAN_READY")
plan_ready = bool(plan and plan.get("redacted_export_bundle_dry_run_plan_ready") is True)
consistency_ready = bool(consistency_gate and consistency_gate.get("redacted_bundle_manifest_consistency_gate_ready") is True)
manifest_ready = bool(manifest and manifest.get("redacted_manual_export_bundle_manifest_ready") is True)
include_files_present = bool(plan and isinstance(plan.get("include_files"), list) and len(plan.get("include_files")) >= 3)
exclude_labels_present = bool(plan and isinstance(plan.get("exclude_labels"), list) and len(plan.get("exclude_labels")) >= 3)

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

inputs_safe = safe(plan) and safe(plan_check) and safe(consistency_gate) and safe(manifest)

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

checks = [
    expect("dry_run_plan_passed", plan_pass),
    expect("dry_run_plan_check_passed", plan_check_pass),
    expect("dry_run_plan_ready", plan_ready),
    expect("manifest_consistency_gate_ready", consistency_ready),
    expect("redacted_manifest_ready", manifest_ready),
    expect("include_files_present", include_files_present),
    expect("exclude_labels_present", exclude_labels_present),
]

false_fields = [
    "bundle_archive_created_by_this_phase",
    "files_copied_to_export_bundle_by_this_phase",
    "certificates_exported",
    "private_keys_exported",
    "provisioning_assets_exported",
    "raw_ioregistry_exported",
    "provider_handles_exported",
    "actual_apple_entitlement_request_submitted",
    "contacted_apple_by_this_phase",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar0_read_attempted",
    "bar0_write_attempted",
    "gpu_command_submission_attempted",
    "current_rtx5070_metal_acceleration_claimed",
    "dock_transparency_blur_acceleration_claimed",
]

for field in false_fields:
    checks.append(expect(f"{field}_false", bool(plan and plan.get(field) is False)))

checks.extend([
    expect("vendor_id", bool(plan and plan.get("expected_vendor_id") == "0x10de")),
    expect("device_id", bool(plan and plan.get("expected_device_id") == "0x2f04")),
    expect("iopcimatch", bool(plan and plan.get("expected_iopcimatch") == "0x2f0410de")),
    expect("driverkit_bundle_identifier", bool(plan and plan.get("expected_driverkit_bundle_identifier") == "dev.h1meka.H1mekaRTXDriver")),
    expect("host_app_bundle_identifier", bool(plan and plan.get("expected_host_app_bundle_identifier") == "dev.h1meka.H1mekaRTXHost")),
])

fail_count = sum(1 for i in checks if i["status"] == "FAIL")
pass_count = sum(1 for i in checks if i["status"] == "PASS")
ready = (
    plan_pass
    and plan_check_pass
    and plan_ready
    and consistency_ready
    and manifest_ready
    and include_files_present
    and exclude_labels_present
    and inputs_safe
    and fail_count == 0
)

out = {
    "schema": "h1mekartx.redacted_export_dry_run_plan_consistency_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_OUTPUT",
    "decision": "PASS_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_READY" if ready else "FAIL_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "dry_run_plan_consistency_gate_only": True,
    "input_dry_run_plan_present": plan is not None,
    "input_dry_run_plan_check_present": plan_check is not None,
    "input_manifest_consistency_gate_present": consistency_gate is not None,
    "input_redacted_manifest_present": manifest is not None,
    "input_dry_run_plan_pass": plan_pass,
    "input_dry_run_plan_check_pass": plan_check_pass,
    "input_dry_run_plan_ready": plan_ready,
    "input_manifest_consistency_gate_ready": consistency_ready,
    "input_redacted_manifest_ready": manifest_ready,
    "include_files_present": include_files_present,
    "exclude_labels_present": exclude_labels_present,
    "inputs_safe": inputs_safe,
    "consistency": checks,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "redacted_export_dry_run_plan_consistency_gate_ready": ready,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63f-redacted-export-bundle-dry-run-inventory-ledger",
}
for field in false_fields:
    out[field] = False
for field in [
    "dry_run_plan_only",
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
    "gpu_command_submission_ready",
    "metal_acceleration_ready",
    "metal_proof_claimed",
    "current_rtx5070_ui_smoothness_claimed",
]:
    out[field] = False

json_path = OUT / "redacted-export-dry-run-plan-consistency-gate.json"
md_path = OUT / "redacted-export-dry-run-plan-consistency-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{i['id']}` | `{i['status']}` |" for i in checks)
md_path.write_text(f"""# Redacted Export Dry-Run Plan Consistency Gate

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Dry-Run Plan Consistency Gate Only: `True`
- Dry-Run Plan PASS: `{out['input_dry_run_plan_pass']}`
- Dry-Run Plan Check PASS: `{out['input_dry_run_plan_check_pass']}`
- Dry-Run Plan Ready: `{out['input_dry_run_plan_ready']}`
- Manifest Consistency Gate Ready: `{out['input_manifest_consistency_gate_ready']}`
- Redacted Manifest Ready: `{out['input_redacted_manifest_ready']}`
- Include Files Present: `{out['include_files_present']}`
- Exclude Labels Present: `{out['exclude_labels_present']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Export Dry-Run Plan Consistency Gate Ready: `{out['redacted_export_dry_run_plan_consistency_gate_ready']}`
- Bundle Archive Created By This Phase: `False`
- Files Copied To Export Bundle By This Phase: `False`
- Certificates Exported: `False`
- Private Keys Exported: `False`
- Provisioning Assets Exported: `False`
- Raw IORegistry Exported: `False`
- Provider Handles Exported: `False`
- Actual Apple Entitlement Request Submitted: `False`
- Contacted Apple By This Phase: `False`
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
