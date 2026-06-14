#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_delegate_diagnostics_remediation_summary.v1"

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
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        obj, _end = decoder.raw_decode(text.lstrip())
        if isinstance(obj, dict):
            return obj
        raise

def has_private_text(value: str) -> bool:
    return any(p.search(str(value or "")) for p in PRIVATE_PATTERNS)

def command_summary(cmd: dict | None) -> dict:
    cmd = cmd or {}
    stdout = str(cmd.get("stdout", ""))
    stderr = str(cmd.get("stderr", ""))
    return {
        "returncode": cmd.get("returncode"),
        "stdout_present": bool(stdout),
        "stderr_present": bool(stderr),
        "raw_stdout_committed": False,
        "raw_stderr_committed": False,
        "command_body_committed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/activation-delegate-diagnostics/activation-delegate-error-diagnostics-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    commands = local_report.get("commands", {}) if local_report else {}
    derived = local_report.get("derived", {}) if local_report else {}
    delegate = local_report.get("delegate", {}) if local_report else {}

    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))

    extension_observed = bool(local_report and local_report.get("extension_identifier_observed") is True)
    activation_submitted = bool(local_report and local_report.get("activation_submitted") is True)
    delegate_did_finish = bool(delegate.get("did_finish"))
    delegate_did_fail = bool(delegate.get("did_fail"))
    delegate_needs_user_approval = bool(delegate.get("needs_user_approval"))
    delegate_timeout = bool(delegate.get("delegate_timeout"))
    delegate_error_text_present = bool(delegate.get("error_text_present"))

    if extension_observed:
        next_gate = "rerun_phase58_phase59_phase60a_phase60b_then_phase61_if_ready"
        remediation_reason = "extension_identifier_observed"
    elif delegate_needs_user_approval:
        next_gate = "approve_system_extension_in_system_settings_then_rerun_phase60d_phase60e"
        remediation_reason = "needs_user_approval"
    elif delegate_did_fail:
        next_gate = "phase60g_activation_error_remediation_plan"
        remediation_reason = "delegate_did_fail"
    elif delegate_timeout:
        next_gate = "phase60h_activation_timeout_host_lifecycle_remediation"
        remediation_reason = "delegate_timeout"
    elif delegate_did_finish and not extension_observed:
        next_gate = "phase60i_bundle_identifier_container_install_location_remediation"
        remediation_reason = "delegate_finished_but_extension_not_visible"
    elif activation_submitted and not extension_observed:
        next_gate = "phase60h_activation_timeout_host_lifecycle_remediation"
        remediation_reason = "activation_submitted_but_no_delegate_visibility"
    else:
        next_gate = "phase60g_activation_error_remediation_plan"
        remediation_reason = "insufficient_delegate_evidence"

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_ACTIVATION_DELEGATE_DIAGNOSTICS_REMEDIATION_GATE",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_delegate_report_present": local_report is not None,
        "local_delegate_decision": local_report.get("decision") if local_report else "NO_LOCAL_DELEGATE_REPORT_PRESENT",
        "activation_submitted_locally": activation_submitted,
        "extension_identifier_observed": extension_observed,
        "status_tokens": local_report.get("status_tokens", []) if local_report else [],
        "delegate_did_finish": delegate_did_finish,
        "delegate_did_fail": delegate_did_fail,
        "delegate_needs_user_approval": delegate_needs_user_approval,
        "delegate_timeout": delegate_timeout,
        "delegate_error_text_present": delegate_error_text_present,
        "delegate_error_domain": delegate.get("error_domain", "none"),
        "delegate_error_code": delegate.get("error_code", "none"),
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
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
        "sanitized_commands": {name: command_summary(cmd) for name, cmd in commands.items()},
        "derived": {
            "build_delegate_diagnostics_host_ok": bool(derived.get("build_delegate_diagnostics_host_ok")),
            "resign_embedded_dext_ok": bool(derived.get("resign_embedded_dext_ok")),
            "verify_embedded_dext_ok": bool(derived.get("verify_embedded_dext_ok")),
            "resign_host_app_ok": bool(derived.get("resign_host_app_ok")),
            "verify_host_app_ok": bool(derived.get("verify_host_app_ok")),
            "delegate_did_finish": bool(derived.get("delegate_did_finish")),
            "delegate_did_fail": bool(derived.get("delegate_did_fail")),
            "delegate_needs_user_approval": bool(derived.get("delegate_needs_user_approval")),
            "delegate_timeout": bool(derived.get("delegate_timeout")),
            "delegate_error_text_present": bool(derived.get("delegate_error_text_present")),
            "extension_visibility_observed_after_delegate": bool(derived.get("extension_visibility_observed_after_delegate")),
            "provider_open_still_blocked": bool(derived.get("provider_open_still_blocked", True)),
            "ioserviceopen_still_blocked": bool(derived.get("ioserviceopen_still_blocked", True)),
            "bar_mapping_still_blocked": bool(derived.get("bar_mapping_still_blocked", True)),
            "gpu_command_submission_still_blocked": bool(derived.get("gpu_command_submission_still_blocked", True)),
            "dock_transparency_blur_proof_still_blocked": bool(derived.get("dock_transparency_blur_proof_still_blocked", True)),
        },
        "remediation": {
            "reason": remediation_reason,
            "next_gate": next_gate,
            "phase61_allowed_now": False,
            "provider_open_allowed_now": False,
            "bar_mapping_allowed_now": False,
            "gpu_command_submission_allowed_now": False
        }
    }

    json_path = out_dir / "activation-delegate-diagnostics-remediation-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{name}` | `{item['returncode']}` | `{item['stdout_present']}` | `{item['stderr_present']}` |"
        for name, item in summary["sanitized_commands"].items()
    ) or "| `none` | `—` | `False` | `False` |"

    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["derived"].items())
    remediation_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["remediation"].items())

    md = f"""# Activation Delegate Diagnostics Remediation Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Local Delegate Report Present: `{summary['local_delegate_report_present']}`
- Local Delegate Decision: `{summary['local_delegate_decision']}`
- Activation Submitted Locally: `{summary['activation_submitted_locally']}`
- Extension Identifier Observed: `{summary['extension_identifier_observed']}`
- Delegate Did Finish: `{summary['delegate_did_finish']}`
- Delegate Did Fail: `{summary['delegate_did_fail']}`
- Delegate Needs User Approval: `{summary['delegate_needs_user_approval']}`
- Delegate Timeout: `{summary['delegate_timeout']}`
- Delegate Error Text Present: `{summary['delegate_error_text_present']}`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Sanitized Commands

| Command | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- |
{cmd_rows}

## Derived

| Key | Value |
| --- | --- |
{derived_rows}

## Remediation

| Key | Value |
| --- | --- |
{remediation_rows}
"""
    md_path = out_dir / "activation-delegate-diagnostics-remediation-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_ACTIVATION_DELEGATE_REMEDIATION_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
