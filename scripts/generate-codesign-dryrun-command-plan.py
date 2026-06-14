#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.codesign_dryrun_command_plan_generated.v1"

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json"
    manifest = read_json(manifest_path)

    planned_commands = manifest.get("planned_commands", [])
    generated = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_CODESIGN_DRYRUN_COMMAND_PLAN",
        "command_plan_only": True,
        "codesign_executed": False,
        "codesign_signing_attempted": False,
        "signed_package_created": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "planned_order": manifest.get("planned_order", []),
        "planned_commands": planned_commands,
        "derived": {
            "command_count": len(planned_commands),
            "all_commands_marked_execute_now_false": all(cmd.get("execute_now") is False for cmd in planned_commands),
            "contains_sign_embedded_dext": any(cmd.get("name") == "sign_embedded_dext" for cmd in planned_commands),
            "contains_verify_embedded_dext": any(cmd.get("name") == "verify_embedded_dext" for cmd in planned_commands),
            "contains_sign_host_app": any(cmd.get("name") == "sign_host_app" for cmd in planned_commands),
            "contains_verify_host_app": any(cmd.get("name") == "verify_host_app" for cmd in planned_commands),
            "contains_entitlement_dump": any(cmd.get("name") == "dump_host_entitlements" for cmd in planned_commands) and any(cmd.get("name") == "dump_dext_entitlements" for cmd in planned_commands),
            "contains_systemextensionsctl_status_capture": any(cmd.get("name") == "capture_systemextensionsctl_status_before_activation" for cmd in planned_commands),
        }
    }

    json_path = out_dir / "codesign-dryrun-command-plan.json"
    json_path.write_text(json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command_rows = "\n".join(
        f"| `{cmd.get('name')}` | `{cmd.get('execute_now')}` | `{ ' '.join(cmd.get('command', [])) }` |"
        for cmd in planned_commands
    )
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in generated["derived"].items())

    md = f"""# Codesign Dry-Run Command Plan

- Generated At UTC: `{generated['generated_at_utc']}`
- Command Plan Only: `True`
- Codesign Executed: `False`
- Codesign Signing Attempted: `False`
- Signed Package Created: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Planned Commands

| Name | Execute Now | Command |
| --- | --- | --- |
{command_rows}

## Derived

| Key | Value |
| --- | --- |
{derived_rows}
"""
    md_path = out_dir / "codesign-dryrun-command-plan.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_CODESIGN_DRYRUN_COMMAND_PLAN_GENERATED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
