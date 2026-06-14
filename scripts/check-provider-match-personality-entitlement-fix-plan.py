#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-personality-entitlement-fix-plan.json"
doc_path = ROOT / "docs/driverkit/provider-match-personality-entitlement-fix-plan.md"
phase60b_path = OUT / "provider-match-repair-readiness-bridge-check.json"
phase60a_path = OUT / "provider-match-evidence-repair-diagnostics-summary.json"

manifest = read_json(manifest_path)
phase60b = read_json(phase60b_path)
phase60a = read_json(phase60a_path)

block_reasons = phase60b.get("block_reasons", []) if phase60b else []
phase60b_ready = bool(phase60b and phase60b.get("provider_match_repair_bridge_ready") is True)

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "phase60b_check_exists", phase60b_path.exists(), str(phase60b_path))
add(checks, "phase60a_summary_exists", phase60a_path.exists(), str(phase60a_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_personality_entitlement_fix_plan.v1"), "manifest schema")
add(checks, "phase60b_schema", bool(phase60b and phase60b.get("schema") == "h1mekartx.provider_match_repair_readiness_bridge_check.v1"), "phase60b schema")
add(checks, "phase60a_schema", bool(phase60a and phase60a.get("schema") == "h1mekartx.provider_match_evidence_repair_diagnostics_summary.v1"), "phase60a schema")

for field in [
    "provider_match_personality_entitlement_fix_plan_ready",
    "fix_plan_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "provider_open_allowed_now",
    "ioserviceopen_allowed_now",
    "bar_mapping_allowed_now",
    "gpu_command_submission_allowed_now",
    "activation_submitted_by_this_phase",
    "deactivation_submitted_by_this_phase",
    "install_attempted",
    "manual_dext_load_attempted",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)

required_fix_areas = [
    "activation host wait/visibility hardening",
    "exact extension identifier confirmation",
    "bundle layout confirmation",
    "IOKit personality confirmation",
    "entitlement confirmation",
    "developer-mode and user approval status confirmation",
]
fix_text = "\n".join(manifest.get("fix_areas", []) if manifest else [])
for item in required_fix_areas:
    add(checks, "fix_area_" + item.replace(" ", "_").replace("/", "_"), item in fix_text, item)

add(checks, "phase60b_currently_blocked", not phase60b_ready, "Phase 60B is blocked")
add(checks, "phase60b_has_extension_status_block_or_other_reason", bool(block_reasons), str(block_reasons))
add(checks, "recommended_next_phase_phase60d", bool(manifest and manifest.get("recommended_next_phase") == "phase60d-activation-wait-system-extension-visibility-hardening"), "Phase 60D")

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PROVIDER_MATCH_PERSONALITY_ENTITLEMENT_FIX_PLAN_READY" if failed == 0 else "FAIL_PROVIDER_MATCH_PERSONALITY_ENTITLEMENT_FIX_PLAN"

report = {
    "schema": "h1mekartx.provider_match_personality_entitlement_fix_plan_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "phase60b_provider_match_repair_bridge_ready": phase60b_ready,
    "phase60b_block_reasons": block_reasons,
    "fix_plan_only": True,
    "provider_open_allowed_now": False,
    "ioserviceopen_allowed_now": False,
    "bar_mapping_allowed_now": False,
    "gpu_command_submission_allowed_now": False,
    "activation_submitted_by_this_phase": False,
    "deactivation_submitted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "recommended_next_phase": "phase60d-activation-wait-system-extension-visibility-hardening",
    "checks": checks,
}

(OUT / "provider-match-personality-entitlement-fix-plan-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
reason_rows = "\n".join(f"| `{r}` |" for r in block_reasons) or "| `none` |"

md = f"""# Provider Match Personality Entitlement Fix Plan Check

- Decision: `{decision}`
- Phase 60B Provider Match Repair Bridge Ready: `{phase60b_ready}`
- Fix Plan Only: `True`
- Provider Open Allowed Now: `False`
- IOServiceOpen Allowed Now: `False`
- BAR Mapping Allowed Now: `False`
- GPU Command Submission Allowed Now: `False`
- Activation Submitted By This Phase: `False`
- Deactivation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Recommended Next Phase: `phase60d-activation-wait-system-extension-visibility-hardening`

## Phase 60B Block Reasons

| Reason |
| --- |
{reason_rows}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "provider-match-personality-entitlement-fix-plan-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
