#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(rel: str):
    p = ROOT / rel
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))

matrix = read_json("release-readiness/sanitized-provider-visibility-evidence-matrix.json")
matrix_check = read_json("release-readiness/sanitized-provider-visibility-evidence-matrix-check.json")
runbook_check = read_json("release-readiness/local-optin-provider-visibility-evidence-capture-runbook-check.json")

matrix_pass = bool(matrix and matrix.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX_READY")
matrix_check_pass = bool(matrix_check and matrix_check.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX_READY")
runbook_check_pass = bool(runbook_check and runbook_check.get("decision") == "PASS_LOCAL_OPTIN_PROVIDER_VISIBILITY_EVIDENCE_CAPTURE_RUNBOOK_READY")

danger_keys = [
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar0_read_attempted",
    "bar0_write_attempted",
    "gpu_command_submission_attempted",
    "current_rtx5070_metal_acceleration_claimed",
    "dock_transparency_blur_acceleration_claimed",
]

def safe(obj):
    return isinstance(obj, dict) and all(obj.get(k) is False for k in danger_keys if k in obj)

inputs_safe = safe(matrix) and safe(matrix_check) and safe(runbook_check)
promotable = matrix_pass and matrix_check_pass and runbook_check_pass and inputs_safe

out = {
    "schema": "h1mekartx.sanitized_provider_visibility_evidence_promotion_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_OUTPUT",
    "decision": "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_READY" if promotable else "FAIL_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "promotion_gate_only": True,
    "input_matrix_present": matrix is not None,
    "input_matrix_check_present": matrix_check is not None,
    "input_runbook_check_present": runbook_check is not None,
    "input_matrix_pass": matrix_pass,
    "input_matrix_check_pass": matrix_check_pass,
    "input_runbook_check_pass": runbook_check_pass,
    "inputs_safe": inputs_safe,
    "sanitized_visibility_evidence_promotable_to_next_planning_gate": promotable,
    "promoted_to_provider_open": False,
    "promoted_to_bar_access": False,
    "promoted_to_gpu_command_submission": False,
    "promoted_to_metal": False,
    "ready_for_provider_open": False,
    "ready_for_bar_access": False,
    "ready_for_gpu_command_submission": False,
    "provider_visibility_commands_executed_by_this_phase": False,
    "raw_capture_parsed_by_this_phase": False,
    "raw_stdout_committed": False,
    "raw_stderr_committed": False,
    "private_paths_committed": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "bar_mmio_mutation_attempted": False,
    "configuration_writes_attempted": False,
    "firmware_load_attempted": False,
    "gpu_reset_attempted": False,
    "framebuffer_init_attempted": False,
    "display_engine_init_attempted": False,
    "gpu_command_submission_attempted": False,
    "metal_proof_claimed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "next_gate": "phase62m-provider-match-readiness-reconciliation-from-visibility-evidence",
}

json_path = OUT / "sanitized-provider-visibility-evidence-promotion-gate.json"
md_path = OUT / "sanitized-provider-visibility-evidence-promotion-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

lines = [
    "# Sanitized Provider Visibility Evidence Promotion Gate",
    "",
    f"- Decision: `{out['decision']}`",
    "- RTX 5070 Target Retained: `True`",
    "- Fallback GPU Substitution Allowed: `False`",
    "- Promotion Gate Only: `True`",
    f"- Input Matrix Present: `{out['input_matrix_present']}`",
    f"- Input Matrix Check Present: `{out['input_matrix_check_present']}`",
    f"- Input Runbook Check Present: `{out['input_runbook_check_present']}`",
    f"- Input Matrix PASS: `{out['input_matrix_pass']}`",
    f"- Input Matrix Check PASS: `{out['input_matrix_check_pass']}`",
    f"- Input Runbook Check PASS: `{out['input_runbook_check_pass']}`",
    f"- Inputs Safe: `{out['inputs_safe']}`",
    f"- Sanitized Visibility Evidence Promotable To Next Planning Gate: `{out['sanitized_visibility_evidence_promotable_to_next_planning_gate']}`",
    "- Promoted To Provider Open: `False`",
    "- Promoted To BAR Access: `False`",
    "- Promoted To GPU Command Submission: `False`",
    "- Promoted To Metal: `False`",
    "- Ready For Provider Open: `False`",
    "- Ready For BAR Access: `False`",
    "- Ready For GPU Command Submission: `False`",
    "- Provider Open Attempted: `False`",
    "- IOServiceOpen Attempted: `False`",
    "- BAR Mapping Attempted: `False`",
    "- BAR0 Read Attempted: `False`",
    "- BAR0 Write Attempted: `False`",
    "- GPU Command Submission Attempted: `False`",
    "- Current RTX 5070 Metal Acceleration Claimed: `False`",
    "- Dock/Transparency/Blur Acceleration Claimed: `False`",
    f"- Next Gate: `{out['next_gate']}`",
    "",
]
md_path.write_text("\n".join(lines), encoding="utf-8")
print("Decision:", out["decision"])
