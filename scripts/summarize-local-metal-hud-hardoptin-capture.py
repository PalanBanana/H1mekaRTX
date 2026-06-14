#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_metal_hud_hardoptin_capture_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

def has_private_text(text: str) -> bool:
    return any(p.search(str(text or "")) for p in PRIVATE_PATTERNS)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/local-metal-hud-hardoptin-capture/local-metal-hud-hardoptin-capture-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = root / args.input
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    local = read_json(input_path)
    raw_text = json.dumps(local or {})

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_capture_report_present": local is not None,
        "local_capture_decision": local.get("decision") if local else "NO_LOCAL_CAPTURE_REPORT_PRESENT",
        "hard_optin_ok": bool(local and local.get("hard_optin_ok")),
        "execute_capture_requested": bool(local and local.get("execute_capture_requested")),
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "target_app_sanitized": "<TARGET_APP>",
        "scenario": local.get("scenario") if local else None,
        "duration_seconds_requested": local.get("duration_seconds_requested") if local else None,
        "duration_seconds_observed": local.get("duration_seconds_observed") if local else None,
        "process_returncode": local.get("process_returncode") if local else None,
        "hud_env_key_count": len(local.get("hud_env_keys_enabled", [])) if local else 0,
        "env_values_committed": False,
        "private_paths_committed": False,
        "private_raw_detected_locally": has_private_text(raw_text),
        "private_text_committed": False,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "metal_hud_enabled_by_this_run": bool(local and local.get("metal_hud_enabled_by_this_run")),
        "metal_workload_run_by_this_run": bool(local and local.get("metal_workload_run_by_this_run")),
        "metal_workload_captured_by_this_run": bool(local and local.get("metal_workload_captured_by_this_run")),
        "metal_performance_report_generated_by_this_run": bool(local and local.get("metal_performance_report_generated_by_this_run")),
        "wrapper_executed_by_ci": False,
        "metal_hud_enabled_by_this_phase": False,
        "metal_workload_run_by_this_phase": False,
        "metal_workload_captured_by_this_phase": False,
        "metal_performance_report_generated_by_this_phase": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61d_allowed_now": False,
        "provider_open_allowed_now": False,
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
        "next_gate": "phase61d-sanitized-local-metal-hud-capture-summary-parser",
    }

    json_path = out_dir / "local-metal-hud-hardoptin-capture-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary.items() if k not in ["schema", "generated_at_utc"])
    md = f"""# Local Metal HUD Hard-Opt-In Capture Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Target App Sanitized: `<TARGET_APP>`
- Env Values Committed: `False`
- Private Paths Committed: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61D Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase61d-sanitized-local-metal-hud-capture-summary-parser`

## Summary

| Key | Value |
| --- | --- |
{rows}
"""
    (out_dir / "local-metal-hud-hardoptin-capture-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'local-metal-hud-hardoptin-capture-summary.md'}")
    print("Decision: PASS_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
