#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/sanitized-provider-visibility-evidence-matrix.json"
doc_path = ROOT / "docs/hackintosh/sanitized-provider-visibility-evidence-matrix.md"
matrix_path = ROOT / "release-readiness/sanitized-provider-visibility-evidence-matrix.json"
matrix_md_path = ROOT / "release-readiness/sanitized-provider-visibility-evidence-matrix.md"

manifest = read_json(manifest_path)
matrix = read_json(matrix_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
matrix_md = matrix_md_path.read_text(encoding="utf-8", errors="replace") if matrix_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "matrix_exists", matrix_path.exists(), str(matrix_path))
add(checks, "matrix_md_exists", matrix_md_path.exists(), str(matrix_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.sanitized_provider_visibility_evidence_matrix.v1"), "manifest schema")
add(checks, "matrix_schema", bool(matrix and matrix.get("schema") == "h1mekartx.sanitized_provider_visibility_evidence_matrix_output.v1"), "matrix schema")
add(checks, "matrix_decision_pass", bool(matrix and matrix.get("decision") == "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX_READY"), "matrix decision")

for obj_name, obj in [("manifest", manifest), ("matrix", matrix)]:
    for field in ["rtx5070_target_retained", "evidence_matrix_only"]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_true", obj.get(field) is True, field)

    for field in [
        "fallback_gpu_substitution_allowed",
        "provider_visibility_commands_executed_by_this_phase",
        "raw_capture_parsed_by_this_phase",
        "raw_stdout_committed",
        "raw_stderr_committed",
        "private_paths_committed",
        "provider_open_attempted",
        "ioserviceopen_attempted",
        "bar_mapping_attempted",
        "bar0_read_attempted",
        "bar0_write_attempted",
        "bar_mmio_mutation_attempted",
        "configuration_writes_attempted",
        "firmware_load_attempted",
        "gpu_reset_attempted",
        "framebuffer_init_attempted",
        "display_engine_init_attempted",
        "gpu_command_submission_attempted",
        "metal_proof_claimed",
        "current_rtx5070_metal_acceleration_claimed",
        "current_rtx5070_ui_smoothness_claimed",
        "dock_transparency_blur_acceleration_claimed",
    ]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_false", obj.get(field) is False, field)

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62k-local-optin-provider-visibility-evidence-capture-runbook"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

matrix_items = matrix.get("matrix", []) if matrix else []
ids = {item.get("id") for item in matrix_items}
for required_id in [
    "rtx5070_target_identity",
    "sanitized_parser_summary_present",
    "sanitized_parser_check_present",
    "raw_capture_availability",
    "hard_opt_in_state",
    "provider_visibility_h1mekartx_token",
    "provider_visibility_iopcidevice_token",
    "provider_visibility_pci_identity_tokens",
    "provider_open_safety",
    "ioserviceopen_safety",
    "bar_mapping_safety",
    "bar0_read_write_safety",
    "gpu_command_safety",
    "metal_proof_state",
    "dock_transparency_blur_proof_state",
]:
    add(checks, f"matrix_has_{required_id}", required_id in ids, required_id)

add(checks, "matrix_fail_count_zero", bool(matrix and matrix.get("fail_count") == 0), "fail_count")
add(checks, "matrix_has_not_proven_items", bool(matrix and matrix.get("not_proven_count", 0) >= 1), "not_proven_count")
add(checks, "matrix_has_blocked_items", bool(matrix and matrix.get("blocked_count", 0) >= 1), "blocked_count")

combined_release = json.dumps(matrix or {}) + "\n" + matrix_md
for private_token in ["/Users/h1meka", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + private_token.replace("/", "_"), private_token not in combined_release, private_token)

for token in [
    "This phase does not execute provider visibility commands",
    "This phase does not parse raw local capture by default",
    "This phase does not open a provider",
    "This phase does not call IOServiceOpen",
    "This phase does not map BAR memory",
    "This phase does not read BAR0",
    "This phase does not write BAR0",
    "This phase does not submit GPU commands",
    "This phase does not claim RTX 5070 Metal acceleration",
    "This phase does not claim Dock/transparency/blur acceleration",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX_READY" if failed == 0 else "FAIL_SANITIZED_PROVIDER_VISIBILITY_EVIDENCE_MATRIX"

report = {
    "schema": "h1mekartx.sanitized_provider_visibility_evidence_matrix_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "evidence_matrix_only": True,
    "provider_visibility_commands_executed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62k-local-optin-provider-visibility-evidence-capture-runbook",
    "checks": checks,
}
(OUT / "sanitized-provider-visibility-evidence-matrix-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "sanitized-provider-visibility-evidence-matrix-check.md").write_text(f"""# Sanitized Provider Visibility Evidence Matrix Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Evidence Matrix Only: `True`
- Provider Visibility Commands Executed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62k-local-optin-provider-visibility-evidence-capture-runbook`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
if failed:
    for c in checks:
        if not c["passed"]:
            print("FAIL:", c["name"], "|", c["detail"])
raise SystemExit(0 if failed == 0 else 1)
