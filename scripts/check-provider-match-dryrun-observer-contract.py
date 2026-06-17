#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/provider-match-dryrun-observer-contract.json"
doc_path = ROOT / "docs/hackintosh/provider-match-dryrun-observer-contract.md"
readiness_summary_path = ROOT / "release-readiness/provider-match-readiness-gate-summary.json"
entitlement_summary_path = ROOT / "release-readiness/local-entitlement-request-status-summary.json"

manifest = read_json(manifest_path)
readiness_summary = read_json(readiness_summary_path)
entitlement_summary = read_json(entitlement_summary_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("readiness_summary_path_known", readiness_summary_path),
    ("entitlement_summary_path_known", entitlement_summary_path),
]:
    add(checks, name, path.exists() or name.endswith("_path_known"), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_dryrun_observer_contract.v1"), "schema")

for field in [
    "provider_match_dryrun_observer_contract_ready",
    "provider_match_observer_not_provider_open",
    "rtx5070_target_retained",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "provider_match_observation_allowed_by_this_phase",
    "provider_match_observed_by_this_phase",
    "provider_open_allowed_by_this_phase",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_allowed_by_this_phase",
    "bar_mapping_attempted",
    "bar0_read_allowed_by_this_phase",
    "bar0_read_attempted",
    "bar0_write_allowed_by_this_phase",
    "bar0_write_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "firmware_load_attempted",
    "gpu_reset_attempted",
    "framebuffer_init_attempted",
    "display_engine_init_attempted",
    "gpu_command_submission_allowed_by_this_phase",
    "gpu_command_submission_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "dock_transparency_blur_acceleration_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("rtx5070_subsystem_vendor_id", "0x1458"),
    ("rtx5070_subsystem_id", "0x417e"),
    ("next_gate", "phase62f-local-provider-match-dryrun-observer-summary"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for field in [
    "driverkit_bundle_identifier_expected",
    "iopcimatch_expected",
    "rtx5070_pci_identity_expected",
    "entitlement_readiness_state",
    "provider_match_readiness_state",
    "provider_visibility_source",
    "provider_match_observed",
    "provider_open_blocked",
    "ioserviceopen_blocked",
    "bar_mapping_blocked",
    "gpu_command_submission_blocked",
]:
    add(checks, f"observer_field_{field}", bool(manifest and field in manifest.get("observer_fields", [])), field)

for token in [
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not map BAR memory",
    "This phase does not read BAR0",
    "This phase does not write BAR0",
    "This phase does not submit GPU commands",
    "This phase does not claim RTX 5070 Metal acceleration",
    "This phase does not claim Dock/transparency/blur acceleration",
    "Provider open remains blocked",
    "BAR mapping remains blocked",
    "GPU command submission remains blocked",
    "Dock/transparency/blur proof remains blocked",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

ready_for_provider_match = bool(readiness_summary and readiness_summary.get("ready_for_provider_match") is True)
missing_ready_fields = readiness_summary.get("missing_ready_fields", []) if readiness_summary else []

summary = {
    "schema": "h1mekartx.provider_match_dryrun_observer_contract_summary.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_PROVIDER_MATCH_DRYRUN_OBSERVER_CONTRACT",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "provider_match_observer_not_provider_open": True,
    "readiness_summary_present": readiness_summary is not None,
    "entitlement_summary_present": entitlement_summary is not None,
    "ready_for_provider_match": ready_for_provider_match,
    "missing_ready_field_count": len(missing_ready_fields),
    "missing_ready_fields": missing_ready_fields,
    "provider_match_observation_allowed_by_this_phase": False,
    "provider_match_observed_by_this_phase": False,
    "provider_open_allowed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_allowed_by_this_phase": False,
    "bar_mapping_attempted": False,
    "bar0_read_allowed_by_this_phase": False,
    "bar0_read_attempted": False,
    "bar0_write_allowed_by_this_phase": False,
    "bar0_write_attempted": False,
    "bar_mmio_mutation_attempted": False,
    "configuration_writes_attempted": False,
    "gpu_command_submission_allowed_by_this_phase": False,
    "gpu_command_submission_attempted": False,
    "framebuffer_init_attempted": False,
    "display_engine_init_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62f-local-provider-match-dryrun-observer-summary",
}
(OUT / "provider-match-dryrun-observer-contract-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

missing = "\n".join(f"- `{x}`" for x in missing_ready_fields) or "- none"
(OUT / "provider-match-dryrun-observer-contract-summary.md").write_text(f"""# Provider Match Dry-Run Observer Contract Summary

- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Provider Match Observer Not Provider Open: `True`
- Readiness Summary Present: `{readiness_summary is not None}`
- Entitlement Summary Present: `{entitlement_summary is not None}`
- Ready For Provider Match: `{ready_for_provider_match}`
- Missing Ready Field Count: `{len(missing_ready_fields)}`
- Provider Match Observation Allowed By This Phase: `False`
- Provider Match Observed By This Phase: `False`
- Provider Open Allowed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Allowed By This Phase: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Allowed By This Phase: `False`
- BAR0 Write Allowed By This Phase: `False`
- GPU Command Submission Allowed By This Phase: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62f-local-provider-match-dryrun-observer-summary`

## Missing Ready Fields

{missing}
""", encoding="utf-8")

add(checks, "summary_provider_match_observation_blocked", summary["provider_match_observation_allowed_by_this_phase"] is False, "observation blocked")
add(checks, "summary_provider_open_blocked", summary["provider_open_allowed_by_this_phase"] is False and summary["provider_open_attempted"] is False, "provider open blocked")
add(checks, "summary_bar_blocked", summary["bar_mapping_allowed_by_this_phase"] is False and summary["bar_mapping_attempted"] is False, "bar blocked")
add(checks, "summary_gpu_commands_blocked", summary["gpu_command_submission_allowed_by_this_phase"] is False and summary["gpu_command_submission_attempted"] is False, "gpu commands blocked")

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PROVIDER_MATCH_DRYRUN_OBSERVER_CONTRACT_READY" if failed == 0 else "FAIL_PROVIDER_MATCH_DRYRUN_OBSERVER_CONTRACT"

report = {
    "schema": "h1mekartx.provider_match_dryrun_observer_contract_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "provider_match_observer_not_provider_open": True,
    "provider_match_observation_allowed_by_this_phase": False,
    "provider_match_observed_by_this_phase": False,
    "provider_open_allowed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62f-local-provider-match-dryrun-observer-summary",
    "checks": checks,
}
(OUT / "provider-match-dryrun-observer-contract-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "provider-match-dryrun-observer-contract-check.md").write_text(f"""# Provider Match Dry-Run Observer Contract Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Provider Match Observer Not Provider Open: `True`
- Provider Match Observation Allowed By This Phase: `False`
- Provider Match Observed By This Phase: `False`
- Provider Open Allowed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62f-local-provider-match-dryrun-observer-summary`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
print("ready_for_provider_match =", ready_for_provider_match)
raise SystemExit(0 if failed == 0 else 1)
