# CI BAR Safety Gates

## Purpose

Stage 9 adds GitHub Actions CI coverage for the BAR safety tooling.

The workflow runs the local BAR safety gate script on pull requests and pushes.

## Workflow

Workflow file:

    .github/workflows/bar-safety-gates.yml

Job:

    Run BAR safety gates

## Local Runner

Local script:

    ./scripts/run-bar-safety-gates.sh

## What It Checks

The gate script runs:

- Python syntax checks for scripts under `scripts/`
- Stage 4 BAR inventory summary fixture validation
- Stage 5 BAR/MMIO safety boundary validation
- Stage 6 BAR access readiness matrix validation
- Stage 7 default-deny BAR access policy validation
- Stage 8 safe forbidden-operation audit fixture
- Stage 8 unsafe forbidden-operation audit fixture
- Stage 8 repository forbidden-operation audit

## Expected Decisions

Expected Stage 6 readiness:

    NOT_READY

Expected Stage 7 policy:

    DENY_ALL_BAR_ACCESS

Expected Stage 8 repository audit:

    PASS_NO_FORBIDDEN_BAR_OPS

or:

    REVIEW_REQUIRED

The repository audit must not produce:

    FAIL_BLOCKED_OPERATION_FOUND

## Safety Boundary

This CI stage is read-only.

It only runs local scripts against temporary fixture files and repository text files.

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

The CI workflow uses Ubuntu and Python only.

It does not require macOS hardware, RTX hardware, PCI device access, DriverKit entitlements, or Metal availability.

The goal is to prevent accidental escalation from documentation and diagnostics into unsafe BAR/MMIO access code.
