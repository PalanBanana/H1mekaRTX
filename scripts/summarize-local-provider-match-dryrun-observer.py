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

manifest = read_json(ROOT / "tools/hackintosh/local-provider-match-dryrun-observer-summary.json") or {}
contract = read_json(ROOT / "release-readiness/provider-match-dryrun-observer-contract-summary.json")
readiness = read_json(ROOT / "release-readiness/provider-match-readiness-gate-summary.json")
entitlement = read_json(ROOT / "release-readiness/local-entitlement-request-status-summary.json")

ready_for_provider_match = bool(readiness and readiness.get("ready_for_provider_match") is True)
missing_ready_fields = readiness.get("missing_ready_fields", []) if readiness else []

summary = {
    "schema": "h1mekartx.local_provider_match_dryrun_observer_summary_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_LOCAL_PROVIDER_MATCH_DRYRUN_OBSERVER_SUMMARY",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_subsystem_vendor_id": "0x1458",
    "expected_subsystem_id": "0x417e",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "dryrun_observer_contract_summary_present": contract is not None,
    "provider_match_readiness_summary_present": readiness is not None,
    "entitlement_summary_present": entitlement is not None,
    "ready_for_provider_match": ready_for_provider_match,
    "missing_ready_field_count": len(missing_ready_fields),
    "missing_ready_fields": missing_ready_fields,
    "provider_match_observation_allowed_by_this_phase": False,
    "provider_match_observed_by_this_phase": False,
    "provider_open_allowed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_allowed_by_this_phase": False,
    "bar_mapping_attempted": False,
    "bar0_read_allowed_by_this_phase": False,
    "bar0_read_attempted": False,
    "bar0_write_allowed_by_this_phase": False,
    "bar0_write_attempted": False,
    "bar_mmio_mutation_attempted": False,
    "configuration_writes_attempted": False,
    "firmware_load_attempted": False,
    "gpu_reset_attempted": False,
    "gpu_command_submission_allowed_by_this_phase": False,
    "gpu_command_submission_attempted": False,
    "framebuffer_init_attempted": False,
    "display_engine_init_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62g-readonly-provider-visibility-command-generator",
}

out_json = OUT / "local-provider-match-dryrun-observer-summary.json"
out_md = OUT / "local-provider-match-dryrun-observer-summary.md"
out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

missing = "\n".join(f"- `{x}`" for x in missing_ready_fields) or "- none"
out_md.write_text(f"""# Local Provider Match Dry-Run Observer Summary

- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Expected Vendor ID: `0x10de`
- Expected Device ID: `0x2f04`
- Expected IOPCIMatch: `0x2f0410de`
- Expected DriverKit Bundle ID: `dev.h1meka.H1mekaRTXDriver`
- Dry-Run Observer Contract Summary Present: `{contract is not None}`
- Provider Match Readiness Summary Present: `{readiness is not None}`
- Entitlement Summary Present: `{entitlement is not None}`
- Ready For Provider Match: `{ready_for_provider_match}`
- Missing Ready Field Count: `{len(missing_ready_fields)}`
- Provider Match Observation Allowed By This Phase: `False`
- Provider Match Observed By This Phase: `False`
- Provider Open Allowed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Allowed By This Phase: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Allowed By This Phase: `False`
- BAR0 Write Allowed By This Phase: `False`
- GPU Command Submission Allowed By This Phase: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62g-readonly-provider-visibility-command-generator`

## Missing Ready Fields

{missing}
""", encoding="utf-8")

print("Wrote JSON:", out_json)
print("Wrote Markdown:", out_md)
print("Decision: PASS_LOCAL_PROVIDER_MATCH_DRYRUN_OBSERVER_SUMMARY_WRITTEN")
