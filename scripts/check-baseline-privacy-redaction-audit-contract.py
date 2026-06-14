#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.baseline_privacy_redaction_audit_contract_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_BASELINE_PRIVACY_REDACTION_AUDIT_GATE",
    "CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER",
    "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
    "CLASSIFICATION_STATIC_CONTRACT",
    "BASELINE_PRIVACY_REDACTION_AUDIT_GATE_ONLY: True",
    "PRIVACY_REDACTION_AUDIT_ONLY: True",
    "HOST_REPORT_BUNDLE_LOCAL_ONLY: True",
    "HOST_REPORT_BUNDLE_NOT_STAGED: True",
    "RAW_LOCAL_LOGS_NOT_COMMITTED: True",
    "RAW_COMMAND_STDOUT_NOT_COMMITTED: True",
    "RAW_COMMAND_STDERR_NOT_COMMITTED: True",
    "PRIVATE_PATHS_NOT_COMMITTED: True",
    "EMAIL_LIKE_IDENTIFIERS_NOT_COMMITTED: True",
    "MEASUREMENT_NOT_ACCELERATION_PROOF: True",
    "UI_COMPOSITOR_PROOF_NOT_CLAIMED: True",
    "METAL_PROOF_NOT_CLAIMED: True",
    "DOCK_ACCELERATION_NOT_CLAIMED: True",
    "TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True",
    "BLUR_ACCELERATION_NOT_CLAIMED: True",
    "WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "BASELINE_PRIVACY_REDACTION_AUDIT_POLICY",
    "BASELINE_PRIVACY_REDACTION_AUDIT_INPUTS",
    "LOCAL_ONLY_PATHS",
    "ALLOWED_SUMMARY_FIELDS",
    "BASELINE_PRIVACY_REDACTION_AUDIT_STATE: ENFORCED",
    "LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_STATE: SUMMARY_ONLY",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check baseline privacy/redaction audit contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "baseline-privacy-redaction-audit.md"
    manifest_path = root / "tools" / "driverkit-activation" / "baseline-privacy-redaction-audit.json"
    audit_report_path = root / "release-readiness" / "baseline-privacy-redaction-audit-check.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("manifest_json_exists", manifest_path.exists(), str(manifest_path)),
        make_check("audit_report_json_exists", audit_report_path.exists(), str(audit_report_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        checks.append(make_check("requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower(), token in contract_text, token))

    manifest = read_json(manifest_path)
    audit_report = read_json(audit_report_path)

    checks.append(make_check("manifest_schema_matches", bool(manifest and manifest.get("schema") == "h1mekartx.baseline_privacy_redaction_audit_gate.v1"), "manifest schema"))
    checks.append(make_check("audit_report_schema_matches", bool(audit_report and audit_report.get("schema") == "h1mekartx.baseline_privacy_redaction_audit_report.v1"), "audit report schema"))

    for name, obj in [("manifest", manifest), ("audit_report", audit_report)]:
        checks.append(make_check(f"{name}_privacy_audit_only", bool(obj and obj.get("privacy_redaction_audit_only") is True), "privacy audit only"))
        checks.append(make_check(f"{name}_host_report_local_only", bool(obj and obj.get("host_report_bundle_local_only") is True), "host report local only"))
        checks.append(make_check(f"{name}_raw_logs_not_committed", bool(obj and obj.get("raw_local_logs_not_committed") is True), "raw logs not committed"))
        checks.append(make_check(f"{name}_raw_stdout_not_committed", bool(obj and obj.get("raw_command_stdout_not_committed") is True), "raw stdout not committed"))
        checks.append(make_check(f"{name}_raw_stderr_not_committed", bool(obj and obj.get("raw_command_stderr_not_committed") is True), "raw stderr not committed"))
        checks.append(make_check(f"{name}_not_acceleration_proof", bool(obj and obj.get("measurement_not_acceleration_proof") is True), "not acceleration proof"))
        checks.append(make_check(f"{name}_ui_not_claimed", bool(obj and obj.get("ui_compositor_proof_not_claimed") is True), "UI not claimed"))
        checks.append(make_check(f"{name}_metal_not_claimed", bool(obj and obj.get("metal_proof_not_claimed") is True), "Metal not claimed"))

    checks.append(make_check("audit_decision_pass", bool(audit_report and audit_report.get("decision") == "PASS_BASELINE_PRIVACY_REDACTION_AUDIT"), "audit decision"))
    checks.append(make_check("forbidden_hits_empty", bool(audit_report and audit_report.get("forbidden_hits") == []), "forbidden hits"))
    checks.append(make_check("staged_host_paths_empty", bool(audit_report and audit_report.get("staged_host_report_paths") == []), "staged host-report-bundle paths"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_BASELINE_PRIVACY_REDACTION_AUDIT_CONTRACT_READY" if failed_count == 0 else "FAIL_BASELINE_PRIVACY_REDACTION_AUDIT_CONTRACT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_BASELINE_PRIVACY_REDACTION_AUDIT_GATE",
        "secondary_classification": "CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 38 baseline privacy/redaction audit contract",
        "baseline_privacy_redaction_audit_gate_only": True,
        "privacy_redaction_audit_only": True,
        "host_report_bundle_local_only": True,
        "raw_local_logs_not_committed": True,
        "raw_command_stdout_not_committed": True,
        "raw_command_stderr_not_committed": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "checks": checks,
    }

    json_path = out_dir / "baseline-privacy-redaction-audit-contract-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Baseline Privacy / Redaction Audit Contract Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Privacy Redaction Audit Only: `{report['privacy_redaction_audit_only']}`
- Host Report Bundle Local Only: `{report['host_report_bundle_local_only']}`
- Raw Local Logs Not Committed: `{report['raw_local_logs_not_committed']}`
- Raw Command Stdout Not Committed: `{report['raw_command_stdout_not_committed']}`
- Raw Command Stderr Not Committed: `{report['raw_command_stderr_not_committed']}`
- Measurement Not Acceleration Proof: `{report['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase verifies the baseline privacy/redaction audit contract. It does not commit raw host-report-bundle artifacts or claim UI compositor acceleration.
"""
    md_path = out_dir / "baseline-privacy-redaction-audit-contract-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
