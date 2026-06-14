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

manifest_path = ROOT / "tools/hackintosh/rtx5070-ui-smoothness-roadmap.json"
doc_path = ROOT / "docs/hackintosh/rtx5070-ui-smoothness-roadmap.md"
phase60r_manifest = ROOT / "tools/driverkit-buildable-scaffold/apple-developer-entitlement-request-checklist.json"
phase60q_manifest = ROOT / "tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json"

manifest = read_json(manifest_path)
phase60r = read_json(phase60r_manifest)
phase60q = read_json(phase60q_manifest)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "phase60r_manifest_present_or_non_blocking", True, str(phase60r_manifest.exists()))
add(checks, "phase60q_manifest_present_or_non_blocking", True, str(phase60q_manifest.exists()))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.rtx5070_ui_smoothness_roadmap.v1"), "manifest schema")

if phase60r:
    add(checks, "phase60r_schema_if_present", phase60r.get("schema") == "h1mekartx.apple_developer_entitlement_request_checklist.v1", "phase60r schema")
else:
    add(checks, "phase60r_schema_if_present", True, "phase60r manifest absent; roadmap remains valid")

if phase60q:
    add(checks, "phase60q_schema_if_present", phase60q.get("schema") == "h1mekartx.provisioning_entitlement_hardblock_gate.v1", "phase60q schema")
else:
    add(checks, "phase60q_schema_if_present", True, "phase60q manifest absent; roadmap remains valid")

for field in [
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
    "must_not_switch_to_fallback_gpu",
    "paid_developer_team_required",
    "driverkit_entitlement_approval_required",
    "system_extension_capability_required",
    "driverkit_pci_transport_entitlement_required",
    "real_driverkit_dext_built_required",
    "system_extension_activation_required",
    "rtx5070_provider_visibility_required",
    "future_provider_open_gate_required",
    "future_bar_mapping_gate_required",
    "future_gpu_command_submission_gate_required",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "amd_igpu_apple_silicon_substitution_allowed",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "current_windowserver_attribution_to_rtx5070_proven",
    "current_core_animation_attribution_to_rtx5070_proven",
    "current_quartzcore_attribution_to_rtx5070_proven",
    "current_metal_compositor_attribution_to_rtx5070_proven",
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

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("next_gate", "phase60u-rtx5070-ui-smoothness-evidence-matrix"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for token in [
    "RTX 5070",
    "Dock smoothness must remain in scope",
    "Transparency / blur smoothness must remain in scope",
    "The target GPU remains RTX 5070",
    "does not switch the project goal to AMD",
    "No spoofed Metal support is used",
    "WindowServer / Core Animation / QuartzCore / Metal compositor path can be attributed to RTX 5070",
    "provider open remains blocked",
    "BAR mapping remains blocked",
    "GPU command submission remains blocked",
    "Metal proof remains blocked",
    "Dock/transparency/blur proof remains blocked",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_").replace("/", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_RTX5070_UI_SMOOTHNESS_ROADMAP_READY" if failed == 0 else "FAIL_RTX5070_UI_SMOOTHNESS_ROADMAP"

report = {
    "schema": "h1mekartx.rtx5070_ui_smoothness_roadmap_check.v1",
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
    "next_gate": "phase60u-rtx5070-ui-smoothness-evidence-matrix",
    "checks": checks,
}

(OUT / "rtx5070-ui-smoothness-roadmap-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# RTX 5070 UI Smoothness Roadmap Check

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
- Next Gate: `phase60u-rtx5070-ui-smoothness-evidence-matrix`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "rtx5070-ui-smoothness-roadmap-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
