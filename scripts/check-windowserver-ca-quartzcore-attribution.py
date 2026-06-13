#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.windowserver_ca_quartzcore_attribution_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA",
    "CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX",
    "CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA",
    "CLASSIFICATION_STATIC_CONTRACT",
    "WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA_ONLY: True",
    "ATTRIBUTION_SCHEMA_ONLY: True",
    "WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True",
    "UI_COMPOSITOR_PROOF_NOT_CLAIMED: True",
    "METAL_PROOF_NOT_CLAIMED: True",
    "WINDOWSERVER_ATTRIBUTION_REQUIRED: True",
    "CORE_ANIMATION_QUARTZCORE_EVIDENCE_REQUIRED: True",
    "METAL_COMPOSITOR_EVIDENCE_REQUIRED: True",
    "REAL_GPU_COMMAND_EVIDENCE_REQUIRED: True",
    "RTX5070_WORKLOAD_ATTRIBUTION_REQUIRED: True",
    "NO_DIRECT_DOCK_INJECTION: True",
    "NO_WINDOWSERVER_PATCHING: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_BUCKETS",
    "WINDOWSERVER_ATTRIBUTION_REQUIRED_FIELDS",
    "CORE_ANIMATION_QUARTZCORE_REQUIRED_FIELDS",
    "METAL_COMPOSITOR_REQUIRED_FIELDS",
    "VALID_ATTRIBUTION_STATES",
    "WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_DEPENDENCY_CHAIN",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "CAMetalLayer",
    "WINDOWSERVER_ATTRIBUTION_SCHEMA_STATE: SCHEMA_ONLY",
    "WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED",
    "CORE_ANIMATION_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED",
    "QUARTZCORE_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_COMPOSITOR_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

VALID_STATES = {
    "NOT_ATTEMPTED",
    "BLOCKED",
    "PRECONDITIONS_INCOMPLETE",
    "CANDIDATE_OBSERVED",
    "ATTRIBUTED",
    "PROVEN",
}

REQUIRED_WINDOWSERVER_FIELDS = {
    "process_name",
    "process_identifier",
    "sample_or_trace_reference",
    "before_baseline_reference",
    "after_candidate_reference",
    "compositor_activity_observed",
    "rtx5070_workload_attribution_state",
    "real_gpu_command_execution_state",
    "ui_scenario_name",
    "frame_pacing_metric",
    "latency_metric",
    "rollback_reference",
    "spoofing_or_patching_absent",
}

REQUIRED_CA_FIELDS = {
    "ca_transaction_observed",
    "quartzcore_layer_activity_observed",
    "layer_tree_or_compositor_reference",
    "metal_layer_or_drawable_reference",
    "blended_transparency_blur_evidence_reference",
    "before_after_delta",
    "objective_metric_reference",
}

REQUIRED_METAL_FIELDS = {
    "metal_device_identity",
    "command_queue_reference",
    "command_buffer_reference",
    "command_execution_reference",
    "drawable_reference",
    "rtx5070_attribution_reference",
    "no_fake_metal_device_spoofing",
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check WindowServer / CA / QuartzCore attribution schema.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "windowserver-ca-quartzcore-attribution.md"
    schema_path = root / "tools" / "driverkit-activation" / "windowserver-ca-quartzcore-attribution.json"
    scenario_path = root / "tools" / "driverkit-activation" / "ui-compositor-scenario-matrix.json"
    preconditions_path = root / "tools" / "driverkit-activation" / "ui-compositor-proof-preconditions.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("attribution_schema_json_exists", schema_path.exists(), str(schema_path)),
        make_check("scenario_matrix_json_exists", scenario_path.exists(), str(scenario_path)),
        make_check("preconditions_json_exists", preconditions_path.exists(), str(preconditions_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        checks.append(make_check("requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower(), token in contract_text, token))

    schema = read_json(schema_path)
    scenario = read_json(scenario_path)
    preconditions = read_json(preconditions_path)

    checks.append(make_check("schema_matches", bool(schema and schema.get("schema") == "h1mekartx.windowserver_ca_quartzcore_attribution.v1"), "schema"))
    checks.append(make_check("schema_only_true", bool(schema and schema.get("attribution_schema_only") is True), "attribution_schema_only=true"))
    checks.append(make_check("windowserver_not_claimed", bool(schema and schema.get("windowserver_attribution_proof_not_claimed") is True), "WindowServer proof not claimed"))
    checks.append(make_check("core_animation_not_claimed", bool(schema and schema.get("core_animation_attribution_proof_not_claimed") is True), "Core Animation proof not claimed"))
    checks.append(make_check("quartzcore_not_claimed", bool(schema and schema.get("quartzcore_attribution_proof_not_claimed") is True), "QuartzCore proof not claimed"))
    checks.append(make_check("metal_compositor_not_claimed", bool(schema and schema.get("metal_compositor_attribution_proof_not_claimed") is True), "Metal compositor proof not claimed"))
    checks.append(make_check("scenario_matrix_loaded", bool(scenario and scenario.get("schema") == "h1mekartx.ui_compositor_scenario_matrix.v1"), "scenario matrix"))
    checks.append(make_check("preconditions_loaded", bool(preconditions and preconditions.get("schema") == "h1mekartx.ui_compositor_proof_preconditions.v1"), "preconditions"))

    states = set(schema.get("valid_attribution_states", [])) if schema else set()
    checks.append(make_check("valid_states_match", states == VALID_STATES, ",".join(sorted(states))))

    checks.append(make_check("windowserver_fields_complete", REQUIRED_WINDOWSERVER_FIELDS.issubset(set(schema.get("windowserver_required_fields", []))) if schema else False, "WindowServer fields"))
    checks.append(make_check("ca_quartzcore_fields_complete", REQUIRED_CA_FIELDS.issubset(set(schema.get("core_animation_quartzcore_required_fields", []))) if schema else False, "CA/QuartzCore fields"))
    checks.append(make_check("metal_fields_complete", REQUIRED_METAL_FIELDS.issubset(set(schema.get("metal_compositor_required_fields", []))) if schema else False, "Metal fields"))

    for field in [
        "windowserver_attribution_proof_state",
        "core_animation_attribution_proof_state",
        "quartzcore_attribution_proof_state",
        "metal_compositor_attribution_proof_state",
        "ui_compositor_proof_state",
        "metal_proof_state",
        "real_gpu_command_execution_proof_state",
        "rtx5070_workload_attribution_proof_state",
    ]:
        checks.append(make_check(f"schema_{field}_not_attempted", bool(schema and schema.get(field) == "NOT_ATTEMPTED"), f"{field}=NOT_ATTEMPTED"))

    for field in [
        "real_gpu_command_execution_attempted",
        "rtx5070_workload_attribution_claimed",
        "real_gpu_acceleration_claimed",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"schema_{field}_false", bool(schema and schema.get(field) is False), f"{field}=false"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA_READY" if failed_count == 0 else "FAIL_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA",
        "secondary_classification": "CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 34 WindowServer / Core Animation / QuartzCore attribution schema",
        "windowserver_ca_quartzcore_attribution_schema_only": True,
        "attribution_schema_only": True,
        "windowserver_attribution_proof_not_claimed": True,
        "core_animation_attribution_proof_not_claimed": True,
        "quartzcore_attribution_proof_not_claimed": True,
        "metal_compositor_attribution_proof_not_claimed": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "windowserver_attribution_schema_state": "SCHEMA_ONLY",
        "windowserver_attribution_proof_state": "NOT_ATTEMPTED",
        "core_animation_attribution_proof_state": "NOT_ATTEMPTED",
        "quartzcore_attribution_proof_state": "NOT_ATTEMPTED",
        "metal_compositor_attribution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "windowserver-ca-quartzcore-attribution-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# WindowServer / Core Animation / QuartzCore Attribution Schema Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Attribution Schema Only: `{report['attribution_schema_only']}`
- WindowServer Attribution Proof Not Claimed: `{report['windowserver_attribution_proof_not_claimed']}`
- Core Animation Attribution Proof Not Claimed: `{report['core_animation_attribution_proof_not_claimed']}`
- QuartzCore Attribution Proof Not Claimed: `{report['quartzcore_attribution_proof_not_claimed']}`
- Metal Compositor Attribution Proof Not Claimed: `{report['metal_compositor_attribution_proof_not_claimed']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- WindowServer Attribution Schema State: `{report['windowserver_attribution_schema_state']}`
- WindowServer Attribution Proof State: `{report['windowserver_attribution_proof_state']}`
- Core Animation Attribution Proof State: `{report['core_animation_attribution_proof_state']}`
- QuartzCore Attribution Proof State: `{report['quartzcore_attribution_proof_state']}`
- Metal Compositor Attribution Proof State: `{report['metal_compositor_attribution_proof_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Timing

Phase 34 defines attribution schema only.

No WindowServer/Core Animation/QuartzCore/Metal compositor attribution proof is claimed.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds WindowServer/Core Animation/QuartzCore/Metal attribution schema only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "windowserver-ca-quartzcore-attribution-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
