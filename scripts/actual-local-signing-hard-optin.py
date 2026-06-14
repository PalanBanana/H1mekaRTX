#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.actual_local_signing_hard_optin_report.v1"

def run_cmd(cmd: list[str], timeout: int = 120) -> dict:
    result = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=timeout)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def load_plist(path: Path) -> dict:
    with path.open("rb") as f:
        return plistlib.load(f)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--i-understand-local-signing", action="store_true")
    parser.add_argument("--signing-identity", default="")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--bundle-root", default="host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app")
    parser.add_argument("--out-dir", default="host-report-bundle/local-signing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bundle_root = (root / args.bundle_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report_base = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_ACTUAL_LOCAL_SIGNING_HARD_OPTIN",
        "local_signing_only": True,
        "host_report_bundle_local_only": True,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
    }

    hard_optin_ok = (
        args.i_understand_local_signing
        and bool(args.signing_identity.strip())
        and args.output_under_host_report_bundle
    )

    local_scope_ok = str(bundle_root).startswith(str((root / "host-report-bundle").resolve()) + os.sep)

    if not hard_optin_ok or not local_scope_ok:
        refusal = {
            **report_base,
            "decision": "REFUSE_SIGNING_HARD_OPTIN_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "codesign_executed": False,
            "codesign_signing_attempted": False,
            "signed_package_created": False,
            "required_flags": {
                "--i-understand-local-signing": args.i_understand_local_signing,
                "--signing-identity": bool(args.signing_identity.strip()),
                "--output-under-host-report-bundle": args.output_under_host_report_bundle,
            },
        }
        write_json(out_dir / "actual-local-signing-hard-optin-report.json", refusal)
        print("Decision: REFUSE_SIGNING_HARD_OPTIN_NOT_SATISFIED")
        return 2

    if not bundle_root.exists():
        missing = {
            **report_base,
            "decision": "REFUSE_SIGNING_BUNDLE_ROOT_MISSING",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "codesign_executed": False,
            "codesign_signing_attempted": False,
            "signed_package_created": False,
            "bundle_root": str(bundle_root),
        }
        write_json(out_dir / "actual-local-signing-hard-optin-report.json", missing)
        print("Decision: REFUSE_SIGNING_BUNDLE_ROOT_MISSING")
        return 3

    if not shutil.which("codesign"):
        missing_codesign = {
            **report_base,
            "decision": "REFUSE_SIGNING_CODESIGN_NOT_FOUND",
            "hard_optin_ok": hard_optin_ok,
            "local_scope_ok": local_scope_ok,
            "codesign_executed": False,
            "codesign_signing_attempted": False,
            "signed_package_created": False,
        }
        write_json(out_dir / "actual-local-signing-hard-optin-report.json", missing_codesign)
        print("Decision: REFUSE_SIGNING_CODESIGN_NOT_FOUND")
        return 4

    host_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements"
    dext_ent = root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements"
    dext_root = bundle_root / "Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext"

    commands = {
        "sign_embedded_dext": [
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
        ],
        "verify_embedded_dext": [
            "codesign",
            "--verify",
            "--strict",
            "--verbose=4",
            str(dext_root),
        ],
        "sign_host_app": [
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
        ],
        "verify_host_app": [
            "codesign",
            "--verify",
            "--strict",
            "--verbose=4",
            str(bundle_root),
        ],
        "dump_host_entitlements": [
            "codesign",
            "-d",
            "--entitlements",
            ":-",
            str(bundle_root),
        ],
        "dump_dext_entitlements": [
            "codesign",
            "-d",
            "--entitlements",
            ":-",
            str(dext_root),
        ],
    }

    results = {}
    for name in [
        "sign_embedded_dext",
        "verify_embedded_dext",
        "sign_host_app",
        "verify_host_app",
        "dump_host_entitlements",
        "dump_dext_entitlements",
    ]:
        results[name] = run_cmd(commands[name])
        if results[name]["returncode"] != 0:
            break

    all_ok = all(results.get(name, {}).get("returncode") == 0 for name in results)

    report = {
        **report_base,
        "decision": "PASS_LOCAL_SIGNING_COMPLETED" if all_ok else "FAIL_LOCAL_SIGNING_COMMAND_FAILED",
        "hard_optin_ok": hard_optin_ok,
        "local_scope_ok": local_scope_ok,
        "codesign_executed": True,
        "codesign_signing_attempted": True,
        "signed_package_created": bool(all_ok),
        "bundle_root_relative": args.bundle_root,
        "dext_root_relative": "host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext",
        "commands": results,
        "derived": {
            "sign_embedded_dext_ok": results.get("sign_embedded_dext", {}).get("returncode") == 0,
            "verify_embedded_dext_ok": results.get("verify_embedded_dext", {}).get("returncode") == 0,
            "sign_host_app_ok": results.get("sign_host_app", {}).get("returncode") == 0,
            "verify_host_app_ok": results.get("verify_host_app", {}).get("returncode") == 0,
            "dump_host_entitlements_ok": results.get("dump_host_entitlements", {}).get("returncode") == 0,
            "dump_dext_entitlements_ok": results.get("dump_dext_entitlements", {}).get("returncode") == 0,
            "activation_still_blocked": True,
            "provider_open_still_blocked": True,
            "bar_mapping_still_blocked": True,
            "gpu_command_submission_still_blocked": True,
        },
    }
    write_json(out_dir / "actual-local-signing-hard-optin-report.json", report)

    rows = "\n".join(
        f"| `{name}` | `{value.get('returncode')}` | `{bool(value.get('stdout'))}` | `{bool(value.get('stderr'))}` |"
        for name, value in results.items()
    )
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in report["derived"].items())

    md = f"""# Actual Local Signing Hard Opt-In Report

- Decision: `{report['decision']}`
- Local Signing Only: `True`
- Host Report Bundle Local Only: `True`
- Codesign Executed: `True`
- Codesign Signing Attempted: `True`
- Signed Package Created: `{bool(all_ok)}`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Commands

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
{rows}

## Derived

| Key | Value |
| --- | --- |
{derived_rows}
"""
    (out_dir / "actual-local-signing-hard-optin-report.md").write_text(md, encoding="utf-8")

    print("Decision:", report["decision"])
    return 0 if all_ok else 5

if __name__ == "__main__":
    raise SystemExit(main())
