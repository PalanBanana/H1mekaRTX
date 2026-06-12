#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_evidence_resolver_static_contract.v1"

RESOLVER = "scripts/resolve-entitlement-evidence.py"

DEFAULT_EVIDENCE = "evidence-templates/entitlement-evidence.sample.json"
READY_EVIDENCE = "evidence-templates/entitlement-evidence.redacted-ready.fixture.json"

SOURCE_FILES = [
    RESOLVER,
    "scripts/check-entitlement-evidence-resolver.py",
    "evidence-templates/entitlement-evidence.sample.json",
    READY_EVIDENCE,
    "docs/metal/entitlement-evidence-resolver.md",
]

REQUIRED_RESOLVER_TERMS = [
    "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
    "GO_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
    "EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED",
    "runtime_allowed_after_resolver",
    "redacted_evidence_resolution_only",
    "manual_review_only",
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "rtx5070_metal_runtime_allowed",
]

REQUIRED_READY_EVIDENCE_TERMS = [
    "PROVIDED_REDACTED",
    "APPROVED_REDACTED",
    "CONFIRMED_REDACTED",
    "TEAM_ID_REDACTED_PRESENT",
    "HOST_APP_BUNDLE_ID_REDACTED_PRESENT",
    "DRIVER_EXTENSION_BUNDLE_ID_REDACTED_PRESENT",
    "\"metal_injection_runtime_allowed_now\": false",
    "\"rtx5070_metal_runtime_allowed\": false",
]

FORBIDDEN_SOURCE_TOKENS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submit", "Request"]),
    "".join(["OSSystem", "Extension", "Manager.shared"]),
    "".join(["OSSystem", "Extension", "Request"]),
    "".join(["IOPCI", "Device"]),
    "".join(["IOService", "GetMatchingServices"]),
    "".join(["Configuration", "Read"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["map", "DeviceMemory"]),
    "".join(["Create", "MemoryMap"]),
    "".join(["sub", "process.run([\"", "io", "reg", "\""]),
    "".join(["sub", "process.run([\"", "system", "_", "profiler", "\""]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_resolver(root: Path, evidence: str, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / RESOLVER),
            "--root",
            str(root),
            "--evidence",
            evidence,
            "--out-dir",
            str(out_dir),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    report_path = out_dir / "entitlement-evidence-resolver-report.json"
    report: dict[str, Any] = {}
    if report_path.exists():
        report = json.loads(report_path.read_text())

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "report": report,
    }


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in SOURCE_FILES:
        path = root / rel
        add_check(checks, f"source_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in SOURCE_FILES)

    for term in REQUIRED_RESOLVER_TERMS:
        add_check(checks, f"resolver_term:{term}", term in source, "found" if term in source else "missing")

    ready_source = read_text(root / READY_EVIDENCE)
    for term in REQUIRED_READY_EVIDENCE_TERMS:
        add_check(checks, f"ready_fixture_term:{term}", term in ready_source, "found" if term in ready_source else "missing")

    for token in FORBIDDEN_SOURCE_TOKENS:
        add_check(checks, f"forbidden_token_absent:{token}", token not in source, "absent" if token not in source else "present")

    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage69-") as tmp:
        tmp_path = Path(tmp)

        sample_dir = tmp_path / "sample"
        sample_dir.mkdir(parents=True, exist_ok=True)
        sample_run = run_resolver(root, DEFAULT_EVIDENCE, sample_dir)

        ready_dir = tmp_path / "ready"
        ready_dir.mkdir(parents=True, exist_ok=True)
        ready_run = run_resolver(root, READY_EVIDENCE, ready_dir)

    sample_report = sample_run.get("report", {})
    ready_report = ready_run.get("report", {})

    add_check(checks, "sample_resolver_returncode", sample_run["returncode"] == 0, f"returncode={sample_run['returncode']}")
    add_check(checks, "ready_resolver_returncode", ready_run["returncode"] == 0, f"returncode={ready_run['returncode']}")

    add_check(checks, "sample_decision_no_go", sample_report.get("decision") == "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE", f"decision={sample_report.get('decision')!r}")
    add_check(checks, "sample_gate_no_go", sample_report.get("gate") == "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE", f"gate={sample_report.get('gate')!r}")
    add_check(checks, "sample_runtime_disabled", sample_report.get("runtime_allowed_after_resolver") is False, f"value={sample_report.get('runtime_allowed_after_resolver')!r}")

    add_check(checks, "ready_decision_present_but_disabled", ready_report.get("decision") == "EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED", f"decision={ready_report.get('decision')!r}")
    add_check(checks, "ready_gate_manual_review", ready_report.get("gate") == "GO_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME", f"gate={ready_report.get('gate')!r}")
    add_check(checks, "ready_evidence_for_review_true", ready_report.get("evidence_ready_for_review") is True, f"value={ready_report.get('evidence_ready_for_review')!r}")
    add_check(checks, "ready_blockers_empty", isinstance(ready_report.get("blockers"), list) and len(ready_report["blockers"]) == 0, f"count={len(ready_report.get('blockers', [])) if isinstance(ready_report.get('blockers'), list) else None!r}")
    add_check(checks, "ready_runtime_disabled", ready_report.get("runtime_allowed_after_resolver") is False, f"value={ready_report.get('runtime_allowed_after_resolver')!r}")
    add_check(checks, "ready_metal_runtime_disabled", ready_report.get("rtx5070_metal_runtime_allowed") is False, f"value={ready_report.get('rtx5070_metal_runtime_allowed')!r}")

    for report_name, report in [
        ("sample", sample_report),
        ("ready", ready_report),
    ]:
        for key in [
            "live_system_queries_allowed",
            "runtime_buttons_enabled",
            "driver_runtime_allowed",
            "driver_installation_allowed",
            "driver_activation_allowed",
            "provider_attach_allowed",
            "device_ownership_allowed",
            "low_level_hardware_path_allowed",
            "rtx5070_metal_runtime_allowed",
        ]:
            add_check(checks, f"{report_name}_blocked:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_ENTITLEMENT_EVIDENCE_RESOLVER_STATIC_CONTRACT" if failed_count == 0 else "FAIL_ENTITLEMENT_EVIDENCE_RESOLVER_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "source_files": SOURCE_FILES,
        "sample_evidence": {
            "path": DEFAULT_EVIDENCE,
            "decision": sample_report.get("decision"),
            "gate": sample_report.get("gate"),
            "runtime_allowed_after_resolver": sample_report.get("runtime_allowed_after_resolver"),
        },
        "ready_evidence": {
            "path": READY_EVIDENCE,
            "decision": ready_report.get("decision"),
            "gate": ready_report.get("gate"),
            "evidence_ready_for_review": ready_report.get("evidence_ready_for_review"),
            "runtime_allowed_after_resolver": ready_report.get("runtime_allowed_after_resolver"),
        },
        "static_contract_ready": failed_count == 0,
        "redacted_ready_fixture_added": True,
        "manual_review_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_static_contract": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 70 should add entitlement resolver CI-style fixture matrix coverage while keeping runtime disabled.",
        "safety_boundary": {
            "read_only": True,
            "static_contract_only": True,
            "redacted_fixture_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    files = [f"- `{item}`" for item in report["source_files"]]

    return "\n".join(
        [
            "# Entitlement Evidence Resolver Static Contract Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Static contract ready: `{report['static_contract_ready']}`",
            "",
            f"Redacted-ready fixture added: `{report['redacted_ready_fixture_added']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Runtime allowed after static contract: `{report['runtime_allowed_after_static_contract']}`",
            "",
            f"Metal injection goal: `{report['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{report['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Sample Evidence Result",
            "",
            f"- Path: `{report['sample_evidence']['path']}`",
            f"- Decision: `{report['sample_evidence']['decision']}`",
            f"- Gate: `{report['sample_evidence']['gate']}`",
            f"- Runtime allowed: `{report['sample_evidence']['runtime_allowed_after_resolver']}`",
            "",
            "## Redacted-ready Evidence Result",
            "",
            f"- Path: `{report['ready_evidence']['path']}`",
            f"- Decision: `{report['ready_evidence']['decision']}`",
            f"- Gate: `{report['ready_evidence']['gate']}`",
            f"- Evidence ready for review: `{report['ready_evidence']['evidence_ready_for_review']}`",
            f"- Runtime allowed: `{report['ready_evidence']['runtime_allowed_after_resolver']}`",
            "",
            "## Source Files",
            "",
            *files,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This stage validates the entitlement evidence resolver static contract and redacted-ready fixture only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate entitlement evidence resolver static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "entitlement-evidence-resolver-static-contract-report.json"
    md_path = out_dir / "entitlement-evidence-resolver-static-contract-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
