#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_ui_baseline_artifact_summary_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER",
    "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
    "CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA",
    "CLASSIFICATION_STATIC_CONTRACT",
    "LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER_ONLY: True",
    "LOCAL_BASELINE_SUMMARY_ONLY: True",
    "HOST_REPORT_BUNDLE_LOCAL_ONLY: True",
    "RAW_LOCAL_LOGS_NOT_COMMITTED: True",
    "RAW_COMMAND_STDOUT_NOT_COMMITTED: True",
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
    "LOCAL_UI_BASELINE_SUMMARIZER_INPUTS",
    "COMMITTED_SUMMARY_OUTPUTS",
    "LOCAL_OUTPUTS_IGNORED_BY_GIT",
    "LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_BUCKETS",
    "LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_STATE: SUMMARY_ONLY",
    "UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED",
    "WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

REQUIRED_COMMAND_KEYS = {
    "sw_vers",
    "uname",
    "system_profiler_displays_json",
    "system_profiler_hardware_json",
    "ioreg_display_connect",
    "ioreg_framebuffer",
    "process_table",
    "windowserver_recent_log",
    "dock_recent_log",
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check local UI baseline artifact summary.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "local-ui-baseline-artifact-summarizer.md"
    manifest_path = root / "tools" / "driverkit-activation" / "local-ui-baseline-artifact-summarizer.json"
    summary_path = root / "release-readiness" / "local-ui-baseline-artifact-summary.json"
    summary_md_path = root / "release-readiness" / "local-ui-baseline-artifact-summary.md"
    baseline_path = root / "host-report-bundle" / "ui-baseline" / "local-readonly-ui-baseline.json"
    collector_manifest_path = root / "tools" / "driverkit-activation" / "local-readonly-ui-baseline-collector.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("summarizer_manifest_json_exists", manifest_path.exists(), str(manifest_path)),
        make_check("summary_json_exists", summary_path.exists(), str(summary_path)),
        make_check("summary_md_exists", summary_md_path.exists(), str(summary_md_path)),
        make_check("local_baseline_input_exists", baseline_path.exists(), str(baseline_path)),
        make_check("collector_manifest_exists", collector_manifest_path.exists(), str(collector_manifest_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        checks.append(make_check("requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower(), token in contract_text, token))

    manifest = read_json(manifest_path)
    summary = read_json(summary_path)
    collector_manifest = read_json(collector_manifest_path)

    checks.append(make_check("manifest_schema_matches", bool(manifest and manifest.get("schema") == "h1mekartx.local_ui_baseline_artifact_summarizer.v1"), "manifest schema"))
    checks.append(make_check("summary_schema_matches", bool(summary and summary.get("schema") == "h1mekartx.local_ui_baseline_artifact_summary.v1"), "summary schema"))
    checks.append(make_check("collector_manifest_loaded", bool(collector_manifest and collector_manifest.get("schema") == "h1mekartx.local_readonly_ui_baseline_collector.v1"), "collector manifest"))

    for name, obj in [("manifest", manifest), ("summary", summary)]:
        checks.append(make_check(f"{name}_summary_only", bool(obj and obj.get("local_baseline_summary_only") is True), "summary only"))
        checks.append(make_check(f"{name}_host_report_local_only", bool(obj and obj.get("host_report_bundle_local_only") is True), "host report local only"))
        checks.append(make_check(f"{name}_raw_logs_not_committed", bool(obj and obj.get("raw_local_logs_not_committed") is True), "raw logs not committed"))
        checks.append(make_check(f"{name}_raw_stdout_not_committed", bool(obj and obj.get("raw_command_stdout_not_committed") is True), "raw stdout not committed"))
        checks.append(make_check(f"{name}_not_acceleration_proof", bool(obj and obj.get("measurement_not_acceleration_proof") is True), "not acceleration proof"))
        checks.append(make_check(f"{name}_ui_not_claimed", bool(obj and obj.get("ui_compositor_proof_not_claimed") is True), "UI proof not claimed"))
        checks.append(make_check(f"{name}_metal_not_claimed", bool(obj and obj.get("metal_proof_not_claimed") is True), "Metal proof not claimed"))

    command_summary = summary.get("command_summary", {}) if summary else {}
    checks.append(make_check("required_command_keys_present", REQUIRED_COMMAND_KEYS.issubset(set(command_summary.keys())), ",".join(sorted(command_summary.keys()))))

    for key, value in command_summary.items():
        checks.append(make_check(f"command_{key}_does_not_include_stdout", "stdout" not in value, key))
        checks.append(make_check(f"command_{key}_does_not_include_stderr", "stderr" not in value, key))

    for field in [
        "ui_frame_pacing_latency_measurement_state",
        "windowserver_attribution_proof_state",
        "core_animation_attribution_proof_state",
        "quartzcore_attribution_proof_state",
        "metal_compositor_attribution_proof_state",
        "ui_compositor_proof_state",
        "metal_proof_state",
        "real_gpu_command_execution_proof_state",
        "rtx5070_workload_attribution_proof_state",
    ]:
        checks.append(make_check(f"summary_{field}_not_attempted", bool(summary and summary.get(field) == "NOT_ATTEMPTED"), f"{field}=NOT_ATTEMPTED"))

    for field in [
        "real_gpu_command_execution_attempted",
        "rtx5070_workload_attribution_claimed",
        "real_gpu_acceleration_claimed",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"summary_{field}_false", bool(summary and summary.get(field) is False), f"{field}=false"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_READY" if failed_count == 0 else "FAIL_LOCAL_UI_BASELINE_ARTIFACT_SUMMARY"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER",
        "secondary_classification": "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 37 local UI baseline artifact summarizer",
        "local_ui_baseline_artifact_summarizer_only": True,
        "local_baseline_summary_only": True,
        "host_report_bundle_local_only": True,
        "raw_local_logs_not_committed": True,
        "raw_command_stdout_not_committed": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "local_ui_baseline_artifact_summary_state": "SUMMARY_ONLY",
        "summary_json_present": summary_path.exists(),
        "local_baseline_input_present": baseline_path.exists(),
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "local-ui-baseline-artifact-summary-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Local UI Baseline Artifact Summary Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Local Baseline Summary Only: `{report['local_baseline_summary_only']}`
- Host Report Bundle Local Only: `{report['host_report_bundle_local_only']}`
- Raw Local Logs Not Committed: `{report['raw_local_logs_not_committed']}`
- Raw Command Stdout Not Committed: `{report['raw_command_stdout_not_committed']}`
- Measurement Not Acceleration Proof: `{report['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Summary JSON Present: `{report['summary_json_present']}`
- Local Baseline Input Present: `{report['local_baseline_input_present']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Timing

Phase 37 summarizes local-only UI baseline artifacts into release-readiness fields.

It does not commit raw local logs or raw command stdout.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds local UI baseline artifact summarization only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "local-ui-baseline-artifact-summary-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
