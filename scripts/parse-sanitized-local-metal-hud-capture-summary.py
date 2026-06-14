#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.sanitized_local_metal_hud_capture_parser_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"Apple Development:[^\n\r]+"),
    re.compile(r"Developer ID Application:[^\n\r]+"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

METRIC_TOKENS = [
    "FPS",
    "GPU",
    "CPU",
    "frame",
    "frame interval",
    "present",
    "encoder",
    "shader",
    "hitch",
    "dropped",
    "composited",
    "direct",
    "resolution",
    "Game Mode",
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

def safe_read(path: Path, limit: int = 300000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""

def file_info(path: Path) -> dict:
    return {
        "present": path.exists() and path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
    }

def token_counts(text: str) -> dict:
    low = text.lower()
    return {token: low.count(token.lower()) for token in METRIC_TOKENS}

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

    raw_dir = root / "host-report-bundle/local-metal-hud-hardoptin-capture/raw"
    raw_stdout_files = sorted(raw_dir.glob("*.stdout.txt")) if raw_dir.exists() else []
    raw_stderr_files = sorted(raw_dir.glob("*.stderr.txt")) if raw_dir.exists() else []
    raw_hud_log_files = sorted(raw_dir.glob("*.metal-hud.log")) if raw_dir.exists() else []

    raw_text = ""
    for p in raw_stdout_files[-5:] + raw_stderr_files[-5:] + raw_hud_log_files[-5:]:
        raw_text += "\n" + safe_read(p)

    local_text = json.dumps(local or {}, sort_keys=True)
    private_raw_detected = has_private_text(local_text) or has_private_text(raw_text)

    hud_env_keys = local.get("hud_env_keys_enabled", []) if local else []
    if not isinstance(hud_env_keys, list):
        hud_env_keys = []

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_SANITIZED_LOCAL_METAL_HUD_CAPTURE_SUMMARY_PARSER",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_capture_report_present": local is not None,
        "local_capture_decision": local.get("decision") if local else "NO_LOCAL_CAPTURE_REPORT_PRESENT",
        "hard_optin_ok": bool(local and local.get("hard_optin_ok")),
        "execute_capture_requested": bool(local and local.get("execute_capture_requested")),
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "target_app_sanitized": "<TARGET_APP>",
        "target_app_path_committed": False,
        "scenario": local.get("scenario") if local else None,
        "duration_seconds_requested": local.get("duration_seconds_requested") if local else None,
        "duration_seconds_observed": local.get("duration_seconds_observed") if local else None,
        "process_returncode": local.get("process_returncode") if local else None,
        "hud_env_key_count": len(hud_env_keys),
        "hud_env_keys_enabled": hud_env_keys,
        "env_values_committed": False,
        "private_paths_committed": False,
        "raw_stdout_file_count": len(raw_stdout_files),
        "raw_stderr_file_count": len(raw_stderr_files),
        "raw_metal_hud_log_file_count": len(raw_hud_log_files),
        "raw_stdout_total_bytes": sum(p.stat().st_size for p in raw_stdout_files if p.exists()),
        "raw_stderr_total_bytes": sum(p.stat().st_size for p in raw_stderr_files if p.exists()),
        "raw_metal_hud_log_total_bytes": sum(p.stat().st_size for p in raw_hud_log_files if p.exists()),
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "raw_metal_hud_log_not_committed": True,
        "raw_stdout_committed": False,
        "raw_stderr_committed": False,
        "raw_metal_hud_log_committed": False,
        "metric_token_counts": token_counts(raw_text),
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "capture_wrapper_executed_by_this_phase": False,
        "metal_hud_enabled_by_this_phase": False,
        "metal_workload_run_by_this_phase": False,
        "metal_workload_captured_by_this_phase": False,
        "metal_performance_report_generated_by_this_phase": False,
        "metal_hud_enabled_by_local_report": bool(local and local.get("metal_hud_enabled_by_this_run")),
        "metal_workload_run_by_local_report": bool(local and local.get("metal_workload_run_by_this_run")),
        "metal_workload_captured_by_local_report": bool(local and local.get("metal_workload_captured_by_this_run")),
        "metal_performance_report_generated_by_local_report": bool(local and local.get("metal_performance_report_generated_by_this_run")),
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61e_allowed_now": False,
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
        "next_gate": "phase61e-local-metal-hud-report-metric-schema",
    }

    json_path = out_dir / "sanitized-local-metal-hud-capture-parser-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary.items() if k not in ["schema", "generated_at_utc", "metric_token_counts", "hud_env_keys_enabled"])
    token_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["metric_token_counts"].items())

    md = f"""# Sanitized Local Metal HUD Capture Parser Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Target App Sanitized: `<TARGET_APP>`
- Target App Path Committed: `False`
- Env Values Committed: `False`
- Private Paths Committed: `False`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Raw Metal HUD Log Not Committed: `True`
- Capture Wrapper Executed By This Phase: `False`
- Metal HUD Enabled By This Phase: `False`
- Metal Workload Run By This Phase: `False`
- Metal Workload Captured By This Phase: `False`
- Metal Performance Report Generated By This Phase: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61E Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase61e-local-metal-hud-report-metric-schema`

## Summary

| Key | Value |
| --- | --- |
{rows}

## Metric Token Counts

| Token | Count |
| --- | ---: |
{token_rows}
"""
    (out_dir / "sanitized-local-metal-hud-capture-parser-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'sanitized-local-metal-hud-capture-parser-summary.md'}")
    print("Decision: PASS_SANITIZED_LOCAL_METAL_HUD_CAPTURE_PARSER_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
