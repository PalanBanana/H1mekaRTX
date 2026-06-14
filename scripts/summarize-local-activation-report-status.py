#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_activation_report_status_summary.v1"
EXT_ID = "dev.h1meka.H1mekaRTXDriver"

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

def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "available": True,
            "returncode": p.returncode,
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
        }
    except FileNotFoundError:
        return {
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "command not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "available": True,
            "returncode": None,
            "stdout": "",
            "stderr": "timeout",
        }

def has_private_text(value: str) -> bool:
    return any(pattern.search(str(value or "")) for pattern in PRIVATE_PATTERNS)

def sanitize_status_tokens(text: str) -> list[str]:
    tokens = []
    for line in str(text or "").splitlines():
        if EXT_ID in line:
            lowered = line.lower()
            if "activated" in lowered:
                tokens.append("activated")
            if "enabled" in lowered:
                tokens.append("enabled")
            if "waiting for user" in lowered or "needs user" in lowered or "awaiting" in lowered:
                tokens.append("needs_user_approval")
            if "terminated" in lowered:
                tokens.append("terminated")
            if "uninstalling" in lowered:
                tokens.append("uninstalling")
            if not tokens:
                tokens.append("extension_identifier_observed")
    return sorted(set(tokens))

def summarize_command(item: dict | None) -> dict:
    item = item or {}
    stdout = str(item.get("stdout", ""))
    stderr = str(item.get("stderr", ""))
    return {
        "returncode": item.get("returncode"),
        "stdout_present": bool(stdout),
        "stderr_present": bool(stderr),
        "raw_stdout_committed": False,
        "raw_stderr_committed": False,
        "command_body_committed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/local-activation/actual-local-activation-hard-optin-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    commands = local_report.get("commands", {}) if local_report else {}
    derived = local_report.get("derived", {}) if local_report else {}

    status = run_cmd(["systemextensionsctl", "list"]) if shutil.which("systemextensionsctl") else {
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "systemextensionsctl not found",
    }

    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))
    private_raw_detected = private_raw_detected or has_private_text(status.get("stdout")) or has_private_text(status.get("stderr"))

    activation_command = commands.get("submit_activation", {})
    status_text = str(status.get("stdout", "")) + "\n" + str(status.get("stderr", ""))
    status_tokens = sanitize_status_tokens(status_text)

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_ACTIVATION_REPORT_STATUS_SANITIZER",
        "sanitizer_only": True,
        "host_report_bundle_local_only": True,
        "local_activation_report_present": local_report is not None,
        "local_activation_decision": local_report.get("decision") if local_report else "NO_LOCAL_ACTIVATION_REPORT_PRESENT",
        "hard_optin_ok": bool(local_report and local_report.get("hard_optin_ok") is True),
        "local_scope_ok": bool(local_report and local_report.get("local_scope_ok") is True),
        "activation_preflight_ready": bool(local_report and local_report.get("activation_preflight_ready") is True),
        "activation_submitted_locally": bool(local_report and local_report.get("activation_submitted") is True),
        "activation_command_returncode": activation_command.get("returncode"),
        "activation_command_completed": bool(activation_command and activation_command.get("returncode") == 0),
        "systemextensionsctl_available": bool(status.get("available")),
        "systemextensionsctl_returncode": status.get("returncode"),
        "extension_identifier": EXT_ID,
        "extension_identifier_observed_in_status": EXT_ID in status_text,
        "system_extension_status_tokens": status_tokens,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "command_body_not_committed": True,
        "signing_identity_not_committed": True,
        "entitlement_dump_body_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "activation_submitted_by_sanitizer": False,
        "deactivation_submitted_by_sanitizer": False,
        "install_attempted": False,
        "dext_load_attempted_by_sanitizer": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "dock_transparency_blur_proof_claimed": False,
        "sanitized_command_summary": {
            name: summarize_command(item)
            for name, item in commands.items()
        },
        "derived": {
            "build_activation_capable_host_ok": bool(derived.get("build_activation_capable_host_ok")),
            "resign_embedded_dext_ok": bool(derived.get("resign_embedded_dext_ok")),
            "verify_embedded_dext_ok": bool(derived.get("verify_embedded_dext_ok")),
            "resign_host_app_ok": bool(derived.get("resign_host_app_ok")),
            "verify_host_app_ok": bool(derived.get("verify_host_app_ok")),
            "activation_request_was_submitted_by_host": bool(derived.get("activation_request_was_submitted_by_host")),
            "provider_open_still_blocked": bool(derived.get("provider_open_still_blocked", True)),
            "bar_mapping_still_blocked": bool(derived.get("bar_mapping_still_blocked", True)),
            "gpu_command_submission_still_blocked": bool(derived.get("gpu_command_submission_still_blocked", True)),
            "dock_transparency_blur_proof_still_blocked": bool(derived.get("dock_transparency_blur_proof_still_blocked", True)),
        },
        "next_gate": "dext_load_and_provider_match_status_sanitizer",
    }

    json_path = out_dir / "local-activation-report-status-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{name}` | `{item['returncode']}` | `{item['stdout_present']}` | `{item['stderr_present']}` |"
        for name, item in summary["sanitized_command_summary"].items()
    ) or "| `none` | `—` | `False` | `False` |"

    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["derived"].items())
    status_rows = "\n".join(f"| `{t}` |" for t in status_tokens) or "| `none` |"

    md = f"""# Local Activation Report + System Extension Status Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Sanitizer Only: `True`
- Host Report Bundle Local Only: `True`
- Local Activation Report Present: `{summary['local_activation_report_present']}`
- Local Activation Decision: `{summary['local_activation_decision']}`
- Hard Opt-In OK: `{summary['hard_optin_ok']}`
- Local Scope OK: `{summary['local_scope_ok']}`
- Activation Preflight Ready: `{summary['activation_preflight_ready']}`
- Activation Submitted Locally: `{summary['activation_submitted_locally']}`
- Activation Command Return Code: `{summary['activation_command_returncode']}`
- Activation Command Completed: `{summary['activation_command_completed']}`
- Systemextensionsctl Available: `{summary['systemextensionsctl_available']}`
- Systemextensionsctl Return Code: `{summary['systemextensionsctl_returncode']}`
- Extension Identifier Observed In Status: `{summary['extension_identifier_observed_in_status']}`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Activation Submitted By Sanitizer: `False`
- Deactivation Submitted By Sanitizer: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Dock Transparency Blur Proof Claimed: `False`

## System Extension Status Tokens

| Token |
| --- |
{status_rows}

## Sanitized Command Summary

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
{cmd_rows}

## Derived Runtime Boundary

| Key | Value |
| --- | --- |
{derived_rows}
"""
    md_path = out_dir / "local-activation-report-status-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_LOCAL_ACTIVATION_REPORT_STATUS_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
