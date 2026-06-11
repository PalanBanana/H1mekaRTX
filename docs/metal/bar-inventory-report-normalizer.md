# BAR Inventory Report Normalizer

## Purpose

Add a Stage 4 report normalizer for Stage 3 BAR inventory diagnostics.

Stage 3 collects OS-visible PCI and IORegistry information.

Stage 4 reads that collected output directory and creates:

- `bar-inventory-summary.json`
- `bar-inventory-summary.md`

This makes future BAR/MMIO research easier to compare across machines, macOS builds, firmware states, and PCI attachment paths.

## Usage

First run Stage 3:

    ./scripts/collect-bar-inventory.sh ~/Desktop/H1mekaRTX-bar-inventory-test

Then run Stage 4:

    ./scripts/summarize-bar-inventory.py ~/Desktop/H1mekaRTX-bar-inventory-test

Optional output directory:

    ./scripts/summarize-bar-inventory.py ~/Desktop/H1mekaRTX-bar-inventory-test --out-dir ~/Desktop/H1mekaRTX-bar-report

## Outputs

### JSON

`bar-inventory-summary.json`

Machine-readable summary containing:

- host macOS version
- kernel version
- expected diagnostics file presence
- RTX 5070 PCI target IDs
- target hit counts
- PCI/BAR keyword hint counts
- log keyword counts
- filtered IORegistry preview
- explicit safety boundary

### Markdown

`bar-inventory-summary.md`

Human-readable report for attaching to issues, PRs, and research notes.

## RTX 5070 PCI Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Safety Boundary

This stage is read-only with respect to the machine and GPU.

The normalizer only reads already-collected text files.

It does not perform:

- PCI config-space writes
- MMIO writes
- BAR memory poking
- GPU reset logic
- GSP initialization
- firmware loading
- display engine initialization
- framebuffer initialization
- Metal acceleration attempts
- DriverKit activation

## Notes

This stage intentionally does not infer BAR sizes or MMIO semantics.

It only records OS-visible hints and keyword counts from the Stage 3 diagnostics output.
