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

assembly = read_json("release-readiness/redacted-export-bundle-assembly-dry-run-manifest.json")
assembly_check = read_json("release-readiness/redacted-export-bundle-assembly-dry-run-manifest-check.json")
inventory_gate = read_json("release-readiness/redacted-export-inventory-consistency-gate.json")
inventory_ledger = read_json("release-readiness/redacted-export-bundle-dry-run-inventory-ledger.json")

assembly_pass = bool(assembly and assembly.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY")
assembly_check_pass = bool(assembly_check and assembly_check.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY")
assembly_ready = bool(assembly and assembly.get("redacted_export_bundle_assembly_dry_run_manifest_ready") is True)
inventory_gate_ready = bool(inventory_gate and inventory_gate.get("redacted_export_inventory_consistency_gate_ready") is True)
inventory_ledger_ready = bool(inventory_ledger and inventory_ledger.get("redacted_export_bundle_dry_run_inventory_ledger_ready") is True)

entries = assembly.get("assembly_entries", []) if isinstance(assembly, dict) else []
assembly_count = assembly.get("assembly_count") if isinstance(assembly, dict) else None
entries_present = bool(entries)
count_matches = entries_present and assembly_count == len(entries)
all_sources_exist = entries_present and all(e.get("source_exists") is True for e in entries)
all_source_paths_relative = entries_present and all(e.get("source_is_relative") is True for e in entries)
all_bundle_paths_relative = entries_present and all(e.get("planned_bundle_path_is_relative") is True for e in entries)
forbidden_absent = entries_present and all(e.get("forbidden_by_label") is False for e in entries)
all_not_copied = entries_present and all(e.get("copied_by_this_phase") is False and e.get("archived_by_this_phase") is False for e in entries)
sha256_present = entries_present and all(isinstance(e.get("source_sha256"), str) and len(e.get("source_sha256")) == 64 for e in entries)
byte_count_present = entries_present and all(isinstance(e.get("source_byte_count"), int) and e.get("source_byte_count") >= 0 for e in entries)

private_tokens = ["/Users/", "/private/var/folders/", "/var/folders/"]
private_paths_absent = all(token not in json.dumps(entries, sort_keys=True) for token in private_tokens)

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

inputs_safe = safe(assembly) and safe(assembly_check) and safe(inventory_gate) and safe(inventory_ledger)

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

checks = [
    expect("assembly_manifest_passed", assembly_pass),
    expect("assembly_manifest_check_passed", assembly_check_pass),
    expect("assembly_manifest_ready", assembly_ready),
    expect("inventory_consistency_gate_ready", inventory_gate_ready),
    expect("inventory_ledger_ready", inventory_ledger_ready),
    expect("assembly_entries_present", entries_present),
    expect("assembly_count_matches", count_matches),
    expect("assembly_all_sources_exist", all_sources_exist),
    expect("assembly_all_source_paths_relative", all_source_paths_relative),
    expect("assembly_all_bundle_paths_relative", all_bundle_paths_relative),
    expect("assembly_forbidden_absent", forbidden_absent),
    expect("assembly_all_not_copied", all_not_copied),
    expect("assembly_sha256_present", sha256_present),
    expect("assembly_byte_count_present", byte_count_present),
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
    checks.append(expect(f"{field}_false", bool(assembly and assembly.get(field) is False)))

checks.extend([
    expect("vendor_id", bool(assembly and assembly.get("expected_vendor_id") == "0x10de")),
    expect("device_id", bool(assembly and assembly.get("expected_device_id") == "0x2f04")),
    expect("iopcimatch", bool(assembly and assembly.get("expected_iopcimatch") == "0x2f0410de")),
    expect("driverkit_bundle_identifier", bool(assembly and assembly.get("expected_driverkit_bundle_identifier") == "dev.h1meka.H1mekaRTXDriver")),
    expect("host_app_bundle_identifier", bool(assembly and assembly.get("expected_host_app_bundle_identifier") == "dev.h1meka.H1mekaRTXHost")),
])

fail_count = sum(1 for item in checks if item["status"] == "FAIL")
pass_count = sum(1 for item in checks if item["status"] == "PASS")
ready = (
    assembly_pass
    and assembly_check_pass
    and assembly_ready
    and inventory_gate_ready
    and inventory_ledger_ready
    and entries_present
    and count_matches
    and all_sources_exist
    and all_source_paths_relative
    and all_bundle_paths_relative
    and forbidden_absent
    and all_not_copied
    and sha256_present
    and byte_count_present
    and private_paths_absent
    and inputs_safe
    and fail_count == 0
)

out = {
    "schema": "h1mekartx.redacted_bundle_assembly_dry_run_consistency_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_BUNDLE_ASSEMBLY_DRY_RUN_CONSISTENCY_GATE_OUTPUT",
    "decision": "PASS_REDACTED_BUNDLE_ASSEMBLY_DRY_RUN_CONSISTENCY_GATE_READY" if ready else "FAIL_REDACTED_BUNDLE_ASSEMBLY_DRY_RUN_CONSISTENCY_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "assembly_dry_run_consistency_gate_only": True,
    "input_assembly_manifest_present": assembly is not None,
    "input_assembly_manifest_check_present": assembly_check is not None,
    "input_inventory_consistency_gate_present": inventory_gate is not None,
    "input_inventory_ledger_present": inventory_ledger is not None,
    "input_assembly_manifest_pass": assembly_pass,
    "input_assembly_manifest_check_pass": assembly_check_pass,
    "input_assembly_manifest_ready": assembly_ready,
    "input_inventory_consistency_gate_ready": inventory_gate_ready,
    "input_inventory_ledger_ready": inventory_ledger_ready,
    "assembly_count": assembly_count,
    "assembly_entry_count": len(entries),
    "assembly_entries_present": entries_present,
    "assembly_count_matches": count_matches,
    "assembly_all_sources_exist": all_sources_exist,
    "assembly_all_source_paths_relative": all_source_paths_relative,
    "assembly_all_bundle_paths_relative": all_bundle_paths_relative,
    "assembly_forbidden_absent": forbidden_absent,
    "assembly_all_not_copied": all_not_copied,
    "assembly_sha256_present": sha256_present,
    "assembly_byte_count_present": byte_count_present,
    "private_paths_absent": private_paths_absent,
    "inputs_safe": inputs_safe,
    "consistency": checks,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "redacted_bundle_assembly_dry_run_consistency_gate_ready": ready,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63j-redacted-entitlement-request-final-review-packet-index",
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

json_path = OUT / "redacted-bundle-assembly-dry-run-consistency-gate.json"
md_path = OUT / "redacted-bundle-assembly-dry-run-consistency-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in checks)
md_path.write_text(f"""# Redacted Bundle Assembly Dry-Run Consistency Gate

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Assembly Dry-Run Consistency Gate Only: `True`
- Assembly Manifest PASS: `{out['input_assembly_manifest_pass']}`
- Assembly Manifest Check PASS: `{out['input_assembly_manifest_check_pass']}`
- Assembly Manifest Ready: `{out['input_assembly_manifest_ready']}`
- Inventory Consistency Gate Ready: `{out['input_inventory_consistency_gate_ready']}`
- Inventory Ledger Ready: `{out['input_inventory_ledger_ready']}`
- Assembly Count: `{out['assembly_count']}`
- Assembly Entry Count: `{out['assembly_entry_count']}`
- Assembly Count Matches: `{out['assembly_count_matches']}`
- Assembly All Sources Exist: `{out['assembly_all_sources_exist']}`
- Assembly All Source Paths Relative: `{out['assembly_all_source_paths_relative']}`
- Assembly All Bundle Paths Relative: `{out['assembly_all_bundle_paths_relative']}`
- Assembly Forbidden Absent: `{out['assembly_forbidden_absent']}`
- Assembly All Not Copied: `{out['assembly_all_not_copied']}`
- Assembly SHA-256 Present: `{out['assembly_sha256_present']}`
- Assembly Byte Count Present: `{out['assembly_byte_count_present']}`
- Private Paths Absent: `{out['private_paths_absent']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Bundle Assembly Dry-Run Consistency Gate Ready: `{out['redacted_bundle_assembly_dry_run_consistency_gate_ready']}`
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
