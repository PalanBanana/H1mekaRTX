#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.no_hardware_activation_readiness_check.v1"

REQUIRED_FILES = [
    "scripts/generate-no-hardware-activation-readiness-review.py",
    "docs/metal/no-hardware-activation-readiness-review.md",
]

REQUIRED_TERMS = [
    "NO_HARDWARE_ACTIVATION_NOT_READY_EVIDENCE_REQUIRED",
    "activation_implementation_allowed",
    "activation_request_allowed",
    "deactivation_request_allowed",
    "manager_submit_allowed",
    "driverkit_activation_allowed",
    "device_ownership_allowed",
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "iopcidevice_provider_attach",
    "maps_bar_memory",
    "performs_mmio_reads",
    "performs_mmio_writes",
]

REQUIRED_FALSE_SAFETY = [
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "implements_activation_controller_runtime_path",
    "driverkit_activation",
    "driverkit_dext_installation",
    "device_ownership_request",
    "iopcidevice_provider_attach",
    "live_extension_status_query",
    "live_pci_probing",
    "runs_ioreg",
    "runs_system_profiler",
    "performs_pci_config_reads",
    "performs_pci_config_writes",
    "performs_mmio_reads",
    "performs_mmio_writes",
    "maps_bar_memory",
    "bar_poking",
    "rtx5070_metal_acceleration_implementation",
    "rtx5070_shader_execution",
    "hardware_command_submission_to_rtx5070",
    "resource_allocation_on_rtx5070",
]

FORBIDDEN_LITERAL_TERMS = [
    "OSSystem" + "ExtensionRequest.",
    "OSSystem" + "ExtensionManager.",
    "IOPCI" + "Device *",
    "Configuration" + "Write",
    "Memory" + "Read",
    "Memory" + "Write",
    "sub" + "process.run([\"ioreg\"",
    "sub" + "process.run([\"system_profiler\"",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def run_generator(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-no-hardware-activation-readiness-review.py"),
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

    source = "\n".join(
        [
            read_text(root / "scripts" / "generate-no-hardware-activation-readiness-review.py"),
            read_text(root / "docs" / "metal" / "no-hardware-activation-readiness-review.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add(f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    review_path = out_dir / "no-hardware-activation-readiness-review.json"
    data = json.loads(review_path.read_text()) if review_path.exists() else {}

    add("review_schema", data.get("schema") == "h1mekartx.no_hardware_activation_readiness_review.v1", f"schema={data.get('schema')!r}")
    add("review_decision", data.get("decision") == "NO_HARDWARE_ACTIVATION_NOT_READY_EVIDENCE_REQUIRED", f"decision={data.get('decision')!r}")
    add("activation_implementation_blocked", data.get("activation_implementation_allowed") is False, f"value={data.get('activation_implementation_allowed')!r}")
    add("activation_request_blocked", data.get("activation_request_allowed") is False, f"value={data.get('activation_request_allowed')!r}")
    add("deactivation_request_blocked", data.get("deactivation_request_allowed") is False, f"value={data.get('deactivation_request_allowed')!r}")
    add("manager_submit_blocked", data.get("manager_submit_allowed") is False, f"value={data.get('manager_submit_allowed')!r}")
    add("driverkit_activation_blocked", data.get("driverkit_activation_allowed") is False, f"value={data.get('driverkit_activation_allowed')!r}")
    add("device_ownership_blocked", data.get("device_ownership_allowed") is False, f"value={data.get('device_ownership_allowed')!r}")
    add("required_no_go_count_positive", data.get("required_no_go_count", 0) > 0, f"required_no_go_count={data.get('required_no_go_count')!r}")

    gates = data.get("evidence_gates", [])
    add("evidence_gates_present", isinstance(gates, list) and len(gates) >= 8, f"count={len(gates) if isinstance(gates, list) else 'not-list'}")
    add("has_no_go_gate", any(isinstance(g, dict) and g.get("status") == "NO_GO" for g in gates), "NO_GO found")
    add("has_pass_gate", any(isinstance(g, dict) and g.get("status") == "PASS" for g in gates), "PASS found")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add("safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add("safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add("safety_review_only", sb.get("review_only") is True, f"value={sb.get('review_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add(f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_NO_HARDWARE_ACTIVATION_READINESS_REVIEW_READY" if failed_count == 0 else "FAIL_NO_HARDWARE_ACTIVATION_READINESS_REVIEW",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "review_only": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "driverkit_activation": False,
            "device_ownership_request": False,
            "live_extension_status_query": False,
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

    return "\n".join(
        [
            "# No-hardware Activation Readiness Check",
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
            "This check validates the no-hardware activation readiness review using local generator output only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, activate DriverKit, request device ownership, query live extension state, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX no-hardware activation readiness review.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "no-hardware-activation-readiness-check.json"
    md_path = out_dir / "no-hardware-activation-readiness-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
