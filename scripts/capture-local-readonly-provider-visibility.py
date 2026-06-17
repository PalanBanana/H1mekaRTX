#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "host-report-bundle" / "readonly-provider-visibility"
OUT = ROOT / "release-readiness"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

OPTIN_ENV = "H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY"
OPTIN_VALUE = "I_UNDERSTAND_READONLY_PROVIDER_VISIBILITY_ONLY"

def sanitize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"/Users/[^\\s\"'`]+", "/Users/REDACTED", text)
    text = re.sub(r"/private/var/folders/[^\\s\"'`]+", "/private/var/folders/REDACTED", text)
    text = re.sub(r"/var/folders/[^\\s\"'`]+", "/var/folders/REDACTED", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "REDACTED_EMAIL", text)
    return text[-12000:]

def run_cmd(name: str, cmd: list[str]) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "name": name,
            "command": cmd,
            "returncode": r.returncode,
            "stdout_tail": sanitize_text(r.stdout),
            "stderr_tail": sanitize_text(r.stderr),
        }
    except Exception as e:
        return {
            "name": name,
            "command": cmd,
            "returncode": None,
            "error": repr(e),
            "stdout_tail": "",
            "stderr_tail": "",
        }

base = {
    "schema": "h1mekartx.local_readonly_provider_visibility_capture.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_LOCAL_READONLY_PROVIDER_VISIBILITY_CAPTURE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "hard_opt_in_required": True,
    "hard_opt_in_env": OPTIN_ENV,
    "hard_opt_in_matched": os.environ.get(OPTIN_ENV) == OPTIN_VALUE,
    "commands_executed": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "bar_mmio_mutation_attempted": False,
    "configuration_writes_attempted": False,
    "gpu_command_submission_attempted": False,
    "framebuffer_init_attempted": False,
    "display_engine_init_attempted": False,
    "metal_proof_claimed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "commands": [],
}

if os.environ.get(OPTIN_ENV) != OPTIN_VALUE:
    base["decision"] = "REFUSED_READONLY_PROVIDER_VISIBILITY_CAPTURE_MISSING_HARD_OPTIN"
    base["refusal_reason"] = f"Set {OPTIN_ENV}={OPTIN_VALUE} to run read-only local capture."
else:
    cmds = [
        ("ioreg_rtx5070_identity_grep", ["/bin/bash", "-lc", "ioreg -l -p IOService | grep -Ei '10de|2f04|0x2f0410de|H1mekaRTX|IOPCIDevice' | head -200"]),
        ("ioreg_h1mekartx_provider", ["/bin/bash", "-lc", "ioreg -l -p IOService -r -n H1mekaRTXDriver 2>/dev/null || true"]),
        ("systemextensions_list", ["/bin/bash", "-lc", "systemextensionsctl list | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true"]),
        ("kmutil_showloaded", ["/bin/bash", "-lc", "kmutil showloaded | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true"]),
        ("driverkit_recent_log", ["/bin/bash", "-lc", "log show --last 30m --style compact --predicate 'eventMessage CONTAINS[c] \"H1mekaRTX\" OR eventMessage CONTAINS[c] \"DriverKit\" OR eventMessage CONTAINS[c] \"PCIDriverKit\"' | tail -300"]),
    ]
    base["commands"] = [run_cmd(name, cmd) for name, cmd in cmds]
    base["commands_executed"] = True
    base["decision"] = "PASS_READONLY_PROVIDER_VISIBILITY_CAPTURE_WRITTEN"

raw_json = RAW / "readonly-provider-visibility-local-capture.json"
raw_md = RAW / "readonly-provider-visibility-local-capture.md"
raw_json.write_text(json.dumps(base, indent=2, sort_keys=True) + "\n", encoding="utf-8")

raw_md.write_text(
    "# Local Read-Only Provider Visibility Capture\n\n"
    f"- Decision: `{base.get('decision')}`\n"
    f"- Hard Opt-In Matched: `{base.get('hard_opt_in_matched')}`\n"
    f"- Commands Executed: `{base.get('commands_executed')}`\n"
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
    "schema": "h1mekartx.local_readonly_provider_visibility_capture_summary.v1",
    "generated_at_utc": base["generated_at_utc"],
    "classification": "CLASSIFICATION_LOCAL_READONLY_PROVIDER_VISIBILITY_CAPTURE_SUMMARY",
    "decision": base.get("decision"),
    "hard_opt_in_matched": base.get("hard_opt_in_matched"),
    "commands_executed": base.get("commands_executed"),
    "command_count": len(base.get("commands", [])),
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "bar_mmio_mutation_attempted": False,
    "configuration_writes_attempted": False,
    "gpu_command_submission_attempted": False,
    "metal_proof_claimed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "raw_capture_written": True,
    "raw_capture_path_redacted": "host-report-bundle/readonly-provider-visibility/readonly-provider-visibility-local-capture.json",
    "next_gate": "phase62i-sanitized-local-provider-visibility-capture-parser",
}
(OUT / "local-readonly-provider-visibility-capture-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
(OUT / "local-readonly-provider-visibility-capture-summary.md").write_text(
    "# Local Read-Only Provider Visibility Capture Summary\n\n"
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
    "- Current RTX 5070 UI Smoothness Claimed: `False`\n"
    "- Dock/Transparency/Blur Acceleration Claimed: `False`\n"
    f"- Raw Capture Path: `{summary['raw_capture_path_redacted']}`\n"
    f"- Next Gate: `{summary['next_gate']}`\n",
    encoding="utf-8",
)

print("Wrote JSON:", raw_json)
print("Wrote Markdown:", raw_md)
print("Wrote summary:", OUT / "local-readonly-provider-visibility-capture-summary.json")
print("Decision:", base.get("decision"))
