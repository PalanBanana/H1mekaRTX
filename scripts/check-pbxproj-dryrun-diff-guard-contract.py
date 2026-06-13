#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.pbxproj_dryrun_diff_guard_contract_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD",
    "CLASSIFICATION_PBXPROJ_METADATA_DRYRUN",
    "CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "PBXPROJ_DRYRUN_DIFF_GUARD_ONLY: True",
    "SANITIZER_REPORT_ONLY: True",
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
    "PBXPROJ_DRYRUN_DIFF_GUARD_INPUTS",
    "PBXPROJ_DRYRUN_DIFF_GUARD_OUTPUTS",
    "FORBIDDEN_PBXPROJ_PROMOTION_MARKERS",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
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
    parser = argparse.ArgumentParser(description="Check pbxproj dry-run diff guard contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "pbxproj-dryrun-diff-guard-contract.md"
    sanitized_json_path = root / "tools" / "driverkit-xcode-layout" / "pbxproj-sanitized-metadata.json"
    sanitized_md_path = root / "tools" / "driverkit-xcode-layout" / "pbxproj-sanitized-metadata.md"
    report_json_path = root / "release-readiness" / "pbxproj-dryrun-diff-guard-check.json"
    forbidden_xcodeproj = root / "tools" / "driverkit-xcode-layout" / "H1mekaRTXDriverKit.xcodeproj"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("sanitized_json_exists", sanitized_json_path.exists(), str(sanitized_json_path)),
        make_check("sanitized_markdown_exists", sanitized_md_path.exists(), str(sanitized_md_path)),
        make_check("guard_report_json_exists", report_json_path.exists(), str(report_json_path)),
        make_check("real_xcodeproj_not_created", not forbidden_xcodeproj.exists(), str(forbidden_xcodeproj)),
    ]

    text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    sanitized = read_json(sanitized_json_path)
    checks.append(make_check(
        "sanitized_schema_matches",
        bool(sanitized and sanitized.get("schema") == "h1mekartx.pbxproj_sanitized_metadata.v1"),
        "h1mekartx.pbxproj_sanitized_metadata.v1",
    ))
    checks.append(make_check(
        "sanitized_report_only_true",
        bool(sanitized and sanitized.get("sanitizer_report_only") is True),
        "sanitizer_report_only=true",
    ))
    for field in [
        "real_xcodeproj_generation_attempted",
        "real_pbxproj_generation_attempted",
        "xcodebuild_invocation_attempted",
        "build_attempted",
        "signing_attempted",
        "install_attempted",
        "driverkit_activation_attempted",
        "system_extension_activation_attempted",
        "dext_load_attempted",
        "provider_open_attempted",
        "bar_mapping_attempted",
        "bar_mmio_mutation_attempted",
        "real_gpu_command_execution_attempted",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(
            f"sanitized_{field}_false",
            bool(sanitized and sanitized.get(field) is False),
            f"{field}=false",
        ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_PBXPROJ_DRYRUN_DIFF_GUARD_CONTRACT_READY" if failed_count == 0 else "FAIL_PBXPROJ_DRYRUN_DIFF_GUARD_CONTRACT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD",
        "secondary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 13 pbxproj dry-run diff guard contract",
        "checks": checks,
    }

    json_path = out_dir / "pbxproj-dryrun-diff-guard-contract-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# PBXProj Dry-Run Diff Guard Contract Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

The pbxproj diff guard contract remains dry-run only and does not create or validate any real Xcode project generation, build, signing, install, activation, provider open, BAR mapping, command submission, UI compositor proof, or Metal proof.
"""
    md_path = out_dir / "pbxproj-dryrun-diff-guard-contract-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
