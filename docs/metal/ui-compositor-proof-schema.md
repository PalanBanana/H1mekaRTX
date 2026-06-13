# UI Compositor Proof Schema

## Purpose

Define the evidence required before this project may claim RTX 5070-backed macOS UI compositor acceleration.

This is a static contract.

This is not Host diagnostics.

This is not Runtime probe.

This is not Real GPU command execution.

This is not UI compositor proof.

This is not Metal proof.

## Claim State

Current decision:

    UI_COMPOSITOR_PROOF_SCHEMA_READY

Current claim state:

    ui_compositor_acceleration_claim_allowed_now: false
    metal_acceleration_claim_allowed_now: false

## UI Surfaces Covered

- Dock movement
- Dock magnification
- Window move
- Window resize
- Mission Control
- Launchpad
- Transparency and blur
- Menu bar and sidebar translucency

## Required Evidence Themes

- target identity
- BAR inventory
- graphics stack visibility
- current UI GPU attribution
- WindowServer/Core Animation timing
- RTX 5070 GPU workload attribution
- UI surface correlation

## Minimum Claim Rule

UI compositor acceleration may be claimed only after target identity, graphics stack visibility, UI GPU attribution, timing evidence, RTX 5070 workload attribution, and UI surface correlation are all present.

## Forbidden Shortcuts

- Treating PCIe visibility as UI acceleration proof.
- Treating BAR inventory as Metal proof.
- Treating IOAccelerator keyword hits as RTX 5070 compositor proof.
- Treating a Metal device list alone as RTX 5070 Metal proof.
- Spoofing a Metal device.
- Patching private frameworks.
- Bypassing SIP or AMFI.
- Injecting into WindowServer or Dock.

## Scripts

Generate the schema:

    ./scripts/generate-ui-compositor-proof-schema.py --out-dir .

Check the schema:

    ./scripts/check-ui-compositor-proof-schema.py --root . --out-dir .

## Safety Boundary

This schema is a static contract only.

No live diagnostics.

No DriverKit activation.

No System Extension activation.

No device ownership request.

No PCI config-space writes.

No MMIO reads.

No MMIO writes.

No BAR mapping.

No BAR poking.

No GPU command submission.

No WindowServer injection.

No Dock injection.

No private framework patching.

No SIP bypass.

No AMFI bypass.

No fake Metal device spoofing.

No RTX 5070 UI compositor acceleration claim.

No RTX 5070 Metal acceleration claim.
