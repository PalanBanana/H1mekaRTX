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

promotion = read_json("release-readiness/noopen-provider-match-dryrun-evidence-promotion-gate.json")
promotion_check = read_json("release-readiness/noopen-provider-match-dryrun-evidence-promotion-gate-check.json")
matrix = read_json("release-readiness/noopen-provider-match-dryrun-evidence-matrix.json")
preflight = read_json("release-readiness/provider-match-preflight-checklist-from-reconciled-evidence.json")

promotion_pass = bool(promotion and promotion.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_PROMOTION_GATE_READY")
promotion_check_pass = bool(promotion_check and promotion_check.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_PROMOTION_GATE_READY")
matrix_ready = bool(matrix and matrix.get("noopen_dryrun_evidence_matrix_ready") is True)
preflight_ready = bool(preflight and preflight.get("provider_match_planning_preflight_ready") is True)
default_refusal = bool(promotion and promotion.get("default_hardoptin_refusal_preserved") is True)
promotable_next = bool(promotion and promotion.get("noopen_dryrun_evidence_promotable_to_next_planning_gate") is True)

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

inputs_safe = safe(promotion) and safe(promotion_check) and safe(matrix) and safe(preflight)

ledger = [
    {"id": "rtx5070_target_identity", "status": "PASS" if promotion and promotion.get("expected_vendor_id") == "0x10de" and promotion.get("expected_device_id") == "0x2f04" and promotion.get("expected_iopcimatch") == "0x2f0410de" else "FAIL"},
    {"id": "preflight_ready", "status": "PASS" if preflight_ready else "FAIL"},
    {"id": "noopen_evidence_matrix_ready", "status": "PASS" if matrix_ready else "FAIL"},
    {"id": "noopen_evidence_promotion_gate_passed", "status": "PASS" if promotion_pass else "FAIL"},
    {"id": "noopen_evidence_promotion_check_passed", "status": "PASS" if promotion_check_pass else "FAIL"},
    {"id": "default_hardoptin_refusal_preserved", "status": "PASS" if default_refusal else "FAIL"},
    {"id": "noopen_evidence_promotable_next_planning_gate", "status": "PASS" if promotable_next else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if promotion and promotion.get("ready_for_provider_open") is False and promotion.get("promoted_to_provider_open") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if promotion and promotion.get("ready_for_bar_access") is False and promotion.get("promoted_to_bar_access") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if promotion and promotion.get("ready_for_gpu_command_submission") is False and promotion.get("promoted_to_gpu_command_submission") is False else "FAIL"},
    {"id": "metal_not_ready", "status": "PASS" if promotion and promotion.get("ready_for_metal") is False and promotion.get("promoted_to_metal") is False else "FAIL"},
    {"id": "dock_blur_not_claimed", "status": "PASS" if promotion and promotion.get("dock_transparency_blur_acceleration_claimed") is False else "FAIL"},
]

fail_count = sum(1 for item in ledger if item["status"] == "FAIL")
pass_count = sum(1 for item in ledger if item["status"] == "PASS")
ready = fail_count == 0 and promotion_pass and promotion_check_pass and matrix_ready and preflight_ready and default_refusal and promotable_next and inputs_safe

out = {
    "schema": "h1mekartx.provider_match_noopen_final_readiness_ledger_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_PROVIDER_MATCH_NOOPEN_FINAL_READINESS_LEDGER_OUTPUT",
    "decision": "PASS_PROVIDER_MATCH_NOOPEN_FINAL_READINESS_LEDGER_READY" if ready else "FAIL_PROVIDER_MATCH_NOOPEN_FINAL_READINESS_LEDGER",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "ledger_only": True,
    "input_promotion_gate_present": promotion is not None,
    "input_promotion_gate_check_present": promotion_check is not None,
    "input_evidence_matrix_present": matrix is not None,
    "input_preflight_present": preflight is not None,
    "input_promotion_gate_pass": promotion_pass,
    "input_promotion_gate_check_pass": promotion_check_pass,
    "input_evidence_matrix_ready": matrix_ready,
    "input_preflight_ready": preflight_ready,
    "default_hardoptin_refusal_preserved": default_refusal,
    "noopen_evidence_promotable_next_planning_gate": promotable_next,
    "inputs_safe": inputs_safe,
    "ledger": ledger,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "provider_match_noopen_final_readiness_ready": ready,
    "provider_open_ready": False,
    "ioserviceopen_ready": False,
    "bar_access_ready": False,
    "gpu_command_submission_ready": False,
    "metal_acceleration_ready": False,
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
    "next_gate": "phase62u-noopen-to-entitlement-request-handoff-ledger"
}

json_path = OUT / "provider-match-noopen-final-readiness-ledger.json"
md_path = OUT / "provider-match-noopen-final-readiness-ledger.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in ledger)
md_path.write_text(f"""# Provider Match No-Open Final Readiness Ledger

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Ledger Only: `True`
- Input Promotion Gate PASS: `{out['input_promotion_gate_pass']}`
- Input Promotion Gate Check PASS: `{out['input_promotion_gate_check_pass']}`
- Input Evidence Matrix Ready: `{out['input_evidence_matrix_ready']}`
- Input Preflight Ready: `{out['input_preflight_ready']}`
- Default Hard-Opt-In Refusal Preserved: `{out['default_hardoptin_refusal_preserved']}`
- No-Open Evidence Promotable Next Planning Gate: `{out['noopen_evidence_promotable_next_planning_gate']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Provider Match No-Open Final Readiness Ready: `{out['provider_match_noopen_final_readiness_ready']}`
- Provider Open Ready: `False`
- IOServiceOpen Ready: `False`
- BAR Access Ready: `False`
- GPU Command Submission Ready: `False`
- Metal Acceleration Ready: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Ledger

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
