#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_compositor_proof_schema_check.v1"

REQUIRED_FILES = [
    "scripts/generate-ui-compositor-proof-schema.py",
    "docs/metal/ui-compositor-proof-schema.md",
]

REQUIRED_SURFACES = [
    "Dock movement",
    "Dock magnification",
    "Window move",
    "Window resize",
    "Mission Control",
    "Launchpad",
    "Transparency and blur",
    "Menu bar and sidebar translucency",
]

REQUIRED_EVIDENCE_IDS = [
    "target_identity",
    "bar_inventory",
    "graphics_stack_visibility",
    "current_ui_gpu_attribution",
    "windowserver_coreanimation_timing",
    "rtx5070_gpu_workload_attribution",
    "ui_surface_correlation",
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
            str(root / "scripts" / "generate-ui-compositor-proof-schema.py"),
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
        "UI_COMPOSITOR_PROOF_SCHEMA_READY",
        "ui_compositor_acceleration_claim_allowed_now",
        "metal_acceleration_claim_allowed_now",
        "WindowServer",
        "Core Animation",
        "QuartzCore",
        "Dock",
        "Mission Control",
        "Launchpad",
        "Transparency and blur",
        "GPU-backed compositor attribution",
        "UI compositor acceleration may be claimed only after",
        "Spoofing a Metal device",
        "Patching private frameworks",
        "Bypassing SIP or AMFI",
        "Injecting into WindowServer or Dock",
    ]
    for term in required_terms:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    forbidden_terms = [
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "Configuration" + "Write",
        "Memory" + "Write",
        "Create" + "Memory" + "Map",
        "ui_compositor_acceleration_claim_allowed_now\": True",
        "metal_acceleration_claim_allowed_now\": True",
        "ui_compositor_proof_claim\": True",
        "metal_proof_claim\": True",
        "csrutil disable",
        "spctl --master-disable",
    ]
    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    generated = run_generator(root, out_dir)
    add("generator_returncode", generated["returncode"] == 0, f"returncode={generated['returncode']}")

    json_path = out_dir / "ui-compositor-proof-schema.json"
    md_path = out_dir / "ui-compositor-proof-schema.md"
    add("schema_json_exists", json_path.exists(), "present" if json_path.exists() else "missing")
    add("schema_md_exists", md_path.exists(), "present" if md_path.exists() else "missing")

    data = json.loads(json_path.read_text()) if json_path.exists() else {}
    add("schema", data.get("schema") == "h1mekartx.ui_compositor_proof_schema.v1", f"schema={data.get('schema')!r}")
    add("decision", data.get("decision") == "UI_COMPOSITOR_PROOF_SCHEMA_READY", f"decision={data.get('decision')!r}")
    add("ui_claim_not_allowed", data.get("ui_compositor_acceleration_claim_allowed_now") is False, f"value={data.get('ui_compositor_acceleration_claim_allowed_now')!r}")
    add("metal_claim_not_allowed", data.get("metal_acceleration_claim_allowed_now") is False, f"value={data.get('metal_acceleration_claim_allowed_now')!r}")

    surfaces = {item.get("surface") for item in data.get("ui_surfaces", []) if isinstance(item, dict)}
    for surface in REQUIRED_SURFACES:
        add(f"surface:{surface}", surface in surfaces, "present" if surface in surfaces else "missing")

    evidence_ids = {item.get("id") for item in data.get("evidence_requirements", []) if isinstance(item, dict)}
    for evidence_id in REQUIRED_EVIDENCE_IDS:
        add(f"evidence_id:{evidence_id}", evidence_id in evidence_ids, "present" if evidence_id in evidence_ids else "missing")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in ["schema_only", "static_contract"]:
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
        "bar_poking",
        "gpu_command_submission",
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
        "decision": "PASS_UI_COMPOSITOR_PROOF_SCHEMA_READY" if failed_count == 0 else "FAIL_UI_COMPOSITOR_PROOF_SCHEMA_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generated,
        "safety_boundary": {
            "read_only_static_check": True,
            "schema_only": True,
            "runs_live_diagnostics": False,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "gpu_command_submission": False,
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


def markdown_report(report: dict[str, Any]) -> str:
    rows = [
        f"| `{item['name']}` | {'PASS' if item['passed'] else 'FAIL'} | {str(item['detail']).replace('|', '\\|')} |"
        for item in report["checks"]
    ]
    return "\n".join(
        [
            "# UI Compositor Proof Schema Check",
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
            "This check validates a static UI compositor proof schema. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, write PCI config space, access MMIO, map BAR memory, submit GPU commands, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, spoof Metal devices, or claim RTX 5070 UI compositor or Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX UI compositor proof schema.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)
    json_path = out_dir / "ui-compositor-proof-schema-check.json"
    md_path = out_dir / "ui-compositor-proof-schema-check.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
