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

manifest = read_json(ROOT / "tools/hackintosh/provider-match-readiness-reconciliation-from-visibility-evidence.json")
out = read_json(ROOT / "release-readiness/provider-match-readiness-reconciliation-from-visibility-evidence.json")
doc_path = ROOT / "docs/hackintosh/provider-match-readiness-reconciliation-from-visibility-evidence.md"
out_md_path = ROOT / "release-readiness/provider-match-readiness-reconciliation-from-visibility-evidence.md"
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
out_md = out_md_path.read_text(encoding="utf-8", errors="replace") if out_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest is not None, "manifest")
add(checks, "output_exists", out is not None, "output")
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "output_md_exists", out_md_path.exists(), str(out_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_readiness_reconciliation_from_visibility_evidence.v1"), "manifest schema")
add(checks, "output_schema", bool(out and out.get("schema") == "h1mekartx.provider_match_readiness_reconciliation_from_visibility_evidence_output.v1"), "output schema")
add(checks, "output_decision_pass", bool(out and out.get("decision") == "PASS_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE_READY"), "output decision")

for obj_name, obj in [("manifest", manifest), ("output", out)]:
    for field in ["rtx5070_target_retained", "reconciliation_only"]:
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
        "provider_open_promoted",
        "bar_access_promoted",
        "gpu_command_submission_promoted",
        "metal_acceleration_promoted",
        "ready_for_provider_open",
        "ready_for_bar_access",
        "ready_for_gpu_command_submission",
    ]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for field in [
    "input_promotion_gate_present",
    "input_promotion_gate_check_present",
    "input_provider_match_readiness_summary_present",
    "input_promotion_gate_pass",
    "input_promotion_gate_check_pass",
    "sanitized_visibility_evidence_promotable_to_next_planning_gate",
    "inputs_safe",
    "provider_match_planning_gate_ready",
]:
    add(checks, f"output_{field}_true", bool(out and out.get(field) is True), field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62n-provider-match-preflight-checklist-from-reconciled-evidence"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62n-provider-match-preflight-checklist-from-reconciled-evidence"),
]:
    add(checks, f"output_{key}", bool(out and out.get(key) == value), f"{key}={value}")

for token in [
    "This phase is reconciliation-only",
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

combined_release = json.dumps(out or {}) + "\n" + out_md
for private_token in ["/Users/h1meka", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + private_token.replace("/", "_"), private_token not in combined_release, private_token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE_READY" if failed == 0 else "FAIL_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE"

report = {
    "schema": "h1mekartx.provider_match_readiness_reconciliation_from_visibility_evidence_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "reconciliation_only": True,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62n-provider-match-preflight-checklist-from-reconciled-evidence",
    "checks": checks,
}
(OUT / "provider-match-readiness-reconciliation-from-visibility-evidence-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = [
    "# Provider Match Readiness Reconciliation From Visibility Evidence Check",
    "",
    f"- Decision: `{decision}`",
    "- RTX 5070 Target Retained: `True`",
    "- Fallback GPU Substitution Allowed: `False`",
    "- Reconciliation Only: `True`",
    "- Provider Open Attempted: `False`",
    "- IOServiceOpen Attempted: `False`",
    "- BAR Mapping Attempted: `False`",
    "- BAR0 Read Attempted: `False`",
    "- BAR0 Write Attempted: `False`",
    "- GPU Command Submission Attempted: `False`",
    "- Current RTX 5070 Metal Acceleration Claimed: `False`",
    "- Dock/Transparency/Blur Acceleration Claimed: `False`",
    "- Next Gate: `phase62n-provider-match-preflight-checklist-from-reconciled-evidence`",
    "",
    "## Checks",
    "",
    "| Check | Status | Detail |",
    "| --- | --- | --- |",
    rows,
    "",
]
(OUT / "provider-match-readiness-reconciliation-from-visibility-evidence-check.md").write_text("\n".join(md), encoding="utf-8")

print("Decision:", decision)
if failed:
    for c in checks:
        if not c["passed"]:
            print("FAIL:", c["name"], "|", c["detail"])
raise SystemExit(0 if failed == 0 else 1)
