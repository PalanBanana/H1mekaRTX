# UI Compositor Sample Diagnostics

## Purpose

Collect a read-only sample around macOS UI compositor activity after the user manually exercises Dock, window movement, window resize, Mission Control, Launchpad, transparency, and blur surfaces.

This is Graphics stack diagnostics.

This is not Runtime probe.

This is not Real GPU command execution.

This is not UI compositor proof.

This is not Metal proof.

## Usage

Run the UI actions first, then collect a sample:

    H1MEKARTX_UI_SAMPLE_LABEL=dock-window-mission-control \
    H1MEKARTX_UI_SAMPLE_LAST=5m \
    ./scripts/collect-ui-compositor-sample.sh ~/Desktop/H1mekaRTX-ui-sample

Summarize:

    ./scripts/summarize-ui-compositor-sample.py --input-dir ~/Desktop/H1mekaRTX-ui-sample

Check with fixtures:

    ./scripts/check-ui-compositor-sample-diagnostics.py --root . --out-dir .

## Suggested Manual Sequence

- Move a window.
- Resize a window.
- Open Mission Control.
- Open Launchpad.
- Move the pointer over Dock icons if Dock magnification is enabled.
- Observe transparency, blur, menu bar, Dock, sidebars, and Notification Center.

## Captured Data

- sample metadata
- macOS version
- uptime
- display report
- display report JSON
- IODisplayConnect IORegistry snapshot
- IOFramebuffer IORegistry snapshot
- IOAccelerator IORegistry snapshot
- WindowServer and Dock process visibility
- UI preference state for reduce transparency, reduce motion, Dock magnification, Dock autohide, and expose animation duration
- filtered graphics IORegistry hints
- recent WindowServer, Dock, CoreAnimation, QuartzCore, Metal, IOAccelerator, IODisplay, IOFramebuffer, blur, backdrop, and vibrancy logs

## Result Classification

The summary may report:

    UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_CAPTURED

That means only that read-only graphics stack diagnostics were captured.

It does not mean RTX 5070 UI compositor acceleration is proven.

## Explicit Non-Claims

- UI compositor proof: `UNPROVEN`
- Metal proof: `UNPROVEN`
- RTX 5070 UI acceleration claim: `NOT_CLAIMED`
- RTX 5070 Metal acceleration claim: `NOT_CLAIMED`

## Safety Boundary

No DriverKit activation.

No System Extension activation.

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

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
