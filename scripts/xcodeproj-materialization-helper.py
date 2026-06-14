#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.xcodeproj_materialization_helper_report.v1"

def run_cmd(cmd: list[str], cwd: Path, timeout: int = 300) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-30000:] if p.stdout else "",
            "stderr": p.stderr[-30000:] if p.stderr else "",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\nTIMEOUT",
        }

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_XCODEPROJ_MATERIALIZATION_HELPER",
        "host_report_bundle_local_only": True,
        "activation_submitted_by_this_phase": False,
        "deactivation_submitted_by_this_phase": False,
        "install_attempted": False,
        "manual_dext_load_attempted": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "firmware_load_attempted": False,
        "gpu_reset_attempted": False,
        "framebuffer_init_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "dock_transparency_blur_proof_claimed": False,
    }

def xcodegen_spec() -> str:
    return """name: H1mekaRTXDriverKit
options:
  bundleIdPrefix: dev.h1meka
settings:
  base:
    MACOSX_DEPLOYMENT_TARGET: "15.0"
targets:
  H1mekaRTXHost:
    type: application
    platform: macOS
    deploymentTarget: "15.0"
    sources:
      - Sources/H1mekaRTXHost
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: dev.h1meka.H1mekaRTXHost
        INFOPLIST_FILE: Config/H1mekaRTXHost-Info.plist
        CODE_SIGN_ENTITLEMENTS: Config/H1mekaRTXHost.entitlements
    dependencies:
      - target: H1mekaRTXDriver
        embed: true
  H1mekaRTXDriver:
    type: system-extension
    platform: macOS
    deploymentTarget: "15.0"
    sources:
      - Sources/H1mekaRTXDriver
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: dev.h1meka.H1mekaRTXDriver
        INFOPLIST_FILE: Config/H1mekaRTXDriver-Info.plist
        CODE_SIGN_ENTITLEMENTS: Config/H1mekaRTXDriver.entitlements
        SDKROOT: driverkit
        DRIVERKIT_DEPLOYMENT_TARGET: "24.0"
        PRODUCT_NAME: H1mekaRTXDriver
"""

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--i-understand-xcodeproj-materialization", action="store_true")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--emit-xcodegen-spec", action="store_true")
    parser.add_argument("--materialize-with-xcodegen", action="store_true")
    parser.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--project-path", default="apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj")
    parser.add_argument("--project-root", default="apps/H1mekaRTXDriverKit")
    parser.add_argument("--out-dir", default="host-report-bundle/xcodeproj-materialization")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    project_root = (root / args.project_root).resolve()
    project_path = (root / args.project_path).resolve()
    report_path = out_dir / "xcodeproj-materialization-helper-report.json"

    mode_count = int(args.emit_xcodegen_spec) + int(args.materialize_with_xcodegen)
    hard_optin_ok = bool(
        args.i_understand_xcodeproj_materialization
        and args.output_under_host_report_bundle
        and mode_count == 1
    )

    output_scope_ok = str(out_dir).startswith(str((root / "host-report-bundle").resolve()) + os.sep)
    project_path_ok = str(project_path).startswith(str((root / "apps/H1mekaRTXDriverKit").resolve()) + os.sep)
    project_root_exists = project_root.exists()

    out_dir.mkdir(parents=True, exist_ok=True)

    if not hard_optin_ok or not output_scope_ok or not project_path_ok or not project_root_exists:
        report = {
            **base_report(),
            "decision": "REFUSE_XCODEPROJ_MATERIALIZATION_HARDOPTIN_OR_SCOPE_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "output_scope_ok": output_scope_ok,
            "project_path_ok": project_path_ok,
            "project_root_exists": project_root_exists,
            "xcodegen_attempted": False,
            "project_generated": False,
            "project_exists_after": project_path.exists(),
        }
        write_json(report_path, report)
        print("Decision: REFUSE_XCODEPROJ_MATERIALIZATION_HARDOPTIN_OR_SCOPE_NOT_SATISFIED")
        return 2

    spec_path = out_dir / "project.yml"
    write_text(spec_path, xcodegen_spec())

    commands = {}
    xcodegen_path = shutil.which("xcodegen")
    project_exists_before = project_path.exists()

    project_generated = False

    if args.emit_xcodegen_spec:
        decision = "PASS_XCODEGEN_SPEC_EMITTED_LOCAL_ONLY"
    else:
        if not xcodegen_path:
            decision = "REFUSE_XCODEGEN_NOT_INSTALLED"
        elif project_path.exists() and not args.replace_existing:
            decision = "REFUSE_PROJECT_EXISTS_WITHOUT_REPLACE_EXISTING"
        else:
            if project_path.exists() and args.replace_existing:
                shutil.rmtree(project_path)
            local_project_yml = project_root / "project.yml"
            write_text(local_project_yml, xcodegen_spec())
            commands["xcodegen_generate"] = run_cmd([xcodegen_path, "generate"], cwd=project_root, timeout=600)
            project_generated = project_path.exists()
            decision = "PASS_XCODEPROJ_MATERIALIZED_LOCALLY" if project_generated else "PASS_XCODEGEN_RAN_PROJECT_NOT_FOUND"

    report = {
        **base_report(),
        "decision": decision,
        "hard_optin_ok": hard_optin_ok,
        "output_scope_ok": output_scope_ok,
        "project_path_ok": project_path_ok,
        "project_root_exists": project_root_exists,
        "mode": "emit_xcodegen_spec" if args.emit_xcodegen_spec else "materialize_with_xcodegen",
        "xcodegen_installed": bool(xcodegen_path),
        "xcodegen_path_present": bool(xcodegen_path),
        "xcodegen_attempted": bool(args.materialize_with_xcodegen and xcodegen_path),
        "project_exists_before": project_exists_before,
        "project_generated": project_generated,
        "project_exists_after": project_path.exists(),
        "project_path": str(project_path),
        "spec_emitted_local_only": spec_path.exists(),
        "next_gate_if_project_exists": "phase60l-real-driverkit-dext-build-gate-local-run",
        "next_gate_if_project_missing": "manual_xcode_creation_or_install_xcodegen",
        "commands": commands,
    }
    write_json(report_path, report)
    print("Decision:", decision)
    return 0 if decision.startswith("PASS") else 3

if __name__ == "__main__":
    raise SystemExit(main())
