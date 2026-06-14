#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.validationfailed_root_cause_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"Apple Development:[^\n\r]+"),
    re.compile(r"Developer ID Application:[^\n\r]+"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
        return obj if isinstance(obj, dict) else None

def has_private_text(text: str) -> bool:
    return any(p.search(str(text or "")) for p in PRIVATE_PATTERNS)

def safe_bool_contains(text: str, token: str) -> bool:
    return token.lower() in str(text or "").lower()

def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "returncode": p.returncode,
            "stdout_present": bool(p.stdout),
            "stderr_present": bool(p.stderr),
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
        }
    except Exception as exc:
        return {
            "returncode": None,
            "stdout_present": False,
            "stderr_present": True,
            "stdout": "",
            "stderr": str(exc),
        }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input-root", default="host-report-bundle/validation-failed-diagnostics")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_root = (root / args.input_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    applications_report = read_json(root / "host-report-bundle/applications-location-remediation/applications-location-activation-remediation-report.json")
    delegate = applications_report.get("delegate", {}) if applications_report else {}
    derived = applications_report.get("derived", {}) if applications_report else {}

    file_host = read_text(input_root / "file-host.txt")
    file_dext = read_text(input_root / "file-dext.txt")
    spctl_host = read_text(input_root / "spctl-host.stderr")
    spctl_dext = read_text(input_root / "spctl-dext.stderr")
    spctl_install_host = read_text(input_root / "spctl-install-host.stderr")
    codesign_dext = read_text(input_root / "codesign-display-dext.txt")
    codesign_verify_dext = read_text(input_root / "codesign-verify-dext.stderr")
    codesign_verify_host = read_text(input_root / "codesign-verify-host.stderr")
    sysext_logs = read_text(input_root / "sysext-validation-logs.txt")

    developer_mode = run_cmd(["systemextensionsctl", "developer"], timeout=20)

    raw_combined = "\n".join([
        file_host,
        file_dext,
        spctl_host,
        spctl_dext,
        spctl_install_host,
        codesign_dext,
        codesign_verify_dext,
        codesign_verify_host,
        sysext_logs,
        developer_mode.get("stdout", ""),
        developer_mode.get("stderr", ""),
    ])

    spctl_host_rejected = safe_bool_contains(spctl_host, "rejected") or safe_bool_contains(spctl_install_host, "rejected")
    spctl_dext_rejected = safe_bool_contains(spctl_dext, "rejected")
    apple_development_signature = safe_bool_contains(codesign_dext, "Apple Development")
    codesign_dext_valid = safe_bool_contains(codesign_verify_dext, "valid on disk") and safe_bool_contains(codesign_verify_dext, "satisfies its Designated Requirement")
    codesign_host_valid = safe_bool_contains(codesign_verify_host, "valid on disk") and safe_bool_contains(codesign_verify_host, "satisfies its Designated Requirement")

    driverkit_entitlement_present = safe_bool_contains(codesign_dext, "com.apple.developer.driverkit")
    pci_entitlement_present = safe_bool_contains(codesign_dext, "com.apple.developer.driverkit.transport.pci")
    pci_vendor_present = safe_bool_contains(codesign_dext, "0x10de")
    pci_device_present = safe_bool_contains(codesign_dext, "0x2f04")

    dext_plain_macho = safe_bool_contains(file_dext, "Mach-O 64-bit executable")
    dext_driverkit_binary_proven = safe_bool_contains(codesign_dext, "DriverKit") and not dext_plain_macho is False
    # Keep conservative: the current local diagnostics do not prove an Xcode-built DriverKit IOService binary.
    dext_xcode_driverkit_build_proven = False

    developer_mode_stdout = developer_mode.get("stdout", "") + "\n" + developer_mode.get("stderr", "")
    developer_mode_observed = bool(developer_mode_stdout.strip())
    developer_mode_on = safe_bool_contains(developer_mode_stdout, "on") or safe_bool_contains(developer_mode_stdout, "enabled")

    root_causes = []
    if spctl_host_rejected or spctl_dext_rejected:
        root_causes.append("spctl_rejected_host_or_dext")
    if not developer_mode_on:
        root_causes.append("developer_mode_not_confirmed_on")
    if not dext_xcode_driverkit_build_proven:
        root_causes.append("real_xcode_built_driverkit_dext_binary_not_proven")
    if not driverkit_entitlement_present:
        root_causes.append("driverkit_entitlement_missing_from_signature")
    if not pci_entitlement_present:
        root_causes.append("pci_transport_entitlement_missing_from_signature")
    if driverkit_entitlement_present and pci_entitlement_present:
        root_causes.append("driverkit_entitlements_present_but_os_acceptance_not_proven")
    if apple_development_signature:
        root_causes.append("apple_development_signed_non_notarized_local_build")

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_VALIDATIONFAILED_ROOT_CAUSE_GATE",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_applications_report_present": applications_report is not None,
        "applications_decision": applications_report.get("decision") if applications_report else "NO_APPLICATIONS_REPORT_PRESENT",
        "delegate_error_domain": delegate.get("error_domain", "none"),
        "delegate_error_code": delegate.get("error_code", "none"),
        "delegate_did_fail": bool(delegate.get("did_fail")),
        "delegate_needs_user_approval": bool(delegate.get("needs_user_approval")),
        "extension_identifier_observed": bool(applications_report and applications_report.get("extension_identifier_observed") is True),
        "staged_to_applications": bool(applications_report and applications_report.get("staged_to_applications") is True),
        "activation_submitted": bool(applications_report and applications_report.get("activation_submitted") is True),
        "codesign_host_valid": codesign_host_valid,
        "codesign_dext_valid": codesign_dext_valid,
        "spctl_host_rejected": spctl_host_rejected,
        "spctl_dext_rejected": spctl_dext_rejected,
        "apple_development_signature": apple_development_signature,
        "driverkit_entitlement_present": driverkit_entitlement_present,
        "pci_transport_entitlement_present": pci_entitlement_present,
        "pci_vendor_0x10de_present": pci_vendor_present,
        "pci_device_0x2f04_present": pci_device_present,
        "dext_plain_macho_executable": dext_plain_macho,
        "dext_xcode_driverkit_build_proven": dext_xcode_driverkit_build_proven,
        "developer_mode_observed": developer_mode_observed,
        "developer_mode_on": developer_mode_on,
        "private_raw_detected_locally": has_private_text(raw_combined),
        "private_text_committed": False,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
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
        "derived": {
            "provider_open_still_blocked": bool(derived.get("provider_open_still_blocked", True)),
            "ioserviceopen_still_blocked": bool(derived.get("ioserviceopen_still_blocked", True)),
            "bar_mapping_still_blocked": bool(derived.get("bar_mapping_still_blocked", True)),
            "gpu_command_submission_still_blocked": bool(derived.get("gpu_command_submission_still_blocked", True)),
            "dock_transparency_blur_proof_still_blocked": bool(derived.get("dock_transparency_blur_proof_still_blocked", True)),
        },
        "root_causes": root_causes,
        "remediation": {
            "phase61_allowed_now": False,
            "provider_open_allowed_now": False,
            "next_gate": "phase60l-real-driverkit-dext-build-gate",
            "local_manual_hint": "enable developer mode for local testing and replace generic C stub with a real Xcode-built DriverKit dext target signed with approved entitlements"
        }
    }

    json_path = out_dir / "validationfailed-root-cause-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    root_rows = "\n".join(f"| `{x}` |" for x in root_causes) or "| `none` |"
    bool_keys = [
        "delegate_error_domain",
        "delegate_error_code",
        "staged_to_applications",
        "activation_submitted",
        "codesign_host_valid",
        "codesign_dext_valid",
        "spctl_host_rejected",
        "spctl_dext_rejected",
        "apple_development_signature",
        "driverkit_entitlement_present",
        "pci_transport_entitlement_present",
        "dext_plain_macho_executable",
        "dext_xcode_driverkit_build_proven",
        "developer_mode_on",
    ]
    detail_rows = "\n".join(f"| `{k}` | `{summary.get(k)}` |" for k in bool_keys)

    md = f"""# ValidationFailed Root-Cause Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Applications Decision: `{summary['applications_decision']}`
- Delegate Error Domain: `{summary['delegate_error_domain']}`
- Delegate Error Code: `{summary['delegate_error_code']}`
- Phase 61 Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Details

| Key | Value |
| --- | --- |
{detail_rows}

## Root Causes

| Root Cause |
| --- |
{root_rows}

## Remediation

- Next Gate: `phase60l-real-driverkit-dext-build-gate`
- Local Manual Hint: `enable developer mode for local testing and replace generic C stub with a real Xcode-built DriverKit dext target signed with approved entitlements`
"""
    md_path = out_dir / "validationfailed-root-cause-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_VALIDATIONFAILED_ROOT_CAUSE_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
