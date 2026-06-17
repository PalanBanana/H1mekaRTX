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

manifest_path = ROOT / "tools/hackintosh/local-provider-match-dryrun-observer-summary.json"
doc_path = ROOT / "docs/hackintosh/local-provider-match-dryrun-observer-summary.md"
summary_path = ROOT / "release-readiness/local-provider-match-dryrun-observer-summary.json"
manifest = read_json(manifest_path)
summary = read_json(summary_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_exists", summary_path.exists(), str(summary_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_provider_match_dryrun_observer_summary.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_provider_match_dryrun_observer_summary_output.v1"), "summary schema")

for obj_name, obj in [("manifest", manifest), ("summary", summary)]:
    for field in [
        "rtx5070_target_retained",
    ]:
        add(checks, f"{obj_name}_{field}_true", bool(obj and obj.get(field) is True), field)

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
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("rtx5070_subsystem_vendor_id", "0x1458"),
    ("rtx5070_subsystem_id", "0x417e"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62g-readonly-provider-visibility-command-generator"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_subsystem_vendor_id", "0x1458"),
    ("expected_subsystem_id", "0x417e"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62g-readonly-provider-visibility-command-generator"),
]:
    add(checks, f"summary_{key}", bool(summary and summary.get(key) == value), f"{key}={value}")

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

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_PROVIDER_MATCH_DRYRUN_OBSERVER_SUMMARY_READY" if failed == 0 else "FAIL_LOCAL_PROVIDER_MATCH_DRYRUN_OBSERVER_SUMMARY"

report = {
    "schema": "h1mekartx.local_provider_match_dryrun_observer_summary_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
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
    "next_gate": "phase62g-readonly-provider-visibility-command-generator",
    "checks": checks,
}
(OUT / "local-provider-match-dryrun-observer-summary-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "local-provider-match-dryrun-observer-summary-check.md").write_text(f"""# Local Provider Match Dry-Run Observer Summary Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
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
- Next Gate: `phase62g-readonly-provider-visibility-command-generator`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
