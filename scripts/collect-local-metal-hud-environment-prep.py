#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_metal_hud_environment_prep_report.v1"

HUD_ENV_PREFIXES = (
    "MTL_",
    "METAL_",
)

HUD_ENV_EXACT = {
    "DEVELOPER_DIR",
    "DYLD_PRINT_STATISTICS",
}

def run_cmd(cmd: list[str], timeout: int = 60) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "returncode": p.returncode,
            "stdout": p.stdout[-20000:] if p.stdout else "",
            "stderr": p.stderr[-20000:] if p.stderr else "",
        }
    except Exception as exc:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }

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

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def env_key_allowed(name: str) -> bool:
    return name in HUD_ENV_EXACT or any(name.startswith(prefix) for prefix in HUD_ENV_PREFIXES) or "HUD" in name.upper()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/local-metal-hud-environment-prep")
    parser.add_argument("--manifest-summary", default="release-readiness/local-metal-hud-capture-manifest-summary.json")
    parser.add_argument("--scenario-summary", default="release-readiness/scenario-marker-aggregation-summary.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = {}
    commands["xcodebuild_version"] = run_cmd(["xcodebuild", "-version"]) if shutil.which("xcodebuild") else {"returncode": None, "stdout": "", "stderr": "xcodebuild not found"}
    commands["xcode_select_path"] = run_cmd(["xcode-select", "-p"]) if shutil.which("xcode-select") else {"returncode": None, "stdout": "", "stderr": "xcode-select not found"}

    if shutil.which("xcrun"):
        commands["xcrun_find_xctrace"] = run_cmd(["xcrun", "--find", "xctrace"])
        commands["xcrun_find_metal"] = run_cmd(["xcrun", "--find", "metal"])
        commands["xcrun_find_metallib"] = run_cmd(["xcrun", "--find", "metallib"])
        commands["xcrun_sdk_macosx"] = run_cmd(["xcrun", "--sdk", "macosx", "--show-sdk-path"])
    else:
        commands["xcrun_find_xctrace"] = {"returncode": None, "stdout": "", "stderr": "xcrun not found"}
        commands["xcrun_find_metal"] = {"returncode": None, "stdout": "", "stderr": "xcrun not found"}
        commands["xcrun_find_metallib"] = {"returncode": None, "stdout": "", "stderr": "xcrun not found"}
        commands["xcrun_sdk_macosx"] = {"returncode": None, "stdout": "", "stderr": "xcrun not found"}

    env_keys_present = sorted([k for k in os.environ.keys() if env_key_allowed(k)])
    hud_env_key_count = len(env_keys_present)

    manifest_summary = read_json(root / args.manifest_summary)
    scenario_summary = read_json(root / args.scenario_summary)

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_LOCAL_METAL_HUD_ENVIRONMENT_PREP_CAPTURED",
        "classification": "CLASSIFICATION_LOCAL_METAL_HUD_ENVIRONMENT_CAPTURE_PREP",
        "host_report_bundle_local_only": True,
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "environment_prep_only": True,
        "xcodebuild_available": commands["xcodebuild_version"].get("returncode") == 0,
        "xcode_select_available": commands["xcode_select_path"].get("returncode") == 0,
        "xcrun_available": shutil.which("xcrun") is not None,
        "xctrace_available": commands["xcrun_find_xctrace"].get("returncode") == 0,
        "metal_tool_available": commands["xcrun_find_metal"].get("returncode") == 0,
        "metallib_tool_available": commands["xcrun_find_metallib"].get("returncode") == 0,
        "macosx_sdk_available": commands["xcrun_sdk_macosx"].get("returncode") == 0,
        "hud_env_keys_present": env_keys_present,
        "hud_env_key_count": hud_env_key_count,
        "env_values_committed": False,
        "manifest_summary_present": manifest_summary is not None,
        "scenario_summary_present": scenario_summary is not None,
        "scenario_marker_event_count": scenario_summary.get("scenario_marker_event_count", 0) if scenario_summary else 0,
        "observed_scenario_count": scenario_summary.get("observed_scenario_count", 0) if scenario_summary else 0,
        "completed_scenario_session_count": scenario_summary.get("completed_scenario_session_count", 0) if scenario_summary else 0,
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
        "phase61b_allowed_now": False,
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
        "next_gate": "phase61b-local-metal-hud-dryrun-launch-command-generator",
        "commands": commands,
    }

    write_json(out_dir / "local-metal-hud-environment-prep-report.json", report)
    print("Decision: PASS_LOCAL_METAL_HUD_ENVIRONMENT_PREP_CAPTURED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
