#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.actual_local_activation_hard_optin_report.v1"

def run_cmd(cmd: list[str], timeout: int = 180) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-20000:],
            "stderr": p.stderr[-20000:],
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

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN",
        "official_systemextensions_path": True,
        "host_report_bundle_local_only": True,
        "provider_open_attempted": False,
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

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--i-understand-local-activation", action="store_true")
    parser.add_argument("--submit-activation", action="store_true")
    parser.add_argument("--signing-identity", default="")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--bundle-root", default="host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app")
    parser.add_argument("--out-dir", default="host-report-bundle/local-activation")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bundle_root = (root / args.bundle_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "actual-local-activation-hard-optin-report.json"

    hard_optin_ok = (
        args.i_understand_local_activation
        and args.submit_activation
        and bool(args.signing_identity.strip())
        and args.output_under_host_report_bundle
    )
    local_scope_ok = str(bundle_root).startswith(str((root / "host-report-bundle").resolve()) + os.sep)

    preflight_path = root / "release-readiness/manual-activation-preflight-after-signed-verification-check.json"
    preflight = read_json(preflight_path)
    activation_preflight_ready = bool(preflight and preflight.get("activation_preflight_ready") is True)

    if not hard_optin_ok or not local_scope_ok or not activation_preflight_ready:
        refusal = {
            **base_report(),
            "decision": "REFUSE_ACTIVATION_HARD_OPTIN_OR_PREFLIGHT_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
            "deactivation_submitted": False,
            "required_flags": {
                "--i-understand-local-activation": args.i_understand_local_activation,
                "--submit-activation": args.submit_activation,
                "--signing-identity": bool(args.signing_identity.strip()),
                "--output-under-host-report-bundle": args.output_under_host_report_bundle,
            },
        }
        write_json(report_path, refusal)
        print("Decision: REFUSE_ACTIVATION_HARD_OPTIN_OR_PREFLIGHT_NOT_SATISFIED")
        return 2

    if not bundle_root.exists():
        refusal = {
            **base_report(),
            "decision": "REFUSE_ACTIVATION_BUNDLE_ROOT_MISSING",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
            "bundle_root": str(bundle_root),
        }
        write_json(report_path, refusal)
        print("Decision: REFUSE_ACTIVATION_BUNDLE_ROOT_MISSING")
        return 3

    if not shutil.which("xcrun"):
        refusal = {
            **base_report(),
            "decision": "REFUSE_ACTIVATION_XCRUN_NOT_FOUND",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
        }
        write_json(report_path, refusal)
        print("Decision: REFUSE_ACTIVATION_XCRUN_NOT_FOUND")
        return 4

    if not shutil.which("codesign"):
        refusal = {
            **base_report(),
            "decision": "REFUSE_ACTIVATION_CODESIGN_NOT_FOUND",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
        }
        write_json(report_path, refusal)
        print("Decision: REFUSE_ACTIVATION_CODESIGN_NOT_FOUND")
        return 5

    host_swift = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift"
    host_exec = bundle_root / "Contents/MacOS/H1mekaRTXHost"
    dext_root = bundle_root / "Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext"
    host_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements"
    dext_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements"

    commands = {}

    commands["build_activation_capable_host"] = run_cmd([
        "xcrun",
        "swiftc",
        "-framework",
        "SystemExtensions",
        str(host_swift),
        "-o",
        str(host_exec),
    ])

    if commands["build_activation_capable_host"]["returncode"] == 0:
        commands["resign_embedded_dext"] = run_cmd([
            "codesign",
            "--force",
            "--timestamp=none",
            "--options",
            "runtime",
            "--entitlements",
            str(dext_ent),
            "--sign",
            args.signing_identity,
            str(dext_root),
        ])

    if commands.get("resign_embedded_dext", {}).get("returncode") == 0:
        commands["verify_embedded_dext"] = run_cmd([
            "codesign",
            "--verify",
            "--strict",
            "--verbose=4",
            str(dext_root),
        ])

    if commands.get("verify_embedded_dext", {}).get("returncode") == 0:
        commands["resign_host_app"] = run_cmd([
            "codesign",
            "--force",
            "--timestamp=none",
            "--options",
            "runtime",
            "--entitlements",
            str(host_ent),
            "--sign",
            args.signing_identity,
            str(bundle_root),
        ])

    if commands.get("resign_host_app", {}).get("returncode") == 0:
        commands["verify_host_app"] = run_cmd([
            "codesign",
            "--verify",
            "--strict",
            "--verbose=4",
            str(bundle_root),
        ])

    commands["systemextensionsctl_before"] = run_cmd(["systemextensionsctl", "list"], timeout=30)

    activation_submitted = False
    if commands.get("verify_host_app", {}).get("returncode") == 0:
        activation_submitted = True
        commands["submit_activation"] = run_cmd([
            str(host_exec),
            "--submit-activation",
        ], timeout=240)

    commands["systemextensionsctl_after"] = run_cmd(["systemextensionsctl", "list"], timeout=30)

    submit_rc = commands.get("submit_activation", {}).get("returncode")
    decision = "PASS_LOCAL_ACTIVATION_COMMAND_COMPLETED" if activation_submitted and submit_rc == 0 else "FAIL_LOCAL_ACTIVATION_COMMAND_FAILED"

    report = {
        **base_report(),
        "decision": decision,
        "hard_optin_ok": hard_optin_ok,
        "local_scope_ok": local_scope_ok,
        "activation_preflight_ready": activation_preflight_ready,
        "activation_submitted": activation_submitted,
        "deactivation_submitted": False,
        "bundle_root_relative": args.bundle_root,
        "extension_identifier": "dev.h1meka.H1mekaRTXDriver",
        "commands": commands,
        "derived": {
            "build_activation_capable_host_ok": commands.get("build_activation_capable_host", {}).get("returncode") == 0,
            "resign_embedded_dext_ok": commands.get("resign_embedded_dext", {}).get("returncode") == 0,
            "verify_embedded_dext_ok": commands.get("verify_embedded_dext", {}).get("returncode") == 0,
            "resign_host_app_ok": commands.get("resign_host_app", {}).get("returncode") == 0,
            "verify_host_app_ok": commands.get("verify_host_app", {}).get("returncode") == 0,
            "activation_command_returncode": submit_rc,
            "activation_request_was_submitted_by_host": activation_submitted,
            "provider_open_still_blocked": True,
            "bar_mapping_still_blocked": True,
            "gpu_command_submission_still_blocked": True,
            "dock_transparency_blur_proof_still_blocked": True,
        },
    }
    write_json(report_path, report)

    rows = "\n".join(
        f"| `{name}` | `{item.get('returncode')}` | `{bool(item.get('stdout'))}` | `{bool(item.get('stderr'))}` |"
        for name, item in commands.items()
    )

    md = f"""# Actual Local Activation Hard Opt-In Report

- Decision: `{decision}`
- Hard Opt-In OK: `{hard_optin_ok}`
- Local Scope OK: `{local_scope_ok}`
- Activation Preflight Ready: `{activation_preflight_ready}`
- Activation Submitted: `{activation_submitted}`
- Deactivation Submitted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Dock Transparency Blur Proof Claimed: `False`

## Commands

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
{rows}
"""
    (out_dir / "actual-local-activation-hard-optin-report.md").write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if decision == "PASS_LOCAL_ACTIVATION_COMMAND_COMPLETED" else 6

if __name__ == "__main__":
    raise SystemExit(main())
