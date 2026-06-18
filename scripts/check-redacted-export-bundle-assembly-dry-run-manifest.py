#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/redacted-export-bundle-assembly-dry-run-manifest.json"
doc_path = ROOT / "docs/hackintosh/redacted-export-bundle-assembly-dry-run-manifest.md"
out_path = OUT / "redacted-export-bundle-assembly-dry-run-manifest.json"
out_md_path = OUT / "redacted-export-bundle-assembly-dry-run-manifest.md"
manifest, out = read_json(manifest_path), read_json(out_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
out_md = out_md_path.read_text(encoding="utf-8", errors="replace") if out_md_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists())
add(checks, "doc_exists", doc_path.exists())
add(checks, "output_exists", out_path.exists())
add(checks, "output_md_exists", out_md_path.exists())
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.redacted_export_bundle_assembly_dry_run_manifest.v1"))
add(checks, "output_schema", bool(out and out.get("schema") == "h1mekartx.redacted_export_bundle_assembly_dry_run_manifest_output.v1"))
add(checks, "output_decision_pass", bool(out and out.get("decision") == "PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY"))
add(checks, "output_ready_true", bool(out and out.get("redacted_export_bundle_assembly_dry_run_manifest_ready") is True))
for f in ["assembly_present","assembly_all_sources_exist","assembly_all_source_paths_relative","assembly_all_bundle_paths_relative","assembly_forbidden_absent","assembly_all_not_copied","assembly_sha256_present","private_paths_absent","inputs_safe"]:
    add(checks, f"output_{f}_true", bool(out and out.get(f) is True))
add(checks, "output_fail_count_zero", bool(out and out.get("fail_count") == 0))
add(checks, "output_checks_all_pass", bool(out and out.get("checks") and all(i.get("status") == "PASS" for i in out["checks"])))
for obj_name, obj in [("manifest", manifest), ("output", out)]:
    if obj is None:
        continue
    add(checks, f"{obj_name}_rtx5070_target_retained_true", obj.get("rtx5070_target_retained") is True)
    for f in ["fallback_gpu_substitution_allowed","bundle_archive_created_by_this_phase","files_copied_to_export_bundle_by_this_phase","certificates_exported","private_keys_exported","provisioning_assets_exported","raw_ioregistry_exported","provider_handles_exported","actual_apple_entitlement_request_submitted","contacted_apple_by_this_phase","provider_open_attempted","ioserviceopen_attempted","bar_mapping_attempted","bar0_read_attempted","bar0_write_attempted","gpu_command_submission_attempted","current_rtx5070_metal_acceleration_claimed","dock_transparency_blur_acceleration_claimed","absolute_paths_recorded"]:
        if f in obj:
            add(checks, f"{obj_name}_{f}_false", obj.get(f) is False)
for key, val in [("rtx5070_vendor_id","0x10de"),("rtx5070_device_id","0x2f04"),("rtx5070_iopcimatch","0x2f0410de"),("driverkit_bundle_identifier","dev.h1meka.H1mekaRTXDriver"),("host_app_bundle_identifier","dev.h1meka.H1mekaRTXHost"),("next_gate","phase63i-redacted-bundle-assembly-dry-run-consistency-gate")]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == val))
for key, val in [("expected_vendor_id","0x10de"),("expected_device_id","0x2f04"),("expected_iopcimatch","0x2f0410de"),("expected_driverkit_bundle_identifier","dev.h1meka.H1mekaRTXDriver"),("expected_host_app_bundle_identifier","dev.h1meka.H1mekaRTXHost"),("next_gate","phase63i-redacted-bundle-assembly-dry-run-consistency-gate")]:
    add(checks, f"output_{key}", bool(out and out.get(key) == val))
for token in ["This phase is assembly-dry-run-manifest-only","This phase only describes a future bundle layout","This phase does not create an export archive","This phase does not copy files into an export bundle","This phase does not export provisioning assets","This phase does not export certificates","This phase does not export private keys","This phase does not export raw IORegistry data","This phase does not export provider handles","This phase does not submit an Apple entitlement request","This phase does not contact Apple","This phase does not open a provider","This phase does not call IOServiceOpen","This phase does not map BAR memory","This phase does not submit GPU commands","This phase does not claim RTX 5070 Metal acceleration","This phase does not claim Dock/transparency/blur acceleration"]:
    add(checks, "doc_contains_" + token.replace(" ", "_"), token in doc)
for raw in ["/Users/", "/private/var/folders/", "/var/folders/"]:
    add(checks, "release_output_private_path_absent_" + raw.replace("/", "_"), raw not in (json.dumps(out or {}) + "\n" + out_md))

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY" if failed == 0 else "FAIL_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST"
report = {
    "schema": "h1mekartx.redacted_export_bundle_assembly_dry_run_manifest_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "assembly_dry_run_manifest_only": True,
    "bundle_archive_created_by_this_phase": False,
    "files_copied_to_export_bundle_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "bar0_read_attempted": False,
    "bar0_write_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "dock_transparency_blur_acceleration_claimed": False,
    "absolute_paths_recorded": False,
    "next_gate": "phase63i-redacted-bundle-assembly-dry-run-consistency-gate",
    "checks": checks,
}
(OUT / "redacted-export-bundle-assembly-dry-run-manifest-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "redacted-export-bundle-assembly-dry-run-manifest-check.md").write_text(f"# Redacted Export Bundle Assembly Dry-Run Manifest Check\n\n- Decision: `{decision}`\n- Next Gate: `phase63i-redacted-bundle-assembly-dry-run-consistency-gate`\n\n| Check | Status | Detail |\n| --- | --- | --- |\n{rows}\n", encoding="utf-8")
print("Decision:", decision)
if failed:
    for c in checks:
        if not c["passed"]:
            print("FAIL:", c["name"], "|", c["detail"])
raise SystemExit(0 if failed == 0 else 1)
