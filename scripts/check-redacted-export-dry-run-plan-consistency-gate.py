#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/redacted-export-dry-run-plan-consistency-gate.json"
doc_path = ROOT / "docs/hackintosh/redacted-export-dry-run-plan-consistency-gate.md"
out_path = ROOT / "release-readiness/redacted-export-dry-run-plan-consistency-gate.json"
out_md_path = ROOT / "release-readiness/redacted-export-dry-run-plan-consistency-gate.md"

manifest = read_json(manifest_path)
out = read_json(out_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
out_md = out_md_path.read_text(encoding="utf-8", errors="replace") if out_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "output_exists", out_path.exists(), str(out_path))
add(checks, "output_md_exists", out_md_path.exists(), str(out_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.redacted_export_dry_run_plan_consistency_gate.v1"), "manifest schema")
add(checks, "output_schema", bool(out and out.get("schema") == "h1mekartx.redacted_export_dry_run_plan_consistency_gate_output.v1"), "output schema")
add(checks, "output_decision_pass", bool(out and out.get("decision") == "PASS_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_READY"), "output decision")
add(checks, "output_ready_true", bool(out and out.get("redacted_export_dry_run_plan_consistency_gate_ready") is True), "ready")
add(checks, "output_include_files_present_true", bool(out and out.get("include_files_present") is True), "include files")
add(checks, "output_exclude_labels_present_true", bool(out and out.get("exclude_labels_present") is True), "exclude labels")
add(checks, "output_fail_count_zero", bool(out and out.get("fail_count") == 0), "fail_count")
add(checks, "output_consistency_all_pass", bool(out and out.get("consistency") and all(i.get("status") == "PASS" for i in out["consistency"])), "consistency")

for obj_name, obj in [("manifest", manifest), ("output", out)]:
    for field in ["rtx5070_target_retained", "fallback_gpu_substitution_allowed"]:
        if obj is not None and field in obj:
            expected = True if field == "rtx5070_target_retained" else False
            add(checks, f"{obj_name}_{field}_{expected}", obj.get(field) is expected, field)
    for field in [
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
    ]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for field in [
    "input_dry_run_plan_pass",
    "input_dry_run_plan_check_pass",
    "input_dry_run_plan_ready",
    "input_manifest_consistency_gate_ready",
    "input_redacted_manifest_ready",
    "inputs_safe",
]:
    add(checks, f"output_{field}_true", bool(out and out.get(field) is True), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("host_app_bundle_identifier", "dev.h1meka.H1mekaRTXHost"),
    ("next_gate", "phase63f-redacted-export-bundle-dry-run-inventory-ledger"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("expected_host_app_bundle_identifier", "dev.h1meka.H1mekaRTXHost"),
    ("next_gate", "phase63f-redacted-export-bundle-dry-run-inventory-ledger"),
]:
    add(checks, f"output_{key}", bool(out and out.get(key) == value), f"{key}={value}")

for token in [
    "This phase is dry-run-plan-consistency-gate-only",
    "This phase does not create an export archive",
    "This phase does not copy files into an export bundle",
    "This phase does not export provisioning assets",
    "This phase does not export certificates",
    "This phase does not export private keys",
    "This phase does not export raw IORegistry data",
    "This phase does not export provider handles",
    "This phase does not submit an Apple entitlement request",
    "This phase does not contact Apple",
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not map BAR memory",
    "This phase does not read BAR0",
    "This phase does not write BAR0",
    "This phase does not submit GPU commands",
    "This phase does not claim RTX 5070 Metal acceleration",
    "This phase does not claim Dock/transparency/blur acceleration",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

combined_release = json.dumps(out or {}) + "\n" + out_md
for raw in ["/Users/", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + raw.replace("/", "_"), raw not in combined_release, raw)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_READY" if failed == 0 else "FAIL_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE"

report = {
    "schema": "h1mekartx.redacted_export_dry_run_plan_consistency_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "dry_run_plan_consistency_gate_only": True,
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
    "next_gate": "phase63f-redacted-export-bundle-dry-run-inventory-ledger",
    "checks": checks,
}
(OUT / "redacted-export-dry-run-plan-consistency-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "redacted-export-dry-run-plan-consistency-gate-check.md").write_text(f"""# Redacted Export Dry-Run Plan Consistency Gate Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Dry-Run Plan Consistency Gate Only: `True`
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
- Next Gate: `phase63f-redacted-export-bundle-dry-run-inventory-ledger`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
if failed:
    for c in checks:
        if not c["passed"]:
            print("FAIL:", c["name"], "|", c["detail"])
raise SystemExit(0 if failed == 0 else 1)
