#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.signed_extension_packaging_plan_resolver_check.v1"

REQUIRED_FILES = [
    "scripts/resolve-signed-extension-packaging-plan.py",
    "scripts/check-signed-extension-packaging-plan-resolver.py",
    "docs/metal/signed-extension-packaging-plan-resolver.md",
    "packaging-plan/signed-extension-packaging-plan.sample.json",
    "packaging-plan/signed-extension-packaging-plan.redacted-ready.fixture.json",
]

REQUIRED_TERMS = [
    "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED",
    "PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
    "GO_PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
    "NO_GO_SIGNED_EXTENSION_PACKAGING_EVIDENCE_INCOMPLETE",
    "packaging_ready_for_manual_review",
    "runtime_allowed_after_packaging_resolver",
    "packaging_plan_only",
    "manual_review_only",
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


def run_resolver(root: Path, out_dir: Path, plan: str) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "resolve-signed-extension-packaging-plan.py"),
            "--root",
            str(root),
            "--plan",
            plan,
            "--out-dir",
            str(out_dir),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    report_path = out_dir / "signed-extension-packaging-plan-resolver-report.json"
    report: dict[str, Any] = {}
    if report_path.exists():
        report = json.loads(report_path.read_text())

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "report": report,
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

    sample_dir = out_dir / "sample-plan"
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_run = run_resolver(root, sample_dir, "packaging-plan/signed-extension-packaging-plan.sample.json")

    ready_dir = out_dir / "ready-plan"
    ready_dir.mkdir(parents=True, exist_ok=True)
    ready_run = run_resolver(root, ready_dir, "packaging-plan/signed-extension-packaging-plan.redacted-ready.fixture.json")

    sample = sample_run.get("report", {})
    ready = ready_run.get("report", {})

    add_check(checks, "sample_resolver_returncode", sample_run["returncode"] == 0, f"returncode={sample_run['returncode']}")
    add_check(checks, "ready_resolver_returncode", ready_run["returncode"] == 0, f"returncode={ready_run['returncode']}")

    add_check(checks, "sample_schema", sample.get("schema") == "h1mekartx.signed_extension_packaging_plan_resolver.v1", f"schema={sample.get('schema')!r}")
    add_check(checks, "ready_schema", ready.get("schema") == "h1mekartx.signed_extension_packaging_plan_resolver.v1", f"schema={ready.get('schema')!r}")

    add_check(checks, "sample_decision_not_ready", sample.get("decision") == "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED", f"decision={sample.get('decision')!r}")
    add_check(checks, "sample_gate_no_go", sample.get("gate") == "NO_GO_SIGNED_EXTENSION_PACKAGING_EVIDENCE_INCOMPLETE", f"gate={sample.get('gate')!r}")
    add_check(checks, "sample_ready_false", sample.get("packaging_ready_for_manual_review") is False, f"value={sample.get('packaging_ready_for_manual_review')!r}")
    add_check(checks, "sample_runtime_false", sample.get("runtime_allowed_after_packaging_resolver") is False, f"value={sample.get('runtime_allowed_after_packaging_resolver')!r}")

    add_check(checks, "ready_decision_manual_review", ready.get("decision") == "PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME", f"decision={ready.get('decision')!r}")
    add_check(checks, "ready_gate_manual_review", ready.get("gate") == "GO_PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME", f"gate={ready.get('gate')!r}")
    add_check(checks, "ready_ready_true", ready.get("packaging_ready_for_manual_review") is True, f"value={ready.get('packaging_ready_for_manual_review')!r}")
    add_check(checks, "ready_runtime_false", ready.get("runtime_allowed_after_packaging_resolver") is False, f"value={ready.get('runtime_allowed_after_packaging_resolver')!r}")

    for label, report in [("sample", sample), ("ready", ready)]:
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
            add_check(checks, f"{label}_blocked:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_SIGNED_EXTENSION_PACKAGING_PLAN_RESOLVER_READY" if failed_count == 0 else "FAIL_SIGNED_EXTENSION_PACKAGING_PLAN_RESOLVER",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "sample_plan": {
            "decision": sample.get("decision"),
            "gate": sample.get("gate"),
            "packaging_ready_for_manual_review": sample.get("packaging_ready_for_manual_review"),
            "runtime_allowed_after_packaging_resolver": sample.get("runtime_allowed_after_packaging_resolver"),
        },
        "ready_plan": {
            "decision": ready.get("decision"),
            "gate": ready.get("gate"),
            "packaging_ready_for_manual_review": ready.get("packaging_ready_for_manual_review"),
            "runtime_allowed_after_packaging_resolver": ready.get("runtime_allowed_after_packaging_resolver"),
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "packaging_plan_resolution_only": True,
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
            "# Signed Extension Packaging Plan Resolver Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Sample Plan",
            "",
            f"- Decision: `{report['sample_plan']['decision']}`",
            f"- Gate: `{report['sample_plan']['gate']}`",
            f"- Ready for manual review: `{report['sample_plan']['packaging_ready_for_manual_review']}`",
            f"- Runtime allowed: `{report['sample_plan']['runtime_allowed_after_packaging_resolver']}`",
            "",
            "## Ready Plan",
            "",
            f"- Decision: `{report['ready_plan']['decision']}`",
            f"- Gate: `{report['ready_plan']['gate']}`",
            f"- Ready for manual review: `{report['ready_plan']['packaging_ready_for_manual_review']}`",
            f"- Runtime allowed: `{report['ready_plan']['runtime_allowed_after_packaging_resolver']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates signed-extension packaging plan resolution only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check signed-extension packaging plan resolver.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "signed-extension-packaging-plan-resolver-check.json"
    md_path = out_dir / "signed-extension-packaging-plan-resolver-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
