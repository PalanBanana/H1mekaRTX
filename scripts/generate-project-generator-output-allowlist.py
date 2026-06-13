#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.project_generator_output_allowlist.v1"

ALLOWED_DRYRUN_OUTPUT_PATHS = [
    "tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.json",
    "tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.md",
    "tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.json",
    "tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.md",
    "release-readiness/nonbuilding-project-generator-dryrun-check.json",
    "release-readiness/nonbuilding-project-generator-dryrun-check.md",
    "release-readiness/project-generator-output-allowlist-gate-check.json",
    "release-readiness/project-generator-output-allowlist-gate-check.md",
]

FORBIDDEN_REAL_PROJECT_OUTPUT_PATHS = [
    "tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj",
    "tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj",
    "H1mekaRTXDriverKit.xcodeproj",
    "H1mekaRTXDriverKit.xcodeproj/project.pbxproj",
]

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate project generator output allowlist dry-run report.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="tools/driverkit-xcode-layout/project-generator-dryrun", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "tools" / "driverkit-xcode-layout" / "project-generator-dryrun" / "project-generator-dryrun-manifest.json"
    manifest = read_json(manifest_path)

    forbidden_existing = [
        path
        for path in FORBIDDEN_REAL_PROJECT_OUTPUT_PATHS
        if (root / path).exists()
    ]

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE",
        "secondary_classification": "CLASSIFICATION_NONBUILDING_PROJECT_GENERATOR_DRYRUN",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "project_generator_output_allowlist_gate_only": True,
        "output_allowlist_report_only": True,
        "promotion_gate_only": True,
        "real_xcodeproj_generation_attempted": False,
        "real_pbxproj_generation_attempted": False,
        "xcode_invocation_attempted": False,
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
        "source_manifest_schema": manifest.get("schema"),
        "allowed_dryrun_output_paths": ALLOWED_DRYRUN_OUTPUT_PATHS,
        "forbidden_real_project_output_paths": FORBIDDEN_REAL_PROJECT_OUTPUT_PATHS,
        "forbidden_real_project_outputs_existing": forbidden_existing,
        "promotion_requirements": [
            "deterministic project generator implementation with explicit output allowlist",
            "dry-run diff approval",
            "pbxproj sanitizer approval",
            "no-build verification gate",
            "approved Apple Developer Team ID",
            "approved DriverKit entitlement evidence",
            "approved PCI transport entitlement evidence",
            "valid signing identity evidence",
            "disposable test install plan",
            "reversible activation/deactivation implementation",
            "explicit user approval flow",
            "rollback plan",
            "no provider open policy",
            "no BAR/MMIO mutation policy",
            "no command submission policy",
            "no UI compositor acceleration claim before proof gate",
            "no Metal proof claim before real GPU-backed workload evidence",
        ],
        "target_pci_provider_matching_manifest": {
            "target_gpu": "NVIDIA RTX 5070",
            "architecture_family": "NVIDIA Blackwell",
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "io_pci_match": "0x2f0410de",
            "expected_provider_class": "IOPCIDevice",
            "expected_driver_family": "PCIDriverKit",
            "expected_pci_transport_entitlement": "com.apple.developer.driverkit.transport.pci",
        },
        "target_user_visible_goal": [
            "smooth Dock animation",
            "working transparency",
            "working blur",
            "smooth window movement and resizing",
            "smooth Mission Control",
            "smooth Launchpad",
            "smooth Stage Manager",
        ],
    }

    json_path = out_dir / "project-generator-output-allowlist.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    allowed_rows = "\n".join(f"| `{path}` | ALLOWED_DRYRUN_OUTPUT |" for path in ALLOWED_DRYRUN_OUTPUT_PATHS)
    forbidden_rows = "\n".join(f"| `{path}` | FORBIDDEN_REAL_PROJECT_OUTPUT |" for path in FORBIDDEN_REAL_PROJECT_OUTPUT_PATHS)

    md = f"""# Project Generator Output Allowlist

- Generated At UTC: `{report['generated_at_utc']}`
- Classification: `{report['classification']}`
- Output Allowlist Report Only: `{report['output_allowlist_report_only']}`
- Promotion Gate Only: `{report['promotion_gate_only']}`
- Real Xcodeproj Generation Attempted: `{report['real_xcodeproj_generation_attempted']}`
- Real PBXProj Generation Attempted: `{report['real_pbxproj_generation_attempted']}`
- Xcode Invocation Attempted: `{report['xcode_invocation_attempted']}`
- Xcodebuild Invocation Attempted: `{report['xcodebuild_invocation_attempted']}`
- Build Attempted: `{report['build_attempted']}`
- Signing Attempted: `{report['signing_attempted']}`
- Install Attempted: `{report['install_attempted']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Allowed Dry-Run Outputs

| Path | Status |
| --- | --- |
{allowed_rows}

## Forbidden Real Project Outputs

| Path | Status |
| --- | --- |
{forbidden_rows}

## Conclusion

This allowlist gate permits dry-run metadata/report outputs only. Real `.xcodeproj`, real `project.pbxproj`, Xcode/xcodebuild, build, signing, install, DriverKit activation, System Extension activation, provider open, BAR mapping, GPU command submission, UI compositor proof, and Metal proof remain blocked.
"""
    md_path = out_dir / "project-generator-output-allowlist.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GENERATED")
    return 0 if not forbidden_existing else 1

if __name__ == "__main__":
    raise SystemExit(main())
