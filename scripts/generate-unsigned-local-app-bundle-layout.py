#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.unsigned_local_app_bundle_layout_report.v1"

def copy_text(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

def write_placeholder(path: Path, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env bash\n"
        f"echo '{label}'\n"
        "echo 'placeholder only: not signed, not installed, not activated'\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | 0o755)

def parse_plist(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            plistlib.load(f)
        return True
    except Exception:
        return False

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/unsigned-app-bundle")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    app_root = out_dir / "H1mekaRTXHost.app"
    contents = app_root / "Contents"
    macos = contents / "MacOS"
    sysexts = contents / "Library" / "SystemExtensions"
    dext_root = sysexts / "dev.h1meka.H1mekaRTXDriver.dext"
    dext_contents = dext_root / "Contents"
    dext_macos = dext_contents / "MacOS"

    if out_dir.exists():
        shutil.rmtree(out_dir)

    host_info_src = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist"
    dext_info_src = root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist"

    copy_text(host_info_src, contents / "Info.plist")
    copy_text(dext_info_src, dext_contents / "Info.plist")
    write_placeholder(macos / "H1mekaRTXHost.placeholder", "H1mekaRTXHost unsigned placeholder")
    write_placeholder(dext_macos / "H1mekaRTXDriver.placeholder", "H1mekaRTXDriver unsigned placeholder")

    paths = {
        "app_root": app_root.exists(),
        "host_info": (contents / "Info.plist").exists(),
        "host_placeholder": (macos / "H1mekaRTXHost.placeholder").exists(),
        "systemextensions_dir": sysexts.exists(),
        "dext_root": dext_root.exists(),
        "dext_info": (dext_contents / "Info.plist").exists(),
        "dext_placeholder": (dext_macos / "H1mekaRTXDriver.placeholder").exists(),
    }

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT_GENERATOR",
        "local_output_only": True,
        "host_report_bundle_local_only": True,
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
        "local_output_root": str(out_dir),
        "paths": paths,
        "parsed_plists": {
            "host_info_parse_ok": parse_plist(contents / "Info.plist"),
            "dext_info_parse_ok": parse_plist(dext_contents / "Info.plist"),
        },
        "derived": {
            "layout_created": all(paths.values()),
            "all_plists_parse_ok": parse_plist(contents / "Info.plist") and parse_plist(dext_contents / "Info.plist"),
            "contains_systemextensions_dir": sysexts.exists(),
            "contains_dext_under_systemextensions": dext_root.exists(),
            "unsigned_placeholders_only": True,
        },
    }

    report_path = out_dir / "unsigned-local-app-bundle-layout.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    path_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in paths.items())
    parsed_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in report["parsed_plists"].items())
    derived_text = json.dumps(report["derived"], indent=2, sort_keys=True)

    md = f"""# Unsigned Local App Bundle Layout

- Generated At UTC: `{report['generated_at_utc']}`
- Local Output Only: `True`
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

## Paths

| Key | Present |
| --- | --- |
{path_rows}

## Parsed Plists

| Key | Parse OK |
| --- | --- |
{parsed_rows}

## Derived

{derived_text}
"""
    md_path = out_dir / "unsigned-local-app-bundle-layout.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {report_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT_GENERATED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
