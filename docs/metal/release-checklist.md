# Release Checklist

## Purpose

Stage 10 adds a release checklist for the BAR safety and diagnostics milestone.

This checklist is intended to be used before creating or publishing a GitHub Release.

## Pre-release Checks

Run locally:

    ./scripts/run-bar-safety-gates.sh

Run release readiness check:

    ./scripts/check-release-readiness.py

Expected local gate result:

    BAR safety gates passed

Expected release readiness result:

    PASS_RELEASE_READY

## Required Git Tags

Current milestone tag:

    v0.4.10-ci-bar-safety-gates

## Required GitHub Actions Workflow

Workflow:

    BAR Safety Gates

Workflow file:

    .github/workflows/bar-safety-gates.yml

Expected workflow status on `main`:

    passing

## README Badge

README should include the BAR Safety Gates workflow badge.

Badge target:

    .github/workflows/bar-safety-gates.yml

## GitHub Release Notes

When drafting a GitHub Release, use GitHub's generated release notes flow when possible.

Release note categories are configured by:

    .github/release.yml

## Safety Boundary

This release is documentation, diagnostics, static analysis, and CI only.

This release does not perform:

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

## Release Body Template

Use this structure when drafting the release:

    ## Summary

    Adds read-only BAR inventory diagnostics, BAR/MMIO risk controls, default-deny BAR access policy, forbidden operation auditing, and CI safety gates.

    ## Safety Boundary

    This release is read-only and does not perform PCI config-space writes, MMIO reads, MMIO writes, BAR mapping, BAR poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, or DriverKit activation.

    ## Validation

    - Local BAR safety gates passed
    - Release readiness check passed
    - GitHub Actions BAR Safety Gates passed on main

    ## Tag

    v0.4.10-ci-bar-safety-gates

## Notes

If GitHub Actions is blocked by billing or budget settings, local validation may still pass, but the public workflow badge will remain red until Actions jobs can run successfully.
