#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_compositor_scenario_matrix_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX",
    "CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA",
    "CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE",
    "CLASSIFICATION_STATIC_CONTRACT",
    "UI_COMPOSITOR_SCENARIO_MATRIX_ONLY: True",
    "UI_COMPOSITOR_PROOF_NOT_CLAIMED: True",
    "METAL_PROOF_NOT_CLAIMED: True",
    "DOCK_ACCELERATION_NOT_CLAIMED: True",
    "TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True",
    "BLUR_ACCELERATION_NOT_CLAIMED: True",
    "MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True",
    "LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True",
    "STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True",
    "SCENARIO_MATRIX_ONLY: True",
    "OBJECTIVE_METRICS_REQUIRED: True",
    "BEFORE_AFTER_BASELINE_REQUIRED: True",
    "WINDOWSERVER_ATTRIBUTION_REQUIRED: True",
    "CORE_ANIMATION_QUARTZCORE_EVIDENCE_REQUIRED: True",
    "METAL_COMPOSITOR_EVIDENCE_REQUIRED: True",
    "REAL_GPU_COMMAND_EVIDENCE_REQUIRED: True",
    "RTX5070_WORKLOAD_ATTRIBUTION_REQUIRED: True",
    "NO_DIRECT_DOCK_INJECTION: True",
    "NO_WINDOWSERVER_PATCHING: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "UI_COMPOSITOR_SCENARIOS",
    "Per-Scenario Required Evidence",
    "UI_COMPOSITOR_SCENARIO_MATRIX_DEPENDENCY_CHAIN",
    "Dock magnification",
    "Dock hide/show",
    "transparency",
    "blur",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "UI_COMPOSITOR_SCENARIO_MATRIX_STATE: MATRIX_ONLY",
    "UI_COMPOSITOR_PROOF_PRECONDITION_STATE: PRECONDITIONS_INCOMPLETE",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
    "DOCK_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "TRANSPARENCY_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "BLUR_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "MISSION_CONTROL_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "LAUNCHPAD_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "STAGE_MANAGER_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
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

REQUIRED_EVIDENCE_ITEMS = {
    "repeatable interaction procedure",
    "before baseline",
    "after candidate run",
    "objective frame pacing metric",
    "objective latency metric",
    "WindowServer attribution evidence",
    "Core Animation / QuartzCore evidence",
    "Metal compositor evidence",
    "real GPU command evidence",
    "RTX 5070 workload attribution evidence",
    "rollback evidence",
    "no spoofing / no patching evidence",
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check UI compositor scenario matrix.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "ui-compositor-scenario-matrix.md"
    matrix_path = root / "tools" / "driverkit-activation" / "ui-compositor-scenario-matrix.json"
    preconditions_path = root / "tools" / "driverkit-activation" / "ui-compositor-proof-preconditions.json"
    firmware_gate_path = root / "tools" / "driverkit-activation" / "firmware-reset-display-init-prohibition-gate.json"
    gpu_gate_path = root / "tools" / "driverkit-activation" / "gpu-command-submission-prohibition-gate.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("scenario_matrix_json_exists", matrix_path.exists(), str(matrix_path)),
        make_check("ui_compositor_preconditions_json_exists", preconditions_path.exists(), str(preconditions_path)),
        make_check("firmware_reset_display_gate_json_exists", firmware_gate_path.exists(), str(firmware_gate_path)),
        make_check("gpu_command_gate_json_exists", gpu_gate_path.exists(), str(gpu_gate_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        checks.append(make_check("requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower(), token in contract_text, token))

    matrix = read_json(matrix_path)
    preconditions = read_json(preconditions_path)
    firmware_gate = read_json(firmware_gate_path)
    gpu_gate = read_json(gpu_gate_path)

    checks.append(make_check("matrix_schema_matches", bool(matrix and matrix.get("schema") == "h1mekartx.ui_compositor_scenario_matrix.v1"), "matrix schema"))
    checks.append(make_check("matrix_only_true", bool(matrix and matrix.get("scenario_matrix_only") is True), "scenario_matrix_only=true"))
    checks.append(make_check("ui_compositor_not_claimed", bool(matrix and matrix.get("ui_compositor_proof_not_claimed") is True), "UI compositor proof not claimed"))
    checks.append(make_check("metal_not_claimed", bool(matrix and matrix.get("metal_proof_not_claimed") is True), "Metal proof not claimed"))
    checks.append(make_check("preconditions_incomplete", bool(matrix and matrix.get("ui_compositor_proof_precondition_state") == "PRECONDITIONS_INCOMPLETE"), "PRECONDITIONS_INCOMPLETE"))
    checks.append(make_check("preconditions_schema_loaded", bool(preconditions and preconditions.get("schema") == "h1mekartx.ui_compositor_proof_preconditions.v1"), "preconditions schema"))
    checks.append(make_check("firmware_gate_enforced", bool(firmware_gate and firmware_gate.get("firmware_reset_display_init_prohibition_state") == "ENFORCED"), "firmware gate enforced"))
    checks.append(make_check("gpu_gate_enforced", bool(gpu_gate and gpu_gate.get("gpu_command_submission_prohibition_state") == "ENFORCED"), "GPU gate enforced"))

    scenarios = matrix.get("scenarios", []) if matrix else []
    scenario_names = {s.get("name") for s in scenarios}
    checks.append(make_check("required_scenarios_present", REQUIRED_SCENARIOS.issubset(scenario_names), ",".join(sorted(scenario_names))))

    for scenario in scenarios:
        name = scenario.get("name", "unknown")
        evidence = set(scenario.get("required_evidence", []))
        checks.append(make_check(f"scenario_{name}_not_attempted", scenario.get("proof_state") == "NOT_ATTEMPTED", name))
        checks.append(make_check(f"scenario_{name}_not_claimed", scenario.get("acceleration_claimed") is False, name))
        checks.append(make_check(f"scenario_{name}_required_evidence_complete", REQUIRED_EVIDENCE_ITEMS.issubset(evidence), name))
        checks.append(make_check(f"scenario_{name}_requires_windowserver", scenario.get("requires_windowserver_attribution") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_metal", scenario.get("requires_metal_compositor_evidence") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_real_gpu_command", scenario.get("requires_real_gpu_command_evidence") is True, name))
        checks.append(make_check(f"scenario_{name}_requires_rtx5070", scenario.get("requires_rtx5070_workload_attribution") is True, name))

    for field in [
        "ui_compositor_proof_state",
        "metal_proof_state",
        "dock_acceleration_proof_state",
        "transparency_acceleration_proof_state",
        "blur_acceleration_proof_state",
        "mission_control_acceleration_proof_state",
        "launchpad_acceleration_proof_state",
        "stage_manager_acceleration_proof_state",
        "real_gpu_command_execution_proof_state",
        "rtx5070_workload_attribution_proof_state",
    ]:
        checks.append(make_check(f"matrix_{field}_not_attempted", bool(matrix and matrix.get(field) == "NOT_ATTEMPTED"), f"{field}=NOT_ATTEMPTED"))

    for field in [
        "real_gpu_command_execution_attempted",
        "rtx5070_workload_attribution_claimed",
        "real_gpu_acceleration_claimed",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"matrix_{field}_false", bool(matrix and matrix.get(field) is False), f"{field}=false"))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_COMPOSITOR_SCENARIO_MATRIX_READY" if failed_count == 0 else "FAIL_UI_COMPOSITOR_SCENARIO_MATRIX"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX",
        "secondary_classification": "CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 33 UI compositor scenario matrix",
        "ui_compositor_scenario_matrix_only": True,
        "scenario_matrix_only": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "mission_control_acceleration_not_claimed": True,
        "launchpad_acceleration_not_claimed": True,
        "stage_manager_acceleration_not_claimed": True,
        "ui_compositor_scenario_matrix_state": "MATRIX_ONLY",
        "ui_compositor_proof_precondition_state": "PRECONDITIONS_INCOMPLETE",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "ui-compositor-scenario-matrix-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# UI Compositor Scenario Matrix Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Scenario Matrix Only: `{report['scenario_matrix_only']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Dock Acceleration Not Claimed: `{report['dock_acceleration_not_claimed']}`
- Transparency Acceleration Not Claimed: `{report['transparency_acceleration_not_claimed']}`
- Blur Acceleration Not Claimed: `{report['blur_acceleration_not_claimed']}`
- Mission Control Acceleration Not Claimed: `{report['mission_control_acceleration_not_claimed']}`
- Launchpad Acceleration Not Claimed: `{report['launchpad_acceleration_not_claimed']}`
- Stage Manager Acceleration Not Claimed: `{report['stage_manager_acceleration_not_claimed']}`
- UI Compositor Scenario Matrix State: `{report['ui_compositor_scenario_matrix_state']}`
- UI Compositor Proof Precondition State: `{report['ui_compositor_proof_precondition_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Timing

Phase 33 defines the UI compositor scenario matrix only.

No Dock/transparency/blur/Mission Control/Launchpad/Stage Manager acceleration is claimed.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds a UI compositor scenario matrix only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "ui-compositor-scenario-matrix-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
