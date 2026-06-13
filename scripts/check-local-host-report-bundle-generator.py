#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.local_host_report_bundle_generator_check.v1"

REQUIRED_FILES = [
    "scripts/create-local-host-report-bundle.py",
    "docs/metal/local-host-report-bundle-generator.md",
]

EXPECTED_BUNDLE_FILES = [
    "bundle.json",
    "README.md",
]

EXPECTED_OPTIONAL_REPORTS = [
    "reports/metal-workload-runtime.json",
    "reports/metal-workload-result-schema.json",
    "reports/metal-workload-regression-manifest.json",
    "reports/host-status.json",
    "reports/host-diagnostics-summary.json",
    "reports/host-diagnostics-summary.md",
    "reports/bar-inventory-summary.json",
    "reports/bar-inventory-summary.md",
    "reports/ui-compositor-proof-schema.json",
    "reports/ui-compositor-proof-schema.md",
    "reports/ui-compositor-sample-summary.json",
    "reports/ui-compositor-sample-summary.md",
    "reports/ui-compositor-readiness-matrix.json",
    "reports/ui-compositor-readiness-matrix.md",
    "reports/ui-gpu-attribution-summary.json",
    "reports/ui-gpu-attribution-summary.md",
    "reports/ui-workload-correlation-report.json",
    "reports/ui-workload-correlation-report.md",
    "reports/rendered-host-status-report.md",
    "reports/safety-gates.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture_reports(fixture_dir: Path) -> None:
    fixture_dir.mkdir(parents=True, exist_ok=True)

    (fixture_dir / "metal-workload-runtime.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.metal_reference_workload_runtime.v1",
                "validationPassed": True,
                "workloadCount": 6,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    (fixture_dir / "metal-workload-result-schema.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.metal_workload_result_schema.v2",
                "decision": "METAL_WORKLOAD_RESULT_SCHEMA_SYNCED_WITH_P1",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    (fixture_dir / "metal-workload-regression-manifest.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.metal_workload_regression_manifest.v2",
                "decision": "METAL_WORKLOAD_REGRESSION_MANIFEST_SYNCED_WITH_P1",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    (fixture_dir / "host-status.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.host_status_report.v1",
                "decision": "HOST_APP_SKELETON_READY_NO_ACTIVATION",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    (fixture_dir / "host-diagnostics-summary.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.host_ui_diagnostics_summary.v1",
                "decisions": {
                    "host_diagnostics_result": "TARGET_PRESENT_HOST_DIAGNOSTICS",
                    "graphics_stack_diagnostics_result": "GRAPHICS_STACK_HINTS_PRESENT",
                    "ui_compositor_proof_result": "UNPROVEN",
                    "metal_proof_result": "UNPROVEN",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "host-diagnostics-summary.md").write_text("# Host Diagnostics Summary\n\nFixture.\n")
    (fixture_dir / "bar-inventory-summary.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.bar_inventory_summary.v1",
                "likely_target_present": True,
                "safety_boundary": {
                    "read_only": True,
                    "mmio_writes": False,
                    "driverkit_activation": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "bar-inventory-summary.md").write_text("# BAR Inventory Summary\n\nFixture.\n")
    (fixture_dir / "ui-compositor-proof-schema.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_compositor_proof_schema.v1",
                "decision": "UI_COMPOSITOR_PROOF_SCHEMA_READY",
                "ui_compositor_acceleration_claim_allowed_now": False,
                "metal_acceleration_claim_allowed_now": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "ui-compositor-proof-schema.md").write_text("# UI Compositor Proof Schema\n\nFixture.\n")
    (fixture_dir / "ui-compositor-sample-summary.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_compositor_sample_summary.v1",
                "decisions": {
                    "sample_result": "UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_CAPTURED",
                    "ui_compositor_proof_result": "UNPROVEN",
                    "metal_proof_result": "UNPROVEN",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "ui-compositor-sample-summary.md").write_text("# UI Compositor Sample Summary\n\nFixture.\n")
    (fixture_dir / "ui-compositor-readiness-matrix.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_compositor_readiness_matrix.v1",
                "decision": "NOT_PROVEN",
                "ui_compositor_acceleration_claim_allowed": False,
                "metal_acceleration_claim_allowed": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "ui-compositor-readiness-matrix.md").write_text("# UI Compositor Readiness Matrix\n\nFixture.\n")
    (fixture_dir / "ui-gpu-attribution-summary.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_gpu_attribution_summary.v1",
                "decisions": {
                    "ui_gpu_attribution_result": "UI_GPU_ATTRIBUTION_CANDIDATES_CAPTURED",
                    "trusted_ui_gpu_attribution_result": "UNPROVEN",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "ui-gpu-attribution-summary.md").write_text("# UI GPU Attribution Summary\n\nFixture.\n")
    (fixture_dir / "ui-workload-correlation-report.json").write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_workload_correlation_report.v1",
                "decisions": {
                    "ui_workload_correlation_result": "UI_WORKLOAD_CORRELATION_CANDIDATES_CAPTURED",
                    "rtx5070_workload_attribution_result": "UNPROVEN",
                    "ui_compositor_proof_result": "UNPROVEN",
                    "metal_proof_result": "UNPROVEN",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (fixture_dir / "ui-workload-correlation-report.md").write_text("# UI Workload Correlation Report\n\nFixture.\n")
    (fixture_dir / "rendered-host-status-report.md").write_text("# Rendered Host Status Report\n\nFixture.\n")
    (fixture_dir / "forbidden-bar-operation-audit.md").write_text("# Safety Gates\n\nFixture.\n")


def run_generator(root: Path, fixture_dir: Path, bundle_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "create-local-host-report-bundle.py"),
            "--input-dir",
            str(fixture_dir),
            "--bundle-dir",
            str(bundle_dir),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    for rel in REQUIRED_FILES:
        path = root / rel
        add(f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(
        [
            read_text(root / "scripts" / "create-local-host-report-bundle.py"),
            read_text(root / "docs" / "metal" / "local-host-report-bundle-generator.md"),
        ]
    )

    required_terms = [
        "LOCAL_HOST_REPORT_BUNDLE_CREATED",
        "LOCAL_ONLY_REPORT_BUNDLE",
        "h1mekartx.host_report_bundle.v1",
        "localFilesOnly",
        "copiesExistingLocalReportsOnly",
        "noLiveExtensionQuery",
        "noSystemExtensionRequests",
        "noDriverKitActivation",
        "noDeviceOwnershipRequest",
        "noPCIConfigAccess",
        "noMMIOAccess",
        "noBARMapping",
        "noRTX5070Acceleration",
        "noHardwareCommandSubmission",
    ]

    for term in required_terms:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    forbidden_terms = [
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "IOPCI" + "Device",
        "Configuration" + "Write",
        "Memory" + "Read",
        "Memory" + "Write",
        "sub" + "process.run([\"ioreg\"",
        "sub" + "process.run([\"system_profiler\"",
    ]

    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "input"
    bundle_dir = out_dir / "fixture" / "host-report-bundle"
    write_fixture_reports(fixture_dir)
    generator = run_generator(root, fixture_dir, bundle_dir)

    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    for rel in EXPECTED_BUNDLE_FILES:
        path = bundle_dir / rel
        add(f"bundle_file:{rel}", path.exists(), "present" if path.exists() else "missing")

    manifest_path = bundle_dir / "bundle.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    add("bundle_schema", manifest.get("schema") == "h1mekartx.host_report_bundle.v1", f"schema={manifest.get('schema')!r}")
    add("bundle_decision", manifest.get("bundleDecision") == "LOCAL_HOST_REPORT_BUNDLE_CREATED", f"decision={manifest.get('bundleDecision')!r}")
    add("bundle_type", manifest.get("bundleType") == "LOCAL_ONLY_REPORT_BUNDLE", f"type={manifest.get('bundleType')!r}")
    add("present_report_count", manifest.get("presentReportCount") == 20, f"presentReportCount={manifest.get('presentReportCount')!r}")

    bundle_reports = {item.get("path") for item in manifest.get("reports", []) if isinstance(item, dict)}

    for rel in EXPECTED_OPTIONAL_REPORTS:
        add(f"bundle_report_record:{rel}", rel in bundle_reports, "present" if rel in bundle_reports else "missing")
        add(f"bundle_report_file:{rel}", (bundle_dir / rel).exists(), "present" if (bundle_dir / rel).exists() else "missing")

    for item in manifest.get("reports", []):
        if not isinstance(item, dict):
            continue
        if item.get("present"):
            add(
                f"report_has_sha256:{item.get('path')}",
                isinstance(item.get("sha256"), str) and len(item.get("sha256", "")) == 64,
                f"sha256={item.get('sha256')!r}",
            )
            add(
                f"report_has_bytes:{item.get('path')}",
                isinstance(item.get("bytes"), int) and item.get("bytes", 0) > 0,
                f"bytes={item.get('bytes')!r}",
            )

    sb = manifest.get("safetyBoundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "localFilesOnly",
        "copiesExistingLocalReportsOnly",
        "noLiveExtensionQuery",
        "noSystemExtensionRequests",
        "noDriverKitActivation",
        "noDeviceOwnershipRequest",
        "noPCIConfigAccess",
        "noMMIOAccess",
        "noBARMapping",
        "noRTX5070Acceleration",
        "noRTX5070ShaderExecution",
        "noHardwareCommandSubmission",
        "noRTX5070ResourceAllocation",
        "noFirmwareLoading",
        "noDisplayInitialization",
        "noFramebufferInitialization",
        "noGPUReset",
    ]:
        add(f"bundle_safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_LOCAL_HOST_REPORT_BUNDLE_GENERATOR_READY" if failed_count == 0 else "FAIL_LOCAL_HOST_REPORT_BUNDLE_GENERATOR_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "fixture_bundle_dir": str(bundle_dir),
        "expected_bundle_files": EXPECTED_BUNDLE_FILES,
        "expected_optional_reports": EXPECTED_OPTIONAL_REPORTS,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_fixture_only": True,
            "copies_existing_local_reports_only": True,
            "local_files_only": True,
            "queries_live_extension_state": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
            "device_ownership_request": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    bundle_files = [f"- `{item}`" for item in report["expected_bundle_files"]]
    optional_reports = [f"- `{item}`" for item in report["expected_optional_reports"]]

    return "\n".join(
        [
            "# Local Host Report Bundle Generator Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Expected Bundle Files",
            "",
            *bundle_files,
            "",
            "## Expected Optional Reports",
            "",
            *optional_reports,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates a local-only bundle generator using local fixture files.",
            "",
            "It does not query live extension state, add System Extension request code, activate DriverKit, submit activation or deactivation requests, submit extension manager requests, request device ownership, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX local host report bundle generator.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "local-host-report-bundle-generator-check.json"
    md_path = out_dir / "local-host-report-bundle-generator-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
