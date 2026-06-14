#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_readonly_rtx5070_ui_baseline_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"Apple Development:[^\n\r]+"),
    re.compile(r"Developer ID Application:[^\n\r]+"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
        return obj if isinstance(obj, dict) else None

def has_private_text(text: str) -> bool:
    return any(p.search(str(text or "")) for p in PRIVATE_PATTERNS)

def command_summary(cmd: dict | None) -> dict:
    cmd = cmd or {}
    stdout = str(cmd.get("stdout", ""))
    stderr = str(cmd.get("stderr", ""))
    return {
        "returncode": cmd.get("returncode"),
        "stdout_present": bool(stdout),
        "stderr_present": bool(stderr),
        "raw_stdout_committed": False,
        "raw_stderr_committed": False,
        "command_body_committed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/local-readonly-rtx5070-ui-baseline/local-readonly-rtx5070-ui-baseline-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local = read_json(root / args.input)
    commands = local.get("commands", {}) if local else {}

    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_READONLY_RTX5070_UI_BASELINE",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_baseline_report_present": local is not None,
        "local_baseline_decision": local.get("decision") if local else "NO_LOCAL_BASELINE_REPORT_PRESENT",
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "display_inventory_collected": bool(local and local.get("display_inventory_collected")),
        "hardware_inventory_collected": bool(local and local.get("hardware_inventory_collected")),
        "iopcidevice_inventory_collected": bool(local and local.get("iopcidevice_inventory_collected")),
        "ioaccelerator_inventory_collected": bool(local and local.get("ioaccelerator_inventory_collected")),
        "iodisplayconnect_inventory_collected": bool(local and local.get("iodisplayconnect_inventory_collected")),
        "rtx5070_identity_token_observed": bool(local and local.get("rtx5070_identity_token_observed")),
        "vendor_10de_observed": bool(local and local.get("vendor_10de_observed")),
        "device_2f04_observed": bool(local and local.get("device_2f04_observed")),
        "iopcimatch_2f0410de_observed": bool(local and local.get("iopcimatch_2f0410de_observed")),
        "metal_string_observed_in_display_inventory": bool(local and local.get("metal_string_observed_in_display_inventory")),
        "windowserver_process_observed": bool(local and local.get("windowserver_process_observed")),
        "dock_process_observed": bool(local and local.get("dock_process_observed")),
        "windowserver_log_observed": bool(local and local.get("windowserver_log_observed")),
        "dock_log_observed": bool(local and local.get("dock_log_observed")),
        "ioaccelerator_token_count": local.get("ioaccelerator_token_count", 0) if local else 0,
        "reduce_transparency_command_returncode": local.get("reduce_transparency_command_returncode") if local else None,
        "reduce_transparency_stdout_present": bool(local and local.get("reduce_transparency_stdout_present")),
        "rtx5070_acceleration_claim_valid": False,
        "rtx5070_ui_smoothness_claim_valid": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61_allowed_now": False,
        "provider_open_allowed_now": False,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "xcodebuild_build_attempted_by_this_phase": False,
        "activation_submitted_by_this_phase": False,
        "deactivation_submitted_by_this_phase": False,
        "install_attempted": False,
        "manual_dext_load_attempted": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "sanitized_commands": {name: command_summary(cmd) for name, cmd in commands.items()},
        "next_gate": "phase60w-dock-transparency-blur-scenario-marker",
    }

    json_path = out_dir / "local-readonly-rtx5070-ui-baseline-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    keys = [
        "local_baseline_report_present",
        "local_baseline_decision",
        "rtx5070_target_retained",
        "fallback_gpu_substitution_allowed",
        "display_inventory_collected",
        "iopcidevice_inventory_collected",
        "rtx5070_identity_token_observed",
        "vendor_10de_observed",
        "device_2f04_observed",
        "iopcimatch_2f0410de_observed",
        "metal_string_observed_in_display_inventory",
        "windowserver_process_observed",
        "dock_process_observed",
        "rtx5070_acceleration_claim_valid",
        "rtx5070_ui_smoothness_claim_valid",
        "phase61_allowed_now",
        "next_gate",
    ]
    rows = "\n".join(f"| `{k}` | `{summary.get(k)}` |" for k in keys)

    md = f"""# Local Read-Only RTX 5070 UI Baseline Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- RTX 5070 Acceleration Claim Valid: `False`
- RTX 5070 UI Smoothness Claim Valid: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60w-dock-transparency-blur-scenario-marker`

## Baseline

| Key | Value |
| --- | --- |
{rows}
"""
    (out_dir / "local-readonly-rtx5070-ui-baseline-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'local-readonly-rtx5070-ui-baseline-summary.md'}")
    print("Decision: PASS_LOCAL_READONLY_RTX5070_UI_BASELINE_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
