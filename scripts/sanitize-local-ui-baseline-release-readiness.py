#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

TARGETS = [
    "release-readiness/local-ui-baseline-artifact-summary.json",
    "release-readiness/local-ui-baseline-artifact-summary.md",
    "release-readiness/local-ui-baseline-artifact-summary-check.json",
    "release-readiness/local-ui-baseline-artifact-summary-check.md",
    "release-readiness/local-readonly-ui-baseline-check.json",
    "release-readiness/local-readonly-ui-baseline-check.md",
]

RAW_PATH_REPLACEMENTS = {
    "host-report-bundle/ui-baseline/local-readonly-ui-baseline.json": "<LOCAL_READONLY_UI_BASELINE_JSON>",
    "host-report-bundle/ui-baseline/local-readonly-ui-baseline.md": "<LOCAL_READONLY_UI_BASELINE_MD>",
}

PRIVATE_PATH_PATTERNS = [
    (re.compile(r"/Users/[^/\\s\"'`]+(?:/[^\\s\"'`]*)?"), "<USER_PATH>"),
    (re.compile(r"/private/var/folders/[^\\s\"'`]+"), "<TMP_PATH>"),
    (re.compile(r"/var/folders/[^\\s\"'`]+"), "<TMP_PATH>"),
]

def sanitize_text(text: str, root: Path) -> str:
    root_text = str(root)
    if root_text:
        text = text.replace(root_text, "<REPO_ROOT>")

    for raw, repl in RAW_PATH_REPLACEMENTS.items():
        text = text.replace(f"<REPO_ROOT>/{raw}", repl)
        text = text.replace(raw, repl)

    for pattern, repl in PRIVATE_PATH_PATTERNS:
        text = pattern.sub(repl, text)

    # One more pass in case path replacement created mixed placeholders.
    for raw, repl in RAW_PATH_REPLACEMENTS.items():
        text = text.replace(f"<REPO_ROOT>/{raw}", repl)
        text = text.replace(raw, repl)

    return text

def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize local UI baseline release-readiness summaries.")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    changed = []

    for rel in TARGETS:
        path = root / rel
        if not path.exists():
            continue
        before = path.read_text(encoding="utf-8", errors="replace")
        after = sanitize_text(before, root)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(rel)

    print("Sanitized files:")
    for rel in changed:
        print(f"- {rel}")
    if not changed:
        print("- none")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
