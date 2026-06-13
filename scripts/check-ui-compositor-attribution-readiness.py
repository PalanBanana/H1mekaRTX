#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_compositor_attribution_readiness.v1"

REQUIRED_TOKENS = [
    "CLASSIFICATION_UI_COMPOSITOR_ATTRIBUTION_READINESS",
    "CLASSIFICATION_GRAPHICS_STACK_DIAGNOSTICS",
    "CLASSIFICATION_STATIC_CONTRACT",
    "OBSERVATION_ONLY: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_DEVICE_OWNERSHIP_REQUEST: True",
    "NO_BAR_MMIO_MUTATION: True",
    "NO_COMMAND_SUBMISSION: True",
    "NO_GSP_FIRMWARE_LOAD: True",
    "NO_GPU_RESET: True",
    "NO_FRAMEBUFFER_INIT: True",
    "NO_DISPLAY_ENGINE_INIT: True",
    "NO_KERNEL_OR_PROCESS_INJECTION: True",
    "NO_SIP_AMFI_BYPASS: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "UI_COMPOSITOR_ATTRIBUTION_REQUIREMENTS",
    "UI_COMPOSITOR_ATTRIBUTION_MATRIX_ROWS",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "IOGraphics",
    "IOAccelerator",
    "IODisplay",
    "Dock",
    "transparency",
    "blur",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
]

MATRIX_ROWS = [
    {
        "name": "WindowServer process visibility",
        "required_for": "UI compositor routing evidence",
        "current_status": "BASELINE_OBSERVABLE_ONLY",
        "promotion_needed": "correlate WindowServer workload with target GPU",
    },
    {
        "name": "Core Animation / QuartzCore evidence path",
        "required_for": "animation and compositor stack evidence",
        "current_status": "EVIDENCE_PATH_DEFINED",
        "promotion_needed": "capture frame timing and compositor routing evidence",
    },
    {
        "name": "Metal compositor visibility",
        "required_for": "Metal-facing compositor path evidence",
        "current_status": "EVIDENCE_PATH_DEFINED",
        "promotion_needed": "prove real target GPU-backed Metal workload",
    },
    {
        "name": "IOGraphics / IOAccelerator / IODisplay hints",
        "required_for": "graphics stack visibility",
        "current_status": "DIAGNOSTIC_HINTS_ONLY",
        "promotion_needed": "tie hints to real runtime workload",
    },
    {
        "name": "RTX 5070 PCI identity",
        "required_for": "target device identity",
        "current_status": "HOST_DIAGNOSTIC_INPUT",
        "promotion_needed": "bind identity to runtime workload evidence",
    },
    {
        "name": "Dock smoothness target",
        "required_for": "user-visible UI goal",
        "current_status": "TARGET_ONLY",
        "promotion_needed": "frame timing plus workload attribution",
    },
    {
        "name": "transparency target",
        "required_for": "user-visible UI goal",
        "current_status": "TARGET_ONLY",
        "promotion_needed": "compositor effect path attribution",
    },
    {
        "name": "blur target",
        "required_for": "user-visible UI goal",
        "current_status": "TARGET_ONLY",
        "promotion_needed": "compositor effect path attribution",
    },
    {
        "name": "Mission Control / Launchpad / Stage Manager targets",
        "required_for": "user-visible UI goal",
        "current_status": "TARGET_ONLY",
        "promotion_needed": "frame timing plus compositor routing evidence",
    },
    {
        "name": "workload attribution blocker",
        "required_for": "UI compositor proof",
        "current_status": "UNPROVEN",
        "promotion_needed": "GPU counters, routing logs, or command evidence",
    },
    {
        "name": "real GPU command execution blocker",
        "required_for": "real GPU work proof",
        "current_status": "NOT_ATTEMPTED",
        "promotion_needed": "safe later-phase command execution proof",
    },
    {
        "name": "UI compositor proof blocker",
        "required_for": "claiming UI acceleration",
        "current_status": "UNPROVEN",
        "promotion_needed": "all higher evidence gates",
    },
    {
        "name": "Metal proof blocker",
        "required_for": "claiming Metal acceleration",
        "current_status": "UNPROVEN",
        "promotion_needed": "real Metal-facing target GPU workload proof",
    },
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def load_optional_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None

def main() -> int:
    parser = argparse.ArgumentParser(description="Check UI compositor attribution readiness matrix contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "ui-compositor-attribution-readiness-matrix.md"
    local_baseline_path = root / "host-report-bundle" / "hackintosh-ui-observability" / "hackintosh-ui-observability-baseline-check.json"

    checks = [make_check("contract_file_exists", contract_path.exists(), str(contract_path))]
    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    optional_baseline = load_optional_json(local_baseline_path)
    checks.append(make_check(
        "optional_local_baseline_json_parseable_or_absent",
        optional_baseline is not None or not local_baseline_path.exists(),
        str(local_baseline_path),
    ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_COMPOSITOR_ATTRIBUTION_READINESS_MATRIX_READY" if failed_count == 0 else "FAIL_UI_COMPOSITOR_ATTRIBUTION_READINESS_MATRIX"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_COMPOSITOR_ATTRIBUTION_READINESS",
        "secondary_classification": "CLASSIFICATION_GRAPHICS_STACK_DIAGNOSTICS",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 6 UI compositor attribution readiness matrix",
        "observation_only": True,
        "hardware_access_attempted": False,
        "driver_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "overall_attribution_state": "UNPROVEN_BLOCKED_BY_MISSING_RUNTIME_AND_WORKLOAD_EVIDENCE",
        "target_user_visible_goal": [
            "smooth Dock animation",
            "working transparency",
            "working blur",
            "smooth window movement and resizing",
            "smooth Mission Control",
            "smooth Launchpad",
            "smooth Stage Manager",
        ],
        "matrix_rows": MATRIX_ROWS,
        "optional_local_baseline_loaded": optional_baseline is not None,
        "checks": checks,
    }

    json_path = out_dir / "ui-compositor-attribution-readiness-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check_rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )
    matrix_rows = "\n".join(
        f"| {row['name']} | {row['required_for']} | {row['current_status']} | {row['promotion_needed']} |"
        for row in MATRIX_ROWS
    )

    md_content = f"""# UI Compositor Attribution Readiness Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Observation Only: `{report['observation_only']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- Real GPU Acceleration Claimed: `{report['real_gpu_acceleration_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`
- Overall Attribution State: `{report['overall_attribution_state']}`

## Target User-Visible UI Goal

This matrix keeps the Hackintosh RTX 5070 macOS UI compositor goal centered:

- Dock animation
- Dock magnification
- transparency
- blur
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager

No UI acceleration success is claimed in this phase.

## Attribution Readiness Matrix

| Evidence Row | Required For | Current Status | Promotion Needed |
| --- | --- | --- | --- |
{matrix_rows}

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Conclusion

RTX 5070 UI compositor attribution remains `UNPROVEN`.

This phase defines what evidence is still missing before any claim about Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, Core Animation, QuartzCore, WindowServer, or Metal compositor acceleration can be made.

## Next Phase Recommendation

Next safe step: prepare a read-only PCI provider matching gate that still avoids driver activation, BAR/MMIO mutation, GPU reset, and command submission.
"""

    md_path = out_dir / "ui-compositor-attribution-readiness-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
