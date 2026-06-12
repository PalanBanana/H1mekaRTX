#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_resolver_fixture_matrix.v1"

RESOLVER = "scripts/resolve-entitlement-evidence.py"

FIXTURES = [
    {
        "name": "sample_incomplete",
        "path": "evidence-templates/entitlement-evidence.sample.json",
        "expected_decision": "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
        "expected_gate": "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
        "expected_ready": False,
        "expected_runtime_allowed": False
    },
    {
        "name": "redacted_ready",
        "path": "evidence-templates/entitlement-evidence.redacted-ready.fixture.json",
        "expected_decision": "EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED",
        "expected_gate": "GO_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
        "expected_ready": True,
        "expected_runtime_allowed": False
    },
    {
        "name": "runtime_requested_negative",
        "path": "evidence-templates/entitlement-evidence.runtime-requested.fixture.json",
        "expected_decision": "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
        "expected_gate": "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE",
        "expected_ready": False,
        "expected_runtime_allowed": False
    }
]

SOURCE_FILES = [
    RESOLVER,
    "scripts/check-entitlement-evidence-resolver.py",
    "scripts/validate-entitlement-evidence-resolver-static-contract.py",
    "evidence-templates/entitlement-evidence.sample.json",
    "evidence-templates/entitlement-evidence.redacted-ready.fixture.json",
    "evidence-templates/entitlement-evidence.runtime-requested.fixture.json",
    "docs/metal/entitlement-evidence-resolver-static-contract.md",
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

    for token in FORBIDDEN_SOURCE_TOKENS:
        add_check(checks, f"forbidden_token_absent:{token}", token not in source, "absent" if token not in source else "present")

    fixture_results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage70-") as tmp:
        tmp_path = Path(tmp)

        for fixture in FIXTURES:
            fixture_out = tmp_path / fixture["name"]
            fixture_out.mkdir(parents=True, exist_ok=True)

            run = run_resolver(root, fixture["path"], fixture_out)
            report = run.get("report", {})

            result = {
                "name": fixture["name"],
                "path": fixture["path"],
                "returncode": run["returncode"],
                "decision": report.get("decision"),
                "gate": report.get("gate"),
                "evidence_ready_for_review": report.get("evidence_ready_for_review"),
                "runtime_allowed_after_resolver": report.get("runtime_allowed_after_resolver"),
                "rtx5070_metal_runtime_allowed": report.get("rtx5070_metal_runtime_allowed"),
                "blockers": report.get("blockers", []),
                "expected_decision": fixture["expected_decision"],
                "expected_gate": fixture["expected_gate"],
                "expected_ready": fixture["expected_ready"],
                "expected_runtime_allowed": fixture["expected_runtime_allowed"],
            }
            fixture_results.append(result)

            add_check(checks, f"{fixture['name']}:returncode", run["returncode"] == 0, f"returncode={run['returncode']}")
            add_check(checks, f"{fixture['name']}:decision", result["decision"] == fixture["expected_decision"], f"actual={result['decision']!r}, expected={fixture['expected_decision']!r}")
            add_check(checks, f"{fixture['name']}:gate", result["gate"] == fixture["expected_gate"], f"actual={result['gate']!r}, expected={fixture['expected_gate']!r}")
            add_check(checks, f"{fixture['name']}:ready", result["evidence_ready_for_review"] is fixture["expected_ready"], f"actual={result['evidence_ready_for_review']!r}, expected={fixture['expected_ready']!r}")
            add_check(checks, f"{fixture['name']}:runtime_disabled", result["runtime_allowed_after_resolver"] is False, f"value={result['runtime_allowed_after_resolver']!r}")
            add_check(checks, f"{fixture['name']}:rtx_runtime_disabled", result["rtx5070_metal_runtime_allowed"] is False, f"value={result['rtx5070_metal_runtime_allowed']!r}")

            if fixture["name"] == "runtime_requested_negative":
                blockers = result.get("blockers", [])
                add_check(
                    checks,
                    "runtime_requested_negative:runtime_claim_blocker",
                    isinstance(blockers, list) and "evidence_file_attempts_to_enable_runtime" in blockers,
                    f"blockers={blockers!r}",
                )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_ENTITLEMENT_RESOLVER_FIXTURE_MATRIX" if failed_count == 0 else "FAIL_ENTITLEMENT_RESOLVER_FIXTURE_MATRIX",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "fixtures": fixture_results,
        "fixture_matrix_ready": failed_count == 0,
        "fixture_count": len(FIXTURES),
        "sample_incomplete_expected_no_go": True,
        "redacted_ready_expected_manual_review_only": True,
        "runtime_requested_expected_rejected": True,
        "manual_review_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_fixture_matrix": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 71 should begin a signed-extension packaging plan matrix while keeping runtime disabled.",
        "safety_boundary": {
            "read_only": True,
            "fixture_matrix_only": True,
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

    fixture_rows = []
    for item in report["fixtures"]:
        fixture_rows.append(
            "| `{name}` | `{decision}` | `{gate}` | `{ready}` | `{runtime}` |".format(
                name=item["name"],
                decision=item["decision"],
                gate=item["gate"],
                ready=item["evidence_ready_for_review"],
                runtime=item["runtime_allowed_after_resolver"],
            )
        )

    return "\n".join(
        [
            "# Entitlement Resolver Fixture Matrix Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Fixture matrix ready: `{report['fixture_matrix_ready']}`",
            "",
            f"Fixture count: `{report['fixture_count']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Runtime allowed after fixture matrix: `{report['runtime_allowed_after_fixture_matrix']}`",
            "",
            f"Metal injection goal: `{report['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{report['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Fixture Results",
            "",
            "| Fixture | Decision | Gate | Ready | Runtime Allowed |",
            "| --- | --- | --- | --- | --- |",
            *fixture_rows,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This stage validates resolver fixture matrix coverage only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate entitlement resolver fixture matrix.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "entitlement-resolver-fixture-matrix-report.json"
    md_path = out_dir / "entitlement-resolver-fixture-matrix-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
