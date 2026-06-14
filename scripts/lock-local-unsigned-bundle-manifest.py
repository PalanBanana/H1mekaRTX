#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_unsigned_bundle_manifest_lock_report.v1"

EXPECTED_RELATIVE_ENTRIES = [
    "H1mekaRTXHost.app/Contents/Info.plist",
    "H1mekaRTXHost.app/Contents/MacOS/H1mekaRTXHost.placeholder",
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist",
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver.placeholder",
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def mode_string(path: Path) -> str:
    return oct(stat.S_IMODE(path.stat().st_mode))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--bundle-root", default="host-report-bundle/unsigned-app-bundle")
    parser.add_argument("--out-dir", default="host-report-bundle/unsigned-app-bundle-manifest-lock")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    bundle_root = (root / args.bundle_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    if bundle_root.exists():
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                rel = path.relative_to(bundle_root).as_posix()
                entries.append({
                    "relative_path": rel,
                    "size_bytes": path.stat().st_size,
                    "mode": mode_string(path),
                    "sha256": sha256_file(path),
                    "executable": os.access(path, os.X_OK),
                })

    entry_map = {item["relative_path"]: item for item in entries}
    expected_status = {rel: rel in entry_map for rel in EXPECTED_RELATIVE_ENTRIES}

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK",
        "manifest_lock_only": True,
        "local_evidence_only": True,
        "host_report_bundle_local_only": True,
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
        "bundle_root_relative": args.bundle_root,
        "entry_count": len(entries),
        "entries": entries,
        "expected_status": expected_status,
        "derived": {
            "bundle_root_exists": bundle_root.exists(),
            "expected_entries_present": all(expected_status.values()),
            "contains_systemextensions_dir": (bundle_root / "H1mekaRTXHost.app/Contents/Library/SystemExtensions").exists(),
            "contains_dext_under_systemextensions": (bundle_root / "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext").exists(),
            "has_host_info_plist": expected_status["H1mekaRTXHost.app/Contents/Info.plist"],
            "has_dext_info_plist": expected_status["H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist"],
            "has_host_placeholder": expected_status["H1mekaRTXHost.app/Contents/MacOS/H1mekaRTXHost.placeholder"],
            "has_dext_placeholder": expected_status["H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver.placeholder"],
            "unsigned_placeholders_only": True,
        },
    }

    json_path = out_dir / "local-unsigned-bundle-manifest-lock.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    entry_rows = "\n".join(
        f"| `{item['relative_path']}` | `{item['size_bytes']}` | `{item['mode']}` | `{item['sha256']}` | `{item['executable']}` |"
        for item in entries
    )
    expected_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in expected_status.items())
    derived_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in report["derived"].items())

    md = f"""# Local Unsigned Bundle Manifest Lock

- Generated At UTC: `{report['generated_at_utc']}`
- Manifest Lock Only: `True`
- Local Evidence Only: `True`
- Host Report Bundle Local Only: `True`
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
- Entry Count: `{report['entry_count']}`

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
    md_path = out_dir / "local-unsigned-bundle-manifest-lock.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_LOCAL_UNSIGNED_BUNDLE_MANIFEST_LOCK_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
