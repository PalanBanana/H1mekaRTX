#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/sanitized-noopen-provider-match-dryrun-output-parser.json"
doc_path = ROOT / "docs/hackintosh/sanitized-noopen-provider-match-dryrun-output-parser.md"
summary_path = ROOT / "release-readiness/sanitized-noopen-provider-match-dryrun-output-parser-summary.json"
summary_md_path = ROOT / "release-readiness/sanitized-noopen-provider-match-dryrun-output-parser-summary.md"

manifest = read_json(manifest_path)
summary = read_json(summary_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
summary_md = summary_md_path.read_text(encoding="utf-8", errors="replace") if summary_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_exists", summary_path.exists(), str(summary_path))
add(checks, "summary_md_exists", summary_md_path.exists(), str(summary_md_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.sanitized_noopen_provider_match_dryrun_output_parser.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.sanitized_noopen_provider_match_dryrun_output_parser_summary.v1"), "summary schema")

summary_decision = str(summary.get("decision", "") if summary else "")
add(
    checks,
    "default_parse_refuses_without_hardoptin",
    bool(summary and summary.get("hard_opt_in_matched") is False and summary.get("raw_capture_read") is False and summary_decision == "REFUSED_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_PARSE_MISSING_HARD_OPTIN"),
    f"decision={summary_decision!r}",
)

for obj_name, obj in [("manifest", manifest), ("summary", summary)]:
    for field in ["rtx5070_target_retained", "hard_opt_in_required"]:
        if obj is not None and field in obj:
            add(checks, f"{obj_name}_{field}_true", obj.get(field) is True, field)
    for field in [
        "fallback_gpu_substitution_allowed",
        "provider_visibility_commands_executed_by_this_phase",
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
    ("next_gate", "phase62r-noopen-provider-match-dryrun-evidence-matrix"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for key, value in [
    ("expected_vendor_id", "0x10de"),
    ("expected_device_id", "0x2f04"),
    ("expected_iopcimatch", "0x2f0410de"),
    ("expected_driverkit_bundle_identifier", "dev.h1meka.H1mekaRTXDriver"),
    ("next_gate", "phase62r-noopen-provider-match-dryrun-evidence-matrix"),
]:
    add(checks, f"summary_{key}", bool(summary and summary.get(key) == value), f"{key}={value}")

for token in [
    "This phase is parser-only by default",
    "This phase does not execute provider match dry-run commands",
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

combined_release = json.dumps(summary or {}) + "\n" + summary_md
for private_token in ["/Users/h1meka", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + private_token.replace("/", "_"), private_token not in combined_release, private_token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT_PARSER_READY" if failed == 0 else "FAIL_SANITIZED_NOOPEN_PROVIDER_MATCH_DRYRUN_OUTPUT_PARSER"

report = {
    "schema": "h1mekartx.sanitized_noopen_provider_match_dryrun_output_parser_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "parser_only": True,
    "provider_visibility_commands_executed_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "next_gate": "phase62r-noopen-provider-match-dryrun-evidence-matrix",
    "checks": checks,
}
(OUT / "sanitized-noopen-provider-match-dryrun-output-parser-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "sanitized-noopen-provider-match-dryrun-output-parser-check.md").write_text(f"""# Sanitized No-Open Provider Match Dry-Run Output Parser Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Parser Only: `True`
- Provider Visibility Commands Executed By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `phase62r-noopen-provider-match-dryrun-evidence-matrix`

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
