#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_compositor_readiness_matrix_check.v1"

REQUIRED_FILES = [
    "scripts/generate-ui-compositor-readiness-matrix.py",
    "docs/metal/ui-compositor-readiness-matrix.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture(fixture_dir: Path) -> tuple[Path, Path, Path]:
    fixture_dir.mkdir(parents=True, exist_ok=True)
    host = fixture_dir / "host-diagnostics-summary.json"
    sample = fixture_dir / "ui-compositor-sample-summary.json"
    schema = fixture_dir / "ui-compositor-proof-schema.json"

    host.write_text(
        json.dumps(
            {
                "schema": "h1mekartx.host_ui_diagnostics_summary.v1",
                "likely_target_present": True,
                "decisions": {
                    "host_diagnostics_result": "TARGET_PRESENT_HOST_DIAGNOSTICS",
                    "graphics_stack_diagnostics_result": "GRAPHICS_STACK_HINTS_PRESENT",
                },
                "target_hits": {"vendor_10de": 1, "device_2f04": 1},
                "bar_inventory_hints": {"assigned_addresses": 1, "reg": 1},
                "graphics_stack_hits": {"windowserver": 1, "dock": 1, "ioaccelerator": 1},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    sample.write_text(
        json.dumps(
            {
                "schema": "h1mekartx.ui_compositor_sample_summary.v1",
                "decisions": {
                    "sample_result": "UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_CAPTURED",
                    "ui_compositor_proof_result": "UNPROVEN",
                    "metal_proof_result": "UNPROVEN",
                    "rtx5070_ui_acceleration_claim": "NOT_CLAIMED",
                    "rtx5070_metal_acceleration_claim": "NOT_CLAIMED",
                },
                "surface_hits": {
                    "dock": 1,
                    "windowserver": 1,
                    "core_animation": 1,
                    "quartzcore": 1,
                    "transparency_blur": 1,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    schema.write_text(
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
    return host, sample, schema


def run_generator(root: Path, host: Path, sample: Path, schema: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-ui-compositor-readiness-matrix.py"),
            "--host-summary",
            str(host),
            "--ui-sample-summary",
            str(sample),
            "--proof-schema",
            str(schema),
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
        "h1mekartx.ui_compositor_readiness_matrix.v1",
        "NOT_PROVEN",
        "ui_compositor_acceleration_claim_allowed",
        "metal_acceleration_claim_allowed",
        "current_ui_gpu_attribution",
        "rtx5070_workload_attribution",
        "ui_surface_correlation",
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
        "ui_compositor_acceleration_claim_allowed\": True",
        "metal_acceleration_claim_allowed\": True",
        "ui_compositor_proof_claim\": True",
        "metal_proof_claim\": True",
        "csrutil disable",
        "spctl --master-disable",
    ]
    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "inputs"
    matrix_out = out_dir / "fixture" / "matrix"
    host, sample, schema = write_fixture(fixture_dir)
    generator = run_generator(root, host, sample, schema, matrix_out)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    json_path = matrix_out / "ui-compositor-readiness-matrix.json"
    md_path = matrix_out / "ui-compositor-readiness-matrix.md"
    add("matrix_json_exists", json_path.exists(), "present" if json_path.exists() else "missing")
    add("matrix_md_exists", md_path.exists(), "present" if md_path.exists() else "missing")

    data = json.loads(json_path.read_text()) if json_path.exists() else {}
    add("matrix_schema", data.get("schema") == "h1mekartx.ui_compositor_readiness_matrix.v1", f"schema={data.get('schema')!r}")
    add("matrix_decision", data.get("decision") == "NOT_PROVEN", f"decision={data.get('decision')!r}")
    add("ui_claim_false", data.get("ui_compositor_acceleration_claim_allowed") is False, f"value={data.get('ui_compositor_acceleration_claim_allowed')!r}")
    add("metal_claim_false", data.get("metal_acceleration_claim_allowed") is False, f"value={data.get('metal_acceleration_claim_allowed')!r}")
    add("blocked_count", data.get("blocked_count", 0) >= 1, f"blocked_count={data.get('blocked_count')!r}")

    req_ids = {item.get("id") for item in data.get("requirements", []) if isinstance(item, dict)}
    for req_id in [
        "proof_schema_ready",
        "target_identity",
        "bar_inventory",
        "graphics_stack_visibility",
        "ui_sample_capture",
        "ui_surface_hints",
        "current_ui_gpu_attribution",
        "rtx5070_workload_attribution",
        "ui_surface_correlation",
    ]:
        add(f"requirement:{req_id}", req_id in req_ids, "present" if req_id in req_ids else "missing")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in ["read_only_report_only", "uses_existing_reports_only"]:
        add(f"safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    for key in [
        "runs_live_diagnostics",
        "driverkit_activation",
        "system_extension_activation",
        "device_ownership_request",
        "pci_config_writes",
        "mmio_reads",
        "mmio_writes",
        "bar_mapping",
        "gpu_command_submission",
        "rtx5070_shader_execution",
        "windowserver_injection",
        "dock_injection",
        "private_framework_patching",
        "sip_bypass",
        "amfi_bypass",
        "fake_metal_device_spoofing",
        "ui_compositor_proof_claim",
        "metal_proof_claim",
    ]:
        add(f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_UI_COMPOSITOR_READINESS_MATRIX_READY" if failed_count == 0 else "FAIL_UI_COMPOSITOR_READINESS_MATRIX_NOT_READY",
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
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "gpu_command_submission": False,
            "ui_compositor_proof_claim": False,
            "metal_proof_claim": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = [
        f"| `{item['name']}` | {'PASS' if item['passed'] else 'FAIL'} | {str(item['detail']).replace('|', '\\|')} |"
        for item in report["checks"]
    ]
    return "\n".join(
        [
            "# UI Compositor Readiness Matrix Check",
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
            "This check uses fixture JSON reports only. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, write PCI config space, access MMIO, map BAR memory, submit GPU commands, prove UI compositor acceleration, or prove Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX UI compositor readiness matrix.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)
    json_path = out_dir / "ui-compositor-readiness-matrix-check.json"
    md_path = out_dir / "ui-compositor-readiness-matrix-check.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")
    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
