# UI GPU Attribution Diagnostics

## Purpose

Collect read-only candidate evidence for which GPU, display, framebuffer, and accelerator paths macOS exposes around WindowServer and Dock.

This is Graphics stack diagnostics.

This is not trusted UI GPU attribution.

This is not Runtime probe.

This is not Real GPU command execution.

This is not UI compositor proof.

This is not Metal proof.

## Usage

Collect:

    H1MEKARTX_UI_ATTRIBUTION_LAST=10m \
    ./scripts/collect-ui-gpu-attribution.sh ~/Desktop/H1mekaRTX-ui-gpu-attribution

Summarize:

    ./scripts/summarize-ui-gpu-attribution.py --input-dir ~/Desktop/H1mekaRTX-ui-gpu-attribution

Check with fixtures:

    ./scripts/check-ui-gpu-attribution-diagnostics.py --root . --out-dir .

## Captured Data

- display report
- display report JSON
- IOFramebuffer IORegistry snapshot
- IOAccelerator IORegistry snapshot
- IODisplayConnect IORegistry snapshot
- WindowServer and Dock process visibility
- filtered display/accelerator IORegistry hints
- recent WindowServer, Dock, IOAccelerator, IOFramebuffer, IODisplay, Metal, GPU, and display logs

## Result Classification

The summary may report:

    UI_GPU_ATTRIBUTION_CANDIDATES_CAPTURED

That means only that candidate attribution diagnostics were captured.

It does not mean the current UI compositor backend is trusted-attributed to RTX 5070.

## Explicit Non-Claims

- Trusted UI GPU attribution: not proven.
- RTX 5070 UI GPU attribution: `UNPROVEN`.
- UI compositor proof: `UNPROVEN`.
- Metal proof: `UNPROVEN`.
- RTX 5070 UI acceleration claim: `NOT_CLAIMED`.
- RTX 5070 Metal acceleration claim: `NOT_CLAIMED`.

## Safety Boundary

No DriverKit activation.

No System Extension activation.

No device ownership request.

No process injection.

No WindowServer injection.

No Dock injection.

No private framework patching.

No SIP bypass.

No AMFI bypass.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No GPU command submission.

No RTX 5070 shader execution.

No trusted UI GPU attribution claim.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
