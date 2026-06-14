#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_proof_promotion_blocker_dashboard_check.v1"

REQUIRED_INPUTS = {
    "dashboard_manifest": "tools/driverkit-activation/ui-proof-promotion-blocker-dashboard.json",
    "ui_evidence_chain_rollup": "tools/driverkit-activation/ui-evidence-chain-rollup.json",
    "ui_evidence_chain_rollup_check": "release-readiness/ui-evidence-chain-rollup-check.json",
    "baseline_privacy_audit": "tools/driverkit-activation/baseline-privacy-redaction-audit.json",
    "baseline_privacy_audit_check": "release-readiness/baseline-privacy-redaction-audit-check.json",
    "activation_ledger": "tools/driverkit-activation/activation-prerequisites-ledger.json",
    "activation_execution_gate": "tools/driverkit-activation/activation-execution-gate.json",
}

REQUIRED_BLOCKER_SUBSTRINGS = [
    "activation prerequisites ledger",
    "System Extension activation proof",
    "System Extension deactivation proof",
    "dext load proof",
    "provider match proof",
    "provider open",
    "BAR mapping",
    "PCI configuration writes",
    "firmware load",
    "GPU reset",
    "framebuffer initialization",
    "display-engine initialization",
    "real GPU command execution",
    "RTX 5070 workload attribution",
    "WindowServer attribution",
    "Core Animation / QuartzCore attribution",
    "Metal compositor attribution",
    "UI frame pacing / latency measurement",
    "before/after UI metric delta",
    "rollback/deactivation evidence",
    "no-spoofing/no-patching proof",
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

def main() -> int:
    parser = argparse.ArgumentParser(description="Check UI proof promotion blocker dashboard.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    loaded = {}
    checks = []

    for key, rel in REQUIRED_INPUTS.items():
        path = root / rel
        obj = read_json(path)
        loaded[key] = obj
        checks.append(make_check(f"input_{key}_exists", path.exists(), rel))
        checks.append(make_check(f"input_{key}_json_parse_ok", obj is not None, rel))

    manifest = loaded.get("dashboard_manifest") or {}
    rollup_check = loaded.get("ui_evidence_chain_rollup_check") or {}
    privacy_check = loaded.get("baseline_privacy_audit_check") or {}
    activation_gate = loaded.get("activation_execution_gate") or {}

    checks.extend([
        make_check("manifest_schema_matches", manifest.get("schema") == "h1mekartx.ui_proof_promotion_blocker_dashboard.v1", "dashboard schema"),
        make_check("promotion_blocked_true", manifest.get("promotion_blocked") is True, "promotion_blocked=true"),
        make_check("ui_promotion_allowed_false", manifest.get("ui_proof_promotion_allowed") is False, "ui promotion false"),
        make_check("dock_promotion_allowed_false", manifest.get("dock_acceleration_promotion_allowed") is False, "dock false"),
        make_check("transparency_promotion_allowed_false", manifest.get("transparency_acceleration_promotion_allowed") is False, "transparency false"),
        make_check("blur_promotion_allowed_false", manifest.get("blur_acceleration_promotion_allowed") is False, "blur false"),
        make_check("metal_promotion_allowed_false", manifest.get("metal_proof_promotion_allowed") is False, "metal false"),
        make_check("ui_not_claimed_true", manifest.get("ui_compositor_proof_not_claimed") is True, "UI proof not claimed"),
        make_check("metal_not_claimed_true", manifest.get("metal_proof_not_claimed") is True, "Metal not claimed"),
        make_check("real_gpu_command_attempted_false", manifest.get("real_gpu_command_execution_attempted") is False, "GPU command false"),
        make_check("rtx5070_claimed_false", manifest.get("rtx5070_workload_attribution_claimed") is False, "RTX attribution false"),
        make_check("rollup_decision_pass", rollup_check.get("decision") == "PASS_UI_EVIDENCE_CHAIN_ROLLUP_READY", "rollup PASS"),
        make_check("privacy_decision_pass", privacy_check.get("decision") == "PASS_BASELINE_PRIVACY_REDACTION_AUDIT", "privacy PASS"),
        make_check("activation_execution_gate_blocks_execute", activation_gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE", "BLOCK_EXECUTE"),
    ])

    blockers = manifest.get("blockers", [])
    checks.append(make_check("blocker_count_at_least_required", len(blockers) >= len(REQUIRED_BLOCKER_SUBSTRINGS), str(len(blockers))))

    joined_blockers = "\n".join(blockers)
    for token in REQUIRED_BLOCKER_SUBSTRINGS:
        checks.append(make_check(f"blocker_contains_{token.lower().replace(' ', '_').replace('/', '_')}", token in joined_blockers, token))

    expected_states = {
        "ui_proof_promotion_blocker_dashboard_state": "BLOCKERS_ENUMERATED",
        "ui_evidence_chain_rollup_state": "ROLLUP_ONLY",
        "baseline_privacy_redaction_audit_state": "ENFORCED",
        "ui_compositor_proof_precondition_state": "PRECONDITIONS_INCOMPLETE",
        "ui_compositor_scenario_matrix_state": "MATRIX_ONLY",
        "windowserver_attribution_schema_state": "SCHEMA_ONLY",
        "ui_frame_pacing_latency_metric_schema_state": "SCHEMA_ONLY",
        "local_ui_baseline_artifact_summary_state": "SUMMARY_ONLY",
        "ui_frame_pacing_latency_measurement_state": "NOT_ATTEMPTED",
        "windowserver_attribution_proof_state": "NOT_ATTEMPTED",
        "core_animation_attribution_proof_state": "NOT_ATTEMPTED",
        "quartzcore_attribution_proof_state": "NOT_ATTEMPTED",
        "metal_compositor_attribution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_proof_state": "NOT_ATTEMPTED",
        "rtx5070_workload_attribution_proof_state": "NOT_ATTEMPTED",
    }

    for key, expected in expected_states.items():
        checks.append(make_check(f"state_{key}_{expected.lower()}", manifest.get(key) == expected, f"{key}={manifest.get(key)}"))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_PROOF_PROMOTION_BLOCKER_DASHBOARD_READY" if failed_count == 0 else "FAIL_UI_PROOF_PROMOTION_BLOCKER_DASHBOARD"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_PROOF_PROMOTION_BLOCKER_DASHBOARD",
        "secondary_classification": "CLASSIFICATION_UI_EVIDENCE_CHAIN_ROLLUP",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 40 UI proof promotion blocker dashboard",
        "ui_proof_promotion_blocker_dashboard_only": True,
        "promotion_blocked": True,
        "ui_proof_promotion_decision": "BLOCK_PROMOTION",
        "ui_proof_promotion_allowed": False,
        "dock_acceleration_promotion_allowed": False,
        "transparency_acceleration_promotion_allowed": False,
        "blur_acceleration_promotion_allowed": False,
        "metal_proof_promotion_allowed": False,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "measurement_not_acceleration_proof": True,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "blockers": blockers,
        "checks": checks,
    }

    json_path = out_dir / "ui-proof-promotion-blocker-dashboard-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    blocker_rows = "\n".join(f"| {idx + 1} | {blocker} |" for idx, blocker in enumerate(blockers))
    check_rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# UI Proof Promotion Blocker Dashboard Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Promotion Decision: `{report['ui_proof_promotion_decision']}`
- UI Proof Promotion Allowed: `{report['ui_proof_promotion_allowed']}`
- Dock Acceleration Promotion Allowed: `{report['dock_acceleration_promotion_allowed']}`
- Transparency Acceleration Promotion Allowed: `{report['transparency_acceleration_promotion_allowed']}`
- Blur Acceleration Promotion Allowed: `{report['blur_acceleration_promotion_allowed']}`
- Metal Proof Promotion Allowed: `{report['metal_proof_promotion_allowed']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Dock Acceleration Not Claimed: `{report['dock_acceleration_not_claimed']}`
- Transparency Acceleration Not Claimed: `{report['transparency_acceleration_not_claimed']}`
- Blur Acceleration Not Claimed: `{report['blur_acceleration_not_claimed']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`

## Promotion Blockers

| # | Blocker |
| ---: | --- |
{blocker_rows}

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Conclusion

This phase adds a UI proof promotion blocker dashboard only. Promotion remains blocked. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "ui-proof-promotion-blocker-dashboard-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
