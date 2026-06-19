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

manifest_path = ROOT / "tools/hackintosh/local-only-final-review-command-checklist.json"
doc_path = ROOT / "docs/hackintosh/local-only-final-review-command-checklist.md"
out_path = ROOT / "release-readiness/local-only-final-review-command-checklist.json"
out_md_path = ROOT / "release-readiness/local-only-final-review-command-checklist.md"

manifest = read_json(manifest_path)
out = read_json(out_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
out_md = out_md_path.read_text(encoding="utf-8", errors="replace") if out_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "output_exists", out_path.exists(), str(out_path))
add(checks, "output_md_exists", out_md_path.exists(), str(out_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_only_final_review_command_checklist.v1"), "manifest schema")
add(checks, "output_schema", bool(out and out.get("schema") == "h1mekartx.local_only_final_review_command_checklist_output.v1"), "output schema")
add(checks, "output_decision_pass", bool(out and out.get("decision") == "PASS_LOCAL_ONLY_FINAL_REVIEW_COMMAND_CHECKLIST_READY"), "output decision")
add(checks, "output_ready_true", bool(out and out.get("local_only_final_review_command_checklist_ready") is True), "ready")
add(checks, "output_input_index_pass_true", bool(out and out.get("input_final_review_packet_index_pass") is True), "input")
add(checks, "output_input_index_check_pass_true", bool(out and out.get("input_final_review_packet_index_check_pass") is True), "input")
add(checks, "output_command_count_9", bool(out and out.get("checklist_command_count") == 9), "command count")
add(checks, "output_commands_all_read_only_true", bool(out and out.get("commands_all_read_only") is True), "commands")
add(checks, "output_commands_all_no_submit_true", bool(out and out.get("commands_all_no_submit") is True), "commands")
add(checks, "output_commands_all_safe_true", bool(out and out.get("commands_all_safe") is True), "commands")
add(checks, "output_commands_no_execution_true", bool(out and out.get("commands_no_execution_by_this_phase") is True), "commands")
add(checks, "output_fail_count_zero", bool(out and out.get("fail_count") == 0), "fail_count")
add(checks, "output_checks_all_pass", bool(out and out.get("checks") and all(i.get("status") == "PASS" for i in out["checks"])), "checks")

for obj_name, obj in [("manifest", manifest), ("output", out)]:
    for field in ["rtx5070_target_retained"]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_true", obj.get(field) is True, field)
    for field in [
        "fallback_gpu_substitution_allowed",
        "checklist_commands_executed_by_this_phase",
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

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("host_app_bundle_identifier", "dev.h1meka.H1mekaRTXHost"),
    ("next_gate", "phase63l-local-only-final-review-command-checklist-consistency-gate"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("expected_host_app_bundle_identifier", "dev.h1meka.H1mekaRTXHost"),
    ("next_gate", "phase63l-local-only-final-review-command-checklist-consistency-gate"),
]:
    add(checks, f"output_{key}", bool(out and out.get(key) == value), f"{key}={value}")

for token in [
    "This phase is local-final-review-command-checklist-only",
    "This phase only records commands that a human can run locally to review redacted artifacts",
    "This phase does not execute the checklist commands",
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
decision = "PASS_LOCAL_ONLY_FINAL_REVIEW_COMMAND_CHECKLIST_READY" if failed == 0 else "FAIL_LOCAL_ONLY_FINAL_REVIEW_COMMAND_CHECKLIST"

report = {
    "schema": "h1mekartx.local_only_final_review_command_checklist_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "local_final_review_command_checklist_only": True,
    "checklist_commands_executed_by_this_phase": False,
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
    "next_gate": "phase63l-local-only-final-review-command-checklist-consistency-gate",
    "checks": checks,
}
(OUT / "local-only-final-review-command-checklist-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "local-only-final-review-command-checklist-check.md").write_text(f"""# Local-Only Final Review Command Checklist Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Local Final Review Command Checklist Only: `True`
- Checklist Commands Executed By This Phase: `False`
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
- Next Gate: `phase63l-local-only-final-review-command-checklist-consistency-gate`

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
