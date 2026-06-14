#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/local-signing-run-instructions-identity-selector.json"
doc_path = ROOT / "docs/driverkit/local-signing-run-instructions-identity-selector.md"
selector_path = ROOT / "scripts/select-local-signing-identity.py"
phase56_path = ROOT / "release-readiness/manual-activation-preflight-after-signed-verification-check.json"

def read_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

manifest = read_json(manifest_path)
phase56 = read_json(phase56_path)
selector_text = selector_path.read_text(encoding="utf-8", errors="replace") if selector_path.exists() else ""

checks = []

def add(name: str, ok: bool, detail: str = ""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

add("manifest_exists", manifest_path.exists(), str(manifest_path))
add("doc_exists", doc_path.exists(), str(doc_path))
add("selector_exists", selector_path.exists(), str(selector_path))
add("phase56_check_exists", phase56_path.exists(), str(phase56_path))
add("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_signing_run_instructions_identity_selector.v1"), "manifest schema")
add("phase57a_required_true", bool(manifest and manifest.get("phase57a_required") is True), "phase57a required")
add("phase57b_allowed_now_false", bool(manifest and manifest.get("phase57b_allowed_now") is False), "phase57b blocked")
add("actual_signing_not_executed_by_this_phase", bool(manifest and manifest.get("actual_signing_executed_by_this_phase") is False), "no signing")
add("activation_not_attempted", bool(manifest and manifest.get("activation_attempted") is False), "no activation")
add("selector_uses_security_find_identity", "security" in selector_text and "find-identity" in selector_text and "codesigning" in selector_text, "security find-identity")
add("selector_prints_hard_optin_command", "--i-understand-local-signing" in selector_text and "--output-under-host-report-bundle" in selector_text, "hard opt-in")
add("phase56_blocks_activation_or_missing_signed_proof", bool(phase56 and phase56.get("activation_preflight_ready") is False), "phase56 blocked")

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PHASE57A_LOCAL_SIGNING_IDENTITY_SELECTOR_READY" if failed == 0 else "FAIL_PHASE57A_LOCAL_SIGNING_IDENTITY_SELECTOR"

report = {
    "schema": "h1mekartx.local_signing_run_instructions_identity_selector_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "phase57a_required": True,
    "phase57b_allowed_now": False,
    "actual_signing_executed_by_this_phase": False,
    "activation_attempted": False,
    "install_attempted": False,
    "provider_open_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "checks": checks,
}
(OUT / "local-signing-run-instructions-identity-selector-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Local Signing Run Instructions + Identity Selector Check

- Decision: `{decision}`
- Phase 57A Required: `True`
- Phase 57B Allowed Now: `False`
- Actual Signing Executed By This Phase: `False`
- Activation Attempted: `False`
- Install Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "local-signing-run-instructions-identity-selector-check.md").write_text(md, encoding="utf-8")
print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
