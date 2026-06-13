#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_compositor_readiness_matrix.v1"


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


def requirement(
    req_id: str,
    name: str,
    level: str,
    status: str,
    evidence: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "id": req_id,
        "name": name,
        "level": level,
        "status": status,
        "evidence": evidence,
        "next_action": next_action,
    }


def build_matrix(
    host_summary: dict[str, Any],
    ui_sample: dict[str, Any],
    proof_schema: dict[str, Any],
    host_path: Path,
    sample_path: Path,
    schema_path: Path,
    ui_gpu_attribution: dict[str, Any] | None = None,
    ui_gpu_attribution_path: Path | None = None,
    ui_workload_correlation: dict[str, Any] | None = None,
    ui_workload_correlation_path: Path | None = None,
) -> dict[str, Any]:
    host_decisions = host_summary.get("decisions", {})
    sample_decisions = ui_sample.get("decisions", {})
    schema_decision = proof_schema.get("decision")

    target_present = host_summary.get("likely_target_present") is True
    host_result = host_decisions.get("host_diagnostics_result")
    graphics_result = host_decisions.get("graphics_stack_diagnostics_result")
    sample_result = sample_decisions.get("sample_result")
    attribution_decisions = ui_gpu_attribution.get("decisions", {}) if ui_gpu_attribution else {}
    attribution_result = attribution_decisions.get("ui_gpu_attribution_result")
    trusted_attribution_result = attribution_decisions.get("trusted_ui_gpu_attribution_result")
    rtx_attribution_result = attribution_decisions.get("rtx5070_ui_gpu_attribution_result")
    workload_decisions = ui_workload_correlation.get("decisions", {}) if ui_workload_correlation else {}
    workload_correlation_result = workload_decisions.get("ui_workload_correlation_result")
    rtx_workload_result = workload_decisions.get("rtx5070_workload_attribution_result")
    trusted_workload_result = workload_decisions.get("trusted_rtx5070_workload_attribution_result")
    ui_surface_correlation_result = workload_decisions.get("ui_surface_correlation_result")

    target_hits = host_summary.get("target_hits", {})
    bar_hints = host_summary.get("bar_inventory_hints", {})
    graphics_hits = host_summary.get("graphics_stack_hits", {})
    sample_hits = ui_sample.get("surface_hits", {})

    requirements = [
        requirement(
            "proof_schema_ready",
            "UI compositor proof schema exists and keeps acceleration claims disabled.",
            "static_contract",
            "PASS"
            if schema_decision == "UI_COMPOSITOR_PROOF_SCHEMA_READY"
            and proof_schema.get("ui_compositor_acceleration_claim_allowed_now") is False
            and proof_schema.get("metal_acceleration_claim_allowed_now") is False
            else "FAIL",
            f"decision={schema_decision!r}, ui_claim_allowed={proof_schema.get('ui_compositor_acceleration_claim_allowed_now')!r}, metal_claim_allowed={proof_schema.get('metal_acceleration_claim_allowed_now')!r}",
            "Regenerate the UI compositor proof schema and keep claim flags disabled.",
        ),
        requirement(
            "target_identity",
            "RTX 5070 target identity is visible in host diagnostics.",
            "host_diagnostics",
            "PASS" if target_present and host_result == "TARGET_PRESENT_HOST_DIAGNOSTICS" else "FAIL",
            f"host_result={host_result!r}, likely_target_present={target_present!r}, vendor_10de={target_hits.get('vendor_10de')!r}, device_2f04={target_hits.get('device_2f04')!r}",
            "Re-run host diagnostics and confirm vendor/device/IOPCIMatch visibility.",
        ),
        requirement(
            "bar_inventory",
            "BAR-like inventory hints are present.",
            "host_diagnostics",
            "PASS"
            if as_int(bar_hints.get("assigned_addresses")) > 0 or as_int(bar_hints.get("reg")) > 0
            else "BLOCKED",
            f"assigned_addresses={bar_hints.get('assigned_addresses')!r}, reg={bar_hints.get('reg')!r}",
            "Collect BAR inventory and keep it as host diagnostics only.",
        ),
        requirement(
            "graphics_stack_visibility",
            "Graphics stack diagnostics include display, framebuffer, accelerator, Metal, WindowServer, and Dock hints.",
            "graphics_stack_diagnostics",
            "PASS"
            if graphics_result == "GRAPHICS_STACK_HINTS_PRESENT"
            and as_int(graphics_hits.get("windowserver")) > 0
            and as_int(graphics_hits.get("dock")) > 0
            and as_int(graphics_hits.get("ioaccelerator")) > 0
            else "BLOCKED",
            f"graphics_result={graphics_result!r}, windowserver={graphics_hits.get('windowserver')!r}, dock={graphics_hits.get('dock')!r}, ioaccelerator={graphics_hits.get('ioaccelerator')!r}",
            "Re-run host diagnostics and inspect WindowServer/Dock/IOAccelerator visibility.",
        ),
        requirement(
            "ui_sample_capture",
            "A UI compositor sample was captured after user-visible UI activity.",
            "graphics_stack_diagnostics",
            "PASS" if sample_result == "UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_CAPTURED" else "BLOCKED",
            f"sample_result={sample_result!r}",
            "Run collect-ui-compositor-sample.sh immediately after Dock/window/Mission Control/Launchpad activity.",
        ),
        requirement(
            "ui_surface_hints",
            "UI sample contains Dock, WindowServer, Core Animation or QuartzCore, and blur/transparency hints.",
            "graphics_stack_diagnostics",
            "PASS"
            if as_int(sample_hits.get("dock")) > 0
            and as_int(sample_hits.get("windowserver")) > 0
            and (
                as_int(sample_hits.get("core_animation")) > 0
                or as_int(sample_hits.get("quartzcore")) > 0
            )
            and as_int(sample_hits.get("transparency_blur")) > 0
            else "BLOCKED",
            f"dock={sample_hits.get('dock')!r}, windowserver={sample_hits.get('windowserver')!r}, core_animation={sample_hits.get('core_animation')!r}, quartzcore={sample_hits.get('quartzcore')!r}, transparency_blur={sample_hits.get('transparency_blur')!r}",
            "Collect a focused UI sample while exercising transparency/blur and animation surfaces.",
        ),
        requirement(
            "current_ui_gpu_attribution",
            "Current UI compositor backend is attributed to a concrete GPU path.",
            "graphics_stack_diagnostics",
            "BLOCKED",
            (
                f"candidate_attribution={attribution_result!r}, "
                f"trusted_attribution={trusted_attribution_result!r}, "
                f"rtx5070_attribution={rtx_attribution_result!r}"
                if ui_gpu_attribution
                else "No UI GPU attribution candidate report is present."
            ),
            "Use UI GPU attribution diagnostics as candidate evidence only; add a trusted attribution source before claiming compositor acceleration.",
        ),
        requirement(
            "rtx5070_workload_attribution",
            "RTX 5070 work is attributed during the same UI compositor sample window.",
            "real_gpu_command_execution",
            "BLOCKED",
            (
                f"candidate_correlation={workload_correlation_result!r}, "
                f"rtx5070_workload_attribution={rtx_workload_result!r}, "
                f"trusted_workload_attribution={trusted_workload_result!r}"
                if ui_workload_correlation
                else "No RTX 5070 command execution, counter, queue, fence, or workload attribution evidence exists."
            ),
            "Do not claim UI acceleration until real GPU command/work attribution exists.",
        ),
        requirement(
            "ui_surface_correlation",
            "UI action interval, compositor timing, and RTX 5070-backed work are correlated.",
            "ui_compositor_proof",
            "BLOCKED",
            (
                f"candidate_correlation={workload_correlation_result!r}, ui_surface_correlation={ui_surface_correlation_result!r}"
                if ui_workload_correlation
                else "Current reports contain diagnostics hints only, not correlated proof."
            ),
            "Add a later correlation report after safe runtime and GPU work attribution exist.",
        ),
    ]

    fail_count = sum(1 for item in requirements if item["status"] == "FAIL")
    blocked_count = sum(1 for item in requirements if item["status"] == "BLOCKED")
    pass_count = sum(1 for item in requirements if item["status"] == "PASS")

    readiness = "INVALID" if fail_count else "NOT_PROVEN"
    if fail_count == 0 and blocked_count == 0:
        readiness = "READY_FOR_UI_COMPOSITOR_PROOF_REVIEW"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "host_summary": str(host_path),
            "ui_sample_summary": str(sample_path),
            "ui_compositor_proof_schema": str(schema_path),
            "ui_gpu_attribution_summary": str(ui_gpu_attribution_path) if ui_gpu_attribution_path else None,
            "ui_workload_correlation_report": str(ui_workload_correlation_path) if ui_workload_correlation_path else None,
        },
        "decision": readiness,
        "ui_compositor_acceleration_claim_allowed": False,
        "metal_acceleration_claim_allowed": False,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "blocked_count": blocked_count,
        "requirements": requirements,
        "safety_boundary": {
            "read_only_report_only": True,
            "uses_existing_reports_only": True,
            "runs_live_diagnostics": False,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "bar_poking": False,
            "gpu_command_submission": False,
            "rtx5070_shader_execution": False,
            "windowserver_injection": False,
            "dock_injection": False,
            "private_framework_patching": False,
            "sip_bypass": False,
            "amfi_bypass": False,
            "fake_metal_device_spoofing": False,
            "ui_compositor_proof_claim": False,
            "metal_proof_claim": False,
        },
    }


def markdown_report(matrix: dict[str, Any]) -> str:
    rows = [
        f"| `{item['id']}` | `{item['level']}` | {item['status']} | `{item['evidence'].replace('|', '\\|')}` | {item['next_action']} |"
        for item in matrix["requirements"]
    ]

    return "\n".join(
        [
            "# UI Compositor Readiness Matrix",
            "",
            f"Generated UTC: `{matrix['generated_at_utc']}`",
            "",
            f"Decision: `{matrix['decision']}`",
            "",
            f"UI compositor acceleration claim allowed: `{matrix['ui_compositor_acceleration_claim_allowed']}`",
            "",
            f"Metal acceleration claim allowed: `{matrix['metal_acceleration_claim_allowed']}`",
            "",
            f"Passed: `{matrix['pass_count']}`",
            "",
            f"Failed: `{matrix['fail_count']}`",
            "",
            f"Blocked: `{matrix['blocked_count']}`",
            "",
            "## Inputs",
            "",
            f"- Host summary: `{matrix['inputs']['host_summary']}`",
            f"- UI sample summary: `{matrix['inputs']['ui_sample_summary']}`",
            f"- UI compositor proof schema: `{matrix['inputs']['ui_compositor_proof_schema']}`",
            f"- UI GPU attribution summary: `{matrix['inputs']['ui_gpu_attribution_summary']}`",
            f"- UI workload correlation report: `{matrix['inputs']['ui_workload_correlation_report']}`",
            "",
            "## Requirements",
            "",
            "| ID | Level | Status | Evidence | Next Action |",
            "| --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This matrix reads existing JSON reports only. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, write PCI config space, access MMIO, map BAR memory, submit GPU commands, execute RTX 5070 shaders, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, spoof Metal devices, or claim RTX 5070 UI compositor or Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX UI compositor readiness matrix.")
    parser.add_argument("--host-summary", required=True, help="host-diagnostics-summary.json")
    parser.add_argument("--ui-sample-summary", required=True, help="ui-compositor-sample-summary.json")
    parser.add_argument("--proof-schema", required=True, help="ui-compositor-proof-schema.json")
    parser.add_argument("--ui-gpu-attribution-summary", default=None, help="Optional ui-gpu-attribution-summary.json")
    parser.add_argument("--ui-workload-correlation-report", default=None, help="Optional ui-workload-correlation-report.json")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    host_path = Path(args.host_summary).expanduser().resolve()
    sample_path = Path(args.ui_sample_summary).expanduser().resolve()
    schema_path = Path(args.proof_schema).expanduser().resolve()
    attribution_path = Path(args.ui_gpu_attribution_summary).expanduser().resolve() if args.ui_gpu_attribution_summary else None
    workload_path = Path(args.ui_workload_correlation_report).expanduser().resolve() if args.ui_workload_correlation_report else None
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    matrix = build_matrix(
        load_json(host_path),
        load_json(sample_path),
        load_json(schema_path),
        host_path,
        sample_path,
        schema_path,
        load_json(attribution_path) if attribution_path else None,
        attribution_path,
        load_json(workload_path) if workload_path else None,
        workload_path,
    )

    json_path = out_dir / "ui-compositor-readiness-matrix.json"
    md_path = out_dir / "ui-compositor-readiness-matrix.md"
    json_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(matrix) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {matrix['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
