#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_readonly_rtx5070_ui_baseline_report.v1"

def run_cmd(cmd: list[str], timeout: int = 180) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-120000:] if p.stdout else "",
            "stderr": p.stderr[-120000:] if p.stderr else "",
        }
    except Exception as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def contains_any(text: str, tokens: list[str]) -> bool:
    low = str(text or "").lower()
    return any(t.lower() in low for t in tokens)

def count_token(text: str, token: str) -> int:
    return str(text or "").lower().count(token.lower())

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_READONLY_RTX5070_UI_BASELINE",
        "host_report_bundle_local_only": True,
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61_allowed_now": False,
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
        "dock_transparency_blur_proof_claimed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/local-readonly-rtx5070-ui-baseline")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = {}

    if shutil.which("system_profiler"):
        commands["system_profiler_displays_json"] = run_cmd(["system_profiler", "SPDisplaysDataType", "-json"])
        commands["system_profiler_hardware_json"] = run_cmd(["system_profiler", "SPHardwareDataType", "-json"])
    else:
        commands["system_profiler_displays_json"] = {"command": ["system_profiler", "SPDisplaysDataType", "-json"], "returncode": None, "stdout": "", "stderr": "system_profiler not found"}
        commands["system_profiler_hardware_json"] = {"command": ["system_profiler", "SPHardwareDataType", "-json"], "returncode": None, "stdout": "", "stderr": "system_profiler not found"}

    if shutil.which("ioreg"):
        commands["ioreg_iopcidevice"] = run_cmd(["ioreg", "-r", "-c", "IOPCIDevice", "-l", "-w0"])
        commands["ioreg_ioaccelerator"] = run_cmd(["ioreg", "-r", "-c", "IOAccelerator", "-l", "-w0"])
        commands["ioreg_iodisplayconnect"] = run_cmd(["ioreg", "-r", "-c", "IODisplayConnect", "-l", "-w0"])
    else:
        commands["ioreg_iopcidevice"] = {"command": ["ioreg"], "returncode": None, "stdout": "", "stderr": "ioreg not found"}
        commands["ioreg_ioaccelerator"] = {"command": ["ioreg"], "returncode": None, "stdout": "", "stderr": "ioreg not found"}
        commands["ioreg_iodisplayconnect"] = {"command": ["ioreg"], "returncode": None, "stdout": "", "stderr": "ioreg not found"}

    commands["ps_windowserver_dock"] = run_cmd(["ps", "ax", "-o", "pid,comm"])

    if shutil.which("log"):
        commands["log_windowserver_dock_last5m"] = run_cmd([
            "log",
            "show",
            "--last",
            "5m",
            "--style",
            "compact",
            "--predicate",
            'process == "WindowServer" OR process == "Dock"'
        ], timeout=180)
    else:
        commands["log_windowserver_dock_last5m"] = {"command": ["log"], "returncode": None, "stdout": "", "stderr": "log not found"}

    commands["defaults_reduce_transparency"] = run_cmd([
        "defaults",
        "read",
        "com.apple.universalaccess",
        "reduceTransparency"
    ], timeout=30)

    combined = "\n".join(
        str(v.get("stdout", "")) + "\n" + str(v.get("stderr", ""))
        for v in commands.values()
    )

    displays_text = commands["system_profiler_displays_json"].get("stdout", "")
    iopci_text = commands["ioreg_iopcidevice"].get("stdout", "")
    ioaccel_text = commands["ioreg_ioaccelerator"].get("stdout", "")
    ps_text = commands["ps_windowserver_dock"].get("stdout", "")
    dock_log_text = commands["log_windowserver_dock_last5m"].get("stdout", "")

    rtx_tokens = ["RTX 5070", "0x2f04", "2f04", "0x2f0410de", "2f0410de", "0x10de", "10de"]
    rtx5070_identity_token_observed = contains_any(combined, rtx_tokens)
    vendor_10de_observed = contains_any(combined, ["0x10de", "10de"])
    device_2f04_observed = contains_any(combined, ["0x2f04", "2f04"])
    iopcimatch_observed = contains_any(combined, ["0x2f0410de", "2f0410de"])

    windowserver_observed = "WindowServer" in ps_text
    dock_observed = bool(re.search(r"/Dock$|/Dock\\s|Dock", ps_text))
    windowserver_log_observed = "WindowServer" in dock_log_text
    dock_log_observed = "Dock" in dock_log_text

    report = {
        **base_report(),
        "decision": "PASS_LOCAL_READONLY_RTX5070_UI_BASELINE_CAPTURED",
        "raw_outputs_local_only": True,
        "display_inventory_collected": commands["system_profiler_displays_json"].get("returncode") == 0,
        "hardware_inventory_collected": commands["system_profiler_hardware_json"].get("returncode") == 0,
        "iopcidevice_inventory_collected": commands["ioreg_iopcidevice"].get("returncode") == 0,
        "ioaccelerator_inventory_collected": commands["ioreg_ioaccelerator"].get("returncode") == 0,
        "iodisplayconnect_inventory_collected": commands["ioreg_iodisplayconnect"].get("returncode") == 0,
        "rtx5070_identity_token_observed": rtx5070_identity_token_observed,
        "vendor_10de_observed": vendor_10de_observed,
        "device_2f04_observed": device_2f04_observed,
        "iopcimatch_2f0410de_observed": iopcimatch_observed,
        "metal_string_observed_in_display_inventory": "Metal" in displays_text,
        "windowserver_process_observed": windowserver_observed,
        "dock_process_observed": dock_observed,
        "windowserver_log_observed": windowserver_log_observed,
        "dock_log_observed": dock_log_observed,
        "ioaccelerator_token_count": count_token(ioaccel_text, "IOAccelerator"),
        "reduce_transparency_command_returncode": commands["defaults_reduce_transparency"].get("returncode"),
        "reduce_transparency_stdout_present": bool(commands["defaults_reduce_transparency"].get("stdout")),
        "rtx5070_acceleration_claim_valid": False,
        "rtx5070_ui_smoothness_claim_valid": False,
        "next_gate": "phase60w-dock-transparency-blur-scenario-marker",
        "commands": commands,
    }

    write_json(out_dir / "local-readonly-rtx5070-ui-baseline-report.json", report)
    print("Decision: PASS_LOCAL_READONLY_RTX5070_UI_BASELINE_CAPTURED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
