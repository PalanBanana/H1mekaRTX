#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.compile_only_failure_sanitizer_summary_check.v1"

FORBIDDEN_PATTERNS = {
    "raw_stdout_key": re.compile(r'"stdout"\s*:'),
    "raw_stderr_key": re.compile(r'"stderr"\s*:'),
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "host_report_bundle_raw_path": re.compile(r"host-report-bundle/compile-only-smoke/compile-only-target-smoke-test\.json"),
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

    manifest_path = root / "tools/driverkit-buildable-scaffold/compile-only-failure-sanitizer-summary.json"
    summary_json_path = root / "release-readiness/compile-only-failure-sanitizer-summary.json"
    summary_md_path = root / "release-readiness/compile-only-failure-sanitizer-summary.md"
    local_input_path = root / "host-report-bundle/compile-only-smoke/compile-only-target-smoke-test.json"

    manifest = read_json(manifest_path)
    summary = read_json(summary_json_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("summary_json_exists", summary_json_path.exists(), str(summary_json_path)),
        make_check("summary_md_exists", summary_md_path.exists(), str(summary_md_path)),
        make_check("local_input_exists", local_input_path.exists(), str(local_input_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.compile_only_failure_sanitizer_summary.v1"), "manifest schema"),
        make_check("summary_schema", bool(summary and summary.get("schema") == "h1mekartx.compile_only_failure_sanitizer_summary_report.v1"), "summary schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("summary", summary)]:
        for field in [
            "raw_stdout_not_committed",
            "raw_stderr_not_committed",
            "host_report_bundle_local_only",
        ]:
            checks.append(make_check(f"{obj_name}_{field}_true", bool(obj and obj.get(field) is True), field))

        for field in [
            "build_artifact_created",
            "signing_attempted",
            "install_attempted",
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
    checks.append(make_check("sanitized_commands_present", bool(sanitized_commands), "sanitized commands"))

    for key, value in sanitized_commands.items():
        checks.append(make_check(f"{key}_raw_stdout_not_committed", value.get("raw_stdout_committed") is False, key))
        checks.append(make_check(f"{key}_raw_stderr_not_committed", value.get("raw_stderr_committed") is False, key))
        checks.append(make_check(f"{key}_returncode_recorded", "returncode" in value, key))
        checks.append(make_check(f"{key}_failed_recorded", "failed" in value, key))

    for rel_path in [
        summary_json_path,
        summary_md_path,
    ]:
        text = rel_path.read_text(encoding="utf-8", errors="replace") if rel_path.exists() else ""
        for name, pattern in FORBIDDEN_PATTERNS.items():
            checks.append(make_check(f"no_{name}_in_{rel_path.name}", not pattern.search(text), name))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY_READY" if failed == 0 else "FAIL_COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY",
        "compile_only_failure_sanitizer_summary_only": True,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "host_report_bundle_local_only": True,
        "build_artifact_created": False,
        "signing_attempted": False,
        "install_attempted": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "compile-only-failure-sanitizer-summary-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    md = f"""# Compile-Only Failure Sanitizer Summary Check

- Decision: `{decision}`
- Compile-Only Failure Sanitizer Summary Only: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Host Report Bundle Local Only: `True`
- Build Artifact Created: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
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
    md_path = out_dir / "compile-only-failure-sanitizer-summary-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
