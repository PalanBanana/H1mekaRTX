#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

FORBIDDEN_PATTERNS = {
    "raw_stdout_key": re.compile(r'"stdout"\s*:'),
    "raw_stderr_key": re.compile(r'"stderr"\s*:'),
    "command_key": re.compile(r'"command"\s*:'),
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "apple_development": re.compile(r"Apple Development:[^\n\r]+"),
    "developer_id_application": re.compile(r"Developer ID Application:[^\n\r]+"),
}

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/local-readonly-rtx5070-ui-baseline-collector.json"
doc_path = ROOT / "docs/hackintosh/local-readonly-rtx5070-ui-baseline-collector.md"
collector_path = ROOT / "scripts/collect-local-readonly-rtx5070-ui-baseline.py"
summary_json = OUT / "local-readonly-rtx5070-ui-baseline-summary.json"
summary_md = OUT / "local-readonly-rtx5070-ui-baseline-summary.md"
matrix_path = ROOT / "tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
matrix = read_json(matrix_path)
collector_text = collector_path.read_text(encoding="utf-8", errors="replace") if collector_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("collector_exists", collector_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("matrix_exists", matrix_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_readonly_rtx5070_ui_baseline_collector.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_readonly_rtx5070_ui_baseline_summary.v1"), "summary schema")
if matrix:
    add(checks, "matrix_schema_if_present", matrix.get("schema") == "h1mekartx.rtx5070_ui_smoothness_evidence_matrix.v1", "matrix schema")
else:
    add(checks, "matrix_schema_if_present", True, "matrix absent; baseline remains valid")

for field in [
    "local_readonly_rtx5070_ui_baseline_collector_ready",
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "current_windowserver_attribution_to_rtx5070_proven",
    "current_core_animation_attribution_to_rtx5070_proven",
    "current_quartzcore_attribution_to_rtx5070_proven",
    "current_metal_compositor_attribution_to_rtx5070_proven",
    "phase61_allowed_now",
    "xcodebuild_build_attempted_by_this_phase",
    "activation_submitted_by_this_phase",
    "deactivation_submitted_by_this_phase",
    "install_attempted",
    "manual_dext_load_attempted",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)
    add(checks, f"summary_{field}_false", bool(summary and summary.get(field) is False), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("next_gate", "phase60w-dock-transparency-blur-scenario-marker"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for token in [
    "system_profiler",
    "SPDisplaysDataType",
    "IOPCIDevice",
    "IOAccelerator",
    "IODisplayConnect",
    "WindowServer",
    "Dock",
    "reduceTransparency",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "collector_contains_" + token.replace(" ", "_").replace("/", "_"), token in collector_text, token)

if summary:
    for field in [
        "local_baseline_report_present",
        "rtx5070_target_retained",
        "raw_stdout_not_committed",
        "raw_stderr_not_committed",
    ]:
        add(checks, f"summary_{field}_true_or_recorded", field in summary and summary.get(field) is not None, field)

    for field in [
        "display_inventory_collected",
        "iopcidevice_inventory_collected",
        "rtx5070_identity_token_observed",
        "vendor_10de_observed",
        "device_2f04_observed",
        "iopcimatch_2f0410de_observed",
        "metal_string_observed_in_display_inventory",
        "windowserver_process_observed",
        "dock_process_observed",
        "rtx5070_acceleration_claim_valid",
        "rtx5070_ui_smoothness_claim_valid",
    ]:
        add(checks, f"summary_{field}_recorded", field in summary, field)

    add(checks, "summary_accel_claim_valid_false", summary.get("rtx5070_acceleration_claim_valid") is False, "accel false")
    add(checks, "summary_smoothness_claim_valid_false", summary.get("rtx5070_ui_smoothness_claim_valid") is False, "smoothness false")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_READONLY_RTX5070_UI_BASELINE_READY" if failed == 0 else "FAIL_LOCAL_READONLY_RTX5070_UI_BASELINE"

report = {
    "schema": "h1mekartx.local_readonly_rtx5070_ui_baseline_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "phase61_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase60w-dock-transparency-blur-scenario-marker",
    "checks": checks,
}

(OUT / "local-readonly-rtx5070-ui-baseline-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Local Read-Only RTX 5070 UI Baseline Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60w-dock-transparency-blur-scenario-marker`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "local-readonly-rtx5070-ui-baseline-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
