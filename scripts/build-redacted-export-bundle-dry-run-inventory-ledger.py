#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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

plan_gate = read_json("release-readiness/redacted-export-dry-run-plan-consistency-gate.json")
plan_gate_check = read_json("release-readiness/redacted-export-dry-run-plan-consistency-gate-check.json")
dry_run_plan = read_json("release-readiness/redacted-export-bundle-dry-run-plan.json")
manifest_gate = read_json("release-readiness/redacted-bundle-manifest-consistency-gate.json")
redacted_manifest = read_json("release-readiness/redacted-manual-export-bundle-manifest.json")

plan_gate_pass = bool(plan_gate and plan_gate.get("decision") == "PASS_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_READY")
plan_gate_check_pass = bool(plan_gate_check and plan_gate_check.get("decision") == "PASS_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_READY")
plan_gate_ready = bool(plan_gate and plan_gate.get("redacted_export_dry_run_plan_consistency_gate_ready") is True)
dry_run_plan_ready = bool(dry_run_plan and dry_run_plan.get("redacted_export_bundle_dry_run_plan_ready") is True)
manifest_gate_ready = bool(manifest_gate and manifest_gate.get("redacted_bundle_manifest_consistency_gate_ready") is True)
redacted_manifest_ready = bool(redacted_manifest and redacted_manifest.get("redacted_manual_export_bundle_manifest_ready") is True)

include_files = dry_run_plan.get("include_files", []) if isinstance(dry_run_plan, dict) else []
if not include_files:
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

exclude_labels = dry_run_plan.get("exclude_labels", []) if isinstance(dry_run_plan, dict) else []

forbidden_rel_substrings = [
    "host-report-bundle",
    "raw-ioregistry",
    "ioregistry-raw",
    "bar-dump",
    "mmio-dump",
    "private-key",
    "certificate",
    "provisioning",
    ".p12",
    ".mobileprovision",
]

def inventory_entry(rel: str):
    abs_path = ROOT / rel
    exists = abs_path.exists() and abs_path.is_file()
    data = abs_path.read_bytes() if exists else b""
    is_relative = not Path(rel).is_absolute()
    forbidden = any(token.lower() in rel.lower() for token in forbidden_rel_substrings)
    return {
        "relative_path": rel,
        "exists": exists,
        "is_relative_path": is_relative,
        "forbidden_by_label": forbidden,
        "copied_by_this_phase": False,
        "archived_by_this_phase": False,
        "byte_count": len(data) if exists else 0,
        "sha256": hashlib.sha256(data).hexdigest() if exists else None,
    }

inventory = [inventory_entry(str(rel)) for rel in include_files]
inventory_count = len(inventory)
inventory_present = inventory_count > 0
inventory_all_exist = all(item["exists"] for item in inventory)
inventory_all_relative = all(item["is_relative_path"] for item in inventory)
inventory_forbidden_absent = all(not item["forbidden_by_label"] for item in inventory)
inventory_all_not_copied = all(item["copied_by_this_phase"] is False and item["archived_by_this_phase"] is False for item in inventory)
exclude_labels_present = isinstance(exclude_labels, list) and len(exclude_labels) >= 3

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

inputs_safe = safe(plan_gate) and safe(plan_gate_check) and safe(dry_run_plan) and safe(manifest_gate) and safe(redacted_manifest)

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

checks = [
    expect("plan_consistency_gate_passed", plan_gate_pass),
    expect("plan_consistency_gate_check_passed", plan_gate_check_pass),
    expect("plan_consistency_gate_ready", plan_gate_ready),
    expect("dry_run_plan_ready", dry_run_plan_ready),
    expect("manifest_consistency_gate_ready", manifest_gate_ready),
    expect("redacted_manifest_ready", redacted_manifest_ready),
    expect("inventory_present", inventory_present),
    expect("inventory_all_exist", inventory_all_exist),
    expect("inventory_all_relative", inventory_all_relative),
    expect("inventory_forbidden_absent", inventory_forbidden_absent),
    expect("inventory_all_not_copied", inventory_all_not_copied),
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
    checks.append(expect(f"{field}_false", bool(dry_run_plan and dry_run_plan.get(field) is False)))

checks.extend([
    expect("vendor_id", bool(dry_run_plan and dry_run_plan.get("expected_vendor_id") == "0x10de")),
    expect("device_id", bool(dry_run_plan and dry_run_plan.get("expected_device_id") == "0x2f04")),
    expect("iopcimatch", bool(dry_run_plan and dry_run_plan.get("expected_iopcimatch") == "0x2f0410de")),
    expect("driverkit_bundle_identifier", bool(dry_run_plan and dry_run_plan.get("expected_driverkit_bundle_identifier") == "dev.h1meka.H1mekaRTXDriver")),
    expect("host_app_bundle_identifier", bool(dry_run_plan and dry_run_plan.get("expected_host_app_bundle_identifier") == "dev.h1meka.H1mekaRTXHost")),
])

fail_count = sum(1 for item in checks if item["status"] == "FAIL")
pass_count = sum(1 for item in checks if item["status"] == "PASS")
ready = (
    plan_gate_pass
    and plan_gate_check_pass
    and plan_gate_ready
    and dry_run_plan_ready
    and manifest_gate_ready
    and redacted_manifest_ready
    and inventory_present
    and inventory_all_exist
    and inventory_all_relative
    and inventory_forbidden_absent
    and inventory_all_not_copied
    and exclude_labels_present
    and inputs_safe
    and fail_count == 0
)

out = {
    "schema": "h1mekartx.redacted_export_bundle_dry_run_inventory_ledger_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER_OUTPUT",
    "decision": "PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER_READY" if ready else "FAIL_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "dry_run_inventory_ledger_only": True,
    "input_plan_consistency_gate_present": plan_gate is not None,
    "input_plan_consistency_gate_check_present": plan_gate_check is not None,
    "input_dry_run_plan_present": dry_run_plan is not None,
    "input_manifest_consistency_gate_present": manifest_gate is not None,
    "input_redacted_manifest_present": redacted_manifest is not None,
    "input_plan_consistency_gate_pass": plan_gate_pass,
    "input_plan_consistency_gate_check_pass": plan_gate_check_pass,
    "input_plan_consistency_gate_ready": plan_gate_ready,
    "input_dry_run_plan_ready": dry_run_plan_ready,
    "input_manifest_consistency_gate_ready": manifest_gate_ready,
    "input_redacted_manifest_ready": redacted_manifest_ready,
    "inventory": inventory,
    "inventory_count": inventory_count,
    "inventory_present": inventory_present,
    "inventory_all_exist": inventory_all_exist,
    "inventory_all_relative": inventory_all_relative,
    "inventory_forbidden_absent": inventory_forbidden_absent,
    "inventory_all_not_copied": inventory_all_not_copied,
    "exclude_labels": exclude_labels,
    "exclude_labels_present": exclude_labels_present,
    "inputs_safe": inputs_safe,
    "checks": checks,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "redacted_export_bundle_dry_run_inventory_ledger_ready": ready,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63g-redacted-export-inventory-consistency-gate",
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
    "absolute_paths_recorded",
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

json_path = OUT / "redacted-export-bundle-dry-run-inventory-ledger.json"
md_path = OUT / "redacted-export-bundle-dry-run-inventory-ledger.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

inventory_rows = "\n".join(
    f"| `{item['relative_path']}` | `{item['exists']}` | `{item['byte_count']}` | `{item['sha256']}` |"
    for item in inventory
)
check_rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in checks)
md_path.write_text(f"""# Redacted Export Bundle Dry-Run Inventory Ledger

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Dry-Run Inventory Ledger Only: `True`
- Plan Consistency Gate PASS: `{out['input_plan_consistency_gate_pass']}`
- Plan Consistency Gate Check PASS: `{out['input_plan_consistency_gate_check_pass']}`
- Plan Consistency Gate Ready: `{out['input_plan_consistency_gate_ready']}`
- Dry-Run Plan Ready: `{out['input_dry_run_plan_ready']}`
- Manifest Consistency Gate Ready: `{out['input_manifest_consistency_gate_ready']}`
- Redacted Manifest Ready: `{out['input_redacted_manifest_ready']}`
- Inventory Count: `{out['inventory_count']}`
- Inventory All Exist: `{out['inventory_all_exist']}`
- Inventory All Relative: `{out['inventory_all_relative']}`
- Inventory Forbidden Absent: `{out['inventory_forbidden_absent']}`
- Inventory All Not Copied: `{out['inventory_all_not_copied']}`
- Exclude Labels Present: `{out['exclude_labels_present']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Export Bundle Dry-Run Inventory Ledger Ready: `{out['redacted_export_bundle_dry_run_inventory_ledger_ready']}`
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

## Inventory

| Relative Path | Exists | Bytes | SHA-256 |
| --- | --- | ---: | --- |
{inventory_rows}

## Checks

| Item | Status |
| --- | --- |
{check_rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
