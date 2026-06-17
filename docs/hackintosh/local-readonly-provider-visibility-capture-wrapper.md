# Local Read-Only Provider Visibility Capture Wrapper

## Purpose

Phase 62H adds a local hard-opt-in wrapper for read-only provider visibility capture.

This phase may execute only read-only discovery commands after explicit local opt-in.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## Opt-In

Default behavior must refuse capture.

Capture is allowed only with:

`H1MEKARTX_ALLOW_READONLY_PROVIDER_VISIBILITY=I_UNDERSTAND_READONLY_PROVIDER_VISIBILITY_ONLY`

## Allowed Read-Only Sources

- `ioreg` read-only tree inspection
- `systemextensionsctl list`
- `kmutil showloaded`
- `log show` recent DriverKit/SystemExtension messages

## Forbidden

- provider open
- IOServiceOpen
- BAR mapping
- BAR0 read
- BAR0 write
- BAR/MMIO mutation
- PCI configuration writes
- firmware loading
- GPU reset
- framebuffer/display-engine init
- GPU command submission
- Metal proof claim
- Dock/transparency/blur acceleration claim

## Local-Only Output

Raw local capture must be written under:

`host-report-bundle/readonly-provider-visibility/`

This directory must remain local-only and must not be committed.

Sanitized summaries may be written under:

`release-readiness/`

## RTX 5070 Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Current State

Current RTX 5070 Metal acceleration is not proven.

Current RTX 5070 UI smoothness is not proven.

Provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR0 read remains blocked.

BAR0 write remains blocked.

GPU command submission remains blocked.

Framebuffer/display path remains blocked.

Metal compositor attribution remains blocked.

Dock/transparency/blur proof remains blocked.

## Next Gate

Phase 62I should add sanitized local provider visibility capture parser.

Phase 62I must still not open a provider.

## Classification

- CLASSIFICATION_LOCAL_READONLY_PROVIDER_VISIBILITY_CAPTURE_WRAPPER
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_HARDOPTIN_READONLY_CAPTURE
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
