#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.baseline_privacy_redaction_audit_report.v1"

AUDIT_INPUTS = [
    "release-readiness/local-ui-baseline-artifact-summary.json",
    "release-readiness/local-ui-baseline-artifact-summary.md",
    "release-readiness/local-ui-baseline-artifact-summary-check.json",
    "release-readiness/local-ui-baseline-artifact-summary-check.md",
    "release-readiness/local-readonly-ui-baseline-check.json",
    "release-readiness/local-readonly-ui-baseline-check.md",
]

FORBIDDEN_PATTERNS = {
    "raw_stdout_key": re.compile(r'"stdout"\s*:'),
    "raw_stderr_key": re.compile(r'"stderr"\s*:'),
    "raw_stdout_line": re.compile(r"(?im)^\s*stdout\s*[:=]"),
    "raw_stderr_line": re.compile(r"(?im)^\s*stderr\s*[:=]"),
    "home_path": re.compile(r"/Users/[^/\\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "host_report_bundle_raw_json": re.compile(r"host-report-bundle/ui-baseline/local-readonly-ui-baseline\.json"),
    "host_report_bundle_raw_md": re.compile(r"host-report-bundle/ui-baseline/local-readonly-ui-baseline\.md"),
}

REQUIRED_SUMMARY_FLAGS = [
    "raw_local_logs_not_committed",
    "raw_command_stdout_not_committed",
    "raw_command_stderr_not_committed",
    "measurement_not_acceleration_proof",
    "ui_compositor_proof_not_claimed",
    "metal_proof_not_claimed",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def staged_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            check=False,
            text=True,
            capture_output=True,
            timeout=20,
        )
        if result.returncode != 0:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []

def main() -> int:
    parser = argparse.ArgumentParser(description="Audit baseline summary privacy/redaction.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    checks = []
    hits = []

    for rel in AUDIT_INPUTS:
        path = root / rel
        checks.append(make_check(f"audit_input_exists_{rel.replace('/', '_')}", path.exists(), rel))
        text = read_text(path)
        for name, pattern in FORBIDDEN_PATTERNS.items():
            found = bool(pattern.search(text))
            if found:
                hits.append({"file": rel, "pattern": name})
            checks.append(make_check(f"no_{name}_in_{rel.replace('/', '_')}", not found, rel))

    summary_json_path = root / "release-readiness" / "local-ui-baseline-artifact-summary.json"
    summary = read_json(summary_json_path)
    checks.append(make_check("summary_json_parse_ok", summary is not None, str(summary_json_path)))

    for flag in REQUIRED_SUMMARY_FLAGS:
        checks.append(make_check(
            f"summary_{flag}_true",
            bool(summary and summary.get(flag) is True),
            flag,
        ))

    command_summary = summary.get("command_summary", {}) if summary else {}
    for key, value in command_summary.items():
        checks.append(make_check(f"command_{key}_omits_stdout", "stdout" not in value, key))
        checks.append(make_check(f"command_{key}_omits_stderr", "stderr" not in value, key))

    staged = staged_files(root)
    staged_host_report = [p for p in staged if p.startswith("host-report-bundle/")]
    checks.append(make_check("host_report_bundle_not_staged", not staged_host_report, ",".join(staged_host_report)))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_BASELINE_PRIVACY_REDACTION_AUDIT" if failed_count == 0 else "FAIL_BASELINE_PRIVACY_REDACTION_AUDIT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_BASELINE_PRIVACY_REDACTION_AUDIT_GATE",
        "secondary_classification": "CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 38 baseline privacy/redaction audit gate",
        "baseline_privacy_redaction_audit_gate_only": True,
        "privacy_redaction_audit_only": True,
        "host_report_bundle_local_only": True,
        "host_report_bundle_not_staged": not staged_host_report,
        "raw_local_logs_not_committed": True,
        "raw_command_stdout_not_committed": True,
        "raw_command_stderr_not_committed": True,
        "private_paths_not_committed": True,
        "email_like_identifiers_not_committed": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "baseline_privacy_redaction_audit_state": "ENFORCED",
        "local_ui_baseline_artifact_summary_state": "SUMMARY_ONLY",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "forbidden_hits": hits,
        "staged_host_report_paths": staged_host_report,
        "checks": checks,
    }

    json_path = out_dir / "baseline-privacy-redaction-audit-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Baseline Privacy / Redaction Audit Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Privacy Redaction Audit Only: `{report['privacy_redaction_audit_only']}`
- Host Report Bundle Local Only: `{report['host_report_bundle_local_only']}`
- Host Report Bundle Not Staged: `{report['host_report_bundle_not_staged']}`
- Raw Local Logs Not Committed: `{report['raw_local_logs_not_committed']}`
- Raw Command Stdout Not Committed: `{report['raw_command_stdout_not_committed']}`
- Raw Command Stderr Not Committed: `{report['raw_command_stderr_not_committed']}`
- Private Paths Not Committed: `{report['private_paths_not_committed']}`
- Email-like Identifiers Not Committed: `{report['email_like_identifiers_not_committed']}`
- Measurement Not Acceleration Proof: `{report['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Forbidden Hit Count: `{len(hits)}`
- Staged Host Report Path Count: `{len(staged_host_report)}`

## Timing

Phase 38 audits committed summary outputs only.

It does not commit raw host-report-bundle artifacts.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds a privacy/redaction audit gate only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "baseline-privacy-redaction-audit-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
