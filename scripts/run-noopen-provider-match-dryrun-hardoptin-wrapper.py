#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
RAW = ROOT / "host-report-bundle/noopen-provider-match-dryrun"
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

OPTIN_ENV = "H1MEKARTX_ALLOW_NOOPEN_PROVIDER_MATCH_DRYRUN"
OPTIN_VALUE = "I_UNDERSTAND_NOOPEN_PROVIDER_MATCH_DRYRUN_ONLY"
MANIFEST_PATH = ROOT / "release-readiness/noopen-provider-match-dryrun-command-manifest.json"

def scrub(text: str) -> str:
    text = text or ""
    text = re.sub(r"/Users/[^\\s\"'`]+", "/Users/REDACTED", text)
    text = re.sub(r"/private/var/folders/[^\\s\"'`]+", "/private/var/folders/REDACTED", text)
    text = re.sub(r"/var/folders/[^\\s\"'`]+", "/var/folders/REDACTED", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "REDACTED_EMAIL", text)
    return text[-12000:]

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))

def run_template(item: dict) -> dict:
    command = str(item.get("template", ""))
    result = {
        "id": item.get("id"),
        "provider_open": False,
        "ioserviceopen": False,
        "bar_mapping": False,
        "bar0_read": False,
        "bar0_write": False,
        "gpu_command_submission": False,
        "returncode": None,
        "stdout_tail": "",
        "stderr_tail": "",
    }
    r = subprocess.run(["/bin/bash", "-lc", command], capture_output=True, text=True, timeout=30)
    result["returncode"] = r.returncode
    result["stdout_tail"] = scrub(r.stdout)
    result["stderr_tail"] = scrub(r.stderr)
    return result

hard_opt_in = os.environ.get(OPTIN_ENV) == OPTIN_VALUE
manifest = read_json(MANIFEST_PATH)
commands = manifest.get("commands", []) if isinstance(manifest, dict) else []

capture = {
    "schema": "h1mekartx.noopen_provider_match_dryrun_hardoptin_capture.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_NOOPEN_PROVIDER_MATCH_DRYRUN_HARDOPTIN_CAPTURE",
    "hard_opt_in_required": True,
    "hard_opt_in_env": OPTIN_ENV,
    "hard_opt_in_matched": hard_opt_in,
    "command_manifest_present": manifest is not None,
    "command_count": len(commands),
    "commands_executed": False,
    "commands": [],
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
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
    "next_gate": "phase62q-sanitized-noopen-provider-match-dryrun-output-parser",
}

if not hard_opt_in:
    capture["decision"] = "REFUSED_NOOPEN_PROVIDER_MATCH_DRYRUN_MISSING_HARD_OPTIN"
elif manifest is None:
    capture["decision"] = "FAIL_NOOPEN_PROVIDER_MATCH_DRYRUN_MISSING_MANIFEST"
else:
    capture["commands"] = [run_template(item) for item in commands]
    capture["commands_executed"] = True
    capture["decision"] = "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_CAPTURE_WRITTEN"

raw_json = RAW / "noopen-provider-match-dryrun-local-capture.json"
raw_md = RAW / "noopen-provider-match-dryrun-local-capture.md"
raw_json.write_text(json.dumps(capture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
raw_md.write_text(
    "# No-Open Provider Match Dry-Run Local Capture\n\n"
    f"- Decision: `{capture['decision']}`\n"
    f"- Hard Opt-In Matched: `{capture['hard_opt_in_matched']}`\n"
    f"- Commands Executed: `{capture['commands_executed']}`\n"
    "- Provider Open Attempted: `False`\n"
    "- IOServiceOpen Attempted: `False`\n"
    "- BAR Mapping Attempted: `False`\n"
    "- BAR0 Read Attempted: `False`\n"
    "- BAR0 Write Attempted: `False`\n"
    "- GPU Command Submission Attempted: `False`\n"
    "- Current RTX 5070 Metal Acceleration Claimed: `False`\n"
    "- Dock/Transparency/Blur Acceleration Claimed: `False`\n",
    encoding="utf-8",
)

summary = {
    "schema": "h1mekartx.noopen_provider_match_dryrun_hardoptin_wrapper_summary.v1",
    "generated_at_utc": capture["generated_at_utc"],
    "decision": capture["decision"],
    "hard_opt_in_matched": capture["hard_opt_in_matched"],
    "command_manifest_present": capture["command_manifest_present"],
    "command_count": capture["command_count"],
    "commands_executed": capture["commands_executed"],
    "raw_capture_written_local_only": True,
    "raw_capture_path_redacted": "host-report-bundle/noopen-provider-match-dryrun/noopen-provider-match-dryrun-local-capture.json",
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62q-sanitized-noopen-provider-match-dryrun-output-parser",
}
(OUT / "noopen-provider-match-dryrun-hardoptin-wrapper-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
(OUT / "noopen-provider-match-dryrun-hardoptin-wrapper-summary.md").write_text(
    "# No-Open Provider Match Dry-Run Hard-Opt-In Wrapper Summary\n\n"
    f"- Decision: `{summary['decision']}`\n"
    f"- Hard Opt-In Matched: `{summary['hard_opt_in_matched']}`\n"
    f"- Commands Executed: `{summary['commands_executed']}`\n"
    f"- Command Count: `{summary['command_count']}`\n"
    "- Provider Open Attempted: `False`\n"
    "- IOServiceOpen Attempted: `False`\n"
    "- BAR Mapping Attempted: `False`\n"
    "- BAR0 Read Attempted: `False`\n"
    "- BAR0 Write Attempted: `False`\n"
    "- GPU Command Submission Attempted: `False`\n"
    "- Current RTX 5070 Metal Acceleration Claimed: `False`\n"
    "- Dock/Transparency/Blur Acceleration Claimed: `False`\n"
    f"- Raw Capture Path: `{summary['raw_capture_path_redacted']}`\n"
    f"- Next Gate: `{summary['next_gate']}`\n",
    encoding="utf-8",
)

print("Decision:", capture["decision"])
