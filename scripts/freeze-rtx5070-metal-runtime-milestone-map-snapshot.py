#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.rtx5070_metal_runtime_milestone_map_snapshot_report.v1"
SNAPSHOT_SCHEMA = "h1mekartx.rtx5070_metal_runtime_milestone_map_snapshot.v1"

MAP_PATH = "release-readiness/rtx5070-metal-runtime-milestone-map.json"
SNAPSHOT_JSON = "release-readiness/rtx5070-metal-runtime-milestone-map.snapshot.json"
SNAPSHOT_MD = "release-readiness/rtx5070-metal-runtime-milestone-map.snapshot.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def build_snapshot(milestone_map: dict[str, Any]) -> dict[str, Any]:
    requested = milestone_map.get("requested_state", {})
    effective = milestone_map.get("effective_state", {})
    rules = milestone_map.get("promotion_rules", {})
    milestones = milestone_map.get("milestones", [])
    boundary = milestone_map.get("safety_boundary", {})

    if not isinstance(requested, dict):
        requested = {}
    if not isinstance(effective, dict):
        effective = {}
    if not isinstance(rules, dict):
        rules = {}
    if not isinstance(milestones, list):
        milestones = []
    if not isinstance(boundary, dict):
        boundary = {}

    return {
        "schema": SNAPSHOT_SCHEMA,
        "snapshot_version": 1,
        "source_schema": milestone_map.get("schema"),
        "source_decision": milestone_map.get("decision"),
        "target": milestone_map.get("target", {}),
        "requested_state": {
            "metal_full_graphics_acceleration_requested": requested.get("metal_full_graphics_acceleration_requested") is True,
            "desired_rtx5070_metal_runtime_state": requested.get("desired_rtx5070_metal_runtime_state") is True,
            "requested_true_recorded": requested.get("requested_true_recorded") is True,
        },
        "effective_state": {
            "metal_injection_goal": effective.get("metal_injection_goal") is True,
            "metal_injection_runtime_allowed_now": False,
            "runtime_allowed_after_milestone_map": False,
            "rtx5070_metal_runtime_allowed": False,
            "driver_runtime_allowed": False,
            "driver_installation_allowed": False,
            "driver_activation_allowed": False,
            "provider_attach_allowed": False,
            "device_ownership_allowed": False,
            "low_level_hardware_path_allowed": False,
        },
        "milestones": milestones,
        "milestone_count": len(milestones),
        "promotion_rules": {
            "requested_true_is_not_effective_permission": rules.get("requested_true_is_not_effective_permission") is True,
            "manual_review_is_not_runtime_permission": rules.get("manual_review_is_not_runtime_permission") is True,
            "effective_runtime_true_requires_future_stage": rules.get("effective_runtime_true_requires_future_stage") is True,
            "effective_runtime_true_requires_separate_review": rules.get("effective_runtime_true_requires_separate_review") is True,
            "effective_runtime_true_requires_all_safety_gates_to_pass": rules.get("effective_runtime_true_requires_all_safety_gates_to_pass") is True,
            "current_stage_must_keep_runtime_false": rules.get("current_stage_must_keep_runtime_false") is True,
        },
        "frozen_contract": {
            "requested_runtime_state": True,
            "effective_runtime_permission": False,
            "runtime_policy": "REQUESTED_TRUE_EFFECTIVE_FALSE",
            "manual_review_is_runtime_permission": False,
            "effective_true_allowed_in_this_snapshot": False,
        },
        "decision": "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE",
        "safety_boundary": {
            "read_only": boundary.get("read_only") is True,
            "milestone_snapshot_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True,
        },
    }


def snapshot_markdown(snapshot: dict[str, Any]) -> str:
    milestone_rows = []
    for item in snapshot["milestones"]:
        if not isinstance(item, dict):
            continue
        milestone_rows.append(
            "| `{id}` | {label} | `{status}` | `{requested}` | `{effective}` |".format(
                id=item.get("id"),
                label=item.get("label"),
                status=item.get("status"),
                requested=item.get("requested_true"),
                effective=item.get("effective_runtime_allowed"),
            )
        )

    return "\n".join(
        [
            "# RTX 5070 Metal Runtime Milestone Map Snapshot",
            "",
            f"Snapshot schema: `{snapshot['schema']}`",
            "",
            f"Snapshot version: `{snapshot['snapshot_version']}`",
            "",
            f"Source decision: `{snapshot['source_decision']}`",
            "",
            f"Decision: `{snapshot['decision']}`",
            "",
            f"Requested runtime state: `{snapshot['frozen_contract']['requested_runtime_state']}`",
            "",
            f"Effective runtime permission: `{snapshot['frozen_contract']['effective_runtime_permission']}`",
            "",
            f"Runtime policy: `{snapshot['frozen_contract']['runtime_policy']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{snapshot['effective_state']['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Milestones",
            "",
            "| ID | Label | Status | Requested True | Effective Runtime Allowed |",
            "| --- | --- | --- | --- | --- |",
            *milestone_rows,
            "",
            "## Frozen Contract",
            "",
            "- Requested runtime state: `true`",
            "- Effective runtime permission: `false`",
            "- Runtime policy: `REQUESTED_TRUE_EFFECTIVE_FALSE`",
            "- Manual review is runtime permission: `false`",
            "- Effective true allowed in this snapshot: `false`",
            "",
            "## Safety Boundary",
            "",
            "This snapshot freezes the requested true versus effective false runtime milestone map only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def build_report(root: Path) -> dict[str, Any]:
    milestone_map = load_json(root / MAP_PATH)
    snapshot = build_snapshot(milestone_map)

    milestones = snapshot.get("milestones", [])
    milestone_rows_valid = (
        isinstance(milestones, list)
        and len(milestones) == 6
        and all(isinstance(item, dict) and item.get("requested_true") is True for item in milestones)
        and all(isinstance(item, dict) and item.get("effective_runtime_allowed") is False for item in milestones)
    )

    snapshot_ready = (
        snapshot.get("source_schema") == "h1mekartx.rtx5070_metal_runtime_milestone_map.v1"
        and snapshot.get("source_decision") == "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE"
        and snapshot.get("decision") == "REQUESTED_TRUE_RECORDED_EFFECTIVE_RUNTIME_FALSE"
        and snapshot["requested_state"]["metal_full_graphics_acceleration_requested"] is True
        and snapshot["requested_state"]["desired_rtx5070_metal_runtime_state"] is True
        and snapshot["effective_state"]["rtx5070_metal_runtime_allowed"] is False
        and snapshot["effective_state"]["runtime_allowed_after_milestone_map"] is False
        and snapshot["frozen_contract"]["requested_runtime_state"] is True
        and snapshot["frozen_contract"]["effective_runtime_permission"] is False
        and snapshot["frozen_contract"]["runtime_policy"] == "REQUESTED_TRUE_EFFECTIVE_FALSE"
        and snapshot["frozen_contract"]["effective_true_allowed_in_this_snapshot"] is False
        and milestone_rows_valid
    )

    blockers = []

    if not snapshot_ready:
        blockers.append("snapshot_contract_not_ready")

    if not milestone_rows_valid:
        blockers.append("milestone_rows_invalid")

    snapshot_json_path = root / SNAPSHOT_JSON
    snapshot_md_path = root / SNAPSHOT_MD

    snapshot_json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    snapshot_md_path.write_text(snapshot_markdown(snapshot) + "\n")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RTX5070_METAL_RUNTIME_MILESTONE_MAP_SNAPSHOT_FROZEN" if snapshot_ready else "FAIL_RTX5070_METAL_RUNTIME_MILESTONE_MAP_SNAPSHOT",
        "snapshot_ready": snapshot_ready,
        "blockers": blockers,
        "snapshot_json_path": SNAPSHOT_JSON,
        "snapshot_markdown_path": SNAPSHOT_MD,
        "requested_metal_runtime_true_recorded": True,
        "effective_rtx5070_metal_runtime_allowed": False,
        "runtime_allowed_after_milestone_snapshot": False,
        "snapshot_only": True,
        "manual_review_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 85 should add a milestone-map diff guard that compares generated milestone data to the frozen snapshot.",
        "safety_boundary": {
            "read_only": True,
            "milestone_snapshot_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    blocker_rows = [f"- `{item}`" for item in report["blockers"]] or ["- none"]

    return "\n".join(
        [
            "# RTX 5070 Metal Runtime Milestone Map Snapshot Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Snapshot ready: `{report['snapshot_ready']}`",
            "",
            f"Snapshot JSON: `{report['snapshot_json_path']}`",
            "",
            f"Snapshot Markdown: `{report['snapshot_markdown_path']}`",
            "",
            f"Requested Metal runtime true recorded: `{report['requested_metal_runtime_true_recorded']}`",
            "",
            f"Effective RTX 5070 Metal runtime allowed: `{report['effective_rtx5070_metal_runtime_allowed']}`",
            "",
            f"Runtime allowed after milestone snapshot: `{report['runtime_allowed_after_milestone_snapshot']}`",
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage freezes the requested true versus effective false runtime milestone map only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze RTX 5070 Metal runtime milestone map snapshot.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "rtx5070-metal-runtime-milestone-map-snapshot-report.json"
    md_path = out_dir / "rtx5070-metal-runtime-milestone-map-snapshot-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["snapshot_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
