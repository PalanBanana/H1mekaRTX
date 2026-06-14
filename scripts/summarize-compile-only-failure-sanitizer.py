#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.compile_only_failure_sanitizer_summary_report.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
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
    parser.add_argument("--input", default="host-report-bundle/compile-only-smoke/compile-only-target-smoke-test.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    commands = local_report.get("commands", {}) if local_report else {}
    plist_results = local_report.get("plist_results", {}) if local_report else {}
    derived = local_report.get("derived", {}) if local_report else {}

    sanitized_commands = {}
    private_leak_detected = False

    for key, item in commands.items():
        stdout = str(item.get("stdout", ""))
        stderr = str(item.get("stderr", ""))
        private_leak_detected = private_leak_detected or has_private_text(stdout) or has_private_text(stderr)
        sanitized_commands[key] = {
            "command_key": key,
            "available": bool(item.get("available")),
            "returncode": item.get("returncode"),
            "failed": item.get("returncode") not in (0, None),
            "stdout_present": bool(stdout),
            "stderr_present": bool(stderr),
            "raw_stdout_committed": False,
            "raw_stderr_committed": False,
        }

    sanitized_plists = {}
    for key, item in plist_results.items():
        sanitized_plists[key] = {
            "present": bool(item.get("present")),
            "parse_ok": bool(item.get("parse_ok")),
            "error_present": bool(item.get("error")),
            "raw_error_committed": False,
        }

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY",
        "secondary_classification": "CLASSIFICATION_COMPILE_ONLY_TARGET_SMOKE_TEST",
        "compile_only_failure_sanitizer_summary_only": True,
        "host_report_bundle_local_only": True,
        "local_input_present": local_report is not None,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_text_detected_in_local_raw_output": private_leak_detected,
        "private_text_committed": False,
        "build_artifact_created": False,
        "signing_attempted": False,
        "install_attempted": False,
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
        "sanitized_plists": sanitized_plists,
        "derived": {
            "compile_only_attempts_recorded": bool(derived.get("compile_only_attempts_recorded")),
            "compile_failures_allowed_at_preflight_stage": bool(derived.get("compile_failures_allowed_at_preflight_stage")),
            "plist_parse_all_ok": bool(derived.get("plist_parse_all_ok")),
            "any_compile_command_failed": any(v["failed"] for v in sanitized_commands.values()),
            "all_raw_output_local_only": True,
        },
    }

    json_path = out_dir / "compile-only-failure-sanitizer-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{key}` | `{value['available']}` | `{value['returncode']}` | `{value['failed']}` | `{value['stdout_present']}` | `{value['stderr_present']}` |"
        for key, value in sanitized_commands.items()
    )
    plist_rows = "\n".join(
        f"| `{key}` | `{value['present']}` | `{value['parse_ok']}` | `{value['error_present']}` |"
        for key, value in sanitized_plists.items()
    )
    derived_text = json.dumps(summary["derived"], indent=2, sort_keys=True)

    md = f"""# Compile-Only Failure Sanitizer Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Compile-Only Failure Sanitizer Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Input Present: `{summary['local_input_present']}`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Private Text Committed: `False`
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

## Sanitized Command Summary

| Command Key | Available | Return Code | Failed | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- | --- |
{cmd_rows}

## Sanitized Plist Summary

| Path | Present | Parse OK | Error Present |
| --- | --- | --- | --- |
{plist_rows}

## Derived Summary

{derived_text}
"""
    md_path = out_dir / "compile-only-failure-sanitizer-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
