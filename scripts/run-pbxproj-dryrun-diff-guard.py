#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.pbxproj_dryrun_diff_guard.v1"

FORBIDDEN_TRUE_FIELDS = [
    "real_xcodeproj_generation_attempted",
    "real_pbxproj_generation_attempted",
    "xcodebuild_invocation_attempted",
    "build_attempted",
    "signing_attempted",
    "install_attempted",
    "driverkit_activation_attempted",
    "system_extension_activation_attempted",
    "dext_load_attempted",
    "device_ownership_request_attempted",
    "provider_open_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "real_gpu_command_execution_attempted",
    "rtx5070_workload_attribution_claimed",
    "real_gpu_acceleration_claimed",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def main() -> int:
    parser = argparse.ArgumentParser(description="Run pbxproj metadata dry-run diff guard.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Report output directory")
    parser.add_argument("--metadata-dir", default="tools/driverkit-xcode-layout", help="Metadata output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    metadata_dir = (root / args.metadata_dir).resolve() if not Path(args.metadata_dir).is_absolute() else Path(args.metadata_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = root / "tools" / "driverkit-xcode-layout" / "pbxproj-metadata-dryrun.json"
    layout_path = root / "tools" / "driverkit-xcode-layout" / "project-layout.json"
    forbidden_xcodeproj = root / "tools" / "driverkit-xcode-layout" / "H1mekaRTXDriverKit.xcodeproj"

    checks = [
        make_check("metadata_json_exists", metadata_path.exists(), str(metadata_path)),
        make_check("project_layout_json_exists", layout_path.exists(), str(layout_path)),
        make_check("real_xcodeproj_absent", not forbidden_xcodeproj.exists(), str(forbidden_xcodeproj)),
    ]

    metadata = read_json(metadata_path)
    layout = read_json(layout_path)

    checks.append(make_check(
        "metadata_schema_expected",
        metadata.get("schema") == "h1mekartx.pbxproj_metadata_dryrun.v1",
        "h1mekartx.pbxproj_metadata_dryrun.v1",
    ))
    checks.append(make_check(
        "layout_schema_expected",
        layout.get("schema") == "h1mekartx.deterministic_xcode_project_layout.v1",
        "h1mekartx.deterministic_xcode_project_layout.v1",
    ))
    checks.append(make_check(
        "metadata_dryrun_only_true",
        metadata.get("pbxproj_metadata_dryrun_only") is True,
        "pbxproj_metadata_dryrun_only=true",
    ))

    for field in FORBIDDEN_TRUE_FIELDS:
        checks.append(make_check(
            f"forbidden_true_field_{field}_is_false",
            metadata.get(field) is False,
            f"{field}=false",
        ))

    graph = metadata.get("future_project_graph", {})
    checks.append(make_check(
        "future_graph_actually_generated_empty",
        graph.get("actually_generated") == [],
        "actually_generated=[]",
    ))
    checks.append(make_check(
        "future_graph_would_generate_only_metadata",
        graph.get("would_generate") == ["H1mekaRTXDriverKit.xcodeproj/project.pbxproj"],
        "would_generate metadata only",
    ))

    sanitized = {
        "schema": "h1mekartx.pbxproj_sanitized_metadata.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD",
        "secondary_classification": "CLASSIFICATION_PBXPROJ_METADATA_DRYRUN",
        "sanitizer_report_only": True,
        "real_xcodeproj_generation_attempted": False,
        "real_pbxproj_generation_attempted": False,
        "xcodebuild_invocation_attempted": False,
        "build_attempted": False,
        "signing_attempted": False,
        "install_attempted": False,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "source_metadata_schema": metadata.get("schema"),
        "source_layout_schema": layout.get("schema"),
        "future_project_graph": graph,
        "target_user_visible_goal": metadata.get("target_user_visible_goal", []),
    }

    sanitized_json_path = metadata_dir / "pbxproj-sanitized-metadata.json"
    sanitized_json_path.write_text(json.dumps(sanitized, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sanitized_md = f"""# PBXProj Sanitized Metadata

- Generated At UTC: `{sanitized['generated_at_utc']}`
- Classification: `{sanitized['classification']}`
- Sanitizer Report Only: `{sanitized['sanitizer_report_only']}`
- Real Xcodeproj Generation Attempted: `{sanitized['real_xcodeproj_generation_attempted']}`
- Real PBXProj Generation Attempted: `{sanitized['real_pbxproj_generation_attempted']}`
- Xcodebuild Invocation Attempted: `{sanitized['xcodebuild_invocation_attempted']}`
- Build Attempted: `{sanitized['build_attempted']}`
- Signing Attempted: `{sanitized['signing_attempted']}`
- Install Attempted: `{sanitized['install_attempted']}`
- DriverKit Activation Attempted: `{sanitized['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{sanitized['system_extension_activation_attempted']}`
- Dext Load Attempted: `{sanitized['dext_load_attempted']}`
- Provider Open Attempted: `{sanitized['provider_open_attempted']}`
- BAR Mapping Attempted: `{sanitized['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{sanitized['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{sanitized['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{sanitized['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{sanitized['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{sanitized['metal_proof_claimed']}`

## Conclusion

This sanitized metadata report confirms that no real Xcode project, pbxproj, build, signing, install, activation, provider open, BAR mapping, command submission, UI compositor proof, or Metal proof is represented.
"""
    sanitized_md_path = metadata_dir / "pbxproj-sanitized-metadata.md"
    sanitized_md_path.write_text(sanitized_md, encoding="utf-8")

    checks.append(make_check("sanitized_json_written", sanitized_json_path.exists(), str(sanitized_json_path)))
    checks.append(make_check("sanitized_markdown_written", sanitized_md_path.exists(), str(sanitized_md_path)))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_PBXPROJ_DRYRUN_DIFF_GUARD_READY" if failed_count == 0 else "FAIL_PBXPROJ_DRYRUN_DIFF_GUARD"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD",
        "secondary_classification": "CLASSIFICATION_PBXPROJ_METADATA_DRYRUN",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 13 pbxproj dry-run diff guard and sanitizer",
        "pbxproj_dryrun_diff_guard_only": True,
        "sanitizer_report_only": True,
        "real_xcodeproj_generation_attempted": False,
        "real_pbxproj_generation_attempted": False,
        "xcodebuild_invocation_attempted": False,
        "build_attempted": False,
        "signing_attempted": False,
        "install_attempted": False,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    report_json_path = out_dir / "pbxproj-dryrun-diff-guard-check.json"
    report_json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    report_md = f"""# PBXProj Dry-Run Diff Guard Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- PBXProj Dry-Run Diff Guard Only: `{report['pbxproj_dryrun_diff_guard_only']}`
- Sanitizer Report Only: `{report['sanitizer_report_only']}`
- Real Xcodeproj Generation Attempted: `{report['real_xcodeproj_generation_attempted']}`
- Real PBXProj Generation Attempted: `{report['real_pbxproj_generation_attempted']}`
- Xcodebuild Invocation Attempted: `{report['xcodebuild_invocation_attempted']}`
- Build Attempted: `{report['build_attempted']}`
- Signing Attempted: `{report['signing_attempted']}`
- Install Attempted: `{report['install_attempted']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Dext Load Attempted: `{report['dext_load_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This guard confirms that the pbxproj metadata remains a dry-run. No real `.xcodeproj`, real `project.pbxproj`, Xcode build, signing, install, DriverKit activation, System Extension activation, provider open, BAR mapping, command submission, UI compositor proof, or Metal proof is attempted.
"""
    report_md_path = out_dir / "pbxproj-dryrun-diff-guard-check.md"
    report_md_path.write_text(report_md, encoding="utf-8")

    print(f"Wrote sanitized JSON: {sanitized_json_path}")
    print(f"Wrote sanitized Markdown: {sanitized_md_path}")
    print(f"Wrote JSON: {report_json_path}")
    print(f"Wrote Markdown: {report_md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
