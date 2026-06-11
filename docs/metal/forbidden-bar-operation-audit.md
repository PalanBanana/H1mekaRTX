# Forbidden BAR Operation Audit

## Purpose

Stage 8 adds a static repository audit for forbidden BAR/MMIO/PCI operation symbols.

This stage is designed to catch accidental escalation from read-only diagnostics into unsafe hardware access code.

## What It Scans For

The audit looks for symbols related to:

- PCI config-space writes
- PCIDriverKit memory reads
- PCIDriverKit memory writes
- legacy IOKit config writes
- legacy IOKit I/O reads and writes
- BAR or device memory mapping
- bus master enablement
- PCI memory space enablement
- PCI DriverKit entitlement usage

## Usage

Run from the repository root:

    ./scripts/audit-forbidden-bar-ops.py

Optional explicit root:

    ./scripts/audit-forbidden-bar-ops.py --root .

Optional output directory:

    ./scripts/audit-forbidden-bar-ops.py --root . --out-dir ~/Desktop/H1mekaRTX-bar-inventory-test

## Outputs

The script writes:

- `forbidden-bar-operation-audit.json`
- `forbidden-bar-operation-audit.md`

## Decisions

| Decision | Meaning |
| --- | --- |
| `PASS_NO_FORBIDDEN_BAR_OPS` | No forbidden operation symbols were found. |
| `REVIEW_REQUIRED` | A review-only pattern was found, such as PCI DriverKit entitlement usage. |
| `FAIL_BLOCKED_OPERATION_FOUND` | A blocked operation pattern was found. |

## Safety Boundary

This stage is read-only.

It scans repository text files only.

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

The audit intentionally excludes documentation files so that safety docs can mention forbidden operations without failing the scan.

The audit script also excludes itself to avoid matching its own forbidden pattern definitions.
