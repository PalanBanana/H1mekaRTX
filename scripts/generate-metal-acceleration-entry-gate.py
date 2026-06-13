#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_acceleration_entry_gate.v1"


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"Missing JSON input: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON input: {path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"JSON input must be an object: {path}")
    return data


def as_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def gate_item(
    gate_id: str,
    name: str,
    level: str,
    status: str,
    evidence: str,
    required_for: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "id": gate_id,
        "name": name,
        "level": level,
        "status": status,
        "evidence": evidence,
        "required_for": required_for,
        "next_action": next_action,
    }


def build_gate(
    host_summary: dict[str, Any],
    bar_summary: dict[str, Any],
    readiness_matrix: dict[str, Any],
    workload_report: dict[str, Any],
    host_path: Path,
    bar_path: Path,
    readiness_path: Path,
    workload_path: Path,
) -> dict[str, Any]:
    host_decisions = host_summary.get("decisions", {})
    workload_decisions = workload_report.get("decisions", {})
    target_hits = host_summary.get("target_hits", {})
    bar_hints = host_summary.get("bar_inventory_hints", {})

    target_visible = (
        host_summary.get("likely_target_present") is True
        and host_decisions.get("host_diagnostics_result") == "TARGET_PRESENT_HOST_DIAGNOSTICS"
    )
    bar_inventory_present = (
        bar_summary.get("schema") == "h1mekartx.bar_inventory_summary.v1"
        and bar_summary.get("likely_target_present") is True
    )
    bar_like_hints = as_int(bar_hints.get("assigned_addresses")) > 0 or as_int(bar_hints.get("reg")) > 0
    ui_candidate_correlation = (
        workload_decisions.get("ui_workload_correlation_result")
        == "UI_WORKLOAD_CORRELATION_CANDIDATES_CAPTURED"
    )

    gates = [
        gate_item(
            "metal-entry-001",
            "RTX 5070 host identity is visible.",
            "host_diagnostics",
            "PASS" if target_visible else "BLOCKED",
            f"host_result={host_decisions.get('host_diagnostics_result')!r}, vendor_10de={target_hits.get('vendor_10de')!r}, device_2f04={target_hits.get('device_2f04')!r}",
            "runtime_probe_preflight",
            "Re-run Phase 1 host diagnostics until RTX 5070 identity is visible.",
        ),
        gate_item(
            "metal-entry-002",
            "BAR inventory summary exists as host diagnostics.",
            "host_diagnostics",
            "PASS" if bar_inventory_present or bar_like_hints else "BLOCKED",
            f"bar_schema={bar_summary.get('schema')!r}, likely_target_present={bar_summary.get('likely_target_present')!r}, assigned_addresses={bar_hints.get('assigned_addresses')!r}, reg={bar_hints.get('reg')!r}",
            "runtime_probe_preflight",
            "Collect BAR inventory as host diagnostics only.",
        ),
        gate_item(
            "metal-entry-003",
            "UI compositor candidate correlation exists.",
            "graphics_stack_diagnostics",
            "PASS" if ui_candidate_correlation else "BLOCKED",
            f"ui_workload_correlation={workload_decisions.get('ui_workload_correlation_result')!r}",
            "runtime_probe_preflight",
            "Generate UI workload correlation candidate report from existing diagnostics.",
        ),
        gate_item(
            "metal-entry-004",
            "Read-only runtime probe harness is implemented and reviewed.",
            "runtime_probe",
            "BLOCKED",
            "No runtime probe harness report exists in the current Phase 1/2 bundle.",
            "driverkit_matching",
            "Next: add a dry-run/read-only runtime probe harness contract before live hardware access.",
        ),
        gate_item(
            "metal-entry-005",
            "DriverKit/System Extension activation path is approved and reversible.",
            "runtime_probe",
            "BLOCKED",
            "No approved activation/deactivation gate is present in this Phase 1/2 bundle.",
            "pcidriverkit_matching",
            "Prepare a reversible DriverKit/System Extension activation gate only after preflight review.",
        ),
        gate_item(
            "metal-entry-006",
            "RTX 5070 PCI provider matching is verified.",
            "runtime_probe",
            "BLOCKED",
            "No live provider attach or IOPCIDevice ownership proof exists.",
            "readonly_bar_probe",
            "Verify provider matching after signed activation is approved.",
        ),
        gate_item(
            "metal-entry-007",
            "Read-only BAR probe evidence exists.",
            "runtime_probe",
            "BLOCKED",
            "No read-only BAR mapping or register-read evidence exists.",
            "command_submission_research",
            "Only consider read-only BAR probing after provider matching and safety policy review.",
        ),
        gate_item(
            "metal-entry-008",
            "RTX 5070 command execution is proven.",
            "real_gpu_command_execution",
            "BLOCKED",
            f"rtx5070_workload_attribution={workload_decisions.get('rtx5070_workload_attribution_result')!r}, real_gpu_command_execution={workload_decisions.get('real_gpu_command_execution_result')!r}",
            "metal_acceleration_implementation",
            "Prove command submission, memory movement, timing, and correctness before Metal acceleration claims.",
        ),
        gate_item(
            "metal-entry-009",
            "macOS UI compositor proof exists.",
            "ui_compositor_proof",
            "BLOCKED",
            f"readiness_decision={readiness_matrix.get('decision')!r}, ui_claim_allowed={readiness_matrix.get('ui_compositor_acceleration_claim_allowed')!r}",
            "metal_acceleration_implementation",
            "Correlate WindowServer/Core Animation/Dock UI work with RTX 5070-backed execution.",
        ),
        gate_item(
            "metal-entry-010",
            "Metal-facing proof exists.",
            "metal_proof",
            "BLOCKED",
            f"metal_claim_allowed={readiness_matrix.get('metal_acceleration_claim_allowed')!r}, metal_proof={workload_decisions.get('metal_proof_result')!r}",
            "metal_acceleration_claim",
            "Do not claim RTX 5070 Metal acceleration until a verified Metal-facing workload runs on RTX 5070.",
        ),
    ]

    blocked_required = [item for item in gates if item["status"] != "PASS"]
    pass_count = sum(1 for item in gates if item["status"] == "PASS")

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "host_summary": str(host_path),
            "bar_inventory_summary": str(bar_path),
            "ui_compositor_readiness_matrix": str(readiness_path),
            "ui_workload_correlation_report": str(workload_path),
        },
        "decision": "METAL_ACCELERATION_IMPLEMENTATION_NOT_READY",
        "plain_answer": {
            "metal_research_development": "IN_PROGRESS_NOW",
            "runtime_probe_development": "NEXT_PHASE",
            "real_rtx5070_metal_acceleration_implementation": "BLOCKED",
            "why": "Host/UI diagnostics are now present, but runtime probe, DriverKit matching, read-only BAR probe, real command execution, UI compositor proof, and Metal-facing proof are still missing.",
        },
        "phase_answer": {
            "current_phase": "Phase 1 + Phase 2 diagnostics with Phase 3 entry gate",
            "next_phase": "Phase 3 runtime probe preflight and read-only harness contract",
            "metal_acceleration_starts_after": [
                "Phase 3 runtime probe evidence",
                "Phase 4/5 reversible DriverKit/System Extension activation gate",
                "Phase 6 PCIDriverKit device matching and read-only BAR probe",
                "Phase 7 real GPU command submission proof",
                "Phase 8 UI compositor proof",
                "Phase 9 Metal-facing proof",
            ],
        },
        "allowed_now": [
            "host diagnostics",
            "graphics stack diagnostics",
            "report-only correlation",
            "runtime probe preflight design",
            "read-only runtime probe harness contract",
            "public Metal reference workloads on the existing system Metal device",
        ],
        "blocked_now": [
            "RTX 5070 Metal acceleration implementation",
            "RTX 5070 shader execution",
            "hardware command submission",
            "DriverKit activation",
            "System Extension activation request",
            "IOPCIDevice ownership request",
            "PCI config-space writes",
            "MMIO reads",
            "MMIO writes",
            "BAR mapping",
            "BAR poking",
            "firmware loading",
            "GSP initialization",
            "display engine initialization",
            "framebuffer initialization",
            "GPU reset logic",
            "private graphics framework patching",
            "fake Metal device spoofing",
        ],
        "gate_pass_count": pass_count,
        "gate_blocked_count": len(blocked_required),
        "gates": gates,
        "claims": {
            "rtx5070_ui_acceleration_claim_allowed": False,
            "rtx5070_metal_acceleration_claim_allowed": False,
            "real_gpu_command_execution_claim_allowed": False,
        },
        "safety_boundary": {
            "read_only_report_only": True,
            "uses_existing_reports_only": True,
            "runs_live_diagnostics": False,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "process_injection": False,
            "windowserver_injection": False,
            "dock_injection": False,
            "private_framework_patching": False,
            "fake_metal_device_spoofing": False,
            "sip_bypass": False,
            "amfi_bypass": False,
            "pci_config_reads": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "bar_poking": False,
            "gpu_command_submission": False,
            "rtx5070_shader_execution": False,
            "rtx5070_memory_movement": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
            "ui_compositor_proof_claim": False,
            "metal_proof_claim": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    gate_rows = [
        f"| `{item['id']}` | `{item['level']}` | {item['status']} | {item['name']} | `{item['evidence'].replace('|', '\\|')}` | {item['next_action']} |"
        for item in data["gates"]
    ]
    allowed = [f"- {item}" for item in data["allowed_now"]]
    blocked = [f"- {item}" for item in data["blocked_now"]]
    phases = [f"- {item}" for item in data["phase_answer"]["metal_acceleration_starts_after"]]

    return "\n".join(
        [
            "# Metal Acceleration Entry Gate",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            "## Plain Answer",
            "",
            f"- Metal research development: `{data['plain_answer']['metal_research_development']}`",
            f"- Runtime probe development: `{data['plain_answer']['runtime_probe_development']}`",
            f"- Real RTX 5070 Metal acceleration implementation: `{data['plain_answer']['real_rtx5070_metal_acceleration_implementation']}`",
            f"- Why: {data['plain_answer']['why']}",
            "",
            "## Phase Answer",
            "",
            f"- Current phase: `{data['phase_answer']['current_phase']}`",
            f"- Next phase: `{data['phase_answer']['next_phase']}`",
            "",
            "Real Metal acceleration can start only after:",
            "",
            *phases,
            "",
            "## Inputs",
            "",
            f"- Host summary: `{data['inputs']['host_summary']}`",
            f"- BAR inventory summary: `{data['inputs']['bar_inventory_summary']}`",
            f"- UI compositor readiness matrix: `{data['inputs']['ui_compositor_readiness_matrix']}`",
            f"- UI workload correlation report: `{data['inputs']['ui_workload_correlation_report']}`",
            "",
            "## Allowed Now",
            "",
            *allowed,
            "",
            "## Blocked Now",
            "",
            *blocked,
            "",
            "## Gates",
            "",
            f"Passed: `{data['gate_pass_count']}`",
            "",
            f"Blocked: `{data['gate_blocked_count']}`",
            "",
            "| Gate | Level | Status | Name | Evidence | Next Action |",
            "| --- | --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Claims",
            "",
            f"- RTX 5070 UI acceleration claim allowed: `{data['claims']['rtx5070_ui_acceleration_claim_allowed']}`",
            f"- RTX 5070 Metal acceleration claim allowed: `{data['claims']['rtx5070_metal_acceleration_claim_allowed']}`",
            f"- Real GPU command execution claim allowed: `{data['claims']['real_gpu_command_execution_claim_allowed']}`",
            "",
            "## Safety Boundary",
            "",
            "This gate reads existing JSON reports only. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, spoof Metal devices, read or write PCI config space, access MMIO, map BAR memory, submit GPU commands, move memory on RTX 5070, execute RTX 5070 shaders, load firmware, initialize GSP, initialize display paths, initialize framebuffer, reset the GPU, claim UI compositor proof, or claim Metal proof.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX Metal acceleration entry gate.")
    parser.add_argument("--host-summary", required=True, help="host-diagnostics-summary.json")
    parser.add_argument("--bar-inventory-summary", required=True, help="bar-inventory-summary.json")
    parser.add_argument("--ui-compositor-readiness-matrix", required=True, help="ui-compositor-readiness-matrix.json")
    parser.add_argument("--ui-workload-correlation-report", required=True, help="ui-workload-correlation-report.json")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    host_path = Path(args.host_summary).expanduser().resolve()
    bar_path = Path(args.bar_inventory_summary).expanduser().resolve()
    readiness_path = Path(args.ui_compositor_readiness_matrix).expanduser().resolve()
    workload_path = Path(args.ui_workload_correlation_report).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_gate(
        load_json(host_path),
        load_json(bar_path),
        load_json(readiness_path),
        load_json(workload_path),
        host_path,
        bar_path,
        readiness_path,
        workload_path,
    )

    json_path = out_dir / "metal-acceleration-entry-gate.json"
    md_path = out_dir / "metal-acceleration-entry-gate.md"
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    print(f"Real RTX 5070 Metal acceleration implementation: {data['plain_answer']['real_rtx5070_metal_acceleration_implementation']}")
    print(f"Next phase: {data['phase_answer']['next_phase']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
