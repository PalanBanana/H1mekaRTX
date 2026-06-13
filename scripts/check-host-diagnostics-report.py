#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_ui_diagnostics_check.v1"

REQUIRED_FILES = [
    "scripts/collect-host-diagnostics.sh",
    "scripts/summarize-host-diagnostics.py",
    "docs/metal/host-ui-diagnostics.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture(input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "sw_vers.txt": "ProductName:\t\tmacOS\nProductVersion:\t\t15.5\nBuildVersion:\t\t24F74\n",
        "uname.txt": "Darwin test.local 24.5.0 Darwin Kernel Version 24.5.0: root:xnu/RELEASE_X86_64 x86_64\n",
        "arch.txt": "i386\n",
        "csrutil-status.txt": "System Integrity Protection status: enabled.\n",
        "system_profiler-SPHardwareDataType.txt": "Model Name: Mac Pro\n",
        "system_profiler-SPPCIDataType.txt": "RTX 5070:\n  Vendor ID: 0x10de\n  Device ID: 0x2f04\n  Subsystem Vendor ID: 0x1458\n  Subsystem ID: 0x417e\n  Class Code: 0x030000\n",
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
        "ioreg-IODeviceTree.txt": "IODeviceTree fixture\n",
        "ioreg-IOService.txt": "IOService fixture\n",
        "ioreg-IOPCIDevice.txt": '"vendor-id" = <de100000>\n"device-id" = <042f0000>\n',
        "ioreg-IODisplayConnect.txt": "IODisplayConnect fixture\n",
        "ioreg-IOFramebuffer.txt": "IOFramebuffer fixture\n",
        "ioreg-IOAccelerator.txt": "IOAccelerator fixture\n",
        "ioreg-rtx5070-filtered.txt": '"IOPCIMatch" = "0x2f0410de"\n"assigned-addresses" = <00000000>\n"reg" = <00000000>\n"class-code" = <00000300>\n"subsystem-vendor-id" = <58140000>\n"subsystem-id" = <7e410000>\n',
        "ioreg-graphics-filtered.txt": "IODisplay IOFramebuffer IOGraphics IOAccelerator Metal GPU display accelerator\n",
        "process-windowserver-dock.txt": "100 1 Ss /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer WindowServer\n200 1 S /System/Library/CoreServices/Dock.app/Contents/MacOS/Dock Dock\n",
        "frameworks-graphics.txt": "/System/Library/Frameworks/Metal.framework\n/System/Library/Frameworks/QuartzCore.framework\n",
        "ui-preferences.txt": "0\n1\n",
        "logs-graphics-ui-last30m.txt": "WindowServer CoreAnimation QuartzCore Metal IOAccelerator IODisplay IOFramebuffer Dock blur transparency\n",
        "README.txt": "Read-only fixture.\n",
    }

    for name, content in files.items():
        (input_dir / name).write_text(content)


def run_summarizer(root: Path, input_dir: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "summarize-host-diagnostics.py"),
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
        "h1mekartx.host_ui_diagnostics_summary.v1",
        "Host diagnostics",
        "Graphics stack diagnostics",
        "UI compositor proof",
        "Metal proof",
        "NOT_CLAIMED",
        "UNPROVEN",
        "No DriverKit activation",
        "No System Extension activation",
        "No PCI config-space writes",
        "No MMIO writes",
        "No BAR mapping",
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
        "metal_acceleration_attempt\": True",
        "ui_compositor_acceleration_claim\": True",
    ]
    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "host-diagnostics"
    summary_out = out_dir / "fixture" / "summary"
    write_fixture(fixture_dir)
    generator = run_summarizer(root, fixture_dir, summary_out)
    add("summarizer_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    json_path = summary_out / "host-diagnostics-summary.json"
    md_path = summary_out / "host-diagnostics-summary.md"
    add("summary_json_exists", json_path.exists(), "present" if json_path.exists() else "missing")
    add("summary_md_exists", md_path.exists(), "present" if md_path.exists() else "missing")

    data = json.loads(json_path.read_text()) if json_path.exists() else {}
    add("summary_schema", data.get("schema") == "h1mekartx.host_ui_diagnostics_summary.v1", f"schema={data.get('schema')!r}")
    add("target_present", data.get("likely_target_present") is True, f"value={data.get('likely_target_present')!r}")
    add("host_result", data.get("decisions", {}).get("host_diagnostics_result") == "TARGET_PRESENT_HOST_DIAGNOSTICS", f"result={data.get('decisions', {}).get('host_diagnostics_result')!r}")
    add("graphics_result", data.get("decisions", {}).get("graphics_stack_diagnostics_result") == "GRAPHICS_STACK_HINTS_PRESENT", f"result={data.get('decisions', {}).get('graphics_stack_diagnostics_result')!r}")
    add("ui_unproven", data.get("decisions", {}).get("ui_compositor_proof_result") == "UNPROVEN", f"result={data.get('decisions', {}).get('ui_compositor_proof_result')!r}")
    add("metal_unproven", data.get("decisions", {}).get("metal_proof_result") == "UNPROVEN", f"result={data.get('decisions', {}).get('metal_proof_result')!r}")
    add("ui_not_claimed", data.get("decisions", {}).get("rtx5070_ui_acceleration_claim") == "NOT_CLAIMED", f"claim={data.get('decisions', {}).get('rtx5070_ui_acceleration_claim')!r}")
    add("metal_not_claimed", data.get("decisions", {}).get("rtx5070_metal_acceleration_claim") == "NOT_CLAIMED", f"claim={data.get('decisions', {}).get('rtx5070_metal_acceleration_claim')!r}")

    classification = data.get("classification", {})
    add("classification_host", classification.get("host_diagnostics") is True, f"value={classification.get('host_diagnostics')!r}")
    add("classification_graphics", classification.get("graphics_stack_diagnostics") is True, f"value={classification.get('graphics_stack_diagnostics')!r}")
    add("classification_runtime_false", classification.get("runtime_probe") is False, f"value={classification.get('runtime_probe')!r}")
    add("classification_gpu_execution_false", classification.get("real_gpu_command_execution") is False, f"value={classification.get('real_gpu_command_execution')!r}")
    add("classification_ui_false", classification.get("ui_compositor_proof") is False, f"value={classification.get('ui_compositor_proof')!r}")
    add("classification_metal_false", classification.get("metal_proof") is False, f"value={classification.get('metal_proof')!r}")

    safety = data.get("safety_boundary", {})
    for key in [
        "read_only",
        "runs_ioreg",
        "runs_system_profiler",
        "runs_log_show",
    ]:
        add(f"safety_true:{key}", safety.get(key) is True, f"value={safety.get(key)!r}")

    for key in [
        "driverkit_activation",
        "system_extension_activation",
        "device_ownership_request",
        "pci_config_writes",
        "mmio_reads",
        "mmio_writes",
        "bar_mapping",
        "bar_poking",
        "gpu_reset",
        "firmware_loading",
        "gsp_initialization",
        "display_engine_init",
        "framebuffer_init",
        "gpu_command_submission",
        "rtx5070_shader_execution",
        "metal_acceleration_attempt",
        "ui_compositor_acceleration_claim",
    ]:
        add(f"safety_false:{key}", safety.get(key) is False, f"value={safety.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_HOST_UI_DIAGNOSTICS_READY" if failed_count == 0 else "FAIL_HOST_UI_DIAGNOSTICS_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "fixture_dir": str(fixture_dir),
        "summary_out": str(summary_out),
        "safety_boundary": {
            "read_only_static_check": True,
            "local_fixture_only": True,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "gpu_command_submission": False,
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
            "# Host + UI Compositor Diagnostics Check",
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
            "This check uses local fixtures only. It validates host diagnostics and graphics stack diagnostics labeling without DriverKit activation, System Extension activation, device ownership, PCI config writes, MMIO, BAR mapping, GPU command submission, UI compositor proof, or Metal proof.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX host + UI compositor diagnostics reports.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)
    json_path = out_dir / "host-ui-diagnostics-check.json"
    md_path = out_dir / "host-ui-diagnostics-check.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
