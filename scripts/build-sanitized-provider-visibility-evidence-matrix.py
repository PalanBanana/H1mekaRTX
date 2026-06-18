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
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))

summary = read_json(ROOT / "release-readiness/sanitized-local-provider-visibility-capture-parser-summary.json")
check = read_json(ROOT / "release-readiness/sanitized-local-provider-visibility-capture-parser-check.json")

def val(key, default=None):
    if isinstance(summary, dict):
        return summary.get(key, default)
    return default

def status_bool(value, true_status="PASS", false_status="MISSING"):
    return true_status if bool(value) else false_status

matrix = [
    {
        "id": "rtx5070_target_identity",
        "status": "PASS" if (
            val("expected_vendor_id") == "0x10de"
            and val("expected_device_id") == "0x2f04"
            and val("expected_iopcimatch") == "0x2f0410de"
        ) else "FAIL",
        "evidence": {
            "expected_vendor_id": val("expected_vendor_id"),
            "expected_device_id": val("expected_device_id"),
            "expected_iopcimatch": val("expected_iopcimatch"),
        },
    },
    {
        "id": "sanitized_parser_summary_present",
        "status": "PASS" if summary is not None else "MISSING",
        "evidence": {"summary_present": summary is not None},
    },
    {
        "id": "sanitized_parser_check_present",
        "status": "PASS" if check is not None else "MISSING",
        "evidence": {"check_present": check is not None, "check_decision": check.get("decision") if isinstance(check, dict) else None},
    },
    {
        "id": "raw_capture_availability",
        "status": "PASS" if val("raw_capture_exists_local") else "MISSING",
        "evidence": {"raw_capture_exists_local": val("raw_capture_exists_local")},
    },
    {
        "id": "hard_opt_in_state",
        "status": "BLOCKED" if val("hard_opt_in_matched") is False else "PASS",
        "evidence": {"hard_opt_in_matched": val("hard_opt_in_matched")},
    },
    {
        "id": "raw_capture_read_state",
        "status": "BLOCKED" if val("raw_capture_read") is False else "PASS",
        "evidence": {"raw_capture_read": val("raw_capture_read")},
    },
    {
        "id": "provider_visibility_h1mekartx_token",
        "status": status_bool(val("detected_any_h1mekartx"), "PASS", "NOT_PROVEN"),
        "evidence": {"detected_any_h1mekartx": val("detected_any_h1mekartx")},
    },
    {
        "id": "provider_visibility_iopcidevice_token",
        "status": status_bool(val("detected_any_iopcidevice"), "PASS", "NOT_PROVEN"),
        "evidence": {"detected_any_iopcidevice": val("detected_any_iopcidevice")},
    },
    {
        "id": "provider_visibility_pci_identity_tokens",
        "status": "PASS" if (val("detected_any_10de") and val("detected_any_2f04")) else "NOT_PROVEN",
        "evidence": {
            "detected_any_10de": val("detected_any_10de"),
            "detected_any_2f04": val("detected_any_2f04"),
            "detected_any_2f0410de": val("detected_any_2f0410de"),
        },
    },
    {
        "id": "provider_open_safety",
        "status": "PASS" if val("provider_open_attempted") is False else "FAIL",
        "evidence": {"provider_open_attempted": val("provider_open_attempted")},
    },
    {
        "id": "ioserviceopen_safety",
        "status": "PASS" if val("ioserviceopen_attempted") is False else "FAIL",
        "evidence": {"ioserviceopen_attempted": val("ioserviceopen_attempted")},
    },
    {
        "id": "bar_mapping_safety",
        "status": "PASS" if val("bar_mapping_attempted") is False else "FAIL",
        "evidence": {"bar_mapping_attempted": val("bar_mapping_attempted")},
    },
    {
        "id": "bar0_read_write_safety",
        "status": "PASS" if (val("bar0_read_attempted") is False and val("bar0_write_attempted") is False) else "FAIL",
        "evidence": {
            "bar0_read_attempted": val("bar0_read_attempted"),
            "bar0_write_attempted": val("bar0_write_attempted"),
        },
    },
    {
        "id": "gpu_command_safety",
        "status": "PASS" if val("gpu_command_submission_attempted") is False else "FAIL",
        "evidence": {"gpu_command_submission_attempted": val("gpu_command_submission_attempted")},
    },
    {
        "id": "metal_proof_state",
        "status": "NOT_PROVEN" if val("current_rtx5070_metal_acceleration_claimed") is False else "FAIL",
        "evidence": {"current_rtx5070_metal_acceleration_claimed": val("current_rtx5070_metal_acceleration_claimed")},
    },
    {
        "id": "dock_transparency_blur_proof_state",
        "status": "NOT_PROVEN" if val("dock_transparency_blur_acceleration_claimed") is False else "FAIL",
        "evidence": {"dock_transparency_blur_acceleration_claimed": val("dock_transparency_blur_acceleration_claimed")},
    },
]

fail_count = sum(1 for item in matrix if item["status"] == "FAIL")
pass_count = sum(1 for item in matrix if item["status"] == "PASS")
blocked_count = sum(1 for item in matrix if item["status"] == "BLOCKED")
missing_count = sum(1 for item in matrix if item["status"] == "MISSING")
not_proven_count = sum(1 for item in matrix if item["status"] == "NOT_PROVEN")

decision = "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX_READY" if fail_count == 0 else "FAIL_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX"

out = {
    "schema": "h1mekartx.sanitized_provider_visibility_evidence_matrix_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX",
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "evidence_matrix_only": True,
    "input_summary_present": summary is not None,
    "input_check_present": check is not None,
    "matrix": matrix,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "missing_count": missing_count,
    "not_proven_count": not_proven_count,
    "fail_count": fail_count,
    "provider_visibility_commands_executed_by_this_phase": False,
    "raw_capture_parsed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62k-local-optin-provider-visibility-evidence-capture-runbook",
}

json_path = OUT / "sanitized-provider-visibility-evidence-matrix.json"
md_path = OUT / "sanitized-provider-visibility-evidence-matrix.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(
    f"| `{item['id']}` | `{item['status']}` | `{json.dumps(item['evidence'], sort_keys=True)}` |"
    for item in matrix
)
md_path.write_text(f"""# Sanitized Provider Visibility Evidence Matrix

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Evidence Matrix Only: `True`
- Input Summary Present: `{summary is not None}`
- Input Check Present: `{check is not None}`
- PASS Count: `{pass_count}`
- BLOCKED Count: `{blocked_count}`
- MISSING Count: `{missing_count}`
- NOT_PROVEN Count: `{not_proven_count}`
- FAIL Count: `{fail_count}`
- Provider Visibility Commands Executed By This Phase: `False`
- Raw Capture Parsed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62k-local-optin-provider-visibility-evidence-capture-runbook`

## Matrix

| Evidence ID | Status | Evidence |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Wrote JSON:", json_path)
print("Wrote Markdown:", md_path)
print("Decision:", decision)
