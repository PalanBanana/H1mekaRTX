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

inventory_ledger = read_json("release-readiness/redacted-export-bundle-dry-run-inventory-ledger.json")
inventory_check = read_json("release-readiness/redacted-export-bundle-dry-run-inventory-ledger-check.json")
plan_gate = read_json("release-readiness/redacted-export-dry-run-plan-consistency-gate.json")
dry_run_plan = read_json("release-readiness/redacted-export-bundle-dry-run-plan.json")

ledger_pass = bool(inventory_ledger and inventory_ledger.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER_READY")
ledger_check_pass = bool(inventory_check and inventory_check.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER_READY")
ledger_ready = bool(inventory_ledger and inventory_ledger.get("redacted_export_bundle_dry_run_inventory_ledger_ready") is True)
plan_gate_ready = bool(plan_gate and plan_gate.get("redacted_export_dry_run_plan_consistency_gate_ready") is True)
dry_run_plan_ready = bool(dry_run_plan and dry_run_plan.get("redacted_export_bundle_dry_run_plan_ready") is True)

inventory = inventory_ledger.get("inventory", []) if isinstance(inventory_ledger, dict) else []
inventory_count = inventory_ledger.get("inventory_count") if isinstance(inventory_ledger, dict) else None
inventory_present = bool(inventory)
inventory_count_matches = inventory_present and inventory_count == len(inventory)
inventory_all_exist = bool(inventory_ledger and inventory_ledger.get("inventory_all_exist") is True and all(i.get("exists") is True for i in inventory))
inventory_all_relative = bool(inventory_ledger and inventory_ledger.get("inventory_all_relative") is True and all(i.get("is_relative_path") is True for i in inventory))
inventory_forbidden_absent = bool(inventory_ledger and inventory_ledger.get("inventory_forbidden_absent") is True and all(i.get("forbidden_by_label") is False for i in inventory))
inventory_all_not_copied = bool(inventory_ledger and inventory_ledger.get("inventory_all_not_copied") is True and all(i.get("copied_by_this_phase") is False and i.get("archived_by_this_phase") is False for i in inventory))
inventory_sha256_present = inventory_present and all(isinstance(i.get("sha256"), str) and len(i.get("sha256")) == 64 for i in inventory)
inventory_byte_count_present = inventory_present and all(isinstance(i.get("byte_count"), int) and i.get("byte_count") >= 0 for i in inventory)
exclude_labels_present = bool(inventory_ledger and inventory_ledger.get("exclude_labels_present") is True)

forbidden_output_tokens = ["/Users/", "/private/var/folders/", "/var/folders/"]
output_text = json.dumps(inventory_ledger or {}, sort_keys=True)
private_paths_absent = all(token not in output_text for token in forbidden_output_tokens)

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

inputs_safe = safe(inventory_ledger) and safe(inventory_check) and safe(plan_gate) and safe(dry_run_plan)

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

checks = [
    expect("inventory_ledger_passed", ledger_pass),
    expect("inventory_ledger_check_passed", ledger_check_pass),
    expect("inventory_ledger_ready", ledger_ready),
    expect("plan_consistency_gate_ready", plan_gate_ready),
    expect("dry_run_plan_ready", dry_run_plan_ready),
    expect("inventory_present", inventory_present),
    expect("inventory_count_matches", inventory_count_matches),
    expect("inventory_all_exist", inventory_all_exist),
    expect("inventory_all_relative", inventory_all_relative),
    expect("inventory_forbidden_absent", inventory_forbidden_absent),
    expect("inventory_all_not_copied", inventory_all_not_copied),
    expect("inventory_sha256_present", inventory_sha256_present),
    expect("inventory_byte_count_present", inventory_byte_count_present),
    expect("exclude_labels_present", exclude_labels_present),
    expect("private_paths_absent", private_paths_absent),
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
    "absolute_paths_recorded",
]

for field in false_fields:
    checks.append(expect(f"{field}_false", bool(inventory_ledger and inventory_ledger.get(field) is False)))

checks.extend([
    expect("vendor_id", bool(inventory_ledger and inventory_ledger.get("expected_vendor_id") == "0x10de")),
    expect("device_id", bool(inventory_ledger and inventory_ledger.get("expected_device_id") == "0x2f04")),
    expect("iopcimatch", bool(inventory_ledger and inventory_ledger.get("expected_iopcimatch") == "0x2f0410de")),
    expect("driverkit_bundle_identifier", bool(inventory_ledger and inventory_ledger.get("expected_driverkit_bundle_identifier") == "dev.h1meka.H1mekaRTXDriver")),
    expect("host_app_bundle_identifier", bool(inventory_ledger and inventory_ledger.get("expected_host_app_bundle_identifier") == "dev.h1meka.H1mekaRTXHost")),
])

fail_count = sum(1 for item in checks if item["status"] == "FAIL")
pass_count = sum(1 for item in checks if item["status"] == "PASS")
ready = (
    ledger_pass
    and ledger_check_pass
    and ledger_ready
    and plan_gate_ready
    and dry_run_plan_ready
    and inventory_present
    and inventory_count_matches
    and inventory_all_exist
    and inventory_all_relative
    and inventory_forbidden_absent
    and inventory_all_not_copied
    and inventory_sha256_present
    and inventory_byte_count_present
    and exclude_labels_present
    and private_paths_absent
    and inputs_safe
    and fail_count == 0
)

out = {
    "schema": "h1mekartx.redacted_export_inventory_consistency_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_EXPORT_INVENTORY_CONSISTENCY_GATE_OUTPUT",
    "decision": "PASS_REDACTED_EXPORT_INVENTORY_CONSISTENCY_GATE_READY" if ready else "FAIL_REDACTED_EXPORT_INVENTORY_CONSISTENCY_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "export_inventory_consistency_gate_only": True,
    "input_inventory_ledger_present": inventory_ledger is not None,
    "input_inventory_ledger_check_present": inventory_check is not None,
    "input_plan_consistency_gate_present": plan_gate is not None,
    "input_dry_run_plan_present": dry_run_plan is not None,
    "input_inventory_ledger_pass": ledger_pass,
    "input_inventory_ledger_check_pass": ledger_check_pass,
    "input_inventory_ledger_ready": ledger_ready,
    "input_plan_consistency_gate_ready": plan_gate_ready,
    "input_dry_run_plan_ready": dry_run_plan_ready,
    "inventory_count": inventory_count,
    "inventory_entry_count": len(inventory),
    "inventory_present": inventory_present,
    "inventory_count_matches": inventory_count_matches,
    "inventory_all_exist": inventory_all_exist,
    "inventory_all_relative": inventory_all_relative,
    "inventory_forbidden_absent": inventory_forbidden_absent,
    "inventory_all_not_copied": inventory_all_not_copied,
    "inventory_sha256_present": inventory_sha256_present,
    "inventory_byte_count_present": inventory_byte_count_present,
    "exclude_labels_present": exclude_labels_present,
    "private_paths_absent": private_paths_absent,
    "inputs_safe": inputs_safe,
    "consistency": checks,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "redacted_export_inventory_consistency_gate_ready": ready,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63h-redacted-export-bundle-assembly-dry-run-manifest",
}
for field in false_fields:
    out[field] = False
for field in [
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

json_path = OUT / "redacted-export-inventory-consistency-gate.json"
md_path = OUT / "redacted-export-inventory-consistency-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in checks)
md_path.write_text(f"""# Redacted Export Inventory Consistency Gate

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Export Inventory Consistency Gate Only: `True`
- Inventory Ledger PASS: `{out['input_inventory_ledger_pass']}`
- Inventory Ledger Check PASS: `{out['input_inventory_ledger_check_pass']}`
- Inventory Ledger Ready: `{out['input_inventory_ledger_ready']}`
- Plan Consistency Gate Ready: `{out['input_plan_consistency_gate_ready']}`
- Dry-Run Plan Ready: `{out['input_dry_run_plan_ready']}`
- Inventory Count: `{out['inventory_count']}`
- Inventory Entry Count: `{out['inventory_entry_count']}`
- Inventory Count Matches: `{out['inventory_count_matches']}`
- Inventory All Exist: `{out['inventory_all_exist']}`
- Inventory All Relative: `{out['inventory_all_relative']}`
- Inventory Forbidden Absent: `{out['inventory_forbidden_absent']}`
- Inventory All Not Copied: `{out['inventory_all_not_copied']}`
- Inventory SHA-256 Present: `{out['inventory_sha256_present']}`
- Inventory Byte Count Present: `{out['inventory_byte_count_present']}`
- Exclude Labels Present: `{out['exclude_labels_present']}`
- Private Paths Absent: `{out['private_paths_absent']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Export Inventory Consistency Gate Ready: `{out['redacted_export_inventory_consistency_gate_ready']}`
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
