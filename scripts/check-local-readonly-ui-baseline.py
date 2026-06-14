#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_readonly_ui_baseline_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
    "CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA",
    "CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA",
    "CLASSIFICATION_STATIC_CONTRACT",
    "LOCAL_READONLY_UI_BASELINE_COLLECTOR_ONLY: True",
    "LOCAL_BASELINE_ONLY: True",
    "HOST_REPORT_BUNDLE_LOCAL_ONLY: True",
    "MEASUREMENT_NOT_ACCELERATION_PROOF: True",
    "UI_COMPOSITOR_PROOF_NOT_CLAIMED: True",
    "METAL_PROOF_NOT_CLAIMED: True",
    "DOCK_ACCELERATION_NOT_CLAIMED: True",
    "TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True",
    "BLUR_ACCELERATION_NOT_CLAIMED: True",
    "MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True",
    "LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True",
    "STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True",
    "OBJECTIVE_METRICS_REQUIRED: True",
    "BEFORE_AFTER_BASELINE_REQUIRED: True",
    "WINDOWSERVER_ATTRIBUTION_REQUIRED: True",
    "CORE_ANIMATION_QUARTZCORE_EVIDENCE_REQUIRED: True",
    "METAL_COMPOSITOR_EVIDENCE_REQUIRED: True",
    "REAL_GPU_COMMAND_EVIDENCE_REQUIRED: True",
    "RTX5070_WORKLOAD_ATTRIBUTION_REQUIRED: True",
    "LOCAL_READONLY_UI_BASELINE_COMMANDS",
    "LOCAL_OUTPUTS_IGNORED_BY_GIT",
    "COMMITTED_CHECK_OUTPUTS",
    "LOCAL_READONLY_UI_BASELINE_BUCKETS",
    "WindowServer",
    "Dock",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "LOCAL_READONLY_UI_BASELINE_STATE: COLLECTED_OR_UNAVAILABLE",
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
    parser = argparse.ArgumentParser(description="Check local read-only UI baseline collector.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "local-readonly-ui-baseline-collector.md"
    manifest_path = root / "tools" / "driverkit-activation" / "local-readonly-ui-baseline-collector.json"
    baseline_path = root / "host-report-bundle" / "ui-baseline" / "local-readonly-ui-baseline.json"
    baseline_md_path = root / "host-report-bundle" / "ui-baseline" / "local-readonly-ui-baseline.md"
    metrics_path = root / "tools" / "driverkit-activation" / "ui-frame-pacing-latency-metrics.json"
    attribution_path = root / "tools" / "driverkit-activation" / "windowserver-ca-quartzcore-attribution.json"
    scenario_path = root / "tools" / "driverkit-activation" / "ui-compositor-scenario-matrix.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("collector_manifest_json_exists", manifest_path.exists(), str(manifest_path)),
        make_check("local_baseline_json_exists", baseline_path.exists(), str(baseline_path)),
        make_check("local_baseline_md_exists", baseline_md_path.exists(), str(baseline_md_path)),
        make_check("metrics_schema_json_exists", metrics_path.exists(), str(metrics_path)),
        make_check("attribution_schema_json_exists", attribution_path.exists(), str(attribution_path)),
        make_check("scenario_matrix_json_exists", scenario_path.exists(), str(scenario_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        checks.append(make_check("requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower(), token in contract_text, token))

    manifest = read_json(manifest_path)
    baseline = read_json(baseline_path)
    metrics = read_json(metrics_path)
    attribution = read_json(attribution_path)
    scenario = read_json(scenario_path)

    checks.append(make_check("manifest_schema_matches", bool(manifest and manifest.get("schema") == "h1mekartx.local_readonly_ui_baseline_collector.v1"), "manifest schema"))
    checks.append(make_check("baseline_schema_matches", bool(baseline and baseline.get("schema") == "h1mekartx.local_readonly_ui_baseline_report.v1"), "baseline schema"))
    checks.append(make_check("metrics_schema_loaded", bool(metrics and metrics.get("schema") == "h1mekartx.ui_frame_pacing_latency_metrics.v1"), "metrics schema"))
    checks.append(make_check("attribution_schema_loaded", bool(attribution and attribution.get("schema") == "h1mekartx.windowserver_ca_quartzcore_attribution.v1"), "attribution schema"))
    checks.append(make_check("scenario_matrix_loaded", bool(scenario and scenario.get("schema") == "h1mekartx.ui_compositor_scenario_matrix.v1"), "scenario matrix"))

    for name, obj in [("manifest", manifest), ("baseline", baseline)]:
        checks.append(make_check(f"{name}_local_baseline_only", bool(obj and obj.get("local_baseline_only") is True), "local_baseline_only=true"))
        checks.append(make_check(f"{name}_not_acceleration_proof", bool(obj and obj.get("measurement_not_acceleration_proof") is True), "measurement_not_acceleration_proof=true"))
        checks.append(make_check(f"{name}_ui_not_claimed", bool(obj and obj.get("ui_compositor_proof_not_claimed") is True), "UI proof not claimed"))
        checks.append(make_check(f"{name}_metal_not_claimed", bool(obj and obj.get("metal_proof_not_claimed") is True), "Metal proof not claimed"))

    commands = baseline.get("commands", {}) if baseline else {}
    command_keys = set(commands.keys())
    checks.append(make_check("required_command_keys_present", REQUIRED_COMMAND_KEYS.issubset(command_keys), ",".join(sorted(command_keys))))

    process_visibility = baseline.get("process_visibility", {}) if baseline else {}
    checks.append(make_check("windowserver_visibility_recorded", "WindowServer" in process_visibility, "WindowServer"))
    checks.append(make_check("dock_visibility_recorded", "Dock" in process_visibility, "Dock"))

    for field in [
        "ui_frame_pacing_latency_measurement_state",
        "windowserver_attribution_proof_state",
        "core_animation_attribution_proof_state",
        "quartzcore_attribution_proof_state",
        "metal_compositor_attribution_proof_state",
        "ui_compositor_proof_state",
        "metal_proof_state",
    ]:
        checks.append(make_check(f"baseline_{field}_not_attempted", bool(baseline and baseline.get(field) == "NOT_ATTEMPTED"), f"{field}=NOT_ATTEMPTED"))

    for field in [
        "real_gpu_command_execution_attempted",
        "rtx5070_workload_attribution_claimed",
        "real_gpu_acceleration_claimed",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"baseline_{field}_false", bool(baseline and baseline.get(field) is False), f"{field}=false"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_LOCAL_READONLY_UI_BASELINE_COLLECTOR_READY" if failed_count == 0 else "FAIL_LOCAL_READONLY_UI_BASELINE_COLLECTOR"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
        "secondary_classification": "CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 36 local read-only UI baseline collector",
        "local_readonly_ui_baseline_collector_only": True,
        "local_baseline_only": True,
        "host_report_bundle_local_only": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "local_readonly_ui_baseline_state": "COLLECTED_OR_UNAVAILABLE",
        "ui_frame_pacing_latency_measurement_state": "NOT_ATTEMPTED",
        "windowserver_attribution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "local-readonly-ui-baseline-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Local Read-Only UI Baseline Collector Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Local Baseline Only: `{report['local_baseline_only']}`
- Host Report Bundle Local Only: `{report['host_report_bundle_local_only']}`
- Measurement Not Acceleration Proof: `{report['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Dock Acceleration Not Claimed: `{report['dock_acceleration_not_claimed']}`
- Transparency Acceleration Not Claimed: `{report['transparency_acceleration_not_claimed']}`
- Blur Acceleration Not Claimed: `{report['blur_acceleration_not_claimed']}`
- Local Read-Only UI Baseline State: `{report['local_readonly_ui_baseline_state']}`
- UI Frame Pacing / Latency Measurement State: `{report['ui_frame_pacing_latency_measurement_state']}`
- WindowServer Attribution Proof State: `{report['windowserver_attribution_proof_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Timing

Phase 36 collects local read-only UI baseline information only.

The local host-report-bundle output is intentionally not committed.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds local read-only UI baseline collection only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "local-readonly-ui-baseline-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
