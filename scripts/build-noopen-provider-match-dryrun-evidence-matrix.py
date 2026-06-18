#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8", errors="replace")) if p.exists() else None

summary = read_json("release-readiness/sanitized-noopen-provider-match-dryrun-output-parser-summary.json")
parser_check = read_json("release-readiness/sanitized-noopen-provider-match-dryrun-output-parser-check.json")
cmd_manifest = read_json("release-readiness/noopen-provider-match-dryrun-command-manifest.json")
wrapper_check = read_json("release-readiness/noopen-provider-match-dryrun-hardoptin-wrapper-check.json")

parser_ok = bool(parser_check and parser_check.get("decision") == "PASS_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT_PARSER_READY")
manifest_ok = bool(cmd_manifest and cmd_manifest.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_COMMAND_MANIFEST_READY")
wrapper_ok = bool(wrapper_check and wrapper_check.get("decision") == "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_HARDOPTIN_WRAPPER_READY")
default_refused = bool(summary and summary.get("decision") == "REFUSED_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_PARSE_MISSING_HARD_OPTIN")

danger = [
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
    return isinstance(obj, dict) and all(obj.get(k) is False for k in danger if k in obj)

inputs_safe = safe(summary) and safe(parser_check) and safe(cmd_manifest) and safe(wrapper_check)

matrix = [
    {"id": "parser_check_passed", "status": "PASS" if parser_ok else "FAIL"},
    {"id": "command_manifest_passed", "status": "PASS" if manifest_ok else "FAIL"},
    {"id": "hardoptin_wrapper_check_passed", "status": "PASS" if wrapper_ok else "FAIL"},
    {"id": "default_parse_refusal", "status": "BLOCKED" if default_refused else "FAIL"},
    {"id": "raw_capture_read_state", "status": "BLOCKED" if summary and summary.get("raw_capture_read") is False else "PASS"},
    {"id": "h1mekartx_token", "status": "PASS" if summary and summary.get("detected_any_h1mekartx") else "NOT_PROVEN"},
    {"id": "iopcidevice_token", "status": "PASS" if summary and summary.get("detected_any_iopcidevice") else "NOT_PROVEN"},
    {"id": "pci_identity_tokens", "status": "PASS" if summary and summary.get("detected_any_10de") and summary.get("detected_any_2f04") else "NOT_PROVEN"},
    {"id": "provider_open_safety", "status": "PASS" if summary and summary.get("provider_open_attempted") is False else "FAIL"},
    {"id": "ioserviceopen_safety", "status": "PASS" if summary and summary.get("ioserviceopen_attempted") is False else "FAIL"},
    {"id": "bar_mapping_safety", "status": "PASS" if summary and summary.get("bar_mapping_attempted") is False else "FAIL"},
    {"id": "bar0_read_write_safety", "status": "PASS" if summary and summary.get("bar0_read_attempted") is False and summary.get("bar0_write_attempted") is False else "FAIL"},
    {"id": "gpu_command_safety", "status": "PASS" if summary and summary.get("gpu_command_submission_attempted") is False else "FAIL"},
    {"id": "metal_not_proven", "status": "NOT_PROVEN" if summary and summary.get("current_rtx5070_metal_acceleration_claimed") is False else "FAIL"},
    {"id": "dock_blur_not_proven", "status": "NOT_PROVEN" if summary and summary.get("dock_transparency_blur_acceleration_claimed") is False else "FAIL"}
]

fail_count = sum(1 for x in matrix if x["status"] == "FAIL")
pass_count = sum(1 for x in matrix if x["status"] == "PASS")
blocked_count = sum(1 for x in matrix if x["status"] == "BLOCKED")
not_proven_count = sum(1 for x in matrix if x["status"] == "NOT_PROVEN")
ready = fail_count == 0 and parser_ok and manifest_ok and wrapper_ok and inputs_safe

out = {
    "schema": "h1mekartx.noopen_provider_match_dryrun_evidence_matrix_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_MATRIX_OUTPUT",
    "decision": "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_MATRIX_READY" if ready else "FAIL_NOOPEN_PROVIDER_MATCH_DRYRUN_EVIDENCE_MATRIX",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "evidence_matrix_only": True,
    "input_parser_summary_present": summary is not None,
    "input_parser_check_present": parser_check is not None,
    "input_command_manifest_present": cmd_manifest is not None,
    "input_wrapper_check_present": wrapper_check is not None,
    "input_parser_check_pass": parser_ok,
    "input_command_manifest_pass": manifest_ok,
    "input_wrapper_check_pass": wrapper_ok,
    "inputs_safe": inputs_safe,
    "matrix": matrix,
    "pass_count": pass_count,
    "blocked_count": blocked_count,
    "not_proven_count": not_proven_count,
    "fail_count": fail_count,
    "noopen_dryrun_evidence_matrix_ready": ready,
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
    "next_gate": "phase62s-noopen-provider-match-dryrun-evidence-promotion-gate"
}

json_path = OUT / "noopen-provider-match-dryrun-evidence-matrix.json"
md_path = OUT / "noopen-provider-match-dryrun-evidence-matrix.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
rows = "\n".join(f"| `{x['id']}` | `{x['status']}` |" for x in matrix)
md_path.write_text(f"""# No-Open Provider Match Dry-Run Evidence Matrix

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Evidence Matrix Only: `True`
- Input Parser Check PASS: `{out['input_parser_check_pass']}`
- Input Command Manifest PASS: `{out['input_command_manifest_pass']}`
- Input Wrapper Check PASS: `{out['input_wrapper_check_pass']}`
- Inputs Safe: `{out['inputs_safe']}`
- PASS Count: `{out['pass_count']}`
- BLOCKED Count: `{out['blocked_count']}`
- NOT_PROVEN Count: `{out['not_proven_count']}`
- FAIL Count: `{out['fail_count']}`
- No-Open Dry-Run Evidence Matrix Ready: `{out['noopen_dryrun_evidence_matrix_ready']}`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Matrix

| Item | Status |
| --- | --- |
{rows}
""", encoding="utf-8")
print("Decision:", out["decision"])
