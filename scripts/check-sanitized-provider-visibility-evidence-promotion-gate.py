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

manifest_path = ROOT / "tools/hackintosh/sanitized-provider-visibility-evidence-promotion-gate.json"
doc_path = ROOT / "docs/hackintosh/sanitized-provider-visibility-evidence-promotion-gate.md"
gate_path = ROOT / "release-readiness/sanitized-provider-visibility-evidence-promotion-gate.json"
gate_md_path = ROOT / "release-readiness/sanitized-provider-visibility-evidence-promotion-gate.md"

manifest = read_json(manifest_path)
gate = read_json(gate_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
gate_md = gate_md_path.read_text(encoding="utf-8", errors="replace") if gate_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "gate_exists", gate_path.exists(), str(gate_path))
add(checks, "gate_md_exists", gate_md_path.exists(), str(gate_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.sanitized_provider_visibility_evidence_promotion_gate.v1"), "manifest schema")
add(checks, "gate_schema", bool(gate and gate.get("schema") == "h1mekartx.sanitized_provider_visibility_evidence_promotion_gate_output.v1"), "gate schema")
add(checks, "gate_decision_pass", bool(gate and gate.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_READY"), "gate decision")

for obj_name, obj in [("manifest", manifest), ("gate", gate)]:
    for field in ["rtx5070_target_retained", "promotion_gate_only"]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_true", obj.get(field) is True, field)
    for field in [
        "fallback_gpu_substitution_allowed",
        "provider_visibility_commands_executed_by_this_phase",
        "raw_capture_parsed_by_this_phase",
        "raw_stdout_committed",
        "raw_stderr_committed",
        "private_paths_committed",
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
        "promoted_to_provider_open",
        "promoted_to_bar_access",
        "promoted_to_gpu_command_submission",
        "promoted_to_metal",
    ]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62m-provider-match-readiness-reconciliation-from-visibility-evidence"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62m-provider-match-readiness-reconciliation-from-visibility-evidence"),
]:
    add(checks, f"gate_{key}", bool(gate and gate.get(key) == value), f"{key}={value}")

for field in [
    "input_matrix_pass",
    "input_matrix_check_pass",
    "input_runbook_check_pass",
    "inputs_safe",
    "sanitized_visibility_evidence_promotable_to_next_planning_gate",
]:
    add(checks, f"gate_{field}_true", bool(gate and gate.get(field) is True), field)

for field in [
    "ready_for_provider_open",
    "ready_for_bar_access",
    "ready_for_gpu_command_submission",
]:
    add(checks, f"gate_{field}_false", bool(gate and gate.get(field) is False), field)

for token in [
    "This phase is promotion-gate-only",
    "This phase does not execute provider visibility capture",
    "This phase does not parse raw capture",
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

combined_release = json.dumps(gate or {}) + "\n" + gate_md
for private_token in ["/Users/h1meka", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + private_token.replace("/", "_"), private_token not in combined_release, private_token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_READY" if failed == 0 else "FAIL_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE"

report = {
    "schema": "h1mekartx.sanitized_provider_visibility_evidence_promotion_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "promotion_gate_only": True,
    "provider_visibility_commands_executed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62m-provider-match-readiness-reconciliation-from-visibility-evidence",
    "checks": checks,
}
(OUT / "sanitized-provider-visibility-evidence-promotion-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = [
    "# Sanitized Provider Visibility Evidence Promotion Gate Check",
    "",
    f"- Decision: `{decision}`",
    "- RTX 5070 Target Retained: `True`",
    "- Fallback GPU Substitution Allowed: `False`",
    "- Promotion Gate Only: `True`",
    "- Provider Open Attempted: `False`",
    "- IOServiceOpen Attempted: `False`",
    "- BAR Mapping Attempted: `False`",
    "- BAR0 Read Attempted: `False`",
    "- BAR0 Write Attempted: `False`",
    "- GPU Command Submission Attempted: `False`",
    "- Current RTX 5070 Metal Acceleration Claimed: `False`",
    "- Dock/Transparency/Blur Acceleration Claimed: `False`",
    "- Next Gate: `phase62m-provider-match-readiness-reconciliation-from-visibility-evidence`",
    "",
    "## Checks",
    "",
    "| Check | Status | Detail |",
    "| --- | --- | --- |",
    rows,
    "",
]
(OUT / "sanitized-provider-visibility-evidence-promotion-gate-check.md").write_text("\n".join(md), encoding="utf-8")

print("Decision:", decision)
if failed:
    for c in checks:
        if not c["passed"]:
            print("FAIL:", c["name"], "|", c["detail"])
raise SystemExit(0 if failed == 0 else 1)
