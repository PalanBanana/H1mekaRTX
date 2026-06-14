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

manifest_path = ROOT / "tools/hackintosh/rtx5070-accelerated-bringup-critical-path-gate.json"
doc_path = ROOT / "docs/hackintosh/rtx5070-accelerated-bringup-critical-path-gate.md"
manifest = read_json(manifest_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.rtx5070_accelerated_bringup_critical_path_gate.v1"), "schema")

for field in [
    "rtx5070_target_retained",
    "acceleration_gate_not_acceleration",
    "driverkit_entitlement_required",
    "pcidriverkit_transport_entitlement_required",
    "system_extension_provisioning_required",
    "provider_match_required",
    "provider_open_policy_required",
    "safe_bar_access_design_required",
    "minimal_gpu_command_path_required",
    "framebuffer_display_path_required",
    "metal_compositor_attribution_required",
    "dock_transparency_blur_metric_gate_required",
    "rtx5070_only_attribution_required",
    "apple_developer_program_required",
]:
    add(checks, f"{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "phase62b_allowed_now",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_attempted",
    "framebuffer_init_attempted",
    "display_engine_init_attempted",
    "metal_hud_enabled_by_this_phase",
    "metal_workload_run_by_this_phase",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]:
    add(checks, f"{field}_false", bool(manifest and manifest.get(field) is False), field)

for gate in [
    "driverkit_entitlement_gate",
    "pcidriverkit_transport_entitlement_gate",
    "system_extension_provisioning_gate",
    "provider_match_gate",
    "provider_open_policy_gate",
    "safe_bar_access_design_gate",
    "bar_readonly_proof_gate",
    "bar_mutation_approval_gate",
    "minimal_gpu_command_path_design_gate",
    "minimal_gpu_command_path_hardoptin_gate",
    "gpu_command_completion_evidence_gate",
    "framebuffer_display_path_design_gate",
    "framebuffer_display_path_hardoptin_gate",
    "windowserver_attribution_gate",
    "core_animation_attribution_gate",
    "quartzcore_attribution_gate",
    "metal_compositor_attribution_gate",
    "dock_transparency_blur_scenario_metric_gate",
    "rtx5070_only_attribution_proof_gate",
]:
    add(checks, f"critical_path_has_{gate}", bool(manifest and gate in manifest.get("critical_path", [])), gate)

add(checks, "apple_fee_usd_99_recorded", bool(manifest and manifest.get("apple_developer_program_official_annual_fee_usd") == 99), "99 USD")
add(checks, "next_gate", bool(manifest and manifest.get("next_gate") == "phase62b-apple-driverkit-pcidriverkit-entitlement-request-package"), "next gate")

for token in [
    "DriverKit entitlement gate",
    "PCIDriverKit transport entitlement gate",
    "Provider match gate",
    "Safe BAR access design gate",
    "Minimal GPU command path design gate",
    "Framebuffer/display path design gate",
    "Metal compositor attribution gate",
    "Dock/transparency/blur scenario metric gate",
    "This phase does not submit GPU commands",
    "This phase does not claim Dock/transparency/blur acceleration",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_RTX5070_ACCELERATED_BRINGUP_CRITICAL_PATH_GATE_READY" if failed == 0 else "FAIL_RTX5070_ACCELERATED_BRINGUP_CRITICAL_PATH_GATE"

report = {
    "schema": "h1mekartx.rtx5070_accelerated_bringup_critical_path_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "acceleration_gate_not_acceleration": True,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase62b-apple-driverkit-pcidriverkit-entitlement-request-package",
    "checks": checks,
}
(OUT / "rtx5070-accelerated-bringup-critical-path-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "rtx5070-accelerated-bringup-critical-path-gate-check.md").write_text(f"""# RTX 5070 Accelerated Bring-Up Critical Path Gate Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Acceleration Gate Not Acceleration: `True`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase62b-apple-driverkit-pcidriverkit-entitlement-request-package`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")
print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
