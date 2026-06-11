#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.release_manifest.v1"

DEFAULT_RELEASE_TAG = "v0.4.11-ci-badge-release-checklist"

MILESTONE_TAGS = [
    "v0.4.3-bar-mmio-safety-map",
    "v0.4.4-bar-inventory-diagnostics",
    "v0.4.5-bar-inventory-report-normalizer",
    "v0.4.6-bar-mmio-risk-ledger",
    "v0.4.7-bar-access-readiness-matrix",
    "v0.4.8-bar-access-policy-default-deny",
    "v0.4.9-forbidden-bar-operation-audit",
    "v0.4.10-ci-bar-safety-gates",
    "v0.4.11-ci-badge-release-checklist",
]

REQUIRED_FILES = [
    "README.md",
    ".github/workflows/bar-safety-gates.yml",
    ".github/release.yml",
    "scripts/collect-bar-inventory.sh",
    "scripts/summarize-bar-inventory.py",
    "scripts/check-bar-safety-boundary.py",
    "scripts/generate-bar-readiness-matrix.py",
    "scripts/generate-bar-access-policy.py",
    "scripts/audit-forbidden-bar-ops.py",
    "scripts/run-bar-safety-gates.sh",
    "scripts/check-release-readiness.py",
    "scripts/generate-release-manifest.py",
    "docs/metal/bar-inventory-diagnostics.md",
    "docs/metal/bar-inventory-report-normalizer.md",
    "docs/metal/bar-mmio-risk-ledger.md",
    "docs/metal/bar-access-readiness-matrix.md",
    "docs/metal/bar-access-policy-default-deny.md",
    "docs/metal/forbidden-bar-operation-audit.md",
    "docs/metal/ci-bar-safety-gates.md",
    "docs/metal/ci-status-badge.md",
    "docs/metal/release-checklist.md",
    "docs/metal/release-manifest.md",
]


def run_git(args: list[str], root: Path, allow_fail: bool = False) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if proc.returncode != 0:
        if allow_fail:
            return ""
        raise SystemExit(
            "git command failed: git {}\n{}".format(" ".join(args), proc.stderr.strip())
        )

    return proc.stdout.strip()


def path_state(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel

    return {
        "path": rel,
        "present": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def tag_state(root: Path, tag: str) -> dict[str, Any]:
    commit = run_git(["rev-parse", "-q", "--verify", f"{tag}^{{commit}}"], root, allow_fail=True)
    subject = ""

    if commit:
        subject = run_git(["log", "-1", "--pretty=%s", commit], root, allow_fail=True)

    return {
        "tag": tag,
        "present": bool(commit),
        "commit": commit,
        "subject": subject,
    }


def build_manifest(root: Path, release_tag: str) -> dict[str, Any]:
    head_commit = run_git(["rev-parse", "HEAD"], root)
    head_subject = run_git(["log", "-1", "--pretty=%s"], root)
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    remote_url = run_git(["config", "--get", "remote.origin.url"], root, allow_fail=True)

    files = [path_state(root, rel) for rel in REQUIRED_FILES]
    tags = [tag_state(root, tag) for tag in MILESTONE_TAGS]

    missing_files = [item["path"] for item in files if not item["present"]]
    missing_tags = [item["tag"] for item in tags if not item["present"]]

    clean_status = run_git(["status", "--porcelain"], root, allow_fail=True)

    decision = "PASS_RELEASE_MANIFEST_READY"
    if missing_files or missing_tags:
        decision = "FAIL_RELEASE_MANIFEST_INCOMPLETE"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "remote_url": remote_url,
        "branch": branch,
        "head": {
            "commit": head_commit,
            "subject": head_subject,
        },
        "release": {
            "tag": release_tag,
            "recommended_title": "H1mekaRTX BAR Safety Diagnostics Milestone",
            "recommended_release_type": "GitHub Release",
            "draft_first": True,
            "generate_release_notes": True,
        },
        "milestone_tags": tags,
        "required_files": files,
        "missing_files": missing_files,
        "missing_tags": missing_tags,
        "working_tree_clean_at_generation": clean_status == "",
        "working_tree_status": clean_status.splitlines(),
        "decision": decision,
        "safety_boundary": {
            "read_only": True,
            "runs_git_metadata_commands": True,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "metal_acceleration_attempt": False,
            "driverkit_activation": False,
        },
    }


def markdown_report(manifest: dict[str, Any]) -> str:
    tag_rows = []
    for item in manifest["milestone_tags"]:
        status = "yes" if item["present"] else "no"
        commit = item["commit"][:12] if item["commit"] else ""
        subject = item["subject"].replace("|", "\\|")
        tag_rows.append(f"| `{item['tag']}` | {status} | `{commit}` | {subject} |")

    file_rows = []
    for item in manifest["required_files"]:
        status = "yes" if item["present"] else "no"
        file_rows.append(f"| `{item['path']}` | {status} | {item['bytes']} |")

    missing_files = manifest["missing_files"]
    missing_tags = manifest["missing_tags"]

    if missing_files:
        missing_file_lines = [f"- `{item}`" for item in missing_files]
    else:
        missing_file_lines = ["- None"]

    if missing_tags:
        missing_tag_lines = [f"- `{item}`" for item in missing_tags]
    else:
        missing_tag_lines = ["- None"]

    return "\n".join(
        [
            "# Release Manifest",
            "",
            f"Generated UTC: `{manifest['generated_at_utc']}`",
            "",
            f"Decision: `{manifest['decision']}`",
            "",
            "## Release",
            "",
            f"Tag: `{manifest['release']['tag']}`",
            "",
            f"Recommended title: `{manifest['release']['recommended_title']}`",
            "",
            f"Draft first: `{manifest['release']['draft_first']}`",
            "",
            f"Generate release notes: `{manifest['release']['generate_release_notes']}`",
            "",
            "## Repository State",
            "",
            f"Branch: `{manifest['branch']}`",
            "",
            f"HEAD: `{manifest['head']['commit'][:12]}`",
            "",
            f"HEAD subject: `{manifest['head']['subject']}`",
            "",
            f"Working tree clean at generation: `{manifest['working_tree_clean_at_generation']}`",
            "",
            "## Missing Files",
            "",
            *missing_file_lines,
            "",
            "## Missing Tags",
            "",
            *missing_tag_lines,
            "",
            "## Milestone Tags",
            "",
            "| Tag | Present | Commit | Subject |",
            "| --- | --- | --- | --- |",
            *tag_rows,
            "",
            "## Required Files",
            "",
            "| File | Present | Bytes |",
            "| --- | --- | ---: |",
            *file_rows,
            "",
            "## Safety Boundary",
            "",
            "This manifest generator reads repository metadata and repository text files only.",
            "",
            "It does not run ioreg, system_profiler, PCI config-space reads, PCI config-space writes, MMIO reads, MMIO writes, BAR memory mapping, BAR memory poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, or DriverKit activation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a release manifest for the H1mekaRTX BAR safety diagnostics milestone."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--release-tag",
        default=DEFAULT_RELEASE_TAG,
        help=f"Release tag to record. Defaults to {DEFAULT_RELEASE_TAG}.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to repo root.",
    )

    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(root, args.release_tag)

    json_path = out_dir / "release-manifest.json"
    md_path = out_dir / "release-manifest.md"

    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(manifest) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {manifest['decision']}")

    if manifest["decision"] != "PASS_RELEASE_MANIFEST_READY":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
