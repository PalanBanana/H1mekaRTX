#!/usr/bin/env python3
from __future__ import annotations

import json
import plistlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def read_plist(path: Path):
    with path.open("rb") as f:
        return plistlib.load(f)

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-xcode-materialization/xcode-driverkit-project-materialization-plan.json"
doc_path = ROOT / "docs/driverkit/xcode-driverkit-project-materialization-plan.md"
manual_path = ROOT / "apps/H1mekaRTXDriverKit/README.md"
host_src = ROOT / "apps/H1mekaRTXDriverKit/Sources/H1mekaRTXHost/H1mekaRTXHost.swift"
dext_src = ROOT / "apps/H1mekaRTXDriverKit/Sources/H1mekaRTXDriver/H1mekaRTXDriver.cpp"
host_plist = ROOT / "apps/H1mekaRTXDriverKit/Config/H1mekaRTXHost-Info.plist"
dext_plist = ROOT / "apps/H1mekaRTXDriverKit/Config/H1mekaRTXDriver-Info.plist"
host_ent = ROOT / "apps/H1mekaRTXDriverKit/Config/H1mekaRTXHost.entitlements"
dext_ent = ROOT / "apps/H1mekaRTXDriverKit/Config/H1mekaRTXDriver.entitlements"
phase60l_manifest = ROOT / "tools/driverkit-buildable-scaffold/real-driverkit-dext-build-gate.json"
expected_project = ROOT / "apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj"

manifest = read_json(manifest_path)
phase60l = read_json(phase60l_manifest)

checks = []
for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("manual_exists", manual_path),
    ("host_source_exists", host_src),
    ("dext_source_exists", dext_src),
    ("host_plist_exists", host_plist),
    ("dext_plist_exists", dext_plist),
    ("host_entitlements_exists", host_ent),
    ("dext_entitlements_exists", dext_ent),
    ("phase60l_manifest_exists", phase60l_manifest),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.xcode_driverkit_project_materialization_plan.v1"), "manifest schema")
add(checks, "phase60l_manifest_schema", bool(phase60l and phase60l.get("schema") == "h1mekartx.real_driverkit_dext_build_gate.v1"), "phase60l schema")
add(checks, "expected_project_not_required_yet", True, str(expected_project))
add(checks, "expected_project_currently_exists_recorded", expected_project.exists() in [True, False], str(expected_project.exists()))

if host_plist.exists():
    hp = read_plist(host_plist)
    add(checks, "host_bundle_id", hp.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXHost", hp.get("CFBundleIdentifier"))
    add(checks, "host_executable", hp.get("CFBundleExecutable") == "H1mekaRTXHost", hp.get("CFBundleExecutable"))

if dext_plist.exists():
    dp = read_plist(dext_plist)
    add(checks, "dext_bundle_id", dp.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXDriver", dp.get("CFBundleIdentifier"))
    add(checks, "dext_executable", dp.get("CFBundleExecutable") == "H1mekaRTXDriver", dp.get("CFBundleExecutable"))
    personalities = dp.get("IOKitPersonalities", {})
    person = personalities.get("H1mekaRTX5070ProviderMatch", {})
    add(checks, "dext_provider_class_iopcidevice", person.get("IOProviderClass") == "IOPCIDevice", person.get("IOProviderClass"))
    add(checks, "dext_iopcimatch", person.get("IOPCIMatch") == "0x2f0410de", person.get("IOPCIMatch"))

if host_src.exists():
    text = host_src.read_text(encoding="utf-8", errors="replace")
    for token in [
        "SystemExtensions",
        "OSSystemExtensionRequest",
        "default_no_activation",
        "submit_activation_request",
    ]:
        add(checks, "host_src_contains_" + token, token in text, token)

if dext_src.exists():
    text = dext_src.read_text(encoding="utf-8", errors="replace")
    for token in [
        "DriverKit/IOService.h",
        "Start(IOService* provider)",
        "no provider open",
        "no BAR mapping",
        "no GPU command submission",
    ]:
        add(checks, "dext_src_contains_" + token.replace(" ", "_").replace("/", "_"), token in text, token)

if manifest:
    for field in [
        "project_materialization_plan_ready",
        "project_inputs_only",
    ]:
        add(checks, f"manifest_{field}_true", manifest.get(field) is True, field)

    for field in [
        "xcodebuild_attempted_by_this_phase",
        "activation_submitted_by_this_phase",
        "deactivation_submitted_by_this_phase",
        "install_attempted",
        "manual_dext_load_attempted",
        "provider_open_attempted",
        "ioserviceopen_attempted",
        "bar_mapping_attempted",
        "bar_mmio_mutation_attempted",
        "configuration_writes_attempted",
        "gpu_command_submission_attempted",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        add(checks, f"manifest_{field}_false", manifest.get(field) is False, field)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_XCODE_DRIVERKIT_PROJECT_MATERIALIZATION_PLAN_READY" if failed == 0 else "FAIL_XCODE_DRIVERKIT_PROJECT_MATERIALIZATION_PLAN"

report = {
    "schema": "h1mekartx.xcode_driverkit_project_materialization_plan_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "project_materialization_plan_ready": failed == 0,
    "expected_project": str(expected_project.relative_to(ROOT)),
    "expected_project_exists": expected_project.exists(),
    "project_inputs_only": True,
    "xcodebuild_attempted_by_this_phase": False,
    "activation_submitted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate_if_project_missing": "phase60n-xcodeproj-materialization-helper",
    "next_gate_if_project_exists": "phase60l-real-driverkit-dext-build-gate-local-run",
    "checks": checks,
}

(OUT / "xcode-driverkit-project-materialization-plan-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Xcode DriverKit Project Materialization Plan Check

- Decision: `{decision}`
- Project Inputs Only: `True`
- Expected Project: `{report['expected_project']}`
- Expected Project Exists: `{report['expected_project_exists']}`
- Xcodebuild Attempted By This Phase: `False`
- Activation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate If Project Missing: `phase60n-xcodeproj-materialization-helper`
- Next Gate If Project Exists: `phase60l-real-driverkit-dext-build-gate-local-run`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "xcode-driverkit-project-materialization-plan-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
