#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8", errors="replace")) if p.exists() else None

gate = read_json("release-readiness/redacted-export-inventory-consistency-gate.json")
gate_check = read_json("release-readiness/redacted-export-inventory-consistency-gate-check.json")
ledger = read_json("release-readiness/redacted-export-bundle-dry-run-inventory-ledger.json")
plan = read_json("release-readiness/redacted-export-bundle-dry-run-plan.json")

gate_pass = bool(gate and gate.get("decision") == "PASS_REDACTED_EXPORT_INVENTORY_CONSISTENCY_GATE_READY")
gate_check_pass = bool(gate_check and gate_check.get("decision") == "PASS_REDACTED_EXPORT_INVENTORY_CONSISTENCY_GATE_READY")
gate_ready = bool(gate and gate.get("redacted_export_inventory_consistency_gate_ready") is True)
ledger_ready = bool(ledger and ledger.get("redacted_export_bundle_dry_run_inventory_ledger_ready") is True)
plan_ready = bool(plan and plan.get("redacted_export_bundle_dry_run_plan_ready") is True)

inventory = ledger.get("inventory", []) if isinstance(ledger, dict) else []
root_name = "H1mekaRTX-redacted-entitlement-request-dry-run"
forbidden = ["host-report-bundle", "raw-ioregistry", "ioregistry-raw", "bar-dump", "mmio-dump", "private-key", "certificate", ".p12", ".mobileprovision"]

def entry(item):
    src = str(item.get("relative_path", ""))
    parts = [p for p in src.split("/") if p and p not in (".", "..")]
    dst = "/".join([root_name] + parts)
    return {
        "source_relative_path": src,
        "planned_bundle_relative_path": dst,
        "source_exists": item.get("exists") is True,
        "source_sha256": item.get("sha256"),
        "source_byte_count": item.get("byte_count"),
        "source_is_relative": item.get("is_relative_path") is True and not Path(src).is_absolute(),
        "planned_bundle_path_is_relative": not Path(dst).is_absolute(),
        "forbidden_by_label": bool(item.get("forbidden_by_label")) or any(x in src.lower() or x in dst.lower() for x in forbidden),
        "copied_by_this_phase": False,
        "archived_by_this_phase": False
    }

assembly = [entry(i) for i in inventory]
assembly_present = bool(assembly)
assembly_all_sources_exist = assembly_present and all(i["source_exists"] for i in assembly)
assembly_all_source_paths_relative = assembly_present and all(i["source_is_relative"] for i in assembly)
assembly_all_bundle_paths_relative = assembly_present and all(i["planned_bundle_path_is_relative"] for i in assembly)
assembly_forbidden_absent = assembly_present and all(not i["forbidden_by_label"] for i in assembly)
assembly_all_not_copied = assembly_present and all(not i["copied_by_this_phase"] and not i["archived_by_this_phase"] for i in assembly)
assembly_sha256_present = assembly_present and all(isinstance(i["source_sha256"], str) and len(i["source_sha256"]) == 64 for i in assembly)
assembly_byte_count_present = assembly_present and all(isinstance(i["source_byte_count"], int) and i["source_byte_count"] >= 0 for i in assembly)
private_paths_absent = all(t not in json.dumps(assembly, sort_keys=True) for t in ["/Users/", "/private/var/folders/", "/var/folders/"])

danger = ["provider_open_attempted","ioserviceopen_attempted","bar_mapping_attempted","bar0_read_attempted","bar0_write_attempted","gpu_command_submission_attempted","current_rtx5070_metal_acceleration_claimed","dock_transparency_blur_acceleration_claimed"]
def safe(obj):
    return isinstance(obj, dict) and all(obj.get(k) is False for k in danger if k in obj)
inputs_safe = safe(gate) and safe(gate_check) and safe(ledger) and safe(plan)

def row(name, ok): return {"id": name, "status": "PASS" if ok else "FAIL"}
checks = [
    row("inventory_consistency_gate_passed", gate_pass),
    row("inventory_consistency_gate_check_passed", gate_check_pass),
    row("inventory_consistency_gate_ready", gate_ready),
    row("inventory_ledger_ready", ledger_ready),
    row("dry_run_plan_ready", plan_ready),
    row("assembly_present", assembly_present),
    row("assembly_count_matches_inventory_count", bool(ledger and ledger.get("inventory_count") == len(assembly))),
    row("assembly_all_sources_exist", assembly_all_sources_exist),
    row("assembly_all_source_paths_relative", assembly_all_source_paths_relative),
    row("assembly_all_bundle_paths_relative", assembly_all_bundle_paths_relative),
    row("assembly_forbidden_absent", assembly_forbidden_absent),
    row("assembly_all_not_copied", assembly_all_not_copied),
    row("assembly_sha256_present", assembly_sha256_present),
    row("assembly_byte_count_present", assembly_byte_count_present),
    row("private_paths_absent", private_paths_absent),
]
false_fields = ["bundle_archive_created_by_this_phase","files_copied_to_export_bundle_by_this_phase","certificates_exported","private_keys_exported","provisioning_assets_exported","raw_ioregistry_exported","provider_handles_exported","actual_apple_entitlement_request_submitted","contacted_apple_by_this_phase","provider_open_attempted","ioserviceopen_attempted","bar_mapping_attempted","bar0_read_attempted","bar0_write_attempted","gpu_command_submission_attempted","current_rtx5070_metal_acceleration_claimed","dock_transparency_blur_acceleration_claimed","absolute_paths_recorded"]
for f in false_fields:
    checks.append(row(f + "_false", bool(ledger and ledger.get(f) is False)))

fail_count = sum(1 for i in checks if i["status"] == "FAIL")
ready = gate_pass and gate_check_pass and gate_ready and ledger_ready and plan_ready and assembly_present and assembly_all_sources_exist and assembly_all_source_paths_relative and assembly_all_bundle_paths_relative and assembly_forbidden_absent and assembly_all_not_copied and assembly_sha256_present and assembly_byte_count_present and private_paths_absent and inputs_safe and fail_count == 0

out = {
    "schema": "h1mekartx.redacted_export_bundle_assembly_dry_run_manifest_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_OUTPUT",
    "decision": "PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY" if ready else "FAIL_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "assembly_dry_run_manifest_only": True,
    "input_inventory_consistency_gate_pass": gate_pass,
    "input_inventory_consistency_gate_check_pass": gate_check_pass,
    "input_inventory_consistency_gate_ready": gate_ready,
    "input_inventory_ledger_ready": ledger_ready,
    "input_dry_run_plan_ready": plan_ready,
    "bundle_root": root_name,
    "assembly_entries": assembly,
    "assembly_count": len(assembly),
    "assembly_present": assembly_present,
    "assembly_all_sources_exist": assembly_all_sources_exist,
    "assembly_all_source_paths_relative": assembly_all_source_paths_relative,
    "assembly_all_bundle_paths_relative": assembly_all_bundle_paths_relative,
    "assembly_forbidden_absent": assembly_forbidden_absent,
    "assembly_all_not_copied": assembly_all_not_copied,
    "assembly_sha256_present": assembly_sha256_present,
    "assembly_byte_count_present": assembly_byte_count_present,
    "private_paths_absent": private_paths_absent,
    "inputs_safe": inputs_safe,
    "checks": checks,
    "pass_count": sum(1 for i in checks if i["status"] == "PASS"),
    "fail_count": fail_count,
    "redacted_export_bundle_assembly_dry_run_manifest_ready": ready,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63i-redacted-bundle-assembly-dry-run-consistency-gate",
}
for f in false_fields:
    out[f] = False
for f in ["provider_visibility_commands_executed_by_this_phase","raw_capture_parsed_by_this_phase","raw_stdout_committed","raw_stderr_committed","private_paths_committed","bar_mmio_mutation_attempted","configuration_writes_attempted","firmware_load_attempted","gpu_reset_attempted","framebuffer_init_attempted","display_engine_init_attempted","gpu_command_submission_ready","metal_acceleration_ready","metal_proof_claimed","current_rtx5070_ui_smoothness_claimed"]:
    out[f] = False

(OUT / "redacted-export-bundle-assembly-dry-run-manifest.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
entries = "\n".join(f"| `{e['source_relative_path']}` | `{e['planned_bundle_relative_path']}` | `{e['source_exists']}` | `{e['source_byte_count']}` | `{e['source_sha256']}` |" for e in assembly)
rows = "\n".join(f"| `{i['id']}` | `{i['status']}` |" for i in checks)
(OUT / "redacted-export-bundle-assembly-dry-run-manifest.md").write_text(f"""# Redacted Export Bundle Assembly Dry-Run Manifest

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Assembly Dry-Run Manifest Only: `True`
- Assembly Count: `{out['assembly_count']}`
- Assembly All Sources Exist: `{out['assembly_all_sources_exist']}`
- Assembly All Source Paths Relative: `{out['assembly_all_source_paths_relative']}`
- Assembly All Bundle Paths Relative: `{out['assembly_all_bundle_paths_relative']}`
- Assembly Forbidden Absent: `{out['assembly_forbidden_absent']}`
- Assembly All Not Copied: `{out['assembly_all_not_copied']}`
- Private Paths Absent: `{out['private_paths_absent']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Export Bundle Assembly Dry-Run Manifest Ready: `{out['redacted_export_bundle_assembly_dry_run_manifest_ready']}`
- Bundle Archive Created By This Phase: `False`
- Files Copied To Export Bundle By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Assembly Entries

| Source Relative Path | Planned Bundle Relative Path | Source Exists | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
{entries}

## Checks

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")
print("Decision:", out["decision"])
