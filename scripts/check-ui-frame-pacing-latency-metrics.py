#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_frame_pacing_latency_metrics_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA",
    "CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA",
    "CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX",
    "CLASSIFICATION_STATIC_CONTRACT",
    "UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_ONLY: True",
    "METRIC_SCHEMA_ONLY: True",
    "MEASUREMENT_NOT_COLLECTED: True",
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
    "UI_FRAME_PACING_LATENCY_METRIC_BUCKETS",
    "UI_FRAME_PACING_LATENCY_REQUIRED_FIELDS",
    "UI_FRAME_PACING_LATENCY_SCENARIOS",
    "VALID_UI_FRAME_PACING_LATENCY_METRIC_STATES",
    "UI_FRAME_PACING_LATENCY_DEPENDENCY_CHAIN",
    "frame_interval_ms_average",
    "frame_interval_ms_p95",
    "frame_time_ms_p99",
    "dropped_frame_count",
    "latency_ms_average",
    "latency_ms_p95",
    "baseline_candidate_delta_percent",
    "WindowServer_attribution_reference",
    "Core_Animation_QuartzCore_attribution_reference",
    "Metal_compositor_attribution_reference",
    "real_GPU_command_evidence_reference",
    "RTX5070_workload_attribution_reference",
    "Dock magnification",
    "transparency",
    "blur",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_STATE: SCHEMA_ONLY",
    "UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED",
    "WINDOWSERVER_ATTRIBUTION_SCHEMA_STATE: SCHEMA_ONLY",
    "WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

REQUIRED_SCENARIOS = {
    "Dock magnification",
    "Dock hide/show",
    "transparency",
    "blur",
    "menu bar translucency",
    "window movement",
    "window resizing",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "desktop space switching",
}

REQUIRED_FIELDS = {
    "scenario_name",
    "measurement_state",
    "baseline_reference",
    "candidate_reference",
    "sample_duration_seconds",
    "display_refresh_hz",
    "frame_interval_ms_average",
    "frame_interval_ms_p50",
    "frame_interval_ms_p95",
    "frame_interval_ms_p99",
    "frame_time_ms_average",
    "frame_time_ms_p50",
    "frame_time_ms_p95",
    "frame_time_ms_p99",
    "dropped_frame_count",
    "hitch_count",
    "latency_ms_average",
    "latency_ms_p95",
    "jitter_ms",
    "baseline_candidate_delta_percent",
    "trace_or_recording_reference",
    "WindowServer_attribution_reference",
    "Core_Animation_QuartzCore_attribution_reference",
    "Metal_compositor_attribution_reference",
    "real_GPU_command_evidence_reference",
    "RTX5070_workload_attribution_reference",
    "rollback_reference",
    "spoofing_or_patching_absent",
}

VALID_STATES = {
    "NOT_ATTEMPTED",
    "BLOCKED",
    "SCHEMA_ONLY",
    "BASELINE_PENDING",
    "CANDIDATE_PENDING",
    "MEASURED",
    "ATTRIBUTED",
    "PROVEN",
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check UI frame pacing / latency metric schema.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "ui-frame-pacing-latency-metrics.md"
    metrics_path = root / "tools" / "driverkit-activation" / "ui-frame-pacing-latency-metrics.json"
    attribution_path = root / "tools" / "driverkit-activation" / "windowserver-ca-quartzcore-attribution.json"
    scenario_path = root / "tools" / "driverkit-activation" / "ui-compositor-scenario-matrix.json"
    preconditions_path = root / "tools" / "driverkit-activation" / "ui-compositor-proof-preconditions.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("metrics_schema_json_exists", metrics_path.exists(), str(metrics_path)),
        make_check("attribution_schema_json_exists", attribution_path.exists(), str(attribution_path)),
        make_check("scenario_matrix_json_exists", scenario_path.exists(), str(scenario_path)),
        make_check("preconditions_json_exists", preconditions_path.exists(), str(preconditions_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        checks.append(make_check("requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower(), token in contract_text, token))

    metrics = read_json(metrics_path)
    attribution = read_json(attribution_path)
    scenario_matrix = read_json(scenario_path)
    preconditions = read_json(preconditions_path)

    checks.append(make_check("metrics_schema_matches", bool(metrics and metrics.get("schema") == "h1mekartx.ui_frame_pacing_latency_metrics.v1"), "metrics schema"))
    checks.append(make_check("metric_schema_only_true", bool(metrics and metrics.get("metric_schema_only") is True), "metric_schema_only=true"))
    checks.append(make_check("measurement_not_collected", bool(metrics and metrics.get("measurement_not_collected") is True), "measurement_not_collected=true"))
    checks.append(make_check("measurement_state_not_attempted", bool(metrics and metrics.get("ui_frame_pacing_latency_measurement_state") == "NOT_ATTEMPTED"), "NOT_ATTEMPTED"))
    checks.append(make_check("attribution_schema_loaded", bool(attribution and attribution.get("schema") == "h1mekartx.windowserver_ca_quartzcore_attribution.v1"), "attribution schema"))
    checks.append(make_check("scenario_matrix_loaded", bool(scenario_matrix and scenario_matrix.get("schema") == "h1mekartx.ui_compositor_scenario_matrix.v1"), "scenario matrix"))
    checks.append(make_check("preconditions_loaded", bool(preconditions and preconditions.get("schema") == "h1mekartx.ui_compositor_proof_preconditions.v1"), "preconditions"))

    states = set(metrics.get("valid_metric_states", [])) if metrics else set()
    checks.append(make_check("valid_metric_states_match", states == VALID_STATES, ",".join(sorted(states))))

    fields = set(metrics.get("required_metric_fields", [])) if metrics else set()
    checks.append(make_check("required_fields_complete", REQUIRED_FIELDS.issubset(fields), ",".join(sorted(fields))))

    scenarios = metrics.get("scenarios", []) if metrics else []
    scenario_names = {s.get("name") for s in scenarios}
    checks.append(make_check("required_scenarios_present", REQUIRED_SCENARIOS.issubset(scenario_names), ",".join(sorted(scenario_names))))

    for scenario in scenarios:
        name = scenario.get("name", "unknown")
        scenario_fields = set(scenario.get("required_metric_fields", []))
        checks.append(make_check(f"scenario_{name}_measurement_not_attempted", scenario.get("measurement_state") == "NOT_ATTEMPTED", name))
        checks.append(make_check(f"scenario_{name}_proof_not_attempted", scenario.get("proof_state") == "NOT_ATTEMPTED", name))
        checks.append(make_check(f"scenario_{name}_not_claimed", scenario.get("acceleration_claimed") is False, name))
        checks.append(make_check(f"scenario_{name}_fields_complete", REQUIRED_FIELDS.issubset(scenario_fields), name))
        checks.append(make_check(f"scenario_{name}_requires_baseline", scenario.get("requires_before_after_baseline") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_frame_pacing", scenario.get("requires_objective_frame_pacing") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_latency", scenario.get("requires_latency_metric") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_windowserver", scenario.get("requires_windowserver_attribution") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_metal", scenario.get("requires_metal_compositor_attribution") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_gpu_command", scenario.get("requires_real_gpu_command_evidence") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_rtx5070", scenario.get("requires_rtx5070_workload_attribution") is True, name))

    for field in [
        "ui_compositor_proof_state",
        "metal_proof_state",
        "real_gpu_command_execution_proof_state",
        "rtx5070_workload_attribution_proof_state",
        "windowserver_attribution_proof_state",
        "core_animation_attribution_proof_state",
        "quartzcore_attribution_proof_state",
        "metal_compositor_attribution_proof_state",
    ]:
        checks.append(make_check(f"metrics_{field}_not_attempted", bool(metrics and metrics.get(field) == "NOT_ATTEMPTED"), f"{field}=NOT_ATTEMPTED"))

    for field in [
        "real_gpu_command_execution_attempted",
        "rtx5070_workload_attribution_claimed",
        "real_gpu_acceleration_claimed",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"metrics_{field}_false", bool(metrics and metrics.get(field) is False), f"{field}=false"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_READY" if failed_count == 0 else "FAIL_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA",
        "secondary_classification": "CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 35 UI frame pacing / latency metric schema",
        "ui_frame_pacing_latency_metric_schema_only": True,
        "metric_schema_only": True,
        "measurement_not_collected": True,
        "ui_frame_pacing_latency_metric_schema_state": "SCHEMA_ONLY",
        "ui_frame_pacing_latency_measurement_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "ui-frame-pacing-latency-metrics-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# UI Frame Pacing / Latency Metric Schema Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Metric Schema Only: `{report['metric_schema_only']}`
- Measurement Not Collected: `{report['measurement_not_collected']}`
- UI Frame Pacing / Latency Metric Schema State: `{report['ui_frame_pacing_latency_metric_schema_state']}`
- UI Frame Pacing / Latency Measurement State: `{report['ui_frame_pacing_latency_measurement_state']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Timing

Phase 35 defines before/after frame pacing and latency metric schema only.

No UI metric is collected and no Dock/transparency/blur acceleration is claimed.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds UI frame pacing / latency metric schema only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "ui-frame-pacing-latency-metrics-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
