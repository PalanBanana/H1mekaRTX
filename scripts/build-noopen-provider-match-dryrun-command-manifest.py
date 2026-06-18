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

preflight = read_json("release-readiness/provider-match-preflight-checklist-from-reconciled-evidence.json")
preflight_check = read_json("release-readiness/provider-match-preflight-checklist-from-reconciled-evidence-check.json")

preflight_pass = bool(preflight and preflight.get("decision") == "PASS_PROVIDER_MATCH_PREFLIGHT_CHECKLIST_FROM_RECONCILED_EVIDENCE_READY")
preflight_check_pass = bool(preflight_check and preflight_check.get("decision") == "PASS_PROVIDER_MATCH_PREFLIGHT_CHECKLIST_FROM_RECONCILED_EVIDENCE_READY")
planning_preflight_ready = bool(preflight and preflight.get("provider_match_planning_preflight_ready") is True)

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

inputs_safe = safe(preflight) and safe(preflight_check)
manifest_ready = preflight_pass and preflight_check_pass and planning_preflight_ready and inputs_safe

commands = [
    {
        "id": "readonly_ioreg_provider_identity_probe",
        "description": "Read-only IORegistry search for RTX 5070 identity and H1mekaRTX naming.",
        "template": "ioreg -l -p IOService | grep -Ei '10de|2f04|0x2f0410de|H1mekaRTX|IOPCIDevice' | head -200",
        "provider_open": False,
        "ioserviceopen": False,
        "bar_mapping": False,
        "bar0_read": False,
        "bar0_write": False,
        "gpu_command_submission": False
    },
    {
        "id": "readonly_systemextensions_list_probe",
        "description": "Read-only System Extension list filtering for H1mekaRTX and DriverKit names.",
        "template": "systemextensionsctl list | grep -Ei 'H1mekaRTX|DriverKit|dev.h1meka' || true",
        "provider_open": False,
        "ioserviceopen": False,
        "bar_mapping": False,
        "bar0_read": False,
        "bar0_write": False,
        "gpu_command_submission": False
    },
    {
        "id": "readonly_driverkit_recent_log_probe",
        "description": "Read-only recent log filtering for DriverKit and H1mekaRTX messages.",
        "template": "log show --last 30m --style compact --predicate 'eventMessage CONTAINS[c] \"H1mekaRTX\" OR eventMessage CONTAINS[c] \"DriverKit\" OR eventMessage CONTAINS[c] \"PCIDriverKit\"' | tail -300",
        "provider_open": False,
        "ioserviceopen": False,
        "bar_mapping": False,
        "bar0_read": False,
        "bar0_write": False,
        "gpu_command_submission": False
    },
    {
        "id": "local_sanitized_summary_probe",
        "description": "Local inspection of previously generated sanitized provider visibility summaries.",
        "template": "python3 - <<'PY2'\nimport json\nfrom pathlib import Path\nfor p in ['release-readiness/provider-match-preflight-checklist-from-reconciled-evidence.json','release-readiness/provider-match-readiness-reconciliation-from-visibility-evidence.json']:\n    d=json.loads(Path(p).read_text())\n    print(p, d.get('decision'))\nPY2",
        "provider_open": False,
        "ioserviceopen": False,
        "bar_mapping": False,
        "bar0_read": False,
        "bar0_write": False,
        "gpu_command_submission": False
    }
]

out = {
    "schema": "h1mekartx.noopen_provider_match_dryrun_command_manifest_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_NOOPEN_PROVIDER_MATCH_DRYRUN_COMMAND_MANIFEST_OUTPUT",
    "decision": "PASS_NOOPEN_PROVIDER_MATCH_DRYRUN_COMMAND_MANIFEST_READY" if manifest_ready else "FAIL_NOOPEN_PROVIDER_MATCH_DRYRUN_COMMAND_MANIFEST",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "command_manifest_only": True,
    "input_preflight_present": preflight is not None,
    "input_preflight_check_present": preflight_check is not None,
    "input_preflight_pass": preflight_pass,
    "input_preflight_check_pass": preflight_check_pass,
    "provider_match_planning_preflight_ready": planning_preflight_ready,
    "inputs_safe": inputs_safe,
    "provider_match_command_manifest_ready": manifest_ready,
    "commands_executed_by_this_phase": False,
    "commands": commands,
    "provider_open_promoted": False,
    "bar_access_promoted": False,
    "gpu_command_submission_promoted": False,
    "metal_acceleration_promoted": False,
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
    "next_gate": "phase62p-noopen-provider-match-dryrun-hardoptin-wrapper",
}

json_path = OUT / "noopen-provider-match-dryrun-command-manifest.json"
md_path = OUT / "noopen-provider-match-dryrun-command-manifest.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(
    f"| `{c['id']}` | provider_open=`{c['provider_open']}` | bar_mapping=`{c['bar_mapping']}` | gpu_cmd=`{c['gpu_command_submission']}` |"
    for c in commands
)
md_path.write_text(f"""# No-Open Provider Match Dry-Run Command Manifest

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Command Manifest Only: `True`
- Input Preflight Present: `{out['input_preflight_present']}`
- Input Preflight Check Present: `{out['input_preflight_check_present']}`
- Input Preflight PASS: `{out['input_preflight_pass']}`
- Input Preflight Check PASS: `{out['input_preflight_check_pass']}`
- Provider Match Planning Preflight Ready: `{out['provider_match_planning_preflight_ready']}`
- Inputs Safe: `{out['inputs_safe']}`
- Provider Match Command Manifest Ready: `{out['provider_match_command_manifest_ready']}`
- Commands Executed By This Phase: `False`
- Provider Open Promoted: `False`
- BAR Access Promoted: `False`
- GPU Command Submission Promoted: `False`
- Metal Acceleration Promoted: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Command Manifest

| Command ID | Provider Open | BAR Mapping | GPU Command |
| --- | --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
