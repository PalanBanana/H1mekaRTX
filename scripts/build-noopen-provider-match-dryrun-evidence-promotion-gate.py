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

matrix = read_json("release-readiness/noopen-provider-match-dryrun-evidence-matrix.json")
matrix_check = read_json("release-readiness/noopen-provider-match-dryrun-evidence-matrix-check.json")
parser_summary = read_json("release-readiness/sanitized-noopen-provider-match-dryrun-output-parser-summary.json")

matrix_pass = bool(matrix and matrix.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_MATRIX_READY")
matrix_check_pass = bool(matrix_check and matrix_check.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_MATRIX_READY")
matrix_ready = bool(matrix and matrix.get("noopen_dryrun_evidence_matrix_ready") is True)
default_refusal = bool(parser_summary and parser_summary.get("decision") == "REFUSED_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_PARSE_MISSING_HARD_OPTIN")

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

inputs_safe = safe(matrix) and safe(matrix_check) and safe(parser_summary)
promotable = matrix_pass and matrix_check_pass and matrix_ready and default_refusal and inputs_safe

out = {
    "schema": "h1mekartx.noopen_provider_match_dryrun_evidence_promotion_gate_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_PROMOTION_GATE_OUTPUT",
    "decision": "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_PROMOTION_GATE_READY" if promotable else "FAIL_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_PROMOTION_GATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "promotion_gate_only": True,
    "input_evidence_matrix_present": matrix is not None,
    "input_evidence_matrix_check_present": matrix_check is not None,
    "input_parser_summary_present": parser_summary is not None,
    "input_evidence_matrix_pass": matrix_pass,
    "input_evidence_matrix_check_pass": matrix_check_pass,
    "noopen_dryrun_evidence_matrix_ready": matrix_ready,
    "default_hardoptin_refusal_preserved": default_refusal,
    "inputs_safe": inputs_safe,
    "noopen_dryrun_evidence_promotable_to_next_planning_gate": promotable,
    "promoted_to_provider_open": False,
    "promoted_to_bar_access": False,
    "promoted_to_gpu_command_submission": False,
    "promoted_to_metal": False,
    "ready_for_provider_open": False,
    "ready_for_bar_access": False,
    "ready_for_gpu_command_submission": False,
    "ready_for_metal": False,
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
    "next_gate": "phase62t-provider-match-noopen-final-readiness-ledger"
}

json_path = OUT / "noopen-provider-match-dryrun-evidence-promotion-gate.json"
md_path = OUT / "noopen-provider-match-dryrun-evidence-promotion-gate.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

md_path.write_text(f"""# No-Open Provider Match Dry-Run Evidence Promotion Gate

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Promotion Gate Only: `True`
- Input Evidence Matrix Present: `{out['input_evidence_matrix_present']}`
- Input Evidence Matrix Check Present: `{out['input_evidence_matrix_check_present']}`
- Input Parser Summary Present: `{out['input_parser_summary_present']}`
- Input Evidence Matrix PASS: `{out['input_evidence_matrix_pass']}`
- Input Evidence Matrix Check PASS: `{out['input_evidence_matrix_check_pass']}`
- No-Open Dry-Run Evidence Matrix Ready: `{out['noopen_dryrun_evidence_matrix_ready']}`
- Default Hard-Opt-In Refusal Preserved: `{out['default_hardoptin_refusal_preserved']}`
- Inputs Safe: `{out['inputs_safe']}`
- No-Open Dry-Run Evidence Promotable To Next Planning Gate: `{out['noopen_dryrun_evidence_promotable_to_next_planning_gate']}`
- Promoted To Provider Open: `False`
- Promoted To BAR Access: `False`
- Promoted To GPU Command Submission: `False`
- Promoted To Metal: `False`
- Ready For Provider Open: `False`
- Ready For BAR Access: `False`
- Ready For GPU Command Submission: `False`
- Ready For Metal: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`
""", encoding="utf-8")

print("Decision:", out["decision"])
