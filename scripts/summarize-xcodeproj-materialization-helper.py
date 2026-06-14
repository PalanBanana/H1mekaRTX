#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.xcodeproj_materialization_helper_summary.v1"

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
    parser.add_argument("--input", default="host-report-bundle/xcodeproj-materialization/xcodeproj-materialization-helper-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    local_report = read_json(root / args.input)

    commands = local_report.get("commands", {}) if local_report else {}
    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_XCODEPROJ_MATERIALIZATION_HELPER",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_materialization_report_present": local_report is not None,
        "local_materialization_decision": local_report.get("decision") if local_report else "NO_LOCAL_MATERIALIZATION_REPORT_PRESENT",
        "mode": local_report.get("mode") if local_report else "none",
        "xcodegen_installed": bool(local_report and local_report.get("xcodegen_installed")),
        "xcodegen_attempted_locally": bool(local_report and local_report.get("xcodegen_attempted")),
        "project_exists_before": bool(local_report and local_report.get("project_exists_before")),
        "project_generated": bool(local_report and local_report.get("project_generated")),
        "project_exists_after": bool(local_report and local_report.get("project_exists_after")),
        "spec_emitted_local_only": bool(local_report and local_report.get("spec_emitted_local_only")),
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "xcodebuild_attempted_by_this_phase": False,
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
            "phase61_allowed_now": False,
            "provider_open_allowed_now": False,
            "next_gate_if_project_exists": "phase60l-real-driverkit-dext-build-gate-local-run",
            "next_gate_if_project_missing": "manual_xcode_creation_or_install_xcodegen"
        }
    }

    json_path = out_dir / "xcodeproj-materialization-helper-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    detail_keys = [
        "local_materialization_report_present",
        "local_materialization_decision",
        "mode",
        "xcodegen_installed",
        "xcodegen_attempted_locally",
        "project_exists_before",
        "project_generated",
        "project_exists_after",
        "spec_emitted_local_only",
    ]
    detail_rows = "\n".join(f"| `{k}` | `{summary.get(k)}` |" for k in detail_keys)

    md = f"""# XcodeProj Materialization Helper Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Project Exists After: `{summary['project_exists_after']}`
- Phase 61 Allowed Now: `False`
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

## Remediation

- If project exists: `phase60l-real-driverkit-dext-build-gate-local-run`
- If project missing: `manual_xcode_creation_or_install_xcodegen`
"""
    (out_dir / "xcodeproj-materialization-helper-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'xcodeproj-materialization-helper-summary.md'}")
    print("Decision: PASS_XCODEPROJ_MATERIALIZATION_HELPER_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
