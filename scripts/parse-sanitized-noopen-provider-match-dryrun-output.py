#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

RAW_PATH = ROOT / "host-report-bundle/noopen-provider-match-dryrun/noopen-provider-match-dryrun-local-capture.json"
OPTIN_ENV = "H1MEKARTX_PARSE_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT"
OPTIN_VALUE = "I_UNDERSTAND_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_PARSE_ONLY"

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))

def scrub(text: str) -> str:
    text = text or ""
    text = re.sub(r"/Users/[^\\s\"'`]+", "/Users/REDACTED", text)
    text = re.sub(r"/private/var/folders/[^\\s\"'`]+", "/private/var/folders/REDACTED", text)
    text = re.sub(r"/var/folders/[^\\s\"'`]+", "/var/folders/REDACTED", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "REDACTED_EMAIL", text)
    return text

def command_summary(item: dict) -> dict:
    stdout = scrub(str(item.get("stdout_tail", "")))
    stderr = scrub(str(item.get("stderr_tail", "")))
    combined = (stdout + "\n" + stderr).lower()
    return {
        "id": item.get("id"),
        "returncode": item.get("returncode"),
        "mentions_h1mekartx": "h1mekartx" in combined,
        "mentions_driverkit": "driverkit" in combined,
        "mentions_pcidriverkit": "pcidriverkit" in combined,
        "mentions_iopcidevice": "iopcidevice" in combined,
        "mentions_10de": "10de" in combined,
        "mentions_2f04": "2f04" in combined,
        "mentions_2f0410de": "2f0410de" in combined,
        "provider_open": False,
        "ioserviceopen": False,
        "bar_mapping": False,
        "bar0_read": False,
        "bar0_write": False,
        "gpu_command_submission": False,
        "raw_stdout_committed": False,
        "raw_stderr_committed": False
    }

hard_opt_in = os.environ.get(OPTIN_ENV) == OPTIN_VALUE
raw_exists = RAW_PATH.exists()
raw = read_json(RAW_PATH) if hard_opt_in and raw_exists else None

summary = {
    "schema": "h1mekartx.sanitized_noopen_provider_match_dryrun_output_parser_summary.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT_PARSER_SUMMARY",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "hard_opt_in_required": True,
    "hard_opt_in_matched": hard_opt_in,
    "raw_capture_exists_local": raw_exists,
    "raw_capture_read": raw is not None,
    "raw_stdout_committed": False,
    "raw_stderr_committed": False,
    "private_paths_committed": False,
    "provider_visibility_commands_executed_by_this_phase": False,
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
    "raw_decision": None,
    "raw_commands_executed": None,
    "command_count": 0,
    "commands": [],
    "detected_any_h1mekartx": False,
    "detected_any_driverkit": False,
    "detected_any_iopcidevice": False,
    "detected_any_10de": False,
    "detected_any_2f04": False,
    "detected_any_2f0410de": False,
    "next_gate": "phase62r-noopen-provider-match-dryrun-evidence-matrix"
}

if not hard_opt_in:
    summary["decision"] = "REFUSED_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_PARSE_MISSING_HARD_OPTIN"
elif raw is None:
    summary["decision"] = "NO_LOCAL_NOOPEN_PROVIDER_MATCH_DRYRUN_CAPTURE_PRESENT"
else:
    cmds = raw.get("commands", []) if isinstance(raw, dict) else []
    parsed = [command_summary(c) for c in cmds if isinstance(c, dict)]
    summary.update({
        "decision": "PASS_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT_PARSED",
        "raw_decision": raw.get("decision"),
        "raw_commands_executed": raw.get("commands_executed"),
        "command_count": len(parsed),
        "commands": parsed,
        "detected_any_h1mekartx": any(c["mentions_h1mekartx"] for c in parsed),
        "detected_any_driverkit": any(c["mentions_driverkit"] for c in parsed),
        "detected_any_iopcidevice": any(c["mentions_iopcidevice"] for c in parsed),
        "detected_any_10de": any(c["mentions_10de"] for c in parsed),
        "detected_any_2f04": any(c["mentions_2f04"] for c in parsed),
        "detected_any_2f0410de": any(c["mentions_2f0410de"] for c in parsed)
    })

json_path = OUT / "sanitized-noopen-provider-match-dryrun-output-parser-summary.json"
md_path = OUT / "sanitized-noopen-provider-match-dryrun-output-parser-summary.md"
json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

cmd_lines = "\n".join(
    f"- `{c.get('id')}` rc=`{c.get('returncode')}` h1mekartx=`{c.get('mentions_h1mekartx')}` driverkit=`{c.get('mentions_driverkit')}` iopcidevice=`{c.get('mentions_iopcidevice')}` 10de=`{c.get('mentions_10de')}` 2f04=`{c.get('mentions_2f04')}`"
    for c in summary.get("commands", [])
) or "- none"

md_path.write_text(f"""# Sanitized No-Open Provider Match Dry-Run Output Parser Summary

- Decision: `{summary['decision']}`
- Hard Opt-In Required: `True`
- Hard Opt-In Matched: `{summary['hard_opt_in_matched']}`
- Raw Capture Exists Local: `{summary['raw_capture_exists_local']}`
- Raw Capture Read: `{summary['raw_capture_read']}`
- Raw stdout Committed: `False`
- Raw stderr Committed: `False`
- Private Paths Committed: `False`
- Provider Visibility Commands Executed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Expected Vendor ID: `0x10de`
- Expected Device ID: `0x2f04`
- Expected IOPCIMatch: `0x2f0410de`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`
- Raw Decision: `{summary['raw_decision']}`
- Raw Commands Executed: `{summary['raw_commands_executed']}`
- Command Count: `{summary['command_count']}`
- Detected Any H1mekaRTX: `{summary['detected_any_h1mekartx']}`
- Detected Any DriverKit: `{summary['detected_any_driverkit']}`
- Detected Any IOPCIDevice: `{summary['detected_any_iopcidevice']}`
- Detected Any 10de: `{summary['detected_any_10de']}`
- Detected Any 2f04: `{summary['detected_any_2f04']}`
- Detected Any 2f0410de: `{summary['detected_any_2f0410de']}`
- Next Gate: `{summary['next_gate']}`

## Sanitized Commands

{cmd_lines}
""", encoding="utf-8")

print("Decision:", summary["decision"])
