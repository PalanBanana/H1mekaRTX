#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.pbxproj_metadata_dryrun_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_PBXPROJ_METADATA_DRYRUN",
    "CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "PBXPROJ_METADATA_DRYRUN_ONLY: True",
    "NO_REAL_XCODEPROJ_GENERATION: True",
    "NO_REAL_PBXPROJ_GENERATION: True",
    "NO_XCODEBUILD_INVOCATION: True",
    "NO_BUILD_ATTEMPTED: True",
    "NO_SIGNING_ATTEMPTED: True",
    "NO_INSTALL_ATTEMPTED: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_DEXT_LOAD: True",
    "NO_DEVICE_OWNERSHIP_REQUEST: True",
    "NO_PROVIDER_OPEN: True",
    "NO_BAR_MAPPING: True",
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
    "PBXPROJ_METADATA_DRYRUN_INPUTS",
    "PBXPROJ_METADATA_DRYRUN_OUTPUTS",
    "FUTURE_PROJECT_GRAPH_CONTRACT",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "H1mekaRTXDriverKit",
    "H1mekaRTXHost",
    "H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXHost",
    "dev.h1meka.H1mekaRTXDriver",
    "com.apple.driverkit",
    "com.apple.developer.driverkit",
    "com.apple.developer.driverkit.transport.pci",
    "com.apple.developer.system-extension.install",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
    "REAL_XCODEPROJ_GENERATION_ATTEMPTED: False",
    "REAL_PBXPROJ_GENERATION_ATTEMPTED: False",
    "XCODEBUILD_INVOCATION_ATTEMPTED: False",
    "BUILD_ATTEMPTED: False",
    "SIGNING_ATTEMPTED: False",
    "INSTALL_ATTEMPTED: False",
    "DRIVERKIT_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False",
    "DEXT_LOAD_ATTEMPTED: False",
    "DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False",
    "PROVIDER_OPEN_ATTEMPTED: False",
    "BAR_MAPPING_ATTEMPTED: False",
    "BAR_MMIO_MUTATION_ATTEMPTED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check pbxproj metadata dry-run contract and outputs.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "pbxproj-metadata-dryrun-contract.md"
    metadata_json_path = root / "tools" / "driverkit-xcode-layout" / "pbxproj-metadata-dryrun.json"
    metadata_md_path = root / "tools" / "driverkit-xcode-layout" / "pbxproj-metadata-dryrun.md"
    forbidden_real_xcodeproj = root / "tools" / "driverkit-xcode-layout" / "H1mekaRTXDriverKit.xcodeproj"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("metadata_json_exists", metadata_json_path.exists(), str(metadata_json_path)),
        make_check("metadata_md_exists", metadata_md_path.exists(), str(metadata_md_path)),
        make_check("real_xcodeproj_not_created", not forbidden_real_xcodeproj.exists(), str(forbidden_real_xcodeproj)),
    ]

    text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    metadata = read_json(metadata_json_path)
    checks.append(make_check(
        "metadata_schema_matches",
        bool(metadata and metadata.get("schema") == "h1mekartx.pbxproj_metadata_dryrun.v1"),
        "h1mekartx.pbxproj_metadata_dryrun.v1",
    ))
    checks.append(make_check(
        "metadata_dryrun_only_true",
        bool(metadata and metadata.get("pbxproj_metadata_dryrun_only") is True),
        "pbxproj_metadata_dryrun_only=true",
    ))
    checks.append(make_check(
        "metadata_no_real_xcodeproj_generation",
        bool(metadata and metadata.get("real_xcodeproj_generation_attempted") is False),
        "real_xcodeproj_generation_attempted=false",
    ))
    checks.append(make_check(
        "metadata_no_real_pbxproj_generation",
        bool(metadata and metadata.get("real_pbxproj_generation_attempted") is False),
        "real_pbxproj_generation_attempted=false",
    ))
    checks.append(make_check(
        "metadata_no_xcodebuild",
        bool(metadata and metadata.get("xcodebuild_invocation_attempted") is False),
        "xcodebuild_invocation_attempted=false",
    ))
    checks.append(make_check(
        "metadata_no_build_sign_install_activation",
        bool(metadata and metadata.get("build_attempted") is False and metadata.get("signing_attempted") is False and metadata.get("install_attempted") is False and metadata.get("driverkit_activation_attempted") is False),
        "no build/sign/install/activation",
    ))

    graph = metadata.get("future_project_graph", {}) if metadata else {}
    checks.append(make_check(
        "future_graph_project_name",
        graph.get("project_name") == "H1mekaRTXDriverKit",
        "H1mekaRTXDriverKit",
    ))
    checks.append(make_check(
        "future_graph_host_bundle_id",
        graph.get("host_bundle_id") == "dev.h1meka.H1mekaRTXHost",
        "dev.h1meka.H1mekaRTXHost",
    ))
    checks.append(make_check(
        "future_graph_dext_bundle_id",
        graph.get("dext_bundle_id") == "dev.h1meka.H1mekaRTXDriver",
        "dev.h1meka.H1mekaRTXDriver",
    ))
    checks.append(make_check(
        "future_graph_actually_generated_empty",
        graph.get("actually_generated") == [],
        "actually_generated=[]",
    ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_PBXPROJ_METADATA_DRYRUN_READY" if failed_count == 0 else "FAIL_PBXPROJ_METADATA_DRYRUN"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_PBXPROJ_METADATA_DRYRUN",
        "secondary_classification": "CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 12 non-building pbxproj metadata generator dry-run",
        "pbxproj_metadata_dryrun_only": True,
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

    json_path = out_dir / "pbxproj-metadata-dryrun-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# PBXProj Metadata Dry-Run Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- PBXProj Metadata Dry-Run Only: `{report['pbxproj_metadata_dryrun_only']}`
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

This phase generated metadata only. It did not create a real `.xcodeproj` or `project.pbxproj`, did not invoke `xcodebuild`, did not build, sign, install, activate, load, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.

## Next Phase Recommendation

Next safe step: add a dry-run diff guard and pbxproj sanitizer contract before any real project generation.
"""

    md_path = out_dir / "pbxproj-metadata-dryrun-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
