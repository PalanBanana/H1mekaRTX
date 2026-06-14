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

matrix_path = ROOT / "tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json"
doc_path = ROOT / "docs/hackintosh/rtx5070-ui-smoothness-evidence-matrix.md"
roadmap_path = ROOT / "tools/hackintosh/rtx5070-ui-smoothness-roadmap.json"

matrix = read_json(matrix_path)
roadmap = read_json(roadmap_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []

for name, path in [
    ("matrix_exists", matrix_path),
    ("doc_exists", doc_path),
    ("roadmap_exists", roadmap_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "matrix_schema", bool(matrix and matrix.get("schema") == "h1mekartx.rtx5070_ui_smoothness_evidence_matrix.v1"), "matrix schema")
if roadmap:
    add(checks, "roadmap_schema_if_present", roadmap.get("schema") == "h1mekartx.rtx5070_ui_smoothness_roadmap.v1", "roadmap schema")
else:
    add(checks, "roadmap_schema_if_present", True, "roadmap absent; matrix remains valid")

for field in [
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
]:
    add(checks, f"matrix_{field}_true", bool(matrix and matrix.get(field) is True), field)

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
    add(checks, f"matrix_{field}_false", bool(matrix and matrix.get(field) is False), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("next_gate", "phase60v-local-readonly-rtx5070-ui-baseline-collector"),
]:
    add(checks, f"matrix_{key}", bool(matrix and matrix.get(key) == value), f"{key}={value}")

levels = matrix.get("evidence_levels", []) if matrix else []
add(checks, "matrix_has_9_levels", len(levels) == 9, f"levels={len(levels)}")
for expected_level in range(0, 9):
    found = [x for x in levels if x.get("level") == expected_level]
    add(checks, f"level_{expected_level}_exists", bool(found), f"level={expected_level}")
    if found:
        add(checks, f"level_{expected_level}_not_passed_now", found[0].get("passed_now") is False, f"passed_now={found[0].get('passed_now')}")

for scenario in [
    "dock_magnification",
    "dock_hide_show",
    "dock_launch_animation",
    "menu_bar_transparency",
    "window_transparency",
    "sheet_blur",
    "sidebar_blur",
    "window_movement",
    "window_resize",
    "mission_control",
    "launchpad",
    "stage_manager",
    "desktop_space_switching",
]:
    add(checks, f"scenario_{scenario}", bool(matrix and scenario in matrix.get("scenarios", [])), scenario)

for metric in [
    "display_refresh_rate",
    "average_frame_interval",
    "p50_frame_interval",
    "p95_frame_interval",
    "p99_frame_interval",
    "dropped_frame_count",
    "hitch_count",
    "latency_average",
    "latency_p95",
    "jitter_score",
    "before_after_delta",
]:
    add(checks, f"metric_{metric}", bool(matrix and metric in matrix.get("metrics", [])), metric)

for token in [
    "RTX 5070 UI Smoothness Evidence Matrix",
    "Fallback GPU substitution is not allowed as proof",
    "Dock magnification",
    "Dock hide/show",
    "window movement",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "WindowServer attribution to RTX 5070",
    "Core Animation attribution to RTX 5070",
    "QuartzCore attribution to RTX 5070",
    "Metal compositor attribution to RTX 5070",
    "provider open remains blocked",
    "BAR mapping remains blocked",
    "GPU command submission remains blocked",
    "Metal proof remains blocked",
    "Dock/transparency/blur proof remains blocked",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_").replace("/", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_RTX5070_UI_SMOOTHNESS_EVIDENCE_MATRIX_READY" if failed == 0 else "FAIL_RTX5070_UI_SMOOTHNESS_EVIDENCE_MATRIX"

report = {
    "schema": "h1mekartx.rtx5070_ui_smoothness_evidence_matrix_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "dock_transparency_blur_scope_retained": True,
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
    "next_gate": "phase60v-local-readonly-rtx5070-ui-baseline-collector",
    "checks": checks,
}

(OUT / "rtx5070-ui-smoothness-evidence-matrix-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# RTX 5070 UI Smoothness Evidence Matrix Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Dock/Transparency/Blur Scope Retained: `True`
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
- Next Gate: `phase60v-local-readonly-rtx5070-ui-baseline-collector`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "rtx5070-ui-smoothness-evidence-matrix-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
