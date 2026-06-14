#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.codesign_identity_entitlement_dryrun_check.v1"

FORBIDDEN_PATTERNS = {
    "raw_stdout_key": re.compile(r'"stdout"\s*:'),
    "raw_stderr_key": re.compile(r'"stderr"\s*:'),
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "host_report_bundle_raw_path": re.compile(r"host-report-bundle/codesign-entitlement-dryrun/codesign-identity-entitlement-dryrun\.json"),
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

    manifest_path = root / "tools/driverkit-buildable-scaffold/codesign-identity-entitlement-dryrun-evidence.json"
    local_report_path = root / "host-report-bundle/codesign-entitlement-dryrun/codesign-identity-entitlement-dryrun.json"
    summary_json_path = root / "release-readiness/codesign-identity-entitlement-dryrun-summary.json"
    summary_md_path = root / "release-readiness/codesign-identity-entitlement-dryrun-summary.md"
    doc_path = root / "docs/driverkit/codesign-identity-entitlement-dryrun-evidence.md"

    manifest = read_json(manifest_path)
    local_report = read_json(local_report_path)
    summary = read_json(summary_json_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("local_report_exists", local_report_path.exists(), str(local_report_path)),
        make_check("summary_json_exists", summary_json_path.exists(), str(summary_json_path)),
        make_check("summary_md_exists", summary_md_path.exists(), str(summary_md_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.codesign_identity_entitlement_dryrun_evidence.v1"), "manifest schema"),
        make_check("local_report_schema", bool(local_report and local_report.get("schema") == "h1mekartx.codesign_identity_entitlement_dryrun_local_report.v1"), "local report schema"),
        make_check("summary_schema", bool(summary and summary.get("schema") == "h1mekartx.codesign_identity_entitlement_dryrun_summary.v1"), "summary schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("local_report", local_report), ("summary", summary)]:
        for field in [
            "codesign_signing_attempted",
            "signed_package_created",
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

    derived = summary.get("derived", {}) if summary else {}
    for field in [
        "host_info_parse_ok",
        "dext_info_parse_ok",
        "host_entitlements_parse_ok",
        "dext_entitlements_parse_ok",
        "host_bundle_id_matches",
        "dext_bundle_id_matches",
        "host_system_extension_entitlement_present",
        "dext_driverkit_entitlement_present",
        "dext_pci_transport_entitlement_present",
    ]:
        checks.append(make_check(f"summary_{field}_true", bool(derived.get(field)), field))

    command_summary = summary.get("command_summary", {}) if summary else {}
    checks.append(make_check("command_summary_present", bool(command_summary), "command summary"))

    for key, value in command_summary.items():
        checks.append(make_check(f"{key}_raw_stdout_not_committed", value.get("raw_stdout_committed") is False, key))
        checks.append(make_check(f"{key}_raw_stderr_not_committed", value.get("raw_stderr_committed") is False, key))

    for path in [summary_json_path, summary_md_path]:
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        for name, pattern in FORBIDDEN_PATTERNS.items():
            checks.append(make_check(f"no_{name}_in_{path.name}", not pattern.search(text), name))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_READY" if failed == 0 else "FAIL_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_EVIDENCE",
        "dryrun_evidence_only": True,
        "host_report_bundle_local_only": True,
        "codesign_identity_discovery_attempted": True,
        "codesign_signing_attempted": False,
        "signed_package_created": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "derived": derived,
        "checks": checks,
    }

    json_path = out_dir / "codesign-identity-entitlement-dryrun-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in derived.items())

    md = f"""# Codesign Identity + Entitlement Dry-Run Check

- Decision: `{decision}`
- Dry-Run Evidence Only: `True`
- Host Report Bundle Local Only: `True`
- Codesign Identity Discovery Attempted: `True`
- Codesign Signing Attempted: `False`
- Signed Package Created: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived Summary

| Key | Value |
| --- | --- |
{derived_rows}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "codesign-identity-entitlement-dryrun-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
