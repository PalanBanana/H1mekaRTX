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

manifest_path = ROOT / "tools/hackintosh/noopen-provider-match-dryrun-hardoptin-wrapper.json"
doc_path = ROOT / "docs/hackintosh/noopen-provider-match-dryrun-hardoptin-wrapper.md"
summary_path = ROOT / "release-readiness/noopen-provider-match-dryrun-hardoptin-wrapper-summary.json"
raw_path = ROOT / "host-report-bundle/noopen-provider-match-dryrun/noopen-provider-match-dryrun-local-capture.json"

manifest = read_json(manifest_path)
summary = read_json(summary_path)
raw = read_json(raw_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_exists", summary_path.exists(), str(summary_path))
add(checks, "raw_capture_exists_local_only", raw_path.exists(), str(raw_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.noopen_provider_match_dryrun_hardoptin_wrapper.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.noopen_provider_match_dryrun_hardoptin_wrapper_summary.v1"), "summary schema")
add(checks, "default_refuses_execution", bool(summary and summary.get("decision") == "REFUSED_NOOPEN_PROVIDER_MATCH_DRYRUN_MISSING_HARD_OPTIN"), "default refusal expected")
add(checks, "default_raw_refuses_execution", bool(raw and raw.get("decision") == "REFUSED_NOOPEN_PROVIDER_MATCH_DRYRUN_MISSING_HARD_OPTIN"), "raw default refusal expected")
add(checks, "default_commands_not_executed", bool(summary and summary.get("commands_executed") is False and raw and raw.get("commands_executed") is False), "commands false")

for obj_name, obj in [("manifest", manifest), ("summary", summary), ("raw", raw)]:
    for field in ["rtx5070_target_retained"]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_true", obj.get(field) is True, field)
    for field in [
        "fallback_gpu_substitution_allowed",
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

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62q-sanitized-noopen-provider-match-dryrun-output-parser"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for token in [
    "This phase defaults to refusal",
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not map BAR memory",
    "This phase does not read BAR0",
    "This phase does not write BAR0",
    "This phase does not submit GPU commands",
    "This phase does not claim RTX 5070 Metal acceleration",
    "This phase does not claim Dock/transparency/blur acceleration",
    "H1MEKARTX_ALLOW_NOOPEN_PROVIDER_MATCH_DRYRUN=I_UNDERSTAND_NOOPEN_PROVIDER_MATCH_DRYRUN_ONLY",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_HARDOPTIN_WRAPPER_READY" if failed == 0 else "FAIL_NOOPEN_PROVIDER_MATCH_DRYRUN_HARDOPTIN_WRAPPER"

report = {
    "schema": "h1mekartx.noopen_provider_match_dryrun_hardoptin_wrapper_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "default_refuses_execution": True,
    "commands_executed_by_default": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62q-sanitized-noopen-provider-match-dryrun-output-parser",
    "checks": checks,
}
(OUT / "noopen-provider-match-dryrun-hardoptin-wrapper-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "noopen-provider-match-dryrun-hardoptin-wrapper-check.md").write_text(f"""# No-Open Provider Match Dry-Run Hard-Opt-In Wrapper Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Default Refuses Execution: `True`
- Commands Executed By Default: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62q-sanitized-noopen-provider-match-dryrun-output-parser`

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
