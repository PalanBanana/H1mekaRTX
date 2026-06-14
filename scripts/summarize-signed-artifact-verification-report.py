#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.signed_artifact_verification_report_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"Developer ID Application:[^\n\r]+"),
    re.compile(r"Apple Development:[^\n\r]+"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def has_private_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in PRIVATE_PATTERNS)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/local-signing/actual-local-signing-hard-optin-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    commands = local_report.get("commands", {}) if local_report else {}
    derived = local_report.get("derived", {}) if local_report else {}

    private_raw_detected = False
    sanitized_commands = {}

    for name, item in commands.items():
        stdout = str(item.get("stdout", ""))
        stderr = str(item.get("stderr", ""))
        private_raw_detected = private_raw_detected or has_private_text(stdout) or has_private_text(stderr) or has_private_text(" ".join(map(str, item.get("command", []))))
        sanitized_commands[name] = {
            "returncode": item.get("returncode"),
            "stdout_present": bool(stdout),
            "stderr_present": bool(stderr),
            "raw_stdout_committed": False,
            "raw_stderr_committed": False,
            "command_body_committed": False,
        }

    local_decision = local_report.get("decision") if local_report else "NO_LOCAL_SIGNING_REPORT_PRESENT"
    signed_package_created = bool(local_report and local_report.get("signed_package_created") is True)
    codesign_executed = bool(local_report and local_report.get("codesign_executed") is True)
    codesign_signing_attempted = bool(local_report and local_report.get("codesign_signing_attempted") is True)

    verification_summary = {
        "sign_embedded_dext_ok": bool(derived.get("sign_embedded_dext_ok")),
        "verify_embedded_dext_ok": bool(derived.get("verify_embedded_dext_ok")),
        "sign_host_app_ok": bool(derived.get("sign_host_app_ok")),
        "verify_host_app_ok": bool(derived.get("verify_host_app_ok")),
        "dump_host_entitlements_ok": bool(derived.get("dump_host_entitlements_ok")),
        "dump_dext_entitlements_ok": bool(derived.get("dump_dext_entitlements_ok")),
    }

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER",
        "local_report_sanitizer_only": True,
        "host_report_bundle_local_only": True,
        "local_signing_report_present": local_report is not None,
        "local_signing_decision": local_decision,
        "hard_optin_ok": bool(local_report and local_report.get("hard_optin_ok") is True),
        "local_scope_ok": bool(local_report and local_report.get("local_scope_ok") is True),
        "codesign_executed_locally": codesign_executed,
        "codesign_signing_attempted_locally": codesign_signing_attempted,
        "signed_package_created_locally": signed_package_created,
        "signed_artifact_verification_ok": bool(
            verification_summary["verify_embedded_dext_ok"]
            and verification_summary["verify_host_app_ok"]
            and verification_summary["dump_host_entitlements_ok"]
            and verification_summary["dump_dext_entitlements_ok"]
        ),
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "command_body_not_committed": True,
        "signing_identity_not_committed": True,
        "entitlement_dump_body_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "codesign_executed_by_sanitizer": False,
        "codesign_signing_attempted_by_sanitizer": False,
        "signed_package_created_by_sanitizer": False,
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
        "sanitized_commands": sanitized_commands,
        "verification_summary": verification_summary,
        "boundary_summary": {
            "activation_still_blocked": bool(derived.get("activation_still_blocked", True)),
            "provider_open_still_blocked": bool(derived.get("provider_open_still_blocked", True)),
            "bar_mapping_still_blocked": bool(derived.get("bar_mapping_still_blocked", True)),
            "gpu_command_submission_still_blocked": bool(derived.get("gpu_command_submission_still_blocked", True)),
        },
        "next_gate": "manual_activation_preflight_only_after_signed_artifact_verification_ok",
    }

    json_path = out_dir / "signed-artifact-verification-report-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command_rows = "\n".join(
        f"| `{name}` | `{item['returncode']}` | `{item['stdout_present']}` | `{item['stderr_present']}` |"
        for name, item in sanitized_commands.items()
    ) or "| `none` | `—` | `False` | `False` |"

    verify_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in verification_summary.items())
    boundary_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in summary["boundary_summary"].items())

    md = f"""# Signed Artifact Verification Report Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Local Report Sanitizer Only: `True`
- Host Report Bundle Local Only: `True`
- Local Signing Report Present: `{summary['local_signing_report_present']}`
- Local Signing Decision: `{summary['local_signing_decision']}`
- Hard Opt-In OK: `{summary['hard_optin_ok']}`
- Local Scope OK: `{summary['local_scope_ok']}`
- Codesign Executed Locally: `{summary['codesign_executed_locally']}`
- Codesign Signing Attempted Locally: `{summary['codesign_signing_attempted_locally']}`
- Signed Package Created Locally: `{summary['signed_package_created_locally']}`
- Signed Artifact Verification OK: `{summary['signed_artifact_verification_ok']}`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Signing Identity Not Committed: `True`
- Entitlement Dump Body Not Committed: `True`
- Codesign Executed By Sanitizer: `False`
- Codesign Signing Attempted By Sanitizer: `False`
- Signed Package Created By Sanitizer: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Sanitized Command Summary

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
{command_rows}

## Verification Summary

| Key | Value |
| --- | --- |
{verify_rows}

## Runtime Boundary Summary

| Key | Value |
| --- | --- |
{boundary_rows}
"""
    md_path = out_dir / "signed-artifact-verification-report-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_SIGNED_ARTIFACT_VERIFICATION_REPORT_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
