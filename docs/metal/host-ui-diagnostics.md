# Host + UI Compositor Diagnostics

## Purpose

Phase 1 adds read-only host diagnostics for RTX 5070 PCIe identity, BAR-like OS inventory, IORegistry visibility, and macOS host state.

It also adds the first graphics stack diagnostics surface for later UI compositor proof work.

This is not runtime probing.

This is not DriverKit activation.

This is not System Extension activation.

This is not RTX 5070 UI compositor proof.

This is not RTX 5070 Metal proof.

## Scripts

Collect on the test machine:

    ./scripts/collect-host-diagnostics.sh

Optional output path:

    ./scripts/collect-host-diagnostics.sh ~/Desktop/H1mekaRTX-host-diagnostics-test

Summarize collected files:

    ./scripts/summarize-host-diagnostics.py --input-dir ~/Desktop/H1mekaRTX-host-diagnostics-test

Check with local fixtures:

    ./scripts/check-host-diagnostics-report.py --root . --out-dir .

## Captured Host Diagnostics

- macOS version
- kernel version
- architecture
- SIP state
- PCI device report
- RTX 5070 vendor ID, device ID, subsystem ID, and class code hints
- IORegistry PCI paths
- BAR-like `assigned-addresses` and `reg` hints

## Captured Graphics Stack Diagnostics

- display report
- parsed display/Metal observations from `system_profiler SPDisplaysDataType -json`
- IODisplay hints
- IOFramebuffer hints
- IOGraphics hints
- IOAccelerator hints
- WindowServer and Dock process visibility
- Metal, QuartzCore, CoreGraphics, IOSurface, and SkyLight framework path visibility
- recent WindowServer, Dock, CoreAnimation, QuartzCore, Metal, IOAccelerator, IODisplay, and IOFramebuffer log hints

## Result Classification

Every generated summary separates:

- Static contract
- Host diagnostics
- Graphics stack diagnostics
- Runtime probe
- Real GPU command execution
- UI compositor proof
- Metal proof

The summary may report that the RTX 5070 is visible as a PCIe device.

That is Host diagnostics only.

The summary may report graphics stack hints.

That is Graphics stack diagnostics only.

## Explicit Non-Claims

The generated report keeps these as unproven or not claimed:

- Runtime probe: `NOT_ATTEMPTED`
- Real GPU command execution: `NOT_ATTEMPTED`
- UI compositor proof: `UNPROVEN`
- Metal proof: `UNPROVEN`
- RTX 5070 UI acceleration claim: `NOT_CLAIMED`
- RTX 5070 Metal acceleration claim: `NOT_CLAIMED`

## Safety Boundary

This phase is read-only diagnostics.

No DriverKit activation.

No System Extension activation.

No device ownership request.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No BAR poking.

No GPU reset.

No firmware loading.

No GSP initialization.

No display engine initialization.

No framebuffer initialization.

No GPU command submission.

No RTX 5070 shader execution.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
