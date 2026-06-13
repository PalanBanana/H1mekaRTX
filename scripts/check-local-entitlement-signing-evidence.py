#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_entitlement_signing_evidence_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE",
    "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "LOCAL_EVIDENCE_COLLECTOR_ONLY: True",
    "READ_ONLY_STATUS_COLLECTION_ONLY: True",
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
    "LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_INPUTS",
    "LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_OUTPUTS",
    "SAFE_LOCAL_STATUS_COMMANDS",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
    "com.apple.developer.system-extension.install",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
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
    parser = argparse.ArgumentParser(description="Check local entitlement/signing evidence collector.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "local-entitlement-signing-evidence-collector.md"
    evidence_path = root / "host-report-bundle" / "local-entitlement-signing-evidence" / "local-entitlement-signing-evidence.json"
    evidence_md_path = root / "host-report-bundle" / "local-entitlement-signing-evidence" / "local-entitlement-signing-evidence.md"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("evidence_json_exists", evidence_path.exists(), str(evidence_path)),
        make_check("evidence_markdown_exists", evidence_md_path.exists(), str(evidence_md_path)),
    ]

    text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    evidence = read_json(evidence_path)
    checks.append(make_check("evidence_schema_matches", bool(evidence and evidence.get("schema") == "h1mekartx.local_entitlement_signing_evidence.v1"), "evidence schema"))
    checks.append(make_check("evidence_read_only_true", bool(evidence and evidence.get("read_only_status_collection_only") is True), "read_only_status_collection_only=true"))

    for field in [
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
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(
            f"evidence_{field}_false",
            bool(evidence and evidence.get(field) is False),
            f"{field}=false",
        ))

    derived = evidence.get("derived_status", {}) if evidence else {}
    checks.append(make_check("entitlement_approval_not_claimed", derived.get("entitlement_approval_claimed") is False, "entitlement_approval_claimed=false"))
    checks.append(make_check("signing_readiness_not_claimed", derived.get("signing_readiness_claimed") is False, "signing_readiness_claimed=false"))
    checks.append(make_check("activation_ready_not_claimed", derived.get("activation_ready_claimed") is False, "activation_ready_claimed=false"))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_READY" if failed_count == 0 else "FAIL_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 18 local entitlement/signing evidence collector",
        "local_evidence_collector_only": True,
        "read_only_status_collection_only": True,
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

    json_path = out_dir / "local-entitlement-signing-evidence-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Local Entitlement / Signing Evidence Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Read-Only Status Collection Only: `{report['read_only_status_collection_only']}`
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
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase collects local entitlement/signing status evidence only. It does not build, sign, install, activate, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "local-entitlement-signing-evidence-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
