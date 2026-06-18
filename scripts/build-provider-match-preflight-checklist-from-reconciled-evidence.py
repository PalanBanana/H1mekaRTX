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

recon = read_json("release-readiness/provider-match-readiness-reconciliation-from-visibility-evidence.json")
recon_check = read_json("release-readiness/provider-match-readiness-reconciliation-from-visibility-evidence-check.json")
promotion = read_json("release-readiness/sanitized-provider-visibility-evidence-promotion-gate.json")

recon_pass = bool(recon and recon.get("decision") == "PASS_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE_READY")
recon_check_pass = bool(recon_check and recon_check.get("decision") == "PASS_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE_READY")
promotion_pass = bool(promotion and promotion.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_READY")
planning_gate_ready = bool(recon and recon.get("provider_match_planning_gate_ready") is True)

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

inputs_safe = safe(recon) and safe(recon_check) and safe(promotion)
preflight_ready = recon_pass and recon_check_pass and promotion_pass and planning_gate_ready and inputs_safe

checklist = [
    {
        "id": "rtx5070_target_identity",
        "status": "PASS" if (recon and recon.get("expected_vendor_id") == "0x10de" and recon.get("expected_device_id") == "0x2f04" and recon.get("expected_iopcimatch") == "0x2f0410de") else "FAIL",
    },
    {"id": "promotion_gate_passed", "status": "PASS" if promotion_pass else "FAIL"},
    {"id": "reconciliation_passed", "status": "PASS" if recon_pass else "FAIL"},
    {"id": "reconciliation_check_passed", "status": "PASS" if recon_check_pass else "FAIL"},
    {"id": "provider_match_planning_gate_ready", "status": "PASS" if planning_gate_ready else "FAIL"},
    {"id": "provider_open_blocked", "status": "PASS" if (recon and recon.get("ready_for_provider_open") is False and recon.get("provider_open_promoted") is False) else "FAIL"},
    {"id": "bar_access_blocked", "status": "PASS" if (recon and recon.get("ready_for_bar_access") is False and recon.get("bar_access_promoted") is False) else "FAIL"},
    {"id": "gpu_command_submission_blocked", "status": "PASS" if (recon and recon.get("ready_for_gpu_command_submission") is False and recon.get("gpu_command_submission_promoted") is False) else "FAIL"},
    {"id": "metal_not_proven", "status": "PASS" if (recon and recon.get("current_rtx5070_metal_acceleration_claimed") is False) else "FAIL"},
    {"id": "dock_transparency_blur_not_proven", "status": "PASS" if (recon and recon.get("dock_transparency_blur_acceleration_claimed") is False) else "FAIL"},
]

fail_count = sum(1 for item in checklist if item["status"] == "FAIL")

out = {
    "schema": "h1mekartx.provider_match_preflight_checklist_from_reconciled_evidence_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_PROVIDER_MATCH_PREFLIGHT_CHECKLIST_FROM_RECONCILED_EVIDENCE_OUTPUT",
    "decision": "PASS_PROVIDER_MATCH_PREFLIGHT_CHECKLIST_FROM_RECONCILED_EVIDENCE_READY" if preflight_ready and fail_count == 0 else "FAIL_PROVIDER_MATCH_PREFLIGHT_CHECKLIST_FROM_RECONCILED_EVIDENCE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "preflight_checklist_only": True,
    "input_reconciliation_present": recon is not None,
    "input_reconciliation_check_present": recon_check is not None,
    "input_promotion_gate_present": promotion is not None,
    "input_reconciliation_pass": recon_pass,
    "input_reconciliation_check_pass": recon_check_pass,
    "input_promotion_gate_pass": promotion_pass,
    "inputs_safe": inputs_safe,
    "provider_match_planning_gate_ready": planning_gate_ready,
    "provider_match_planning_preflight_ready": preflight_ready and fail_count == 0,
    "checklist": checklist,
    "fail_count": fail_count,
    "provider_open_ready": False,
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
    "next_gate": "phase62o-noopen-provider-match-dryrun-command-manifest",
}

json_path = OUT / "provider-match-preflight-checklist-from-reconciled-evidence.json"
md_path = OUT / "provider-match-preflight-checklist-from-reconciled-evidence.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{item['id']}` | `{item['status']}` |" for item in checklist)
md_path.write_text(f"""# Provider Match Preflight Checklist From Reconciled Evidence

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Preflight Checklist Only: `True`
- Input Reconciliation Present: `{out['input_reconciliation_present']}`
- Input Reconciliation Check Present: `{out['input_reconciliation_check_present']}`
- Input Promotion Gate Present: `{out['input_promotion_gate_present']}`
- Input Reconciliation PASS: `{out['input_reconciliation_pass']}`
- Input Reconciliation Check PASS: `{out['input_reconciliation_check_pass']}`
- Input Promotion Gate PASS: `{out['input_promotion_gate_pass']}`
- Inputs Safe: `{out['inputs_safe']}`
- Provider Match Planning Gate Ready: `{out['provider_match_planning_gate_ready']}`
- Provider Match Planning Preflight Ready: `{out['provider_match_planning_preflight_ready']}`
- Provider Open Ready: `False`
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

## Checklist

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
