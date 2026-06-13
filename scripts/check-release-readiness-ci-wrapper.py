#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_readiness_ci_wrapper_check.v1"

REQUIRED_FILES = [
    "scripts/run-release-readiness-ci.sh",
    "scripts/check-release-readiness-ci-wrapper.py",
    "docs/metal/release-readiness-ci-wrapper.md",
    ".github/workflows/release-readiness.yml",
]

REQUIRED_TERMS = [
    "PASS_RELEASE_READINESS_CI_WRAPPER",
    "PASS_RELEASE_READINESS_CI_WRAPPER_READY",
    "ci_wrapper_ready",
    "ci_wrapper_only",
    "manual_review_only",
    "runtime_allowed_after_release_readiness_ci_wrapper",
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "rtx5070_metal_runtime_allowed",
    "run-release-readiness-ci.sh",
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


def run_wrapper(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "bash",
            str(root / "scripts" / "run-release-readiness-ci.sh"),
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

    report_path = out_dir / "release-readiness-ci-wrapper-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-10000:],
        "stderr": proc.stderr[-10000:],
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

    bash_check = subprocess.run(
        ["bash", "-n", str(root / "scripts" / "run-release-readiness-ci.sh")],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    add_check(checks, "bash_syntax", bash_check.returncode == 0, f"returncode={bash_check.returncode}, stderr={bash_check.stderr[-1000:]!r}")

    workflow_text = read_text(root / ".github/workflows/release-readiness.yml")
    add_check(checks, "workflow_uses_wrapper", "bash scripts/run-release-readiness-ci.sh" in workflow_text, "workflow wrapper command")
    add_check(checks, "workflow_no_secrets", "secrets." not in workflow_text, "no secrets reference")
    add_check(checks, "workflow_no_runtime_label", "runtime-enabled" not in workflow_text, "no runtime-enabled marker")

    wrapper_run = run_wrapper(root, out_dir)
    add_check(checks, "wrapper_returncode", wrapper_run["returncode"] == 0, f"returncode={wrapper_run['returncode']}")

    report = wrapper_run["report"]

    add_check(checks, "wrapper_schema", report.get("schema") == "h1mekartx.release_readiness_ci_wrapper_report.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "wrapper_decision", report.get("decision") == "PASS_RELEASE_READINESS_CI_WRAPPER", f"decision={report.get('decision')!r}")
    add_check(checks, "wrapper_ready", report.get("ci_wrapper_ready") is True, f"value={report.get('ci_wrapper_ready')!r}")
    add_check(checks, "wrapper_failed_count_zero", report.get("failed_count") == 0, f"failed_count={report.get('failed_count')!r}")
    add_check(checks, "manual_review_only", report.get("manual_review_only") is True, f"value={report.get('manual_review_only')!r}")
    add_check(checks, "ci_wrapper_only", report.get("ci_wrapper_only") is True, f"value={report.get('ci_wrapper_only')!r}")
    add_check(checks, "runtime_false", report.get("runtime_allowed_after_release_readiness_ci_wrapper") is False, f"value={report.get('runtime_allowed_after_release_readiness_ci_wrapper')!r}")
    add_check(checks, "rtx_runtime_false", report.get("rtx5070_metal_runtime_allowed") is False, f"value={report.get('rtx5070_metal_runtime_allowed')!r}")

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
        "ci_wrapper_only",
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
        "decision": "PASS_RELEASE_READINESS_CI_WRAPPER_READY" if failed_count == 0 else "FAIL_RELEASE_READINESS_CI_WRAPPER",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "wrapper_run": {
            "returncode": wrapper_run["returncode"],
            "stdout": wrapper_run["stdout"],
            "stderr": wrapper_run["stderr"],
        },
        "safety_boundary": {
            "read_only_static_check": True,
            "ci_wrapper_only": True,
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
            "# Release Readiness CI Wrapper Check",
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
            "This check validates the top-level release-readiness CI wrapper only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check top-level release-readiness CI wrapper.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "release-readiness-ci-wrapper-check.json"
    md_path = out_dir / "release-readiness-ci-wrapper-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
