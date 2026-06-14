#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_evidence_chain_rollup_check.v1"

INPUTS = {
    "ui_preconditions": "tools/driverkit-activation/ui-compositor-proof-preconditions.json",
    "scenario_matrix": "tools/driverkit-activation/ui-compositor-scenario-matrix.json",
    "attribution_schema": "tools/driverkit-activation/windowserver-ca-quartzcore-attribution.json",
    "metric_schema": "tools/driverkit-activation/ui-frame-pacing-latency-metrics.json",
    "baseline_collector": "tools/driverkit-activation/local-readonly-ui-baseline-collector.json",
    "baseline_summary": "tools/driverkit-activation/local-ui-baseline-artifact-summarizer.json",
    "privacy_audit": "tools/driverkit-activation/baseline-privacy-redaction-audit.json",
    "privacy_audit_check": "release-readiness/baseline-privacy-redaction-audit-check.json",
    "privacy_audit_contract_check": "release-readiness/baseline-privacy-redaction-audit-contract-check.json",
}

REQUIRED_TRUE_FLAGS = [
    "ui_compositor_proof_not_claimed",
    "metal_proof_not_claimed",
]

REQUIRED_FALSE_FLAGS = [
    "real_gpu_command_execution_attempted",
    "rtx5070_workload_attribution_claimed",
    "real_gpu_acceleration_claimed",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def state_of(obj: dict | None, key: str, default: str = "UNKNOWN") -> str:
    if not isinstance(obj, dict):
        return default
    return str(obj.get(key, default))

def first_state(default: str, *items: tuple[dict | None, str]) -> str:
    for obj, key in items:
        value = state_of(obj, key, "UNKNOWN")
        if value != "UNKNOWN":
            return value
    return default

def derived_not_attempted_from_claim_flag(obj: dict | None, claim_key: str) -> str:
    if isinstance(obj, dict) and obj.get(claim_key) is False:
        return "NOT_ATTEMPTED"
    return "UNKNOWN"

def main() -> int:
    parser = argparse.ArgumentParser(description="Create UI evidence chain rollup.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    loaded = {}
    checks = []

    for key, rel in INPUTS.items():
        path = root / rel
        obj = read_json(path)
        loaded[key] = obj
        checks.append(make_check(f"input_{key}_exists", path.exists(), rel))
        checks.append(make_check(f"input_{key}_json_parse_ok", obj is not None, rel))

    for key, obj in loaded.items():
        if key.endswith("_check"):
            continue
        for flag in REQUIRED_TRUE_FLAGS:
            checks.append(make_check(f"{key}_{flag}_true", bool(obj and obj.get(flag) is True), flag))
        for flag in REQUIRED_FALSE_FLAGS:
            checks.append(make_check(f"{key}_{flag}_false", bool(obj and obj.get(flag) is False), flag))

    privacy_check = loaded.get("privacy_audit_check")
    privacy_contract = loaded.get("privacy_audit_contract_check")
    checks.append(make_check(
        "privacy_audit_decision_pass",
        bool(privacy_check and privacy_check.get("decision") == "PASS_BASELINE_PRIVACY_REDACTION_AUDIT"),
        "PASS_BASELINE_PRIVACY_REDACTION_AUDIT",
    ))
    checks.append(make_check(
        "privacy_contract_decision_pass",
        bool(privacy_contract and privacy_contract.get("decision") == "PASS_BASELINE_PRIVACY_REDACTION_AUDIT_CONTRACT_READY"),
        "PASS_BASELINE_PRIVACY_REDACTION_AUDIT_CONTRACT_READY",
    ))
    checks.append(make_check(
        "privacy_forbidden_hits_empty",
        bool(privacy_check and privacy_check.get("forbidden_hits") == []),
        "forbidden_hits=[]",
    ))
    checks.append(make_check(
        "privacy_staged_host_report_paths_empty",
        bool(privacy_check and privacy_check.get("staged_host_report_paths") == []),
        "staged_host_report_paths=[]",
    ))

    summary = {
        "ui_compositor_proof_precondition_state": state_of(loaded.get("ui_preconditions"), "ui_compositor_proof_precondition_state"),
        "ui_compositor_scenario_matrix_state": state_of(loaded.get("scenario_matrix"), "ui_compositor_scenario_matrix_state"),
        "windowserver_attribution_schema_state": state_of(loaded.get("attribution_schema"), "windowserver_attribution_schema_state"),
        "ui_frame_pacing_latency_metric_schema_state": state_of(loaded.get("metric_schema"), "ui_frame_pacing_latency_metric_schema_state"),
        "local_readonly_ui_baseline_state": state_of(loaded.get("baseline_collector"), "local_readonly_ui_baseline_state"),
        "local_ui_baseline_artifact_summary_state": state_of(loaded.get("baseline_summary"), "local_ui_baseline_artifact_summary_state"),
        "baseline_privacy_redaction_audit_state": state_of(loaded.get("privacy_audit"), "baseline_privacy_redaction_audit_state"),
        "ui_frame_pacing_latency_measurement_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("metric_schema"), "ui_frame_pacing_latency_measurement_state"),
            (loaded.get("baseline_summary"), "ui_frame_pacing_latency_measurement_state"),
            (loaded.get("baseline_collector"), "ui_frame_pacing_latency_measurement_state"),
        ),
        "windowserver_attribution_proof_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("attribution_schema"), "windowserver_attribution_proof_state"),
            (loaded.get("baseline_summary"), "windowserver_attribution_proof_state"),
            (loaded.get("baseline_collector"), "windowserver_attribution_proof_state"),
        ),
        "core_animation_attribution_proof_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("attribution_schema"), "core_animation_attribution_proof_state"),
            (loaded.get("baseline_summary"), "core_animation_attribution_proof_state"),
            (loaded.get("baseline_collector"), "core_animation_attribution_proof_state"),
        ),
        "quartzcore_attribution_proof_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("attribution_schema"), "quartzcore_attribution_proof_state"),
            (loaded.get("baseline_summary"), "quartzcore_attribution_proof_state"),
            (loaded.get("baseline_collector"), "quartzcore_attribution_proof_state"),
        ),
        "metal_compositor_attribution_proof_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("attribution_schema"), "metal_compositor_attribution_proof_state"),
            (loaded.get("baseline_summary"), "metal_compositor_attribution_proof_state"),
            (loaded.get("baseline_collector"), "metal_compositor_attribution_proof_state"),
        ),
        "ui_compositor_proof_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("ui_preconditions"), "ui_compositor_proof_state"),
            (loaded.get("scenario_matrix"), "ui_compositor_proof_state"),
            (loaded.get("metric_schema"), "ui_compositor_proof_state"),
            (loaded.get("baseline_summary"), "ui_compositor_proof_state"),
        ),
        "metal_proof_state": first_state(
            "NOT_ATTEMPTED",
            (loaded.get("ui_preconditions"), "metal_proof_state"),
            (loaded.get("scenario_matrix"), "metal_proof_state"),
            (loaded.get("metric_schema"), "metal_proof_state"),
            (loaded.get("baseline_summary"), "metal_proof_state"),
        ),
        "real_gpu_command_execution_proof_state": first_state(
            derived_not_attempted_from_claim_flag(loaded.get("ui_preconditions"), "real_gpu_command_execution_attempted"),
            (loaded.get("ui_preconditions"), "real_gpu_command_execution_proof_state"),
            (loaded.get("scenario_matrix"), "real_gpu_command_execution_proof_state"),
            (loaded.get("metric_schema"), "real_gpu_command_execution_proof_state"),
            (loaded.get("baseline_summary"), "real_gpu_command_execution_proof_state"),
        ),
        "rtx5070_workload_attribution_proof_state": first_state(
            derived_not_attempted_from_claim_flag(loaded.get("ui_preconditions"), "rtx5070_workload_attribution_claimed"),
            (loaded.get("ui_preconditions"), "rtx5070_workload_attribution_proof_state"),
            (loaded.get("scenario_matrix"), "rtx5070_workload_attribution_proof_state"),
            (loaded.get("metric_schema"), "rtx5070_workload_attribution_proof_state"),
            (loaded.get("baseline_summary"), "rtx5070_workload_attribution_proof_state"),
        ),
    }

    expected = {
        "ui_compositor_proof_precondition_state": "PRECONDITIONS_INCOMPLETE",
        "ui_compositor_scenario_matrix_state": "MATRIX_ONLY",
        "windowserver_attribution_schema_state": "SCHEMA_ONLY",
        "ui_frame_pacing_latency_metric_schema_state": "SCHEMA_ONLY",
        "local_ui_baseline_artifact_summary_state": "SUMMARY_ONLY",
        "baseline_privacy_redaction_audit_state": "ENFORCED",
        "ui_frame_pacing_latency_measurement_state": "NOT_ATTEMPTED",
        "windowserver_attribution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_proof_state": "NOT_ATTEMPTED",
        "rtx5070_workload_attribution_proof_state": "NOT_ATTEMPTED",
    }

    for key, expected_value in expected.items():
        checks.append(make_check(f"state_{key}_{expected_value.lower()}", summary.get(key) == expected_value, f"{key}={summary.get(key)}"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_EVIDENCE_CHAIN_ROLLUP_READY" if failed_count == 0 else "FAIL_UI_EVIDENCE_CHAIN_ROLLUP"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_EVIDENCE_CHAIN_ROLLUP",
        "secondary_classification": "CLASSIFICATION_BASELINE_PRIVACY_REDACTION_AUDIT_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 39 release-readiness UI evidence chain rollup",
        "ui_evidence_chain_rollup_only": True,
        "release_readiness_rollup_only": True,
        "host_report_bundle_local_only": True,
        "raw_local_logs_not_committed": True,
        "raw_command_stdout_not_committed": True,
        "raw_command_stderr_not_committed": True,
        "private_paths_not_committed": True,
        "email_like_identifiers_not_committed": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "ui_evidence_chain_rollup_state": "ROLLUP_ONLY",
        "chain_summary": summary,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "ui-evidence-chain-rollup-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check_rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    summary_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary.items())

    md = f"""# UI Evidence Chain Rollup Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- UI Evidence Chain Rollup Only: `{report['ui_evidence_chain_rollup_only']}`
- Release Readiness Rollup Only: `{report['release_readiness_rollup_only']}`
- Host Report Bundle Local Only: `{report['host_report_bundle_local_only']}`
- Raw Local Logs Not Committed: `{report['raw_local_logs_not_committed']}`
- Raw Command Stdout Not Committed: `{report['raw_command_stdout_not_committed']}`
- Raw Command Stderr Not Committed: `{report['raw_command_stderr_not_committed']}`
- Measurement Not Acceleration Proof: `{report['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Dock Acceleration Not Claimed: `{report['dock_acceleration_not_claimed']}`
- Transparency Acceleration Not Claimed: `{report['transparency_acceleration_not_claimed']}`
- Blur Acceleration Not Claimed: `{report['blur_acceleration_not_claimed']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Chain Summary

| Evidence Node | State |
| --- | --- |
{summary_rows}

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Conclusion

This phase adds a release-readiness UI evidence chain rollup only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "ui-evidence-chain-rollup-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
