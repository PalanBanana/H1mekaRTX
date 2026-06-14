#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.signed_artifact_verification_report_sanitizer_check.v1"

FORBIDDEN_PATTERNS = {
    "raw_stdout_key": re.compile(r'"stdout"\s*:'),
    "raw_stderr_key": re.compile(r'"stderr"\s*:'),
    "command_key": re.compile(r'"command"\s*:'),
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "developer_id_application": re.compile(r"Developer ID Application:[^\n\r]+"),
    "apple_development": re.compile(r"Apple Development:[^\n\r]+"),
    "host_report_bundle_raw_path": re.compile(r"host-report-bundle/local-signing/actual-local-signing-hard-optin-report\.json"),
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "tools/driverkit-buildable-scaffold/signed-artifact-verification-report-sanitizer.json"
    summary_json_path = root / "release-readiness/signed-artifact-verification-report-summary.json"
    summary_md_path = root / "release-readiness/signed-artifact-verification-report-summary.md"
    doc_path = root / "docs/driverkit/signed-artifact-verification-report-sanitizer.md"
    phase54_path = root / "tools/driverkit-buildable-scaffold/actual-local-signing-hard-optin.json"

    manifest = read_json(manifest_path)
    summary = read_json(summary_json_path)
    phase54 = read_json(phase54_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("summary_json_exists", summary_json_path.exists(), str(summary_json_path)),
        make_check("summary_md_exists", summary_md_path.exists(), str(summary_md_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("phase54_manifest_exists", phase54_path.exists(), str(phase54_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.signed_artifact_verification_report_sanitizer.v1"), "manifest schema"),
        make_check("summary_schema", bool(summary and summary.get("schema") == "h1mekartx.signed_artifact_verification_report_summary.v1"), "summary schema"),
        make_check("phase54_schema", bool(phase54 and phase54.get("schema") == "h1mekartx.actual_local_signing_hard_optin.v1"), "phase54 schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("summary", summary)]:
        for field in [
            "raw_stdout_not_committed",
            "raw_stderr_not_committed",
            "signing_identity_not_committed",
            "entitlement_dump_body_not_committed",
        ]:
            checks.append(make_check(f"{obj_name}_{field}_true", bool(obj and obj.get(field) is True), field))

        for field in [
            "codesign_executed_by_sanitizer",
            "codesign_signing_attempted_by_sanitizer",
            "signed_package_created_by_sanitizer",
            "install_attempted",
            "submit_activation_allowed_now",
            "system_extension_activation_attempted",
            "system_extension_deactivation_attempted",
            "dext_load_attempted",
            "provider_open_attempted",
            "bar_mapping_attempted",
            "bar_mmio_mutation_attempted",
            "configuration_writes_attempted",
            "gpu_command_submission_attempted",
            "ui_compositor_proof_claimed",
            "metal_proof_claimed",
        ]:
            checks.append(make_check(f"{obj_name}_{field}_false", bool(obj and obj.get(field) is False), field))

    sanitized_commands = summary.get("sanitized_commands", {}) if summary else {}
    checks.append(make_check("sanitized_commands_present_or_no_report", isinstance(sanitized_commands, dict), "sanitized commands dict"))

    for name, value in sanitized_commands.items():
        checks.append(make_check(f"{name}_raw_stdout_not_committed", value.get("raw_stdout_committed") is False, name))
        checks.append(make_check(f"{name}_raw_stderr_not_committed", value.get("raw_stderr_committed") is False, name))
        checks.append(make_check(f"{name}_command_body_not_committed", value.get("command_body_committed") is False, name))

    boundary = summary.get("boundary_summary", {}) if summary else {}
    for field in [
        "activation_still_blocked",
        "provider_open_still_blocked",
        "bar_mapping_still_blocked",
        "gpu_command_submission_still_blocked",
    ]:
        checks.append(make_check(f"boundary_{field}_true", bool(boundary.get(field)), field))

    for path in [summary_json_path, summary_md_path]:
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        for name, pattern in FORBIDDEN_PATTERNS.items():
            checks.append(make_check(f"no_{name}_in_{path.name}", not pattern.search(text), name))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER_READY" if failed == 0 else "FAIL_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER",
        "local_report_sanitizer_only": True,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "signing_identity_not_committed": True,
        "entitlement_dump_body_not_committed": True,
        "codesign_executed_by_sanitizer": False,
        "codesign_signing_attempted_by_sanitizer": False,
        "signed_package_created_by_sanitizer": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "signed-artifact-verification-report-sanitizer-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Signed Artifact Verification Report Sanitizer Check

- Decision: `{decision}`
- Local Report Sanitizer Only: `True`
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

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "signed-artifact-verification-report-sanitizer-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
