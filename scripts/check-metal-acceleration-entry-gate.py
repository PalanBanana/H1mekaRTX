#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_acceleration_entry_gate_check.v1"

REQUIRED_FILES = [
    "scripts/generate-metal-acceleration-entry-gate.py",
    "docs/metal/metal-acceleration-entry-gate.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture(fixture_dir: Path) -> tuple[Path, Path, Path, Path]:
    fixture_dir.mkdir(parents=True, exist_ok=True)
    host = fixture_dir / "host-diagnostics-summary.json"
    bar = fixture_dir / "bar-inventory-summary.json"
    readiness = fixture_dir / "ui-compositor-readiness-matrix.json"
    workload = fixture_dir / "ui-workload-correlation-report.json"

    host.write_text(
        json.dumps(
            {
                "schema": "h1mekartx.host_ui_diagnostics_summary.v1",
                "likely_target_present": True,
                "decisions": {
                    "host_diagnostics_result": "TARGET_PRESENT_HOST_DIAGNOSTICS",
                    "graphics_stack_diagnostics_result": "GRAPHICS_STACK_HINTS_PRESENT",
                },
                "target_hits": {
                    "vendor_10de": 2,
                    "device_2f04": 1,
                    "iopcimatch_2f0410de": 1,
                },
                "bar_inventory_hints": {
                    "assigned_addresses": 1,
                    "reg": 1,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    bar.write_text(
        json.dumps(
            {
                "schema": "h1mekartx.bar_inventory_summary.v1",
                "likely_target_present": True,
                "safety_boundary": {
                    "read_only": True,
                    "driverkit_activation": False,
                    "mmio_writes": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    readiness.write_text(
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
    workload.write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_workload_correlation_report.v1",
                "decisions": {
                    "ui_workload_correlation_result": "UI_WORKLOAD_CORRELATION_CANDIDATES_CAPTURED",
                    "rtx5070_workload_attribution_result": "UNPROVEN",
                    "real_gpu_command_execution_result": "NOT_ATTEMPTED",
                    "ui_compositor_proof_result": "UNPROVEN",
                    "metal_proof_result": "UNPROVEN",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return host, bar, readiness, workload


def run_generator(root: Path, host: Path, bar: Path, readiness: Path, workload: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-metal-acceleration-entry-gate.py"),
            "--host-summary",
            str(host),
            "--bar-inventory-summary",
            str(bar),
            "--ui-compositor-readiness-matrix",
            str(readiness),
            "--ui-workload-correlation-report",
            str(workload),
            "--out-dir",
            str(out_dir),
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

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)
    required_terms = [
        "h1mekartx.metal_acceleration_entry_gate.v1",
        "METAL_ACCELERATION_IMPLEMENTATION_NOT_READY",
        "IN_PROGRESS_NOW",
        "NEXT_PHASE",
        "BLOCKED",
        "Phase 3 runtime probe",
        "Phase 7 real GPU command submission proof",
        "Phase 9 Metal-facing proof",
        "rtx5070_metal_acceleration_claim_allowed",
        "real_gpu_command_execution_claim_allowed",
        "No DriverKit activation",
        "No System Extension activation",
        "No GPU command submission",
        "No RTX 5070 shader execution",
        "No RTX 5070 UI compositor acceleration claim",
        "No RTX 5070 Metal acceleration claim",
    ]
    for term in required_terms:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    forbidden_terms = [
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "Configuration" + "Write",
        "Memory" + "Write",
        "Create" + "Memory" + "Map",
        "rtx5070_metal_acceleration_claim_allowed\": True",
        "real_gpu_command_execution_claim_allowed\": True",
        "gpu_command_submission\": True",
        "rtx5070_shader_execution\": True",
        "metal_proof_claim\": True",
        "csrutil disable",
        "spctl --master-disable",
    ]
    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "inputs"
    report_out = out_dir / "fixture" / "report"
    host, bar, readiness, workload = write_fixture(fixture_dir)
    generator = run_generator(root, host, bar, readiness, workload, report_out)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    json_path = report_out / "metal-acceleration-entry-gate.json"
    md_path = report_out / "metal-acceleration-entry-gate.md"
    add("gate_json_exists", json_path.exists(), "present" if json_path.exists() else "missing")
    add("gate_md_exists", md_path.exists(), "present" if md_path.exists() else "missing")

    data = json.loads(json_path.read_text()) if json_path.exists() else {}
    add("gate_schema", data.get("schema") == "h1mekartx.metal_acceleration_entry_gate.v1", f"schema={data.get('schema')!r}")
    add("decision_not_ready", data.get("decision") == "METAL_ACCELERATION_IMPLEMENTATION_NOT_READY", f"decision={data.get('decision')!r}")
    plain = data.get("plain_answer", {})
    add("research_in_progress", plain.get("metal_research_development") == "IN_PROGRESS_NOW", f"value={plain.get('metal_research_development')!r}")
    add("runtime_probe_next", plain.get("runtime_probe_development") == "NEXT_PHASE", f"value={plain.get('runtime_probe_development')!r}")
    add("real_metal_blocked", plain.get("real_rtx5070_metal_acceleration_implementation") == "BLOCKED", f"value={plain.get('real_rtx5070_metal_acceleration_implementation')!r}")
    claims = data.get("claims", {})
    add("ui_claim_false", claims.get("rtx5070_ui_acceleration_claim_allowed") is False, f"value={claims.get('rtx5070_ui_acceleration_claim_allowed')!r}")
    add("metal_claim_false", claims.get("rtx5070_metal_acceleration_claim_allowed") is False, f"value={claims.get('rtx5070_metal_acceleration_claim_allowed')!r}")
    add("command_claim_false", claims.get("real_gpu_command_execution_claim_allowed") is False, f"value={claims.get('real_gpu_command_execution_claim_allowed')!r}")
    add("blocked_gates_present", data.get("gate_blocked_count", 0) >= 1, f"blocked={data.get('gate_blocked_count')!r}")

    gate_ids = {item.get("id") for item in data.get("gates", []) if isinstance(item, dict)}
    for gate_id in [
        "metal-entry-001",
        "metal-entry-004",
        "metal-entry-008",
        "metal-entry-009",
        "metal-entry-010",
    ]:
        add(f"gate:{gate_id}", gate_id in gate_ids, "present" if gate_id in gate_ids else "missing")

    safety = data.get("safety_boundary", {})
    for key in ["read_only_report_only", "uses_existing_reports_only"]:
        add(f"safety_true:{key}", safety.get(key) is True, f"value={safety.get(key)!r}")
    for key in [
        "runs_live_diagnostics",
        "driverkit_activation",
        "system_extension_activation",
        "device_ownership_request",
        "process_injection",
        "windowserver_injection",
        "dock_injection",
        "private_framework_patching",
        "fake_metal_device_spoofing",
        "sip_bypass",
        "amfi_bypass",
        "pci_config_reads",
        "pci_config_writes",
        "mmio_reads",
        "mmio_writes",
        "bar_mapping",
        "bar_poking",
        "gpu_command_submission",
        "rtx5070_shader_execution",
        "rtx5070_memory_movement",
        "firmware_loading",
        "gsp_initialization",
        "display_engine_init",
        "framebuffer_init",
        "gpu_reset",
        "ui_compositor_proof_claim",
        "metal_proof_claim",
    ]:
        add(f"safety_false:{key}", safety.get(key) is False, f"value={safety.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_METAL_ACCELERATION_ENTRY_GATE_READY" if failed_count == 0 else "FAIL_METAL_ACCELERATION_ENTRY_GATE_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_fixture_check": True,
            "uses_existing_reports_only": True,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "gpu_command_submission": False,
            "rtx5070_shader_execution": False,
            "ui_compositor_proof": False,
            "metal_proof": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = [
        f"| `{item['name']}` | {'PASS' if item['passed'] else 'FAIL'} | {str(item['detail']).replace('|', '\\|')} |"
        for item in report["checks"]
    ]
    return "\n".join(
        [
            "# Metal Acceleration Entry Gate Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check uses fixture JSON reports only. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, access MMIO, map BAR memory, submit GPU commands, execute RTX 5070 shaders, claim UI compositor proof, or claim Metal proof.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX Metal acceleration entry gate.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)
    json_path = out_dir / "metal-acceleration-entry-gate-check.json"
    md_path = out_dir / "metal-acceleration-entry-gate-check.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")
    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
