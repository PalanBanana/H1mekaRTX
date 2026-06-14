#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_delegate_error_diagnostics_report.v1"
EXT_ID = "dev.h1meka.H1mekaRTXDriver"

def run_cmd(cmd: list[str], timeout: int = 300) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-50000:] if p.stdout else "",
            "stderr": p.stderr[-50000:] if p.stderr else "",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\\nTIMEOUT",
        }

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\\n", encoding="utf-8")

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def parse_events(text: str) -> dict:
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
        "replacement_requested": "replacement_requested" in events,
        "result_text": data.get("H1MEKARTX_SYSEXT_RESULT_TEXT") or data.get("H1MEKARTX_SYSEXT_RESULT") or "none",
        "error_text_present": bool(data.get("H1MEKARTX_SYSEXT_ERROR_TEXT") or data.get("H1MEKARTX_SYSEXT_ERROR_DESCRIPTION")),
        "error_domain": data.get("H1MEKARTX_SYSEXT_ERROR_DOMAIN", "none"),
        "error_code": data.get("H1MEKARTX_SYSEXT_ERROR_CODE", "none"),
    }

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

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--i-understand-activation-delegate-diagnostics", action="store_true")
    parser.add_argument("--submit-activation", action="store_true")
    parser.add_argument("--signing-identity", default="")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=180)
    parser.add_argument("--log-last", default="10m")
    parser.add_argument("--bundle-root", default="host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app")
    parser.add_argument("--out-dir", default="host-report-bundle/activation-delegate-diagnostics")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bundle_root = (root / args.bundle_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "activation-delegate-error-diagnostics-report.json"

    hard_optin_ok = (
        args.i_understand_activation_delegate_diagnostics
        and args.submit_activation
        and bool(args.signing_identity.strip())
        and args.output_under_host_report_bundle
    )
    local_scope_ok = str(bundle_root).startswith(str((root / "host-report-bundle").resolve()) + os.sep)

    preflight = read_json(root / "release-readiness/manual-activation-preflight-after-signed-verification-check.json")
    activation_preflight_ready = bool(preflight and preflight.get("activation_preflight_ready") is True)

    base = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_ACTIVATION_DELEGATE_ERROR_DIAGNOSTICS",
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

    if not hard_optin_ok or not local_scope_ok or not activation_preflight_ready:
        report = {
            **base,
            "decision": "REFUSE_DELEGATE_DIAGNOSTICS_HARDOPTIN_OR_PREFLIGHT_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "activation_preflight_ready": activation_preflight_ready,
            "activation_submitted": False,
            "delegate_diagnostics_attempted": False,
        }
        write_json(report_path, report)
        print("Decision: REFUSE_DELEGATE_DIAGNOSTICS_HARDOPTIN_OR_PREFLIGHT_NOT_SATISFIED")
        return 2

    host_exec = bundle_root / "Contents/MacOS/H1mekaRTXHost"
    dext_root = bundle_root / "Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext"
    host_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements"
    dext_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements"
    swift_src = out_dir / "H1mekaRTXActivationDiagnosticsHost.swift"
    swift_src.write_text((root / "tools/driverkit-buildable-scaffold/H1mekaRTXActivationDiagnosticsHost.swift").read_text(encoding="utf-8"), encoding="utf-8")

    commands = {}

    commands["build_delegate_diagnostics_host"] = run_cmd([
        "xcrun", "swiftc", "-framework", "SystemExtensions", str(swift_src), "-o", str(host_exec)
    ])

    if commands["build_delegate_diagnostics_host"]["returncode"] == 0:
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
            "--entitlements", str(host_ent), "--sign", args.signing_identity, str(bundle_root)
        ])

    if commands.get("resign_host_app", {}).get("returncode") == 0:
        commands["verify_host_app"] = run_cmd([
            "codesign", "--verify", "--strict", "--verbose=4", str(bundle_root)
        ])

    commands["systemextensionsctl_before"] = systemextensionsctl_list()

    activation_submitted = False
    if commands.get("verify_host_app", {}).get("returncode") == 0:
        activation_submitted = True
        commands["submit_activation_with_delegate"] = run_cmd([
            str(host_exec),
            "--submit-activation",
            "--extension-id", EXT_ID,
            "--wait-seconds", str(args.wait_seconds),
        ], timeout=args.wait_seconds + 60)

    commands["systemextensionsctl_after"] = systemextensionsctl_list()

    if shutil.which("log"):
        commands["log_show_sysext_kernelmanagerd"] = run_cmd([
            "log", "show", "--last", args.log_last, "--style", "compact",
            "--predicate", 'process == "sysextd" OR process == "kernelmanagerd" OR process == "syspolicyd"'
        ], timeout=90)

    delegate_text = ""
    if "submit_activation_with_delegate" in commands:
        delegate_text = (commands["submit_activation_with_delegate"].get("stdout") or "") + "\\n" + (commands["submit_activation_with_delegate"].get("stderr") or "")

    parsed_delegate = parse_events(delegate_text)
    status_text = (commands["systemextensionsctl_after"].get("stdout") or "") + "\\n" + (commands["systemextensionsctl_after"].get("stderr") or "")
    tokens = status_tokens(status_text)
    extension_observed = EXT_ID.lower() in status_text.lower()

    decision = "PASS_DELEGATE_DIAGNOSTICS_EXTENSION_VISIBLE" if extension_observed else "PASS_DELEGATE_DIAGNOSTICS_CAPTURED_EXTENSION_NOT_VISIBLE"

    report = {
        **base,
        "decision": decision,
        "hard_optin_ok": hard_optin_ok,
        "local_scope_ok": local_scope_ok,
        "activation_preflight_ready": activation_preflight_ready,
        "activation_submitted": activation_submitted,
        "delegate_diagnostics_attempted": True,
        "extension_identifier": EXT_ID,
        "extension_identifier_observed": extension_observed,
        "status_tokens": tokens,
        "delegate": parsed_delegate,
        "commands": commands,
        "derived": {
            "build_delegate_diagnostics_host_ok": commands.get("build_delegate_diagnostics_host", {}).get("returncode") == 0,
            "resign_embedded_dext_ok": commands.get("resign_embedded_dext", {}).get("returncode") == 0,
            "verify_embedded_dext_ok": commands.get("verify_embedded_dext", {}).get("returncode") == 0,
            "resign_host_app_ok": commands.get("resign_host_app", {}).get("returncode") == 0,
            "verify_host_app_ok": commands.get("verify_host_app", {}).get("returncode") == 0,
            "delegate_did_finish": parsed_delegate.get("did_finish"),
            "delegate_did_fail": parsed_delegate.get("did_fail"),
            "delegate_needs_user_approval": parsed_delegate.get("needs_user_approval"),
            "delegate_timeout": parsed_delegate.get("delegate_timeout"),
            "delegate_error_text_present": parsed_delegate.get("error_text_present"),
            "extension_visibility_observed_after_delegate": extension_observed,
            "provider_open_still_blocked": True,
            "ioserviceopen_still_blocked": True,
            "bar_mapping_still_blocked": True,
            "gpu_command_submission_still_blocked": True,
            "dock_transparency_blur_proof_still_blocked": True,
        },
    }

    write_json(report_path, report)
    (out_dir / "activation-delegate-error-diagnostics-report.md").write_text(
        "# Activation Delegate Error Diagnostics Report\\n\\n"
        f"- Decision: `{decision}`\\n"
        f"- Activation Submitted: `{activation_submitted}`\\n"
        f"- Extension Identifier Observed: `{extension_observed}`\\n"
        f"- Status Tokens: `{','.join(tokens) if tokens else 'none'}`\\n"
        f"- Delegate Did Finish: `{parsed_delegate.get('did_finish')}`\\n"
        f"- Delegate Did Fail: `{parsed_delegate.get('did_fail')}`\\n"
        f"- Delegate Needs User Approval: `{parsed_delegate.get('needs_user_approval')}`\\n"
        f"- Delegate Timeout: `{parsed_delegate.get('delegate_timeout')}`\\n"
        "- Provider Open Attempted: `False`\\n"
        "- IOServiceOpen Attempted: `False`\\n"
        "- BAR Mapping Attempted: `False`\\n"
        "- GPU Command Submission Attempted: `False`\\n",
        encoding="utf-8",
    )

    print("Decision:", decision)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
