#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "host-report-bundle" / "local-signing-identity-selector"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def run(cmd: list[str]) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=30)
        return {"command": cmd, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as e:
        return {"command": cmd, "returncode": None, "stdout": "", "stderr": str(e)}

def sanitize_identity(line: str) -> dict:
    # Example line:
    # 1) HASH "Apple Development: Name (TEAMID)"
    m = re.search(r'\)\s+([A-Fa-f0-9]+)\s+"(.+)"', line)
    if not m:
        return {"raw_line_present": bool(line), "hash_present": False, "display_name": "", "team_id_hint": ""}
    display = m.group(2)
    team = ""
    tm = re.search(r"\(([A-Z0-9]{10})\)", display)
    if tm:
        team = tm.group(1)
    return {
        "raw_line_present": True,
        "hash_present": True,
        "display_name": display,
        "team_id_hint": team,
        "recommended_arg": display,
    }

def main() -> int:
    if not shutil.which("security"):
        report = {
            "schema": "h1mekartx.local_signing_identity_selector_report.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "security_available": False,
            "identity_count": 0,
            "identities": [],
            "activation_attempted": False,
            "install_attempted": False,
            "provider_open_attempted": False,
            "bar_mapping_attempted": False,
            "gpu_command_submission_attempted": False,
        }
        (OUT_DIR / "identity-selector-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("security not found")
        return 1

    result = run(["security", "find-identity", "-v", "-p", "codesigning"])
    lines = [ln.strip() for ln in result["stdout"].splitlines() if ")" in ln and '"' in ln]
    identities = [sanitize_identity(ln) for ln in lines]

    report = {
        "schema": "h1mekartx.local_signing_identity_selector_report.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "security_available": True,
        "returncode": result["returncode"],
        "identity_count": len(identities),
        "identities": identities,
        "activation_attempted": False,
        "install_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
    }

    (OUT_DIR / "identity-selector-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("== Available signing identities ==")
    if not identities:
        print("No codesigning identity detected.")
        return 2

    for idx, item in enumerate(identities, 1):
        print(f"{idx}. {item['display_name']}")
        if item.get("team_id_hint"):
            print(f"   Team ID hint: {item['team_id_hint']}")
        print("")

    print("Use one identity exactly like this:")
    print("")
    print('python3 scripts/actual-local-signing-hard-optin.py --root . --i-understand-local-signing --signing-identity "IDENTITY_NAME_HERE" --output-under-host-report-bundle')
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
