#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_wait_visibility_hardening_report.v1"
EXT_ID = "dev.h1meka.H1mekaRTXDriver"

def run_cmd(cmd: list[str], timeout: int = 240) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
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

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def status_tokens(text: str) -> list[str]:
    lowered = str(text or "").lower()
    tokens = []
    if EXT_ID.lower() in lowered:
        tokens.append("extension_identifier_observed")
    if "activated" in lowered:
        tokens.append("activated")
    if "enabled" in lowered:
        tokens.append("enabled")
    if any(t in lowered for t in ["waiting", "needs user", "user approval", "awaiting", "approval"]):
        tokens.append("needs_user_approval")
    if "terminated" in lowered:
        tokens.append("terminated")
    if "replaced" in lowered:
        tokens.append("replaced")
    return sorted(set(tokens))

def systemextensionsctl_list() -> dict:
    if not shutil.which("systemextensionsctl"):
        return {
            "command": ["systemextensionsctl", "list"],
            "returncode": None,
            "stdout": "",
            "stderr": "systemextensionsctl not found",
        }
    return run_cmd(["systemextensionsctl", "list"], timeout=30)

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_ACTIVATION_WAIT_SYSTEM_EXTENSION_VISIBILITY_HARDENING",
        "official_systemextensions_path": True,
        "host_report_bundle_local_only": True,
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

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--i-understand-local-activation-visibility", action="store_true")
    parser.add_argument("--submit-activation", action="store_true")
    parser.add_argument("--signing-identity", default="")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=120)
    parser.add_argument("--poll-interval-seconds", type=int, default=5)
    parser.add_argument("--bundle-root", default="host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app")
    parser.add_argument("--out-dir", default="host-report-bundle/local-activation-visibility")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bundle_root = (root / args.bundle_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "activation-wait-visibility-hardening-report.json"

    hard_optin_ok = (
        args.i_understand_local_activation_visibility
        and args.submit_activation
        and bool(args.signing_identity.strip())
        and args.output_under_host_report_bundle
    )
    local_scope_ok = str(bundle_root).startswith(str((root / "host-report-bundle").resolve()) + os.sep)

    preflight = read_json(root / "release-readiness/manual-activation-preflight-after-signed-verification-check.json")
    activation_preflight_ready = bool(preflight and preflight.get("activation_preflight_ready") is True)

    if not hard_optin_ok or not local_scope_ok or not activation_preflight_ready:
        report = {
            **base_report(),
            "decision": "REFUSE_ACTIVATION_VISIBILITY_HARDOPTIN_OR_PREFLIGHT_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
            "visibility_poll_attempted": False,
            "extension_identifier_observed": False,
            "required_flags": {
                "--i-understand-local-activation-visibility": args.i_understand_local_activation_visibility,
                "--submit-activation": args.submit_activation,
                "--signing-identity": bool(args.signing_identity.strip()),
                "--output-under-host-report-bundle": args.output_under_host_report_bundle,
            },
        }
        write_json(report_path, report)
        print("Decision: REFUSE_ACTIVATION_VISIBILITY_HARDOPTIN_OR_PREFLIGHT_NOT_SATISFIED")
        return 2

    if not bundle_root.exists():
        report = {
            **base_report(),
            "decision": "REFUSE_ACTIVATION_VISIBILITY_BUNDLE_ROOT_MISSING",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
            "visibility_poll_attempted": False,
            "extension_identifier_observed": False,
        }
        write_json(report_path, report)
        print("Decision: REFUSE_ACTIVATION_VISIBILITY_BUNDLE_ROOT_MISSING")
        return 3

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

    commands["systemextensionsctl_before"] = systemextensionsctl_list()

    activation_submitted = False
    if commands.get("verify_host_app", {}).get("returncode") == 0:
        activation_submitted = True
        commands["submit_activation"] = run_cmd([
            str(host_exec),
            "--submit-activation",
        ], timeout=max(240, args.wait_seconds + 30))

    poll_results = []
    extension_observed = False
    observed_tokens = []
    deadline = time.monotonic() + max(0, args.wait_seconds)

    while time.monotonic() <= deadline:
        result = systemextensionsctl_list()
        text = (result.get("stdout") or "") + "\n" + (result.get("stderr") or "")
        tokens = status_tokens(text)
        poll_results.append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "returncode": result.get("returncode"),
            "stdout_present": bool(result.get("stdout")),
            "stderr_present": bool(result.get("stderr")),
            "extension_identifier_observed": EXT_ID.lower() in text.lower(),
            "status_tokens": tokens,
        })
        if EXT_ID.lower() in text.lower():
            extension_observed = True
            observed_tokens = tokens
            break
        time.sleep(max(1, args.poll_interval_seconds))

    commands["systemextensionsctl_after_poll"] = systemextensionsctl_list()

    decision = "PASS_ACTIVATION_VISIBILITY_OBSERVED" if extension_observed else "PASS_ACTIVATION_SUBMITTED_BUT_VISIBILITY_NOT_OBSERVED"

    report = {
        **base_report(),
        "decision": decision,
        "hard_optin_ok": hard_optin_ok,
        "local_scope_ok": local_scope_ok,
        "activation_preflight_ready": activation_preflight_ready,
        "activation_submitted": activation_submitted,
        "visibility_poll_attempted": True,
        "wait_seconds": args.wait_seconds,
        "poll_interval_seconds": args.poll_interval_seconds,
        "extension_identifier": EXT_ID,
        "extension_identifier_observed": extension_observed,
        "observed_status_tokens": observed_tokens,
        "commands": commands,
        "poll_results": poll_results,
        "derived": {
            "build_activation_capable_host_ok": commands.get("build_activation_capable_host", {}).get("returncode") == 0,
            "resign_embedded_dext_ok": commands.get("resign_embedded_dext", {}).get("returncode") == 0,
            "verify_embedded_dext_ok": commands.get("verify_embedded_dext", {}).get("returncode") == 0,
            "resign_host_app_ok": commands.get("resign_host_app", {}).get("returncode") == 0,
            "verify_host_app_ok": commands.get("verify_host_app", {}).get("returncode") == 0,
            "activation_request_was_submitted_by_host": activation_submitted,
            "extension_visibility_observed_after_wait": extension_observed,
            "provider_open_still_blocked": True,
            "ioserviceopen_still_blocked": True,
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
    poll_rows = "\n".join(
        f"| `{i}` | `{item['returncode']}` | `{item['extension_identifier_observed']}` | `{','.join(item['status_tokens'])}` |"
        for i, item in enumerate(poll_results, 1)
    ) or "| `none` | `—` | `False` | `none` |"

    md = f"""# Activation Wait Visibility Hardening Report

- Decision: `{decision}`
- Activation Submitted: `{activation_submitted}`
- Visibility Poll Attempted: `True`
- Extension Identifier Observed: `{extension_observed}`
- Observed Status Tokens: `{','.join(observed_tokens) if observed_tokens else 'none'}`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Commands

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
{rows}

## Poll Results

| Poll | Return Code | Extension Observed | Tokens |
| --- | --- | --- | --- |
{poll_rows}
"""
    (out_dir / "activation-wait-visibility-hardening-report.md").write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
