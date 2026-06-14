#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_unsigned_bundle_manifest_lock_check.v1"

REQUIRED_ENTRIES = [
    "H1mekaRTXHost.app/Contents/Info.plist",
    "H1mekaRTXHost.app/Contents/MacOS/H1mekaRTXHost.placeholder",
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist",
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver.placeholder",
]

FORBIDDEN_PATTERNS = {
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "host_report_bundle_raw_path": re.compile(r"host-report-bundle/unsigned-app-bundle-manifest-lock/local-unsigned-bundle-manifest-lock\.json"),
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "tools/driverkit-buildable-scaffold/local-unsigned-bundle-manifest-lock.json"
    local_report_path = root / "host-report-bundle/unsigned-app-bundle-manifest-lock/local-unsigned-bundle-manifest-lock.json"
    summary_json_path = root / "release-readiness/local-unsigned-bundle-manifest-lock-summary.json"
    summary_md_path = root / "release-readiness/local-unsigned-bundle-manifest-lock-summary.md"
    doc_path = root / "docs/driverkit/local-unsigned-bundle-manifest-lock.md"

    manifest = read_json(manifest_path)
    local_report = read_json(local_report_path)
    summary = read_json(summary_json_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("local_report_exists", local_report_path.exists(), str(local_report_path)),
        make_check("summary_json_exists", summary_json_path.exists(), str(summary_json_path)),
        make_check("summary_md_exists", summary_md_path.exists(), str(summary_md_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_unsigned_bundle_manifest_lock.v1"), "manifest schema"),
        make_check("local_report_schema", bool(local_report and local_report.get("schema") == "h1mekartx.local_unsigned_bundle_manifest_lock_report.v1"), "local report schema"),
        make_check("summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_unsigned_bundle_manifest_lock_summary.v1"), "summary schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("local_report", local_report), ("summary", summary)]:
        for field in [
            "signed_package_created",
            "codesign_attempted",
            "install_attempted",
            "submit_activation_allowed_now",
            "system_extension_activation_attempted",
            "system_extension_deactivation_attempted",
            "dext_load_attempted",
            "provider_open_attempted",
            "bar_mapping_attempted",
            "bar_mmio_mutation_attempted",
            "configuration_writes_attempted",
            "gpu_command_submission_attempted",
            "ui_compositor_proof_claimed",
            "metal_proof_claimed",
        ]:
            checks.append(make_check(f"{obj_name}_{field}_false", bool(obj and obj.get(field) is False), field))

    entries = summary.get("entries", []) if summary else []
    entry_map = {item.get("relative_path"): item for item in entries}

    checks.append(make_check("entry_count_at_least_required", len(entries) >= len(REQUIRED_ENTRIES), str(len(entries))))

    for rel in REQUIRED_ENTRIES:
        item = entry_map.get(rel)
        checks.append(make_check("required_entry_present_" + rel.replace("/", "_"), item is not None, rel))
        checks.append(make_check("required_entry_sha256_" + rel.replace("/", "_"), bool(item and len(str(item.get("sha256", ""))) == 64), rel))
        checks.append(make_check("required_entry_size_" + rel.replace("/", "_"), bool(item and int(item.get("size_bytes", 0)) > 0), rel))

    derived = summary.get("derived", {}) if summary else {}
    for field in [
        "bundle_root_exists",
        "expected_entries_present",
        "contains_systemextensions_dir",
        "contains_dext_under_systemextensions",
        "has_host_info_plist",
        "has_dext_info_plist",
        "has_host_placeholder",
        "has_dext_placeholder",
        "unsigned_placeholders_only",
    ]:
        checks.append(make_check(f"derived_{field}_true", bool(derived.get(field)), field))

    for path in [summary_json_path, summary_md_path]:
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        for name, pattern in FORBIDDEN_PATTERNS.items():
            checks.append(make_check(f"no_{name}_in_{path.name}", not pattern.search(text), name))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK_READY" if failed == 0 else "FAIL_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK",
        "manifest_lock_only": True,
        "host_report_bundle_local_only": True,
        "raw_absolute_paths_committed": False,
        "signed_package_created": False,
        "codesign_attempted": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "entry_count": len(entries),
        "checks": checks,
    }

    json_path = out_dir / "local-unsigned-bundle-manifest-lock-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Local Unsigned Bundle Manifest Lock Check

- Decision: `{decision}`
- Manifest Lock Only: `True`
- Host Report Bundle Local Only: `True`
- Raw Absolute Paths Committed: `False`
- Signed Package Created: `False`
- Codesign Attempted: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Entry Count: `{len(entries)}`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "local-unsigned-bundle-manifest-lock-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
