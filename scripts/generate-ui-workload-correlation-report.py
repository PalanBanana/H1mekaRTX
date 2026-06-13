#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_workload_correlation_report.v1"


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


def build_signal(name: str, level: str, status: str, evidence: str) -> dict[str, str]:
    return {
        "name": name,
        "level": level,
        "status": status,
        "evidence": evidence,
    }


def build_report(
    host_summary: dict[str, Any],
    ui_sample: dict[str, Any],
    ui_gpu_attribution: dict[str, Any],
    host_path: Path,
    sample_path: Path,
    attribution_path: Path,
) -> dict[str, Any]:
    host_decisions = host_summary.get("decisions", {})
    sample_decisions = ui_sample.get("decisions", {})
    attribution_decisions = ui_gpu_attribution.get("decisions", {})

    target_hits = host_summary.get("target_hits", {})
    sample_hits = ui_sample.get("surface_hits", {})
    attribution_hits = ui_gpu_attribution.get("candidate_hits", {})

    host_result = host_decisions.get("host_diagnostics_result")
    sample_result = sample_decisions.get("sample_result")
    attribution_result = attribution_decisions.get("ui_gpu_attribution_result")
    trusted_attribution = attribution_decisions.get("trusted_ui_gpu_attribution_result")
    rtx_attribution = attribution_decisions.get("rtx5070_ui_gpu_attribution_result")

    sample_window = ui_sample.get("metadata", {}).get("log_window", "")
    attribution_window = ui_gpu_attribution.get("metadata", {}).get("log_window", "")

    host_target_visible = (
        host_summary.get("likely_target_present") is True
        and host_result == "TARGET_PRESENT_HOST_DIAGNOSTICS"
    )
    ui_sample_captured = sample_result == "UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_CAPTURED"
    ui_surface_hints = (
        as_int(sample_hits.get("windowserver")) > 0
        and as_int(sample_hits.get("dock")) > 0
        and (
            as_int(sample_hits.get("core_animation")) > 0
            or as_int(sample_hits.get("quartzcore")) > 0
        )
    )
    attribution_candidates = attribution_result == "UI_GPU_ATTRIBUTION_CANDIDATES_CAPTURED"
    rtx_candidate_hints = (
        as_int(target_hits.get("vendor_10de")) > 0
        and (
            as_int(target_hits.get("device_2f04")) > 0
            or as_int(target_hits.get("iopcimatch_2f0410de")) > 0
        )
        and (
            as_int(attribution_hits.get("nvidia")) > 0
            or as_int(attribution_hits.get("rtx5070")) > 0
        )
    )
    sample_windows_recorded = bool(sample_window) and bool(attribution_window)

    signals = [
        build_signal(
            "host_target_visible",
            "host_diagnostics",
            "PASS" if host_target_visible else "BLOCKED",
            f"host_result={host_result!r}, vendor_10de={target_hits.get('vendor_10de')!r}, device_2f04={target_hits.get('device_2f04')!r}",
        ),
        build_signal(
            "ui_sample_captured",
            "graphics_stack_diagnostics",
            "PASS" if ui_sample_captured else "BLOCKED",
            f"sample_result={sample_result!r}, sample_window={sample_window!r}",
        ),
        build_signal(
            "ui_surface_hints",
            "graphics_stack_diagnostics",
            "PASS" if ui_surface_hints else "BLOCKED",
            f"windowserver={sample_hits.get('windowserver')!r}, dock={sample_hits.get('dock')!r}, core_animation={sample_hits.get('core_animation')!r}, quartzcore={sample_hits.get('quartzcore')!r}",
        ),
        build_signal(
            "ui_gpu_attribution_candidates",
            "graphics_stack_diagnostics",
            "PASS" if attribution_candidates else "BLOCKED",
            f"candidate_attribution={attribution_result!r}, trusted_attribution={trusted_attribution!r}, rtx5070_attribution={rtx_attribution!r}",
        ),
        build_signal(
            "rtx5070_candidate_hints",
            "graphics_stack_diagnostics",
            "PASS" if rtx_candidate_hints else "BLOCKED",
            f"host_vendor_10de={target_hits.get('vendor_10de')!r}, host_device_2f04={target_hits.get('device_2f04')!r}, attribution_nvidia={attribution_hits.get('nvidia')!r}, attribution_rtx5070={attribution_hits.get('rtx5070')!r}",
        ),
        build_signal(
            "sample_windows_recorded",
            "graphics_stack_diagnostics",
            "PASS" if sample_windows_recorded else "BLOCKED",
            f"sample_window={sample_window!r}, attribution_window={attribution_window!r}",
        ),
        build_signal(
            "trusted_rtx5070_workload_attribution",
            "real_gpu_command_execution",
            "BLOCKED",
            "No command queue, fence, counter, memory movement, shader execution, or trusted RTX 5070 workload attribution is present.",
        ),
        build_signal(
            "ui_surface_to_rtx5070_work_correlation",
            "ui_compositor_proof",
            "BLOCKED",
            "Candidate diagnostics are not a timestamped proof that WindowServer/Core Animation work executed on RTX 5070.",
        ),
    ]

    blocked_count = sum(1 for item in signals if item["status"] == "BLOCKED")
    pass_count = sum(1 for item in signals if item["status"] == "PASS")
    candidate_ready = (
        host_target_visible
        and ui_sample_captured
        and ui_surface_hints
        and attribution_candidates
        and sample_windows_recorded
    )

    candidate_result = (
        "UI_WORKLOAD_CORRELATION_CANDIDATES_CAPTURED"
        if candidate_ready
        else "INSUFFICIENT_UI_WORKLOAD_CORRELATION_CANDIDATES"
    )

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "host_summary": str(host_path),
            "ui_sample_summary": str(sample_path),
            "ui_gpu_attribution_summary": str(attribution_path),
        },
        "classification": {
            "static_contract": False,
            "host_diagnostics": True,
            "graphics_stack_diagnostics": True,
            "runtime_probe": False,
            "real_gpu_command_execution": False,
            "ui_compositor_proof": False,
            "metal_proof": False,
        },
        "decisions": {
            "ui_workload_correlation_result": candidate_result,
            "rtx5070_workload_attribution_result": "UNPROVEN",
            "trusted_rtx5070_workload_attribution_result": "UNPROVEN",
            "real_gpu_command_execution_result": "NOT_ATTEMPTED",
            "ui_surface_correlation_result": "UNPROVEN",
            "ui_compositor_proof_result": "UNPROVEN",
            "metal_proof_result": "UNPROVEN",
            "rtx5070_ui_acceleration_claim": "NOT_CLAIMED",
            "rtx5070_metal_acceleration_claim": "NOT_CLAIMED",
        },
        "sample_window": {
            "ui_sample_log_window": sample_window,
            "ui_gpu_attribution_log_window": attribution_window,
        },
        "signals": signals,
        "pass_count": pass_count,
        "blocked_count": blocked_count,
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
            "sip_bypass": False,
            "amfi_bypass": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "gpu_command_submission": False,
            "rtx5070_shader_execution": False,
            "rtx5070_memory_movement": False,
            "trusted_rtx5070_workload_attribution_claim": False,
            "ui_compositor_proof_claim": False,
            "metal_proof_claim": False,
        },
    }


def signal_rows(signals: list[dict[str, str]]) -> list[str]:
    return [
        f"| `{item['name']}` | `{item['level']}` | {item['status']} | `{item['evidence'].replace('|', '\\|')}` |"
        for item in signals
    ]


def markdown_report(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# UI Workload Correlation Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            "## Decisions",
            "",
            f"- UI workload correlation result: `{report['decisions']['ui_workload_correlation_result']}`",
            f"- RTX 5070 workload attribution result: `{report['decisions']['rtx5070_workload_attribution_result']}`",
            f"- Trusted RTX 5070 workload attribution result: `{report['decisions']['trusted_rtx5070_workload_attribution_result']}`",
            f"- Real GPU command execution result: `{report['decisions']['real_gpu_command_execution_result']}`",
            f"- UI surface correlation result: `{report['decisions']['ui_surface_correlation_result']}`",
            f"- UI compositor proof result: `{report['decisions']['ui_compositor_proof_result']}`",
            f"- Metal proof result: `{report['decisions']['metal_proof_result']}`",
            f"- RTX 5070 UI acceleration claim: `{report['decisions']['rtx5070_ui_acceleration_claim']}`",
            f"- RTX 5070 Metal acceleration claim: `{report['decisions']['rtx5070_metal_acceleration_claim']}`",
            "",
            "## Inputs",
            "",
            f"- Host summary: `{report['inputs']['host_summary']}`",
            f"- UI sample summary: `{report['inputs']['ui_sample_summary']}`",
            f"- UI GPU attribution summary: `{report['inputs']['ui_gpu_attribution_summary']}`",
            "",
            "## Sample Window",
            "",
            f"- UI sample log window: `{report['sample_window']['ui_sample_log_window']}`",
            f"- UI GPU attribution log window: `{report['sample_window']['ui_gpu_attribution_log_window']}`",
            "",
            "## Signals",
            "",
            "| Signal | Level | Status | Evidence |",
            "| --- | --- | --- | --- |",
            *signal_rows(report["signals"]),
            "",
            "## Safety Boundary",
            "",
            "This report reads existing JSON reports only. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, write PCI config space, access MMIO, map BAR memory, submit GPU commands, move memory on RTX 5070, execute RTX 5070 shaders, claim trusted RTX 5070 workload attribution, prove UI compositor acceleration, or prove Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX UI workload correlation report.")
    parser.add_argument("--host-summary", required=True, help="host-diagnostics-summary.json")
    parser.add_argument("--ui-sample-summary", required=True, help="ui-compositor-sample-summary.json")
    parser.add_argument("--ui-gpu-attribution-summary", required=True, help="ui-gpu-attribution-summary.json")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    host_path = Path(args.host_summary).expanduser().resolve()
    sample_path = Path(args.ui_sample_summary).expanduser().resolve()
    attribution_path = Path(args.ui_gpu_attribution_summary).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(
        load_json(host_path),
        load_json(sample_path),
        load_json(attribution_path),
        host_path,
        sample_path,
        attribution_path,
    )

    json_path = out_dir / "ui-workload-correlation-report.json"
    md_path = out_dir / "ui-workload-correlation-report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"UI workload correlation: {report['decisions']['ui_workload_correlation_result']}")
    print("RTX 5070 workload attribution: UNPROVEN")
    print("UI compositor proof: UNPROVEN")
    print("Metal proof: UNPROVEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
