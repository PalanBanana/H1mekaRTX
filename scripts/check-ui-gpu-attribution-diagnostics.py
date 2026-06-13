#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_gpu_attribution_diagnostics_check.v1"

REQUIRED_FILES = [
    "scripts/collect-ui-gpu-attribution.sh",
    "scripts/summarize-ui-gpu-attribution.py",
    "docs/metal/ui-gpu-attribution-diagnostics.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture(input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "attribution-metadata.json": json.dumps(
            {
                "schema": "h1mekartx.ui_gpu_attribution_metadata.v1",
                "logWindow": "10m",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "sw_vers.txt": "ProductName:\t\tmacOS\nProductVersion:\t\t15.5\nBuildVersion:\t\t24F74\n",
        "system_profiler-SPDisplaysDataType.txt": "NVIDIA RTX 5070:\n  Chipset Model: NVIDIA RTX 5070\n  Vendor: NVIDIA (0x10de)\n  Device ID: 0x2f04\n  Metal Support: Unsupported\n",
        "system_profiler-SPDisplaysDataType.json": json.dumps(
            {
                "SPDisplaysDataType": [
                    {
                        "_name": "NVIDIA RTX 5070",
                        "sppci_model": "NVIDIA RTX 5070",
                        "spdisplays_vendor": "NVIDIA (0x10de)",
                        "spdisplays_device-id": "0x2f04",
                        "spdisplays_metal": "Unsupported",
                    }
                ]
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "ioreg-IOFramebuffer.txt": "IOFramebuffer fixture display framebuffer\n",
        "ioreg-IOAccelerator.txt": "IOAccelerator fixture accelerator GPU\n",
        "ioreg-IODisplayConnect.txt": "IODisplayConnect fixture display\n",
        "process-windowserver-dock.txt": "100 1 Ss WindowServer WindowServer\n200 1 S Dock Dock\n",
        "ioreg-display-accelerator-filtered.txt": "IOFramebuffer IOAccelerator IODisplay Metal GPU NVIDIA 10de 2f04 display accelerator\n",
        "logs-ui-gpu-attribution.txt": "WindowServer Dock IOAccelerator IOFramebuffer IODisplay Metal GPU display\n",
        "README.txt": "Read-only fixture.\n",
    }
    for name, content in files.items():
        (input_dir / name).write_text(content)


def run_summarizer(root: Path, input_dir: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "summarize-ui-gpu-attribution.py"),
            "--input-dir",
            str(input_dir),
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
        "h1mekartx.ui_gpu_attribution_summary.v1",
        "UI GPU attribution diagnostics",
        "UI_GPU_ATTRIBUTION_CANDIDATES_CAPTURED",
        "Trusted UI GPU attribution: not proven",
        "trusted_ui_gpu_attribution_result",
        "rtx5070_ui_gpu_attribution_result",
        "UNPROVEN",
        "NOT_CLAIMED",
        "No DriverKit activation",
        "No System Extension activation",
        "No WindowServer injection",
        "No Dock injection",
        "No MMIO reads",
        "No GPU command submission",
    ]
    for term in required_terms:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    forbidden_terms = [
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "Configuration" + "Write",
        "Memory" + "Write",
        "Create" + "Memory" + "Map",
        "trusted_ui_gpu_attribution_claim\": True",
        "ui_compositor_proof_claim\": True",
        "metal_proof_claim\": True",
        "csrutil disable",
        "spctl --master-disable",
    ]
    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "ui-gpu-attribution"
    summary_out = out_dir / "fixture" / "summary"
    write_fixture(fixture_dir)
    generator = run_summarizer(root, fixture_dir, summary_out)
    add("summarizer_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    json_path = summary_out / "ui-gpu-attribution-summary.json"
    md_path = summary_out / "ui-gpu-attribution-summary.md"
    add("summary_json_exists", json_path.exists(), "present" if json_path.exists() else "missing")
    add("summary_md_exists", md_path.exists(), "present" if md_path.exists() else "missing")

    data = json.loads(json_path.read_text()) if json_path.exists() else {}
    decisions = data.get("decisions", {})
    add("summary_schema", data.get("schema") == "h1mekartx.ui_gpu_attribution_summary.v1", f"schema={data.get('schema')!r}")
    add("candidate_result", decisions.get("ui_gpu_attribution_result") == "UI_GPU_ATTRIBUTION_CANDIDATES_CAPTURED", f"result={decisions.get('ui_gpu_attribution_result')!r}")
    add("trusted_unproven", decisions.get("trusted_ui_gpu_attribution_result") == "UNPROVEN", f"result={decisions.get('trusted_ui_gpu_attribution_result')!r}")
    add("rtx_unproven", decisions.get("rtx5070_ui_gpu_attribution_result") == "UNPROVEN", f"result={decisions.get('rtx5070_ui_gpu_attribution_result')!r}")
    add("ui_unproven", decisions.get("ui_compositor_proof_result") == "UNPROVEN", f"result={decisions.get('ui_compositor_proof_result')!r}")
    add("metal_unproven", decisions.get("metal_proof_result") == "UNPROVEN", f"result={decisions.get('metal_proof_result')!r}")
    add("ui_not_claimed", decisions.get("rtx5070_ui_acceleration_claim") == "NOT_CLAIMED", f"claim={decisions.get('rtx5070_ui_acceleration_claim')!r}")
    add("metal_not_claimed", decisions.get("rtx5070_metal_acceleration_claim") == "NOT_CLAIMED", f"claim={decisions.get('rtx5070_metal_acceleration_claim')!r}")

    safety = data.get("safety_boundary", {})
    for key in ["read_only", "runs_ioreg", "runs_system_profiler", "runs_log_show"]:
        add(f"safety_true:{key}", safety.get(key) is True, f"value={safety.get(key)!r}")
    for key in [
        "driverkit_activation",
        "system_extension_activation",
        "device_ownership_request",
        "process_injection",
        "windowserver_injection",
        "dock_injection",
        "private_framework_patching",
        "sip_bypass",
        "amfi_bypass",
        "pci_config_writes",
        "mmio_reads",
        "mmio_writes",
        "bar_mapping",
        "gpu_command_submission",
        "rtx5070_shader_execution",
        "trusted_ui_gpu_attribution_claim",
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
        "decision": "PASS_UI_GPU_ATTRIBUTION_DIAGNOSTICS_READY" if failed_count == 0 else "FAIL_UI_GPU_ATTRIBUTION_DIAGNOSTICS_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_fixture_check": True,
            "driverkit_activation": False,
            "system_extension_activation": False,
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
            "trusted_ui_gpu_attribution_claim": False,
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
            "# UI GPU Attribution Diagnostics Check",
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
            "This check validates UI GPU attribution diagnostics using local fixtures only. It does not activate DriverKit or System Extensions, request device ownership, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, write PCI config space, access MMIO, map BAR memory, submit GPU commands, claim trusted UI GPU attribution, prove UI compositor acceleration, or prove Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX UI GPU attribution diagnostics.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)
    json_path = out_dir / "ui-gpu-attribution-diagnostics-check.json"
    md_path = out_dir / "ui-gpu-attribution-diagnostics-check.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")
    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
