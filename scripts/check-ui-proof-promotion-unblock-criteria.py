#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_proof_promotion_unblock_criteria_check.v1"

REQUIRED_INPUTS = {
    "criteria": "tools/driverkit-activation/ui-proof-promotion-unblock-criteria.json",
    "phase40_dashboard": "tools/driverkit-activation/ui-proof-promotion-blocker-dashboard.json",
    "phase40_check": "release-readiness/ui-proof-promotion-blocker-dashboard-check.json",
    "phase39_rollup": "tools/driverkit-activation/ui-evidence-chain-rollup.json",
    "activation_ledger": "tools/driverkit-activation/activation-prerequisites-ledger.json",
    "activation_execution_gate": "tools/driverkit-activation/activation-execution-gate.json",
}

REQUIRED_BLOCKER_TOKENS = [
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
    "WindowServer",
    "Core Animation / QuartzCore",
    "Metal compositor",
    "UI frame pacing",
    "before/after UI metric delta",
    "rollback",
]

REQUIRED_ALLOWED_SCOPE_TOKENS = [
    "buildable DriverKit host app scaffold",
    "buildable dext scaffold",
    "deterministic Info.plist generation",
    "deterministic entitlement template validation",
    "official SystemExtensions activation/deactivation wrapper in dry-run mode first",
    "signing identity discovery",
    "entitlement approval evidence collection",
    "provider matching proof collection",
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
    parser = argparse.ArgumentParser(description="Check UI proof promotion unblock criteria contract.")
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

    criteria = loaded.get("criteria") or {}
    phase40 = loaded.get("phase40_dashboard") or {}
    phase40_check = loaded.get("phase40_check") or {}
    activation_gate = loaded.get("activation_execution_gate") or {}

    checks.extend([
        make_check("criteria_schema_matches", criteria.get("schema") == "h1mekartx.ui_proof_promotion_unblock_criteria.v1", "criteria schema"),
        make_check("unblock_criteria_only_true", criteria.get("unblock_criteria_only") is True, "criteria only"),
        make_check("promotion_blocked_true", criteria.get("promotion_blocked") is True, "promotion blocked"),
        make_check("ui_promotion_allowed_false", criteria.get("ui_proof_promotion_allowed") is False, "UI promotion false"),
        make_check("metal_promotion_allowed_false", criteria.get("metal_proof_promotion_allowed") is False, "Metal promotion false"),
        make_check("real_development_allowed_scope_defined", criteria.get("real_development_allowed_scope_defined") is True, "allowed scope"),
        make_check("runtime_access_not_allowed_yet", criteria.get("real_development_runtime_access_not_allowed_yet") is True, "runtime blocked"),
        make_check("phase40_dashboard_loaded", phase40.get("schema") == "h1mekartx.ui_proof_promotion_blocker_dashboard.v1", "phase40"),
        make_check("phase40_check_pass", phase40_check.get("decision") == "PASS_UI_PROOF_PROMOTION_BLOCKER_DASHBOARD_READY", "phase40 check"),
        make_check("activation_gate_blocks_execute", activation_gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE", "BLOCK_EXECUTE"),
    ])

    crit_list = criteria.get("criteria", [])
    checks.append(make_check("criteria_count_at_least_12", len(crit_list) >= 12, str(len(crit_list))))

    joined = json.dumps(crit_list, sort_keys=True)
    for token in REQUIRED_BLOCKER_TOKENS:
        checks.append(make_check(f"criteria_contains_{token.lower().replace(' ', '_').replace('/', '_')}", token in joined, token))

    allowed_scope = criteria.get("real_development_allowed_scope", [])
    joined_scope = "\n".join(allowed_scope)
    for token in REQUIRED_ALLOWED_SCOPE_TOKENS:
        checks.append(make_check(f"allowed_scope_contains_{token.lower().replace(' ', '_').replace('/', '_')}", token in joined_scope, token))

    for entry in crit_list:
        blocker = str(entry.get("blocker", "unknown"))
        checks.append(make_check(f"entry_{blocker[:50]}_has_unblock_requires", bool(entry.get("unblock_requires")), blocker))
        checks.append(make_check(f"entry_{blocker[:50]}_not_proven", entry.get("current_state") in {"BLOCKED", "NOT_ATTEMPTED", "FORBIDDEN"}, blocker))

    for field in [
        "driverkit_activation_attempted",
        "system_extension_activation_attempted",
        "system_extension_deactivation_attempted",
        "dext_load_attempted",
        "provider_open_attempted",
        "bar_mapping_attempted",
        "bar_mmio_mutation_attempted",
        "configuration_writes_attempted",
        "gpu_command_submission_attempted",
        "real_gpu_command_execution_attempted",
        "rtx5070_workload_attribution_claimed",
        "real_gpu_acceleration_claimed",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"criteria_{field}_false", criteria.get(field) is False, field))

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_PROOF_PROMOTION_UNBLOCK_CRITERIA_READY" if failed_count == 0 else "FAIL_UI_PROOF_PROMOTION_UNBLOCK_CRITERIA"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_PROOF_PROMOTION_UNBLOCK_CRITERIA_CONTRACT",
        "secondary_classification": "CLASSIFICATION_UI_PROOF_PROMOTION_BLOCKER_DASHBOARD",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 41 UI proof promotion unblock criteria contract",
        "unblock_criteria_only": True,
        "promotion_blocked": True,
        "ui_proof_promotion_decision": "BLOCK_PROMOTION",
        "ui_proof_promotion_allowed": False,
        "metal_proof_promotion_allowed": False,
        "real_development_allowed_scope_defined": True,
        "real_development_runtime_access_not_allowed_yet": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "criteria_count": len(crit_list),
        "checks": checks,
    }

    json_path = out_dir / "ui-proof-promotion-unblock-criteria-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    criteria_rows = "\n".join(
        f"| {idx + 1} | {entry.get('blocker')} | {entry.get('current_state')} | {len(entry.get('unblock_requires', []))} |"
        for idx, entry in enumerate(crit_list)
    )
    check_rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# UI Proof Promotion Unblock Criteria Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Unblock Criteria Only: `{report['unblock_criteria_only']}`
- Promotion Blocked: `{report['promotion_blocked']}`
- UI Proof Promotion Decision: `{report['ui_proof_promotion_decision']}`
- UI Proof Promotion Allowed: `{report['ui_proof_promotion_allowed']}`
- Metal Proof Promotion Allowed: `{report['metal_proof_promotion_allowed']}`
- Real Development Allowed Scope Defined: `{report['real_development_allowed_scope_defined']}`
- Runtime Access Not Allowed Yet: `{report['real_development_runtime_access_not_allowed_yet']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- Criteria Count: `{report['criteria_count']}`

## Criteria Summary

| # | Blocker | Current State | Required Evidence Count |
| ---: | --- | --- | ---: |
{criteria_rows}

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Conclusion

This phase defines unblock criteria only. Promotion remains blocked. Real development may proceed only inside the allowed build/scaffold/evidence scope, not runtime provider/BAR/MMIO/GPU command/UI acceleration access.
"""
    md_path = out_dir / "ui-proof-promotion-unblock-criteria-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
