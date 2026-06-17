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
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/readonly-provider-visibility-command-generator.json"
doc_path = ROOT / "docs/hackintosh/readonly-provider-visibility-command-generator.md"
template_path = ROOT / "release-readiness/readonly-provider-visibility-command-template.json"
template_md_path = ROOT / "release-readiness/readonly-provider-visibility-command-template.md"

manifest = read_json(manifest_path)
template = read_json(template_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
template_md = template_md_path.read_text(encoding="utf-8", errors="replace") if template_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "template_exists", template_path.exists(), str(template_path))
add(checks, "template_md_exists", template_md_path.exists(), str(template_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.readonly_provider_visibility_command_generator.v1"), "manifest schema")
add(checks, "template_schema", bool(template and template.get("schema") == "h1mekartx.readonly_provider_visibility_command_template.v1"), "template schema")

for obj_name, obj in [("manifest", manifest), ("template", template)]:
    for field in [
        "rtx5070_target_retained",
    ]:
        add(checks, f"{obj_name}_{field}_true", bool(obj and obj.get(field) is True), field)

    for field in [
        "fallback_gpu_substitution_allowed",
        "commands_executed_by_this_phase",
        "provider_visibility_capture_attempted",
        "provider_open_attempted",
        "ioserviceopen_attempted",
        "bar_mapping_attempted",
        "bar0_read_attempted",
        "bar0_write_attempted",
        "gpu_command_submission_attempted",
        "current_rtx5070_metal_acceleration_claimed",
        "current_rtx5070_ui_smoothness_claimed",
        "dock_transparency_blur_acceleration_claimed",
    ]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62h-local-readonly-provider-visibility-capture-wrapper"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

commands = template.get("commands", []) if template else []
add(checks, "template_has_commands", len(commands) >= 4, f"count={len(commands)}")
for item in commands:
    name = item.get("name", "unknown")
    for field in ["executes_provider_open", "maps_bar", "reads_bar0", "writes_bar0", "submits_gpu_commands"]:
        add(checks, f"command_{name}_{field}_false", item.get(field) is False, field)

# Only generated command strings are scanned for forbidden executable tokens.
# The docs and JSON intentionally contain forbidden token names as safety documentation.
command_text = "\n".join(str(item.get("command", "")) for item in commands)
for forbidden in [
    "IOServiceOpen(",
    "ioreg -w",
    "nvram ",
    "kextload",
    "kmutil load",
    "setpci",
    "pciconf",
]:
    add(checks, "forbidden_absent_from_commands_" + forbidden.replace(" ", "_"), forbidden not in command_text, forbidden)

for token in [
    "This phase does not execute provider visibility commands",
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not map BAR memory",
    "This phase does not read BAR0",
    "This phase does not write BAR0",
    "This phase does not submit GPU commands",
    "This phase does not claim RTX 5070 Metal acceleration",
    "This phase does not claim Dock/transparency/blur acceleration",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_READONLY_PROVIDER_VISIBILITY_COMMAND_GENERATOR_READY" if failed == 0 else "FAIL_READONLY_PROVIDER_VISIBILITY_COMMAND_GENERATOR"

report = {
    "schema": "h1mekartx.readonly_provider_visibility_command_generator_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "command_template_only": True,
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
    "next_gate": "phase62h-local-readonly-provider-visibility-capture-wrapper",
    "checks": checks,
}
(OUT / "readonly-provider-visibility-command-generator-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "readonly-provider-visibility-command-generator-check.md").write_text(f"""# Read-Only Provider Visibility Command Generator Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Command Template Only: `True`
- Commands Executed By This Phase: `False`
- Provider Visibility Capture Attempted: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62h-local-readonly-provider-visibility-capture-wrapper`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
