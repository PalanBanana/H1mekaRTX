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

consistency = read_json("release-readiness/redacted-bundle-manifest-consistency-gate.json")
consistency_check = read_json("release-readiness/redacted-bundle-manifest-consistency-gate-check.json")
manifest = read_json("release-readiness/redacted-manual-export-bundle-manifest.json")
export_checklist = read_json("release-readiness/manual-entitlement-request-packet-export-checklist.json")

consistency_pass = bool(consistency and consistency.get("decision") == "PASS_REDACTED_BUNDLE_MANIFEST_CONSISTENCY_GATE_READY")
consistency_check_pass = bool(consistency_check and consistency_check.get("decision") == "PASS_REDACTED_BUNDLE_MANIFEST_CONSISTENCY_GATE_READY")
consistency_ready = bool(consistency and consistency.get("redacted_bundle_manifest_consistency_gate_ready") is True)
manifest_ready = bool(manifest and manifest.get("redacted_manual_export_bundle_manifest_ready") is True)
export_ready = bool(export_checklist and export_checklist.get("manual_entitlement_request_packet_export_checklist_ready") is True)

include_files = [
    "docs/hackintosh/driverkit-entitlement-request-notes-template.md",
    "release-readiness/entitlement-request-package-skeleton.md",
    "release-readiness/entitlement-request-evidence-checklist.md",
    "release-readiness/entitlement-request-package-consistency-gate.md",
    "release-readiness/entitlement-request-pre-submission-packet-ledger.md",
    "release-readiness/entitlement-request-local-submission-readiness-gate.md",
    "release-readiness/manual-entitlement-request-packet-export-checklist.md",
    "release-readiness/redacted-manual-export-bundle-manifest.md",
    "release-readiness/redacted-bundle-manifest-consistency-gate.md",
]

exclude_labels = [
    "HOST_REPORT_BUNDLE",
    "RAW_STDOUT_STDERR",
    "PRIVATE_LOCAL_PATHS",
    "CERTIFICATES",
    "PRIVATE_KEYS",
    "PROVISIONING_PROFILES",
    "APPLE_ACCOUNT_EMAIL_UNLESS_APPROVED",
    "TEAM_ID_UNLESS_APPROVED",
    "DEVICE_SERIAL_NUMBERS",
    "RAW_IOREGISTRY_DUMPS",
    "BAR_MMIO_DATA",
    "PROVIDER_HANDLES",
    "KERNEL_LOGS_WITH_PRIVATE_PATHS",
]

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

inputs_safe = safe(consistency) and safe(consistency_check) and safe(manifest) and safe(export_checklist)
include_files_exist = all((ROOT / p).exists() for p in include_files)

items = [
    {"id": "redacted_bundle_manifest_consistency_gate_passed", "status": "PASS" if consistency_pass else "FAIL"},
    {"id": "redacted_bundle_manifest_consistency_gate_check_passed", "status": "PASS" if consistency_check_pass else "FAIL"},
    {"id": "redacted_bundle_manifest_consistency_gate_ready", "status": "PASS" if consistency_ready else "FAIL"},
    {"id": "redacted_manifest_ready", "status": "PASS" if manifest_ready else "FAIL"},
    {"id": "manual_export_checklist_ready", "status": "PASS" if export_ready else "FAIL"},
    {"id": "include_files_exist", "status": "PASS" if include_files_exist else "FAIL"},
    {"id": "dry_run_plan_only", "status": "PASS"},
    {"id": "real_archive_not_created", "status": "BLOCKED"},
    {"id": "files_not_copied_by_this_phase", "status": "BLOCKED"},
    {"id": "secrets_not_exported", "status": "BLOCKED"},
    {"id": "apple_request_not_submitted", "status": "BLOCKED"},
    {"id": "provider_open_blocked", "status": "PASS" if manifest and manifest.get("provider_open_attempted") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if manifest and manifest.get("bar_mapping_attempted") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if manifest and manifest.get("gpu_command_submission_attempted") is False else "FAIL"},
    {"id": "metal_acceleration_not_claimed", "status": "PASS" if manifest and manifest.get("current_rtx5070_metal_acceleration_claimed") is False else "FAIL"},
]

fail_count = sum(1 for i in items if i["status"] == "FAIL")
pass_count = sum(1 for i in items if i["status"] == "PASS")
blocked_count = sum(1 for i in items if i["status"] == "BLOCKED")
ready = consistency_pass and consistency_check_pass and consistency_ready and manifest_ready and export_ready and include_files_exist and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.redacted_export_bundle_dry_run_plan_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_EXPORT_BUNDLE_DRY_RUN_PLAN_OUTPUT",
    "decision": "PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_PLAN_READY" if ready else "FAIL_REDACTED_EXPORT_BUNDLE_DRY_RUN_PLAN",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "dry_run_plan_only": True,
    "input_consistency_gate_present": consistency is not None,
    "input_consistency_gate_check_present": consistency_check is not None,
    "input_redacted_manifest_present": manifest is not None,
    "input_manual_export_checklist_present": export_checklist is not None,
    "input_consistency_gate_pass": consistency_pass,
    "input_consistency_gate_check_pass": consistency_check_pass,
    "input_consistency_gate_ready": consistency_ready,
    "input_redacted_manifest_ready": manifest_ready,
    "input_manual_export_checklist_ready": export_ready,
    "include_files": include_files,
    "exclude_labels": exclude_labels,
    "include_files_exist": include_files_exist,
    "inputs_safe": inputs_safe,
    "items": items,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "fail_count": fail_count,
    "redacted_export_bundle_dry_run_plan_ready": ready,
    "bundle_archive_created_by_this_phase": False,
    "files_copied_to_export_bundle_by_this_phase": False,
    "certificates_exported": False,
    "private_keys_exported": False,
    "provisioning_assets_exported": False,
    "raw_ioregistry_exported": False,
    "provider_handles_exported": False,
    "actual_apple_entitlement_request_submitted": False,
    "contacted_apple_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63e-redacted-export-dry-run-plan-consistency-gate",
}

json_path = OUT / "redacted-export-bundle-dry-run-plan.json"
md_path = OUT / "redacted-export-bundle-dry-run-plan.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

include_rows = "\n".join(f"| `{p}` |" for p in include_files)
exclude_rows = "\n".join(f"| `{p}` |" for p in exclude_labels)
item_rows = "\n".join(f"| `{i['id']}` | `{i['status']}` |" for i in items)
md_path.write_text(f"""# Redacted Export Bundle Dry-Run Plan

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Dry-Run Plan Only: `True`
- Consistency Gate PASS: `{out['input_consistency_gate_pass']}`
- Consistency Gate Check PASS: `{out['input_consistency_gate_check_pass']}`
- Consistency Gate Ready: `{out['input_consistency_gate_ready']}`
- Redacted Manifest Ready: `{out['input_redacted_manifest_ready']}`
- Manual Export Checklist Ready: `{out['input_manual_export_checklist_ready']}`
- Include Files Exist: `{out['include_files_exist']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Export Bundle Dry-Run Plan Ready: `{out['redacted_export_bundle_dry_run_plan_ready']}`
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

## Include Files

| File |
| --- |
{include_rows}

## Exclude Labels

| Label |
| --- |
{exclude_rows}

## Items

| Item | Status |
| --- | --- |
{item_rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
