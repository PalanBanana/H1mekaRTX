#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.github_release_draft_pack.v1"

DEFAULT_TAG = "v0.4.12-release-manifest-generator"
DEFAULT_TITLE = "H1mekaRTX BAR Safety Diagnostics Milestone"

SAFETY_BOUNDARY_TEXT = (
    "This release is read-only and does not perform PCI config-space writes, "
    "MMIO reads, MMIO writes, BAR memory mapping, BAR memory poking, GPU reset logic, "
    "firmware loading, GSP initialization, display engine initialization, framebuffer "
    "initialization, Metal acceleration attempts, or DriverKit activation."
)

RELEASE_HIGHLIGHTS = [
    "BAR inventory diagnostics",
    "BAR inventory report normalization",
    "BAR/MMIO risk ledger",
    "BAR access readiness matrix",
    "default-deny BAR access policy",
    "forbidden BAR operation static audit",
    "CI BAR safety gates",
    "CI badge and release checklist",
    "release manifest generation",
]

REQUIRED_VALIDATION_COMMANDS = [
    "./scripts/run-bar-safety-gates.sh",
    "./scripts/check-release-readiness.py --root . --out-dir .",
    "./scripts/generate-release-manifest.py --root . --out-dir .",
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


def tag_commit(root: Path, tag: str) -> str:
    return run_git(["rev-parse", "-q", "--verify", f"{tag}^{{commit}}"], root, allow_fail=True)


def build_release_body(tag: str, target_commit: str) -> str:
    highlights = "\n".join(f"- {item}" for item in RELEASE_HIGHLIGHTS)
    validation = "\n".join(f"- `{item}`" for item in REQUIRED_VALIDATION_COMMANDS)

    return "\n".join(
        [
            "## Summary",
            "",
            "Adds the BAR safety diagnostics milestone for H1mekaRTX.",
            "",
            "This milestone keeps RTX 5070 PCI/BAR research in a read-only diagnostics, reporting, policy, audit, CI, and release-preparation boundary.",
            "",
            "## Highlights",
            "",
            highlights,
            "",
            "## Safety Boundary",
            "",
            SAFETY_BOUNDARY_TEXT,
            "",
            "## Validation",
            "",
            validation,
            "",
            "Expected validation results:",
            "",
            "- `BAR safety gates passed`",
            "- `PASS_RELEASE_READY`",
            "- `PASS_RELEASE_MANIFEST_READY`",
            "",
            "## Release Tag",
            "",
            f"`{tag}`",
            "",
            "## Target Commit",
            "",
            f"`{target_commit}`",
            "",
            "## Notes",
            "",
            "Use GitHub's generated release notes flow to append merged PRs, contributors, and the full changelog when drafting the final GitHub Release.",
            "",
        ]
    )


def build_submit_checklist(tag: str, title: str) -> str:
    return "\n".join(
        [
            "# GitHub Release Submit Checklist",
            "",
            "## Release Settings",
            "",
            f"- Tag: `{tag}`",
            f"- Title: `{title}`",
            "- Target: `main`",
            "- Draft first: `true`",
            "- Prerelease: `false`",
            "- Generate release notes: `true`",
            "",
            "## Before Publishing",
            "",
            "- Confirm `BAR Safety Gates` is green on `main`.",
            "- Confirm local `./scripts/run-bar-safety-gates.sh` passes.",
            "- Confirm `./scripts/check-release-readiness.py --root . --out-dir .` returns `PASS_RELEASE_READY`.",
            "- Confirm `./scripts/generate-release-manifest.py --root . --out-dir .` returns `PASS_RELEASE_MANIFEST_READY`.",
            "- Confirm the release body includes the safety boundary.",
            "- Confirm no release asset contains generated local audit artifacts unless intentionally attached.",
            "",
            "## Safety Boundary",
            "",
            SAFETY_BOUNDARY_TEXT,
            "",
        ]
    )


def build_pack(root: Path, tag: str, title: str) -> dict[str, Any]:
    head_commit = run_git(["rev-parse", "HEAD"], root)
    head_subject = run_git(["log", "-1", "--pretty=%s"], root)
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    remote_url = run_git(["config", "--get", "remote.origin.url"], root, allow_fail=True)
    tag_target = tag_commit(root, tag)

    body = build_release_body(tag, tag_target or head_commit)

    payload = {
        "tag_name": tag,
        "target_commitish": "main",
        "name": title,
        "body": body,
        "draft": True,
        "prerelease": False,
        "generate_release_notes": True,
    }

    decision = "PASS_RELEASE_DRAFT_READY"
    problems: list[str] = []

    if not tag_target:
        decision = "FAIL_RELEASE_DRAFT_NOT_READY"
        problems.append(f"tag not found: {tag}")

    if branch != "main":
        problems.append(f"generated from branch {branch}; expected main after merge")

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
            "tag": tag,
            "tag_commit": tag_target,
            "title": title,
            "target_commitish": "main",
            "draft": True,
            "prerelease": False,
            "generate_release_notes": True,
        },
        "api_payload": payload,
        "decision": decision,
        "problems": problems,
        "safety_boundary": {
            "read_only": True,
            "runs_git_metadata_commands": True,
            "calls_github_api": False,
            "creates_github_release": False,
            "uploads_release_assets": False,
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare local GitHub Release draft files for the H1mekaRTX BAR safety diagnostics milestone."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--tag",
        default=DEFAULT_TAG,
        help=f"Release tag. Defaults to {DEFAULT_TAG}.",
    )
    parser.add_argument(
        "--title",
        default=DEFAULT_TITLE,
        help=f"Release title. Defaults to {DEFAULT_TITLE}.",
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

    pack = build_pack(root, args.tag, args.title)

    draft_path = out_dir / "github-release-draft.md"
    payload_path = out_dir / "github-release-api-payload.json"
    checklist_path = out_dir / "github-release-submit-checklist.md"

    draft_path.write_text(pack["api_payload"]["body"] + "\n")
    payload_path.write_text(json.dumps(pack["api_payload"], indent=2, sort_keys=True) + "\n")
    checklist_path.write_text(build_submit_checklist(args.tag, args.title) + "\n")

    pack_path = out_dir / "github-release-draft-pack.json"
    pack_md_path = out_dir / "github-release-draft-pack.md"

    pack_path.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n")
    pack_md_path.write_text(
        "\n".join(
            [
                "# GitHub Release Draft Pack",
                "",
                f"Generated UTC: `{pack['generated_at_utc']}`",
                "",
                f"Decision: `{pack['decision']}`",
                "",
                f"Tag: `{pack['release']['tag']}`",
                "",
                f"Title: `{pack['release']['title']}`",
                "",
                f"Draft: `{pack['release']['draft']}`",
                "",
                f"Prerelease: `{pack['release']['prerelease']}`",
                "",
                f"Generate release notes: `{pack['release']['generate_release_notes']}`",
                "",
                "## Problems",
                "",
                *([f"- `{p}`" for p in pack["problems"]] or ["- None"]),
                "",
                "## Output Files",
                "",
                "- `github-release-draft.md`",
                "- `github-release-api-payload.json`",
                "- `github-release-submit-checklist.md`",
                "- `github-release-draft-pack.json`",
                "- `github-release-draft-pack.md`",
                "",
                "## Safety Boundary",
                "",
                SAFETY_BOUNDARY_TEXT,
                "",
            ]
        )
        + "\n"
    )

    print(f"Wrote: {draft_path}")
    print(f"Wrote: {payload_path}")
    print(f"Wrote: {checklist_path}")
    print(f"Wrote: {pack_path}")
    print(f"Wrote: {pack_md_path}")
    print(f"Decision: {pack['decision']}")

    if pack["decision"] != "PASS_RELEASE_DRAFT_READY":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
