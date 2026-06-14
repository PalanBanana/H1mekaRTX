#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_apple_team_capability_evidence_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"Apple Development:[^\n\r]+"),
    re.compile(r"Developer ID Application:[^\n\r]+"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

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
    parser.add_argument("--input", default="host-report-bundle/local-apple-team-capability-evidence/local-apple-team-capability-evidence-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local = read_json(root / args.input)
    commands = local.get("commands", {}) if local else {}

    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_evidence_report_present": local is not None,
        "local_evidence_decision": local.get("decision") if local else "NO_LOCAL_EVIDENCE_REPORT_PRESENT",
        "xcode_present": bool(local and local.get("xcode_present")),
        "driverkit_sdk_present": bool(local and local.get("driverkit_sdk_present")),
        "macosx_sdk_present": bool(local and local.get("macosx_sdk_present")),
        "apple_development_identity_present": bool(local and local.get("apple_development_identity_present")),
        "xcode_project_present": bool(local and local.get("xcode_project_present")),
        "phase60q_hardblock_check_present": bool(local and local.get("phase60q_hardblock_check_present")),
        "phase60r_checklist_check_present": bool(local and local.get("phase60r_checklist_check_present")),
        "previous_build_log_present": bool(local and local.get("previous_build_log_present")),
        "personal_team_blocker_observed": bool(local and local.get("personal_team_blocker_observed")),
        "system_extension_capability_blocker_observed": bool(local and local.get("system_extension_capability_blocker_observed")),
        "driverkit_enable_blocker_observed": bool(local and local.get("driverkit_enable_blocker_observed")),
        "host_profile_missing_observed": bool(local and local.get("host_profile_missing_observed")),
        "dext_profile_missing_observed": bool(local and local.get("dext_profile_missing_observed")),
        "paid_team_proven": bool(local and local.get("paid_team_proven")),
        "driverkit_entitlement_approval_proven": bool(local and local.get("driverkit_entitlement_approval_proven")),
        "pci_transport_entitlement_approval_proven": bool(local and local.get("pci_transport_entitlement_approval_proven")),
        "system_extension_capability_proven": bool(local and local.get("system_extension_capability_proven")),
        "phase61_allowed_now": False,
        "provider_open_allowed_now": False,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "xcodebuild_build_attempted_by_this_phase": False,
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
        "remediation": {
            "next_gate_if_paid_team_and_entitlements_proven": "rerun_phase60l_real_driverkit_dext_build_gate",
            "next_gate_if_not_proven": "wait_for_paid_team_and_apple_entitlement_approval"
        }
    }

    json_path = out_dir / "local-apple-team-capability-evidence-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    keys = [
        "xcode_present",
        "driverkit_sdk_present",
        "macosx_sdk_present",
        "apple_development_identity_present",
        "xcode_project_present",
        "personal_team_blocker_observed",
        "system_extension_capability_blocker_observed",
        "driverkit_enable_blocker_observed",
        "host_profile_missing_observed",
        "dext_profile_missing_observed",
        "paid_team_proven",
        "driverkit_entitlement_approval_proven",
        "pci_transport_entitlement_approval_proven",
        "system_extension_capability_proven",
        "phase61_allowed_now",
    ]
    rows = "\n".join(f"| `{k}` | `{summary.get(k)}` |" for k in keys)

    md = f"""# Local Apple Team Capability Evidence Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Evidence Report Present: `{summary['local_evidence_report_present']}`
- Phase 61 Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Evidence

| Key | Value |
| --- | --- |
{rows}

## Remediation

- If paid team and entitlements are proven: `rerun_phase60l_real_driverkit_dext_build_gate`
- If not proven: `wait_for_paid_team_and_apple_entitlement_approval`
"""
    (out_dir / "local-apple-team-capability-evidence-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'local-apple-team-capability-evidence-summary.md'}")
    print("Decision: PASS_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
