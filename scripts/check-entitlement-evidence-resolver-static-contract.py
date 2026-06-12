#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_evidence_resolver_static_contract_check.v1"

REQUIRED_FILES = [
    "scripts/validate-entitlement-evidence-resolver-static-contract.py",
    "scripts/check-entitlement-evidence-resolver-static-contract.py",
    "docs/metal/entitlement-evidence-resolver-static-contract.md",
    "evidence-templates/entitlement-evidence.redacted-ready.fixture.json",
]

REQUIRED_TERMS = [
    "PASS_ENTITLEMENT_EVIDENCE_RESOLVER_STATIC_CONTRACT",
    "static_contract_ready",
    "redacted_ready_fixture_added",
    "manual_review_only",
    "GO_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
    "EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED",
    "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
    "runtime_allowed_after_static_contract",
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "rtx5070_metal_runtime_allowed",
]

FORBIDDEN_LITERAL_TERMS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submit", "Request"]),
    "".join(["OSSystem", "Extension", "Manager.shared"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
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


def run_validator(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "validate-entitlement-evidence-resolver-static-contract.py"),
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-5000:],
        "stderr": proc.stderr[-5000:],
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{token}", token not in source, "absent" if token not in source else "present")

    ready_fixture_path = root / "evidence-templates/entitlement-evidence.redacted-ready.fixture.json"
    ready_fixture = json.loads(ready_fixture_path.read_text()) if ready_fixture_path.exists() else {}
    ready_evidence = ready_fixture.get("evidence", {}) if isinstance(ready_fixture, dict) else {}
    if not isinstance(ready_evidence, dict):
        ready_evidence = {}

    add_check(
        checks,
        "ready_fixture_schema",
        ready_fixture.get("schema") == "h1mekartx.entitlement_evidence_input.v1",
        f"schema={ready_fixture.get('schema')!r}",
    )
    add_check(
        checks,
        "ready_fixture_runtime_false",
        ready_evidence.get("metal_injection_runtime_allowed_now") is False,
        f"value={ready_evidence.get('metal_injection_runtime_allowed_now')!r}",
    )
    add_check(
        checks,
        "ready_fixture_rtx_runtime_false",
        ready_evidence.get("rtx5070_metal_runtime_allowed") is False,
        f"value={ready_evidence.get('rtx5070_metal_runtime_allowed')!r}",
    )
    add_check(
        checks,
        "ready_fixture_goal_true",
        ready_evidence.get("metal_injection_goal") is True,
        f"value={ready_evidence.get('metal_injection_goal')!r}",
    )

    validator_run = run_validator(root, out_dir)
    add_check(checks, "validator_returncode", validator_run["returncode"] == 0, f"returncode={validator_run['returncode']}")

    report_path = out_dir / "entitlement-evidence-resolver-static-contract-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(
        checks,
        "contract_schema",
        report.get("schema") == "h1mekartx.entitlement_evidence_resolver_static_contract.v1",
        f"schema={report.get('schema')!r}",
    )
    add_check(
        checks,
        "contract_decision",
        report.get("decision") == "PASS_ENTITLEMENT_EVIDENCE_RESOLVER_STATIC_CONTRACT",
        f"decision={report.get('decision')!r}",
    )
    add_check(
        checks,
        "contract_failed_count_zero",
        report.get("failed_count") == 0,
        f"failed_count={report.get('failed_count')!r}",
    )
    add_check(
        checks,
        "contract_ready",
        report.get("static_contract_ready") is True,
        f"value={report.get('static_contract_ready')!r}",
    )
    add_check(
        checks,
        "ready_fixture_added",
        report.get("redacted_ready_fixture_added") is True,
        f"value={report.get('redacted_ready_fixture_added')!r}",
    )
    add_check(
        checks,
        "manual_review_only",
        report.get("manual_review_only") is True,
        f"value={report.get('manual_review_only')!r}",
    )
    add_check(
        checks,
        "runtime_after_contract_false",
        report.get("runtime_allowed_after_static_contract") is False,
        f"value={report.get('runtime_allowed_after_static_contract')!r}",
    )
    add_check(
        checks,
        "metal_goal_recorded",
        report.get("metal_injection_goal") is True,
        f"value={report.get('metal_injection_goal')!r}",
    )
    add_check(
        checks,
        "metal_runtime_not_allowed_now",
        report.get("metal_injection_runtime_allowed_now") is False,
        f"value={report.get('metal_injection_runtime_allowed_now')!r}",
    )

    sample = report.get("sample_evidence", {})
    ready = report.get("ready_evidence", {})
    if not isinstance(sample, dict):
        sample = {}
    if not isinstance(ready, dict):
        ready = {}

    add_check(
        checks,
        "sample_no_go",
        sample.get("decision") == "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
        f"decision={sample.get('decision')!r}",
    )
    add_check(
        checks,
        "ready_present_but_disabled",
        ready.get("decision") == "EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED",
        f"decision={ready.get('decision')!r}",
    )
    add_check(
        checks,
        "ready_manual_review_gate",
        ready.get("gate") == "GO_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
        f"gate={ready.get('gate')!r}",
    )
    add_check(
        checks,
        "ready_runtime_false",
        ready.get("runtime_allowed_after_resolver") is False,
        f"value={ready.get('runtime_allowed_after_resolver')!r}",
    )

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
        add_check(checks, f"blocked:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    sb = report.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "read_only",
        "static_contract_only",
        "redacted_fixture_only",
        "manual_review_only",
        "no_runtime",
        "no_driver_installation",
        "no_driver_activation",
        "no_provider_attach",
        "no_device_ownership",
        "no_low_level_hardware_path",
        "no_rtx5070_metal_runtime",
    ]:
        add_check(checks, f"safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_ENTITLEMENT_EVIDENCE_RESOLVER_STATIC_CONTRACT_READY" if failed_count == 0 else "FAIL_ENTITLEMENT_EVIDENCE_RESOLVER_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "validator_run": validator_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "static_contract_only": True,
            "redacted_fixture_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True,
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
            "# Entitlement Evidence Resolver Static Contract Check",
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
            "This check validates the entitlement evidence resolver static contract and redacted-ready fixture only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check entitlement evidence resolver static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "entitlement-evidence-resolver-static-contract-check.json"
    md_path = out_dir / "entitlement-evidence-resolver-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
