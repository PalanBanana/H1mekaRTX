# GitHub Release Draft Pack

## Purpose

Stage 12 adds a local GitHub Release draft pack generator.

This prepares files that can be used when drafting the GitHub Release for the BAR safety diagnostics milestone.

## Usage

Run from the repository root:

    ./scripts/prepare-github-release-draft.py

Explicit tag:

    ./scripts/prepare-github-release-draft.py --tag v0.4.12-release-manifest-generator

Optional output directory:

    ./scripts/prepare-github-release-draft.py --out-dir ~/Desktop/H1mekaRTX-release-draft

## Outputs

The script writes:

- `github-release-draft.md`
- `github-release-api-payload.json`
- `github-release-submit-checklist.md`
- `github-release-draft-pack.json`
- `github-release-draft-pack.md`

## Expected Decision

Expected result:

    PASS_RELEASE_DRAFT_READY

## Release Guidance

Recommended tag:

    v0.4.12-release-manifest-generator

Recommended title:

    H1mekaRTX BAR Safety Diagnostics Milestone

Recommended GitHub Release options:

- Draft first: true
- Prerelease: false
- Generate release notes: true

## Safety Boundary

This stage is read-only.

It only reads Git metadata and writes local draft files.

It does not call the GitHub API.

It does not create a GitHub Release.

It does not upload release assets.

It does not perform:

- ioreg collection
- system_profiler collection
- PCI config-space reads
- PCI config-space writes
- MMIO reads
- MMIO writes
- BAR memory mapping
- BAR memory poking
- GPU reset logic
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- Metal acceleration attempts
- DriverKit activation

## Notes

The generated API payload is for review only.

Create the final GitHub Release manually through GitHub's release UI unless a later stage explicitly adds release publishing automation.
