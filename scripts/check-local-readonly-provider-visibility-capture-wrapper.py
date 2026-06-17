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

manifest_path = ROOT / "tools/hackintosh/local-readonly-provider-visibility-capture-wrapper.json"
doc_path = ROOT / "docs/hackintosh/local-readonly-provider-visibility-capture-wrapper.md"
summary_path = ROOT / "release-readiness/local-readonly-provider-visibility-capture-summary.json"
raw_capture_path = ROOT / "host-report-bundle/readonly-provider-visibility/readonly-provider-visibility-local-capture.json"

manifest = read_json(manifest_path)
summary = read_json(summary_path)
raw_capture = read_json(raw_capture_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_exists", summary_path.exists(), str(summary_path))
add(checks, "raw_capture_exists_local_only", raw_capture_path.exists(), str(raw_capture_path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_readonly_provider_visibility_capture_wrapper.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_readonly_provider_visibility_capture_summary.v1"), "summary schema")

for field in [
    "rtx5070_target_retained",
    "hard_opt_in_required",
    "default_refuses_capture",
    "allowed_readonly_capture",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for key, value in [
    ("hard_opt_in_env", "H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY"),
    ("hard_opt_in_value", "I_UNDERSTAND_READONLY_PROVIDER_VISIBILITY_ONLY"),
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62i-sanitized-local-provider-visibility-capture-parser"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

# Default CI/local verification must refuse capture and execute no discovery commands.
summary_decision = str(summary.get("decision", "") if summary else "").strip()
add(
    checks,
    "default_summary_refused_missing_hardoptin",
    bool(
        summary
        and summary.get("hard_opt_in_matched") is False
        and summary.get("commands_executed") is False
        and summary_decision.startswith("REFUSED_READONLY_PROVIDER_VISIBILITY_CAPTURE")
        and "HARD_OPTIN" in summary_decision
    ),
    f"default refusal expected, got {summary_decision!r}",
)
add(
    checks,
    "default_summary_hardoptin_false",
    bool(summary and summary.get("hard_opt_in_matched") is False),
    "hard opt-in false",
)
add(
    checks,
    "default_summary_commands_executed_false",
    bool(summary and summary.get("commands_executed") is False),
    "commands executed false",
)
raw_decision = str(raw_capture.get("decision", "") if raw_capture else "").strip()
add(
    checks,
    "default_raw_capture_refused_missing_hardoptin",
    bool(
        raw_capture
        and raw_capture.get("hard_opt_in_matched") is False
        and raw_capture.get("commands_executed") is False
        and raw_decision.startswith("REFUSED_READONLY_PROVIDER_VISIBILITY_CAPTURE")
        and "HARD_OPTIN" in raw_decision
    ),
    f"raw default refusal expected, got {raw_decision!r}",
)
add(
    checks,
    "default_raw_capture_commands_executed_false",
    bool(raw_capture and raw_capture.get("commands_executed") is False),
    "raw commands executed false",
)

# All dangerous activity must remain false in manifest, summary, and raw capture when present.
danger_false_fields = [
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
]

for obj_name, obj in [
    ("manifest", manifest),
    ("summary", summary),
    ("raw_capture", raw_capture),
]:
    for field in danger_false_fields:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for token in [
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not map BAR memory",
    "This phase does not read BAR0",
    "This phase does not write BAR0",
    "This phase does not submit GPU commands",
    "This phase does not claim RTX 5070 Metal acceleration",
    "This phase does not claim Dock/transparency/blur acceleration",
    "Default behavior must refuse capture",
    "host-report-bundle/readonly-provider-visibility/",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

# Ensure no local-only raw report is accidentally represented as a release artifact.
add(
    checks,
    "summary_raw_path_redacted_under_host_report_bundle",
    bool(summary and str(summary.get("raw_capture_path_redacted", "")).startswith("host-report-bundle/readonly-provider-visibility/")),
    "raw path redacted",
)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_READONLY_PROVIDER_VISIBILITY_CAPTURE_WRAPPER_READY" if failed == 0 else "FAIL_LOCAL_READONLY_PROVIDER_VISIBILITY_CAPTURE_WRAPPER"

report = {
    "schema": "h1mekartx.local_readonly_provider_visibility_capture_wrapper_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "hard_opt_in_required": True,
    "default_refuses_capture": True,
    "commands_executed_by_default": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62i-sanitized-local-provider-visibility-capture-parser",
    "checks": checks,
}
(OUT / "local-readonly-provider-visibility-capture-wrapper-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(
    f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |"
    for c in checks
)
(OUT / "local-readonly-provider-visibility-capture-wrapper-check.md").write_text(f"""# Local Read-Only Provider Visibility Capture Wrapper Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Hard Opt-In Required: `True`
- Default Refuses Capture: `True`
- Commands Executed By Default: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62i-sanitized-local-provider-visibility-capture-parser`

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
