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

promotion = read_json("release-readiness/sanitized-provider-visibility-evidence-promotion-gate.json")
promotion_check = read_json("release-readiness/sanitized-provider-visibility-evidence-promotion-gate-check.json")
readiness = read_json("release-readiness/provider-match-readiness-gate-summary.json")

promotion_pass = bool(promotion and promotion.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_READY")
promotion_check_pass = bool(promotion_check and promotion_check.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_PROMOTION_GATE_READY")
visibility_promotable = bool(promotion and promotion.get("sanitized_visibility_evidence_promotable_to_next_planning_gate") is True)
previous_ready = readiness.get("ready_for_provider_match") if isinstance(readiness, dict) else None
missing = readiness.get("missing_ready_fields", []) if isinstance(readiness, dict) else []

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

inputs_safe = safe(promotion) and safe(promotion_check) and safe(readiness)
planning_ready = promotion_pass and promotion_check_pass and visibility_promotable and inputs_safe

out = {
    "schema": "h1mekartx.provider_match_readiness_reconciliation_from_visibility_evidence_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE_OUTPUT",
    "decision": "PASS_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE_READY" if planning_ready else "FAIL_PROVIDER_MATCH_READINESS_RECONCILIATION_FROM_VISIBILITY_EVIDENCE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "reconciliation_only": True,
    "input_promotion_gate_present": promotion is not None,
    "input_promotion_gate_check_present": promotion_check is not None,
    "input_provider_match_readiness_summary_present": readiness is not None,
    "input_promotion_gate_pass": promotion_pass,
    "input_promotion_gate_check_pass": promotion_check_pass,
    "sanitized_visibility_evidence_promotable_to_next_planning_gate": visibility_promotable,
    "inputs_safe": inputs_safe,
    "previous_ready_for_provider_match": previous_ready,
    "previous_missing_ready_field_count": len(missing) if isinstance(missing, list) else 0,
    "previous_missing_ready_fields": missing if isinstance(missing, list) else [],
    "provider_match_planning_gate_ready": planning_ready,
    "ready_for_provider_open": False,
    "ready_for_bar_access": False,
    "ready_for_gpu_command_submission": False,
    "ready_for_metal": False,
    "provider_open_promoted": False,
    "bar_access_promoted": False,
    "gpu_command_submission_promoted": False,
    "metal_acceleration_promoted": False,
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
    "next_gate": "phase62n-provider-match-preflight-checklist-from-reconciled-evidence"
}

json_path = OUT / "provider-match-readiness-reconciliation-from-visibility-evidence.json"
md_path = OUT / "provider-match-readiness-reconciliation-from-visibility-evidence.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

missing_md = "\n".join(f"- `{x}`" for x in out["previous_missing_ready_fields"]) or "- none"
md = "".join([
    "# Provider Match Readiness Reconciliation From Visibility Evidence\n\n",
    f"- Decision: `{out['decision']}`\n",
    "- RTX 5070 Target Retained: `True`\n",
    "- Fallback GPU Substitution Allowed: `False`\n",
    "- Reconciliation Only: `True`\n",
    f"- Input Promotion Gate PASS: `{out['input_promotion_gate_pass']}`\n",
    f"- Input Promotion Gate Check PASS: `{out['input_promotion_gate_check_pass']}`\n",
    f"- Sanitized Visibility Evidence Promotable To Next Planning Gate: `{out['sanitized_visibility_evidence_promotable_to_next_planning_gate']}`\n",
    f"- Inputs Safe: `{out['inputs_safe']}`\n",
    f"- Previous Ready For Provider Match: `{out['previous_ready_for_provider_match']}`\n",
    f"- Provider Match Planning Gate Ready: `{out['provider_match_planning_gate_ready']}`\n",
    "- Ready For Provider Open: `False`\n",
    "- Ready For BAR Access: `False`\n",
    "- Ready For GPU Command Submission: `False`\n",
    "- Ready For Metal: `False`\n",
    "- Provider Open Promoted: `False`\n",
    "- BAR Access Promoted: `False`\n",
    "- GPU Command Submission Promoted: `False`\n",
    "- Metal Acceleration Promoted: `False`\n",
    "- Provider Open Attempted: `False`\n",
    "- IOServiceOpen Attempted: `False`\n",
    "- BAR Mapping Attempted: `False`\n",
    "- BAR0 Read Attempted: `False`\n",
    "- BAR0 Write Attempted: `False`\n",
    "- GPU Command Submission Attempted: `False`\n",
    "- Current RTX 5070 Metal Acceleration Claimed: `False`\n",
    "- Dock/Transparency/Blur Acceleration Claimed: `False`\n",
    f"- Next Gate: `{out['next_gate']}`\n\n",
    "## Previous Missing Ready Fields\n\n",
    missing_md,
    "\n",
])
md_path.write_text(md, encoding="utf-8")
print("Decision:", out["decision"])
