#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

summary_path = ROOT / "release-readiness/local-provider-match-dryrun-observer-summary.json"
summary = None
if summary_path.exists():
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

ready_for_provider_match = bool(summary and summary.get("ready_for_provider_match") is True)
missing_ready_fields = summary.get("missing_ready_fields", []) if summary else []

commands = [
    {
        "name": "ioreg_search_rtx5070_pci_identity",
        "command": "ioreg -l -p IOService | grep -Ei '10de|2f04|0x2f0410de|H1mekaRTX|IOPCIDevice' | head -200",
        "executes_provider_open": False,
        "maps_bar": False,
        "reads_bar0": False,
        "writes_bar0": False,
        "submits_gpu_commands": False,
    },
    {
        "name": "ioreg_full_provider_visibility_readonly",
        "command": "ioreg -l -p IOService -r -n H1mekaRTXDriver 2>/dev/null || true",
        "executes_provider_open": False,
        "maps_bar": False,
        "reads_bar0": False,
        "writes_bar0": False,
        "submits_gpu_commands": False,
    },
    {
        "name": "systemextensions_list_readonly",
        "command": "systemextensionsctl list | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true",
        "executes_provider_open": False,
        "maps_bar": False,
        "reads_bar0": False,
        "writes_bar0": False,
        "submits_gpu_commands": False,
    },
    {
        "name": "kmutil_loaded_readonly",
        "command": "kmutil showloaded | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true",
        "executes_provider_open": False,
        "maps_bar": False,
        "reads_bar0": False,
        "writes_bar0": False,
        "submits_gpu_commands": False,
    },
    {
        "name": "driverkit_log_readonly_recent",
        "command": "log show --last 30m --style compact --predicate 'eventMessage CONTAINS[c] \"H1mekaRTX\" OR eventMessage CONTAINS[c] \"DriverKit\" OR eventMessage CONTAINS[c] \"PCIDriverKit\"' | tail -300",
        "executes_provider_open": False,
        "maps_bar": False,
        "reads_bar0": False,
        "writes_bar0": False,
        "submits_gpu_commands": False,
    },
]

forbidden_tokens = [
    "IOServiceOpen",
    "ioreg -w",
    "nvram",
    "kextload",
    "kmutil load",
    "dd ",
    "pciconf",
    "setpci",
    "ioreg -c IOPCIDevice -w",
]

template = {
    "schema": "h1mekartx.readonly_provider_visibility_command_template.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_READONLY_PROVIDER_VISIBILITY_COMMAND_TEMPLATE",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "ready_for_provider_match": ready_for_provider_match,
    "missing_ready_field_count": len(missing_ready_fields),
    "missing_ready_fields": missing_ready_fields,
    "commands_executed_by_this_phase": False,
    "provider_visibility_capture_attempted": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "commands": commands,
    "forbidden_tokens": forbidden_tokens,
    "next_gate": "phase62h-local-readonly-provider-visibility-capture-wrapper",
}

json_path = OUT / "readonly-provider-visibility-command-template.json"
md_path = OUT / "readonly-provider-visibility-command-template.md"

json_path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")

lines = [
    "# Read-Only Provider Visibility Command Template",
    "",
    f"- Generated At UTC: `{template['generated_at_utc']}`",
    "- RTX 5070 Target Retained: `True`",
    "- Fallback GPU Substitution Allowed: `False`",
    f"- Ready For Provider Match: `{ready_for_provider_match}`",
    f"- Missing Ready Field Count: `{len(missing_ready_fields)}`",
    "- Commands Executed By This Phase: `False`",
    "- Provider Open Attempted: `False`",
    "- IOServiceOpen Attempted: `False`",
    "- BAR Mapping Attempted: `False`",
    "- BAR0 Read Attempted: `False`",
    "- BAR0 Write Attempted: `False`",
    "- GPU Command Submission Attempted: `False`",
    "- Current RTX 5070 Metal Acceleration Claimed: `False`",
    "- Current RTX 5070 UI Smoothness Claimed: `False`",
    "- Dock/Transparency/Blur Acceleration Claimed: `False`",
    f"- Next Gate: `{template['next_gate']}`",
    "",
    "## Commands",
    "",
]
for item in commands:
    lines.append(f"### {item['name']}")
    lines.append("")
    lines.append("```bash")
    lines.append(item["command"])
    lines.append("```")
    lines.append("")

lines.extend([
    "## Forbidden Tokens",
    "",
    *[f"- `{x}`" for x in forbidden_tokens],
    "",
    "## Missing Ready Fields",
    "",
    *([f"- `{x}`" for x in missing_ready_fields] if missing_ready_fields else ["- none"]),
    "",
])

md_path.write_text("\n".join(lines), encoding="utf-8")

print("Wrote JSON:", json_path)
print("Wrote Markdown:", md_path)
print("Decision: PASS_READONLY_PROVIDER_VISIBILITY_COMMAND_TEMPLATE_WRITTEN")
