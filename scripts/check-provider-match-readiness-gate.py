#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

REQUIRED_READY_FIELDS = [
    "apple_developer_program_active",
    "apple_team_id_available",
    "driverkit_entitlement_request_submitted",
    "pcidriverkit_transport_entitlement_request_submitted",
    "system_extension_capability_requested",
    "host_app_id_configured",
    "driver_app_id_configured",
    "driverkit_entitlement_approved",
    "pcidriverkit_transport_entitlement_approved",
    "system_extension_capability_approved",
    "provisioning_profiles_regenerated_after_approval",
]

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/provider-match-readiness-gate.json"
doc_path = ROOT / "docs/hackintosh/provider-match-readiness-gate.md"
entitlement_summary_path = ROOT / "release-readiness/local-entitlement-request-status-summary.json"
collector_manifest_path = ROOT / "tools/hackintosh/local-entitlement-request-status-collector.json"

manifest = read_json(manifest_path)
entitlement_summary = read_json(entitlement_summary_path)
collector_manifest = read_json(collector_manifest_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("entitlement_summary_exists", entitlement_summary_path),
    ("collector_manifest_exists", collector_manifest_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_readiness_gate.v1"), "schema")
if collector_manifest:
    add(checks, "collector_manifest_schema_if_present", collector_manifest.get("schema") == "h1mekartx.local_entitlement_request_status_collector.v1", "collector manifest schema")
else:
    add(checks, "collector_manifest_schema_if_present", True, "collector manifest absent; gate remains valid")

for field in [
    "provider_match_readiness_gate_ready",
    "provider_match_gate_not_provider_open",
    "rtx5070_target_retained",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "provider_match_attempted_by_this_phase",
    "provider_open_allowed_by_this_phase",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_allowed_by_this_phase",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_allowed_by_this_phase",
    "gpu_command_submission_attempted",
    "framebuffer_init_attempted",
    "display_engine_init_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("rtx5070_subsystem_vendor_id", "0x1458"),
    ("rtx5070_subsystem_id", "0x417e"),
    ("next_gate", "phase62e-provider-match-dryrun-observer-contract"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for field in REQUIRED_READY_FIELDS:
    add(checks, f"manifest_requires_{field}", bool(manifest and field in manifest.get("required_ready_fields", [])), field)
    add(checks, f"doc_mentions_{field}", field in doc, field)

ready_from_summary = bool(entitlement_summary and entitlement_summary.get("ready_for_provider_match") is True)
missing_fields = entitlement_summary.get("missing_ready_fields", REQUIRED_READY_FIELDS) if entitlement_summary else REQUIRED_READY_FIELDS
provider_match_ready = ready_from_summary and len(missing_fields) == 0

summary = {
    "schema": "h1mekartx.provider_match_readiness_gate_summary.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_PROVIDER_MATCH_READINESS_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "provider_match_gate_not_provider_open": True,
    "entitlement_summary_present": entitlement_summary is not None,
    "ready_for_provider_match": provider_match_ready,
    "ready_for_provider_match_source": ready_from_summary,
    "missing_ready_field_count": len(missing_fields),
    "missing_ready_fields": missing_fields,
    "provider_match_attempted_by_this_phase": False,
    "provider_open_allowed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_allowed_by_this_phase": False,
    "bar_mapping_attempted": False,
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
    "next_gate": "phase62e-provider-match-dryrun-observer-contract",
}
(OUT / "provider-match-readiness-gate-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

missing = "\n".join(f"- `{x}`" for x in missing_fields) or "- none"
(OUT / "provider-match-readiness-gate-summary.md").write_text(f"""# Provider Match Readiness Gate Summary

- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Provider Match Gate Not Provider Open: `True`
- Entitlement Summary Present: `{entitlement_summary is not None}`
- Ready For Provider Match: `{provider_match_ready}`
- Missing Ready Field Count: `{len(missing_fields)}`
- Provider Match Attempted By This Phase: `False`
- Provider Open Allowed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Allowed By This Phase: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Allowed By This Phase: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Next Gate: `phase62e-provider-match-dryrun-observer-contract`

## Missing Ready Fields

{missing}
""", encoding="utf-8")

add(checks, "summary_ready_for_provider_match_recorded", "ready_for_provider_match" in summary, "summary ready field")
add(checks, "summary_provider_match_not_attempted", summary["provider_match_attempted_by_this_phase"] is False, "no provider match")
add(checks, "summary_provider_open_blocked", summary["provider_open_allowed_by_this_phase"] is False and summary["provider_open_attempted"] is False, "provider open blocked")
add(checks, "summary_gpu_commands_blocked", summary["gpu_command_submission_allowed_by_this_phase"] is False and summary["gpu_command_submission_attempted"] is False, "gpu commands blocked")

for token in [
    "Provider match is blocked until entitlement status is ready",
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not submit GPU commands",
    "This phase does not claim Dock/transparency/blur acceleration",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PROVIDER_MATCH_READINESS_GATE_READY" if failed == 0 else "FAIL_PROVIDER_MATCH_READINESS_GATE"

report = {
    "schema": "h1mekartx.provider_match_readiness_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "provider_match_gate_not_provider_open": True,
    "ready_for_provider_match": provider_match_ready,
    "provider_match_attempted_by_this_phase": False,
    "provider_open_allowed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "next_gate": "phase62e-provider-match-dryrun-observer-contract",
    "checks": checks,
}
(OUT / "provider-match-readiness-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "provider-match-readiness-gate-check.md").write_text(f"""# Provider Match Readiness Gate Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Provider Match Gate Not Provider Open: `True`
- Ready For Provider Match: `{provider_match_ready}`
- Provider Match Attempted By This Phase: `False`
- Provider Open Allowed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Next Gate: `phase62e-provider-match-dryrun-observer-contract`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
print("ready_for_provider_match =", provider_match_ready)
raise SystemExit(0 if failed == 0 else 1)
