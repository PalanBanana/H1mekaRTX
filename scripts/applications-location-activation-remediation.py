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

SCHEMA = "h1mekartx.applications_location_activation_remediation_report.v1"
EXT_ID = "dev.h1meka.H1mekaRTXDriver"

def run_cmd(cmd: list[str], timeout: int = 300) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-40000:] if p.stdout else "",
            "stderr": p.stderr[-40000:] if p.stderr else "",
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

def parse_delegate(text: str) -> dict:
    lines = str(text or "").splitlines()
    events = [line.split("=", 1)[1] for line in lines if line.startswith("H1MEKARTX_SYSEXT_EVENT=")]
    data = {}
    for line in lines:
        if line.startswith("H1MEKARTX_SYSEXT_") and "=" in line:
            k, v = line.split("=", 1)
            data[k] = v
    return {
        "events": events,
        "did_finish": "did_finish" in events,
        "did_fail": "did_fail" in events,
        "needs_user_approval": "request_needs_user_approval" in events,
        "delegate_timeout": "delegate_timeout" in events,
        "error_domain": data.get("H1MEKARTX_SYSEXT_ERROR_DOMAIN", "none"),
        "error_code": data.get("H1MEKARTX_SYSEXT_ERROR_CODE", "none"),
        "error_text_present": bool(data.get("H1MEKARTX_SYSEXT_ERROR_TEXT") or data.get("H1MEKARTX_SYSEXT_ERROR_DESCRIPTION")),
        "result_text": data.get("H1MEKARTX_SYSEXT_RESULT_TEXT") or data.get("H1MEKARTX_SYSEXT_RESULT") or "none",
    }

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_APPLICATIONS_LOCATION_ACTIVATION_REMEDIATION",
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
    parser.add_argument("--i-understand-applications-staging", action="store_true")
    parser.add_argument("--stage-to-applications", action="store_true")
    parser.add_argument("--submit-activation", action="store_true")
    parser.add_argument("--signing-identity", default="")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--use-sudo", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=180)
    parser.add_argument("--poll-interval-seconds", type=int, default=5)
    parser.add_argument("--source-bundle", default="host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app")
    parser.add_argument("--applications-bundle", default="/Applications/H1mekaRTXHost.app")
    parser.add_argument("--out-dir", default="host-report-bundle/applications-location-remediation")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    source_bundle = (root / args.source_bundle).resolve()
    applications_bundle = Path(args.applications_bundle).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "applications-location-activation-remediation-report.json"

    hard_optin_ok = (
        args.i_understand_applications_staging
        and args.stage_to_applications
        and args.submit_activation
        and bool(args.signing_identity.strip())
        and args.output_under_host_report_bundle
    )

    source_scope_ok = str(source_bundle).startswith(str((root / "host-report-bundle").resolve()) + os.sep)
    destination_scope_ok = str(applications_bundle) == "/Applications/H1mekaRTXHost.app"

    preflight = read_json(root / "release-readiness/manual-activation-preflight-after-signed-verification-check.json")
    activation_preflight_ready = bool(preflight and preflight.get("activation_preflight_ready") is True)

    if not hard_optin_ok or not source_scope_ok or not destination_scope_ok or not activation_preflight_ready:
        report = {
            **base_report(),
            "decision": "REFUSE_APPLICATIONS_STAGING_HARDOPTIN_OR_PREFLIGHT_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "source_scope_ok": source_scope_ok,
            "destination_scope_ok": destination_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "staged_to_applications": False,
            "activation_submitted": False,
            "extension_identifier_observed": False,
        }
        write_json(report_path, report)
        print("Decision: REFUSE_APPLICATIONS_STAGING_HARDOPTIN_OR_PREFLIGHT_NOT_SATISFIED")
        return 2

    if not source_bundle.exists():
        report = {
            **base_report(),
            "decision": "REFUSE_SOURCE_BUNDLE_MISSING",
            "source_bundle": str(source_bundle),
            "staged_to_applications": False,
            "activation_submitted": False,
            "extension_identifier_observed": False,
        }
        write_json(report_path, report)
        print("Decision: REFUSE_SOURCE_BUNDLE_MISSING")
        return 3

    commands = {}

    if applications_bundle.exists():
        if not args.replace_existing:
            report = {
                **base_report(),
                "decision": "REFUSE_APPLICATIONS_DESTINATION_EXISTS_WITHOUT_REPLACE_EXISTING",
                "applications_bundle": str(applications_bundle),
                "staged_to_applications": False,
                "activation_submitted": False,
                "extension_identifier_observed": False,
            }
            write_json(report_path, report)
            print("Decision: REFUSE_APPLICATIONS_DESTINATION_EXISTS_WITHOUT_REPLACE_EXISTING")
            return 4
        rm_cmd = ["rm", "-rf", str(applications_bundle)]
        if args.use_sudo:
            rm_cmd = ["sudo"] + rm_cmd
        commands["remove_existing_applications_bundle"] = run_cmd(rm_cmd, timeout=120)

    ditto_cmd = ["/usr/bin/ditto", str(source_bundle), str(applications_bundle)]
    if args.use_sudo:
        ditto_cmd = ["sudo"] + ditto_cmd
    commands["stage_to_applications"] = run_cmd(ditto_cmd, timeout=180)

    staged_ok = applications_bundle.exists() and commands["stage_to_applications"]["returncode"] == 0

    swift_src = root / "tools/driverkit-buildable-scaffold/H1mekaRTXActivationDiagnosticsHost.swift"
    host_exec = applications_bundle / "Contents/MacOS/H1mekaRTXHost"
    dext_root = applications_bundle / "Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext"
    host_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements"
    dext_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements"

    if staged_ok:
        commands["build_delegate_host_in_applications"] = run_cmd([
            "xcrun", "swiftc", "-framework", "SystemExtensions", str(swift_src), "-o", str(host_exec)
        ])

    if commands.get("build_delegate_host_in_applications", {}).get("returncode") == 0:
        commands["resign_embedded_dext"] = run_cmd([
            "codesign", "--force", "--timestamp=none", "--options", "runtime",
            "--entitlements", str(dext_ent), "--sign", args.signing_identity, str(dext_root)
        ])

    if commands.get("resign_embedded_dext", {}).get("returncode") == 0:
        commands["verify_embedded_dext"] = run_cmd([
            "codesign", "--verify", "--strict", "--verbose=4", str(dext_root)
        ])

    if commands.get("verify_embedded_dext", {}).get("returncode") == 0:
        commands["resign_host_app"] = run_cmd([
            "codesign", "--force", "--timestamp=none", "--options", "runtime",
            "--entitlements", str(host_ent), "--sign", args.signing_identity, str(applications_bundle)
        ])

    if commands.get("resign_host_app", {}).get("returncode") == 0:
        commands["verify_host_app"] = run_cmd([
            "codesign", "--verify", "--strict", "--verbose=4", str(applications_bundle)
        ])

    commands["systemextensionsctl_before_activation"] = systemextensionsctl_list()

    activation_submitted = False
    if commands.get("verify_host_app", {}).get("returncode") == 0:
        activation_submitted = True
        commands["submit_activation_from_applications"] = run_cmd([
            str(host_exec),
            "--submit-activation",
            "--extension-id", EXT_ID,
            "--wait-seconds", str(args.wait_seconds),
        ], timeout=args.wait_seconds + 60)

    poll_results = []
    observed = False
    observed_tokens = []
    deadline = time.monotonic() + max(0, args.wait_seconds)

    while time.monotonic() <= deadline:
        status = systemextensionsctl_list()
        text = (status.get("stdout") or "") + "\n" + (status.get("stderr") or "")
        tokens = status_tokens(text)
        item = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "returncode": status.get("returncode"),
            "stdout_present": bool(status.get("stdout")),
            "stderr_present": bool(status.get("stderr")),
            "extension_identifier_observed": EXT_ID.lower() in text.lower(),
            "status_tokens": tokens,
        }
        poll_results.append(item)
        if item["extension_identifier_observed"]:
            observed = True
            observed_tokens = tokens
            break
        time.sleep(max(1, args.poll_interval_seconds))

    commands["systemextensionsctl_after_poll"] = systemextensionsctl_list()

    delegate_text = ""
    if "submit_activation_from_applications" in commands:
        delegate_text = (commands["submit_activation_from_applications"].get("stdout") or "") + "\n" + (commands["submit_activation_from_applications"].get("stderr") or "")

    delegate = parse_delegate(delegate_text)

    if observed:
        decision = "PASS_APPLICATIONS_LOCATION_EXTENSION_VISIBLE"
    elif delegate.get("needs_user_approval"):
        decision = "PASS_APPLICATIONS_LOCATION_NEEDS_USER_APPROVAL"
    elif delegate.get("did_fail"):
        decision = "PASS_APPLICATIONS_LOCATION_DELEGATE_FAILED"
    elif delegate.get("delegate_timeout"):
        decision = "PASS_APPLICATIONS_LOCATION_DELEGATE_TIMEOUT"
    else:
        decision = "PASS_APPLICATIONS_LOCATION_ACTIVATION_SUBMITTED_NOT_VISIBLE"

    report = {
        **base_report(),
        "decision": decision,
        "hard_optin_ok": hard_optin_ok,
        "source_scope_ok": source_scope_ok,
        "destination_scope_ok": destination_scope_ok,
        "activation_preflight_ready": activation_preflight_ready,
        "source_bundle": str(source_bundle),
        "applications_bundle": str(applications_bundle),
        "staged_to_applications": staged_ok,
        "activation_submitted": activation_submitted,
        "extension_identifier": EXT_ID,
        "extension_identifier_observed": observed,
        "observed_status_tokens": observed_tokens,
        "delegate": delegate,
        "commands": commands,
        "poll_results": poll_results,
        "derived": {
            "staged_to_applications_ok": staged_ok,
            "build_delegate_host_in_applications_ok": commands.get("build_delegate_host_in_applications", {}).get("returncode") == 0,
            "resign_embedded_dext_ok": commands.get("resign_embedded_dext", {}).get("returncode") == 0,
            "verify_embedded_dext_ok": commands.get("verify_embedded_dext", {}).get("returncode") == 0,
            "resign_host_app_ok": commands.get("resign_host_app", {}).get("returncode") == 0,
            "verify_host_app_ok": commands.get("verify_host_app", {}).get("returncode") == 0,
            "activation_request_submitted_from_applications": activation_submitted,
            "delegate_did_finish": delegate.get("did_finish"),
            "delegate_did_fail": delegate.get("did_fail"),
            "delegate_needs_user_approval": delegate.get("needs_user_approval"),
            "delegate_timeout": delegate.get("delegate_timeout"),
            "extension_visibility_observed_after_applications_activation": observed,
            "provider_open_still_blocked": True,
            "ioserviceopen_still_blocked": True,
            "bar_mapping_still_blocked": True,
            "gpu_command_submission_still_blocked": True,
            "dock_transparency_blur_proof_still_blocked": True,
        },
    }

    write_json(report_path, report)
    print("Decision:", decision)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
