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

final_ledger = read_json("release-readiness/provider-match-noopen-final-readiness-ledger.json")
final_check = read_json("release-readiness/provider-match-noopen-final-readiness-ledger-check.json")
promotion = read_json("release-readiness/noopen-provider-match-dryrun-evidence-promotion-gate.json")
preflight = read_json("release-readiness/provider-match-preflight-checklist-from-reconciled-evidence.json")

final_pass = bool(final_ledger and final_ledger.get("decision") == "PASS_PROVIDER_MATCH_NOOPEN_FINAL_READINESS_LEDGER_READY")
final_check_pass = bool(final_check and final_check.get("decision") == "PASS_PROVIDER_MATCH_NOOPEN_FINAL_READINESS_LEDGER_READY")
final_ready = bool(final_ledger and final_ledger.get("provider_match_noopen_final_readiness_ready") is True)
promotion_pass = bool(promotion and promotion.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_PROMOTION_GATE_READY")
preflight_ready = bool(preflight and preflight.get("provider_match_planning_preflight_ready") is True)

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

inputs_safe = safe(final_ledger) and safe(final_check) and safe(promotion) and safe(preflight)
handoff_ready = final_pass and final_check_pass and final_ready and promotion_pass and preflight_ready and inputs_safe

ledger = [
    {"id": "final_noopen_readiness_ledger_passed", "status": "PASS" if final_pass else "FAIL"},
    {"id": "final_noopen_readiness_check_passed", "status": "PASS" if final_check_pass else "FAIL"},
    {"id": "final_noopen_readiness_ready", "status": "PASS" if final_ready else "FAIL"},
    {"id": "noopen_promotion_gate_passed", "status": "PASS" if promotion_pass else "FAIL"},
    {"id": "provider_match_preflight_ready", "status": "PASS" if preflight_ready else "FAIL"},
    {"id": "inputs_safe", "status": "PASS" if inputs_safe else "FAIL"},
    {"id": "entitlement_request_package_not_created_yet", "status": "BLOCKED"},
    {"id": "driverkit_entitlement_not_approved_yet", "status": "BLOCKED"},
    {"id": "driverkit_profile_not_created_yet", "status": "BLOCKED"},
    {"id": "provider_open_blocked", "status": "PASS" if final_ledger and final_ledger.get("provider_open_ready") is False and final_ledger.get("provider_open_attempted") is False else "FAIL"},
    {"id": "ioserviceopen_blocked", "status": "PASS" if final_ledger and final_ledger.get("ioserviceopen_ready") is False and final_ledger.get("ioserviceopen_attempted") is False else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if final_ledger and final_ledger.get("bar_access_ready") is False and final_ledger.get("bar_mapping_attempted") is False else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if final_ledger and final_ledger.get("gpu_command_submission_ready") is False and final_ledger.get("gpu_command_submission_attempted") is False else "FAIL"},
    {"id": "metal_acceleration_not_ready", "status": "PASS" if final_ledger and final_ledger.get("metal_acceleration_ready") is False and final_ledger.get("current_rtx5070_metal_acceleration_claimed") is False else "FAIL"}
]

fail_count = sum(1 for item in ledger if item["status"] == "FAIL")
pass_count = sum(1 for item in ledger if item["status"] == "PASS")
blocked_count = sum(1 for item in ledger if item["status"] == "BLOCKED")
ready = handoff_ready and fail_count == 0

out = {
    "schema": "h1mekartx.noopen_to_entitlement_request_handoff_ledger_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_NOOPEN_TO_ENTITLEMENT_REQUEST_HANDOFF_LEDGER_OUTPUT",
    "decision": "PASS_NOOPEN_TO_ENTITLEMENT_REQUEST_HANDOFF_LEDGER_READY" if ready else "FAIL_NOOPEN_TO_ENTITLEMENT_REQUEST_HANDOFF_LEDGER",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "handoff_ledger_only": True,
    "input_final_readiness_ledger_present": final_ledger is not None,
    "input_final_readiness_ledger_check_present": final_check is not None,
    "input_noopen_promotion_gate_present": promotion is not None,
    "input_preflight_present": preflight is not None,
    "input_final_readiness_ledger_pass": final_pass,
    "input_final_readiness_ledger_check_pass": final_check_pass,
    "input_final_readiness_ready": final_ready,
    "input_noopen_promotion_gate_pass": promotion_pass,
    "input_preflight_ready": preflight_ready,
    "inputs_safe": inputs_safe,
    "ledger": ledger,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "fail_count": fail_count,
    "noopen_to_entitlement_request_handoff_ready": ready,
    "provider_match_noopen_final_readiness_ready": final_ready,
    "entitlement_request_package_ready": False,
    "driverkit_entitlement_approved": False,
    "driverkit_profile_created": False,
    "driverkit_profile_ready": False,
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
    "next_gate": "phase62v-entitlement-request-package-skeleton"
}

json_path = OUT / "noopen-to-entitlement-request-handoff-ledger.json"
md_path = OUT / "noopen-to-entitlement-request-handoff-ledger.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in ledger)
md_path.write_text(f"""# No-Open To Entitlement Request Handoff Ledger

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Handoff Ledger Only: `True`
- Input Final Readiness Ledger PASS: `{out['input_final_readiness_ledger_pass']}`
- Input Final Readiness Ledger Check PASS: `{out['input_final_readiness_ledger_check_pass']}`
- Input Final Readiness Ready: `{out['input_final_readiness_ready']}`
- Input No-Open Promotion Gate PASS: `{out['input_noopen_promotion_gate_pass']}`
- Input Preflight Ready: `{out['input_preflight_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- FAIL Count: `{out['fail_count']}`
- No-Open To Entitlement Request Handoff Ready: `{out['noopen_to_entitlement_request_handoff_ready']}`
- Provider Match No-Open Final Readiness Ready: `{out['provider_match_noopen_final_readiness_ready']}`
- Entitlement Request Package Ready: `False`
- DriverKit Entitlement Approved: `False`
- DriverKit Profile Created: `False`
- DriverKit Profile Ready: `False`
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
