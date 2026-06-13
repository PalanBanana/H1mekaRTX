# Phase 1 Diagnostics Bundle Runner

## Purpose

Create one local evidence folder for Phase 1 RTX 5070 host diagnostics and early graphics stack diagnostics.

This runner combines:

- host diagnostics collection
- host diagnostics JSON/Markdown summary
- BAR inventory collection
- BAR inventory JSON/Markdown summary
- local host report bundle creation
- local diagnostics index creation

## Usage

From the repository root:

    ./scripts/create-phase1-diagnostics-bundle.sh

Optional output path:

    ./scripts/create-phase1-diagnostics-bundle.sh ~/Desktop/H1mekaRTX-phase1-diagnostics-test

## Primary Outputs

- host-diagnostics-summary.json
- host-diagnostics-summary.md
- bar-inventory-summary.json
- bar-inventory-summary.md
- local-diagnostics-index.json
- local-diagnostics-index.md
- host-report-bundle/bundle.json
- host-report-bundle/README.md

## Raw Captures

- host-diagnostics-raw/
- bar-inventory-raw/

## Classification

- Host diagnostics: collected.
- Graphics stack diagnostics: collected.
- Runtime probe: not attempted.
- Real GPU command execution: not attempted.
- UI compositor proof: unproven.
- Metal proof: unproven.

## Safety Boundary

This runner performs read-only diagnostics collection and local report generation.

No DriverKit activation.

No System Extension activation.

No device ownership request.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No BAR poking.

No GPU command submission.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
