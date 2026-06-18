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

manifest_path = ROOT / "tools/hackintosh/redacted-manual-export-bundle-manifest.json"
doc_path = ROOT / "docs/hackintosh/redacted-manual-export-bundle-manifest.md"
out_path = ROOT / "release-readiness/redacted-manual-export-bundle-manifest.json"
out_md_path = ROOT / "release-readiness/redacted-manual-export-bundle-manifest.md"

manifest = read_json(manifest_path)
out = read_json(out_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
out_md = out_md_path.read_text(encoding="utf-8", errors="replace") if out_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "output_exists", out_path.exists(), str(out_path))
add(checks, "output_md_exists", out_md_path.exists(), str(out_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.redacted_manual_export_bundle_manifest.v1"), "manifest schema")
add(checks, "output_schema", bool(out and out.get("schema") == "h1mekartx.redacted_manual_export_bundle_manifest_output.v1"), "output schema")
add(checks, "output_decision_pass", bool(out and out.get("decision") == "PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY"), "output decision")
add(checks, "output_ready_true", bool(out and out.get("redacted_manual_export_bundle_manifest_ready") is True), "ready")
add(checks, "output_fail_count_zero", bool(out and out.get("fail_count") == 0), "fail_count")
add(checks, "output_blocked_count_at_least_six", bool(out and out.get("blocked_count", 0) >= 6), "blocked_count")
add(checks, "output_placeholder_count_at_least_two", bool(out and out.get("placeholder_count", 0) >= 2), "placeholder_count")

for obj_name, obj in [("manifest", manifest), ("output", out)]:
    for field in ["rtx5070_target_retained", "redacted_manifest_only"]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_true", obj.get(field) is True, field)
    for field in [
        "fallback_gpu_substitution_allowed",
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
        "provider_visibility_commands_executed_by_this_phase",
        "raw_capture_parsed_by_this_phase",
        "raw_stdout_committed",
        "raw_stderr_committed",
        "private_paths_committed",
        "provider_open_ready",
        "ioserviceopen_ready",
        "bar_access_ready",
        "gpu_command_submission_ready",
        "metal_acceleration_ready",
        "provider_open_attempted",
        "ioserviceopen_attempted",
        "bar_mapping_attempted",
        "bar0_read_attempted",
        "bar0_write_attempted",
        "bar_mmio_mutation_attempted",
        "configuration_writes_attempted",
        "firmware_load_attempted",
        "gpu_reset_attempted",
        "framebuffer_init_attempted",
        "display_engine_init_attempted",
        "gpu_command_submission_attempted",
        "metal_proof_claimed",
        "current_rtx5070_metal_acceleration_claimed",
        "current_rtx5070_ui_smoothness_claimed",
        "dock_transparency_blur_acceleration_claimed",
    ]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for field in [
    "input_manual_export_checklist_pass",
    "input_manual_export_check_pass",
    "input_manual_export_checklist_ready",
    "input_local_submission_readiness_ready",
    "input_pre_submission_packet_ready",
    "input_evidence_checklist_ready",
    "request_notes_template_ready",
    "inputs_safe",
]:
    add(checks, f"output_{field}_true", bool(out and out.get(field) is True), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("host_app_bundle_identifier", "dev.h1meka.H1mekaRTXHost"),
    ("next_gate", "phase63c-redacted-bundle-manifest-consistency-gate"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("expected_host_app_bundle_identifier", "dev.h1meka.H1mekaRTXHost"),
    ("next_gate", "phase63c-redacted-bundle-manifest-consistency-gate"),
]:
    add(checks, f"output_{key}", bool(out and out.get(key) == value), f"{key}={value}")

for token in [
    "This phase is redacted-manifest-only",
    "This phase does not create an export archive",
    "This phase does not export provisioning assets",
    "This phase does not export certificates",
    "This phase does not export private keys",
    "This phase does not submit an Apple entitlement request",
    "This phase does not contact Apple",
    "This phase does not create an App ID",
    "This phase does not create a provisioning profile",
    "This phase does not sign a DriverKit extension",
    "This phase does not load or activate a DriverKit extension",
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
for private_token in ["/Users/h1meka", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + private_token.replace("/", "_"), private_token not in combined_release, private_token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY" if failed == 0 else "FAIL_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST"

report = {
    "schema": "h1mekartx.redacted_manual_export_bundle_manifest_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "redacted_manifest_only": True,
    "bundle_archive_created_by_this_phase": False,
    "certificates_exported": False,
    "private_keys_exported": False,
    "provisioning_assets_exported": False,
    "raw_ioregistry_exported": False,
    "provider_handles_exported": False,
    "actual_apple_entitlement_request_submitted": False,
    "contacted_apple_by_this_phase": False,
    "driverkit_entitlement_requested_by_this_phase": False,
    "driverkit_profile_ready": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase63c-redacted-bundle-manifest-consistency-gate",
    "checks": checks,
}
(OUT / "redacted-manual-export-bundle-manifest-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "redacted-manual-export-bundle-manifest-check.md").write_text(f"""# Redacted Manual Export Bundle Manifest Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Redacted Manifest Only: `True`
- Bundle Archive Created By This Phase: `False`
- Certificates Exported: `False`
- Private Keys Exported: `False`
- Provisioning Assets Exported: `False`
- Raw IORegistry Exported: `False`
- Provider Handles Exported: `False`
- Actual Apple Entitlement Request Submitted: `False`
- Contacted Apple By This Phase: `False`
- DriverKit Entitlement Requested By This Phase: `False`
- DriverKit Profile Ready: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase63c-redacted-bundle-manifest-consistency-gate`

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
