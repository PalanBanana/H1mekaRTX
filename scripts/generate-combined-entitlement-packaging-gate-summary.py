#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.combined_entitlement_packaging_gate_summary.v1"

ENTITLEMENT_RESOLVER = "scripts/resolve-entitlement-evidence.py"
PACKAGING_RESOLVER = "scripts/resolve-signed-extension-packaging-plan.py"

ENTITLEMENT_SAMPLE = "evidence-templates/entitlement-evidence.sample.json"
ENTITLEMENT_READY = "evidence-templates/entitlement-evidence.redacted-ready.fixture.json"
ENTITLEMENT_RUNTIME_NEGATIVE = "evidence-templates/entitlement-evidence.runtime-requested.fixture.json"

PACKAGING_SAMPLE = "packaging-plan/signed-extension-packaging-plan.sample.json"
PACKAGING_READY = "packaging-plan/signed-extension-packaging-plan.redacted-ready.fixture.json"
PACKAGING_RUNTIME_NEGATIVE = "packaging-plan/signed-extension-packaging-plan.runtime-requested.fixture.json"

SOURCE_FILES = [
    ENTITLEMENT_RESOLVER,
    PACKAGING_RESOLVER,
    ENTITLEMENT_SAMPLE,
    ENTITLEMENT_READY,
    ENTITLEMENT_RUNTIME_NEGATIVE,
    PACKAGING_SAMPLE,
    PACKAGING_READY,
    PACKAGING_RUNTIME_NEGATIVE,
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


def run_entitlement(root: Path, evidence: str, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / ENTITLEMENT_RESOLVER),
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
        "report": report,
        "stdout": proc.stdout[-3000:],
        "stderr": proc.stderr[-3000:],
    }


def run_packaging(root: Path, plan: str, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / PACKAGING_RESOLVER),
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
        "report": report,
        "stdout": proc.stdout[-3000:],
        "stderr": proc.stderr[-3000:],
    }


def combined_case(
    name: str,
    entitlement_run: dict[str, Any],
    packaging_run: dict[str, Any],
) -> dict[str, Any]:
    entitlement = entitlement_run.get("report", {})
    packaging = packaging_run.get("report", {})

    entitlement_ready = entitlement.get("evidence_ready_for_review") is True
    packaging_ready = packaging.get("packaging_ready_for_manual_review") is True

    entitlement_runtime = entitlement.get("runtime_allowed_after_resolver") is True or entitlement.get("rtx5070_metal_runtime_allowed") is True
    packaging_runtime = packaging.get("runtime_allowed_after_packaging_resolver") is True or packaging.get("rtx5070_metal_runtime_allowed") is True

    blockers: list[str] = []

    if entitlement_run.get("returncode") != 0:
        blockers.append("entitlement_resolver_failed")

    if packaging_run.get("returncode") != 0:
        blockers.append("packaging_resolver_failed")

    if entitlement_runtime:
        blockers.append("entitlement_attempts_runtime")

    if packaging_runtime:
        blockers.append("packaging_attempts_runtime")

    if not entitlement_ready:
        blockers.append("entitlement_not_ready_for_manual_review")

    if not packaging_ready:
        blockers.append("packaging_not_ready_for_manual_review")

    if entitlement_ready and packaging_ready and not entitlement_runtime and not packaging_runtime:
        decision = "COMBINED_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME"
        gate = "GO_COMBINED_MANUAL_REVIEW_NO_RUNTIME"
        ready_for_manual_review = True
    else:
        decision = "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED"
        gate = "NO_GO_COMBINED_GATE"
        ready_for_manual_review = False

    return {
        "name": name,
        "decision": decision,
        "gate": gate,
        "ready_for_manual_review": ready_for_manual_review,
        "runtime_allowed_after_combined_gate": False,
        "rtx5070_metal_runtime_allowed": False,
        "entitlement": {
            "decision": entitlement.get("decision"),
            "gate": entitlement.get("gate"),
            "ready": entitlement_ready,
            "runtime_allowed": entitlement.get("runtime_allowed_after_resolver"),
            "rtx_runtime_allowed": entitlement.get("rtx5070_metal_runtime_allowed"),
        },
        "packaging": {
            "decision": packaging.get("decision"),
            "gate": packaging.get("gate"),
            "ready": packaging_ready,
            "runtime_allowed": packaging.get("runtime_allowed_after_packaging_resolver"),
            "rtx_runtime_allowed": packaging.get("rtx5070_metal_runtime_allowed"),
        },
        "blockers": blockers,
    }


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in SOURCE_FILES:
        path = root / rel
        add_check(checks, f"source_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in SOURCE_FILES)

    for token in FORBIDDEN_SOURCE_TOKENS:
        add_check(checks, f"forbidden_token_absent:{token}", token not in source, "absent" if token not in source else "present")

    with tempfile.TemporaryDirectory(prefix="h1mekartx-stage75-") as tmp:
        tmp_path = Path(tmp)

        sample_ent_dir = tmp_path / "sample-entitlement"
        sample_pack_dir = tmp_path / "sample-packaging"
        ready_ent_dir = tmp_path / "ready-entitlement"
        ready_pack_dir = tmp_path / "ready-packaging"
        runtime_ent_dir = tmp_path / "runtime-entitlement"
        runtime_pack_dir = tmp_path / "runtime-packaging"

        for item in [
            sample_ent_dir,
            sample_pack_dir,
            ready_ent_dir,
            ready_pack_dir,
            runtime_ent_dir,
            runtime_pack_dir,
        ]:
            item.mkdir(parents=True, exist_ok=True)

        sample_case = combined_case(
            "sample_incomplete",
            run_entitlement(root, ENTITLEMENT_SAMPLE, sample_ent_dir),
            run_packaging(root, PACKAGING_SAMPLE, sample_pack_dir),
        )

        ready_case = combined_case(
            "redacted_ready",
            run_entitlement(root, ENTITLEMENT_READY, ready_ent_dir),
            run_packaging(root, PACKAGING_READY, ready_pack_dir),
        )

        runtime_negative_case = combined_case(
            "runtime_requested_negative",
            run_entitlement(root, ENTITLEMENT_RUNTIME_NEGATIVE, runtime_ent_dir),
            run_packaging(root, PACKAGING_RUNTIME_NEGATIVE, runtime_pack_dir),
        )

    cases = [sample_case, ready_case, runtime_negative_case]

    case_by_name = {item["name"]: item for item in cases}

    add_check(
        checks,
        "sample_decision_not_ready",
        case_by_name["sample_incomplete"]["decision"] == "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED",
        f"decision={case_by_name['sample_incomplete']['decision']!r}",
    )
    add_check(
        checks,
        "sample_runtime_false",
        case_by_name["sample_incomplete"]["runtime_allowed_after_combined_gate"] is False,
        f"value={case_by_name['sample_incomplete']['runtime_allowed_after_combined_gate']!r}",
    )

    add_check(
        checks,
        "ready_decision_manual_review",
        case_by_name["redacted_ready"]["decision"] == "COMBINED_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
        f"decision={case_by_name['redacted_ready']['decision']!r}",
    )
    add_check(
        checks,
        "ready_gate_manual_review",
        case_by_name["redacted_ready"]["gate"] == "GO_COMBINED_MANUAL_REVIEW_NO_RUNTIME",
        f"gate={case_by_name['redacted_ready']['gate']!r}",
    )
    add_check(
        checks,
        "ready_runtime_false",
        case_by_name["redacted_ready"]["runtime_allowed_after_combined_gate"] is False,
        f"value={case_by_name['redacted_ready']['runtime_allowed_after_combined_gate']!r}",
    )

    add_check(
        checks,
        "runtime_negative_decision_not_ready",
        case_by_name["runtime_requested_negative"]["decision"] == "NOT_READY_COMBINED_ENTITLEMENT_PACKAGING_EVIDENCE_REQUIRED",
        f"decision={case_by_name['runtime_requested_negative']['decision']!r}",
    )
    add_check(
        checks,
        "runtime_negative_runtime_false",
        case_by_name["runtime_requested_negative"]["runtime_allowed_after_combined_gate"] is False,
        f"value={case_by_name['runtime_requested_negative']['runtime_allowed_after_combined_gate']!r}",
    )
    add_check(
        checks,
        "runtime_negative_has_blockers",
        len(case_by_name["runtime_requested_negative"]["blockers"]) > 0,
        f"blockers={case_by_name['runtime_requested_negative']['blockers']!r}",
    )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY" if failed_count == 0 else "FAIL_COMBINED_ENTITLEMENT_PACKAGING_GATE_SUMMARY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "cases": cases,
        "combined_gate_summary_ready": failed_count == 0,
        "case_count": len(cases),
        "sample_incomplete_expected_no_go": True,
        "redacted_ready_expected_manual_review_only": True,
        "runtime_requested_expected_rejected": True,
        "manual_review_only": True,
        "combined_gate_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_combined_gate": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 76 should add a combined gate static contract checker and CI-style summary badge while keeping runtime disabled.",
        "safety_boundary": {
            "read_only": True,
            "combined_gate_summary_only": True,
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
    case_rows = []
    for item in report["cases"]:
        case_rows.append(
            "| `{name}` | `{decision}` | `{gate}` | `{ready}` | `{runtime}` |".format(
                name=item["name"],
                decision=item["decision"],
                gate=item["gate"],
                ready=item["ready_for_manual_review"],
                runtime=item["runtime_allowed_after_combined_gate"],
            )
        )

    check_rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        check_rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# Combined Entitlement Packaging Gate Summary",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Combined gate summary ready: `{report['combined_gate_summary_ready']}`",
            "",
            f"Case count: `{report['case_count']}`",
            "",
            f"Combined gate only: `{report['combined_gate_only']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Runtime allowed after combined gate: `{report['runtime_allowed_after_combined_gate']}`",
            "",
            f"Metal injection goal: `{report['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{report['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Combined Cases",
            "",
            "| Case | Decision | Gate | Ready | Runtime Allowed |",
            "| --- | --- | --- | --- | --- |",
            *case_rows,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *check_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage adds a combined entitlement-plus-packaging gate summary only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate combined entitlement-plus-packaging gate summary.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "combined-entitlement-packaging-gate-summary-report.json"
    md_path = out_dir / "combined-entitlement-packaging-gate-summary-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
