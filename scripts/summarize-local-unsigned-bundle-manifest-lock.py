#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_unsigned_bundle_manifest_lock_summary.v1"

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/unsigned-app-bundle-manifest-lock/local-unsigned-bundle-manifest-lock.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    entries = local_report.get("entries", []) if local_report else []
    derived = local_report.get("derived", {}) if local_report else {}
    expected_status = local_report.get("expected_status", {}) if local_report else {}

    sanitized_entries = [
        {
            "relative_path": item["relative_path"],
            "size_bytes": item["size_bytes"],
            "mode": item["mode"],
            "sha256": item["sha256"],
            "executable": item["executable"],
        }
        for item in entries
    ]

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK",
        "manifest_lock_summary_only": True,
        "host_report_bundle_local_only": True,
        "local_input_present": local_report is not None,
        "raw_absolute_paths_committed": False,
        "signed_package_created": False,
        "codesign_attempted": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "entry_count": len(sanitized_entries),
        "entries": sanitized_entries,
        "expected_status": expected_status,
        "derived": derived,
    }

    json_path = out_dir / "local-unsigned-bundle-manifest-lock-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    entry_rows = "\n".join(
        f"| `{item['relative_path']}` | `{item['size_bytes']}` | `{item['mode']}` | `{item['sha256']}` | `{item['executable']}` |"
        for item in sanitized_entries
    )
    expected_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in expected_status.items())
    derived_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in derived.items())

    md = f"""# Local Unsigned Bundle Manifest Lock Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Manifest Lock Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Input Present: `{summary['local_input_present']}`
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
- Entry Count: `{summary['entry_count']}`

## Entries

| Relative Path | Size Bytes | Mode | SHA-256 | Executable |
| --- | ---: | --- | --- | --- |
{entry_rows}

## Expected Entry Status

| Relative Path | Present |
| --- | --- |
{expected_rows}

## Derived

| Key | Value |
| --- | --- |
{derived_rows}
"""
    md_path = out_dir / "local-unsigned-bundle-manifest-lock-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
