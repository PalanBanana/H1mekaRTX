# Provider Match Dry-Run Observer Contract

## Purpose

Phase 62E adds a provider match dry-run observer contract for RTX 5070 DriverKit / PCIDriverKit bring-up.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

This phase does not claim Dock/transparency/blur acceleration.

## Dry-Run Observer Scope

This phase defines the evidence that a future observer may collect without provider open:

- DriverKit bundle identifier expected
- IOPCIMatch expected
- RTX 5070 PCI identity expected
- entitlement readiness state
- provider match readiness state
- provider visibility source
- provider match observed boolean
- provider open blocked boolean
- IOServiceOpen blocked boolean
- BAR mapping blocked boolean
- GPU command submission blocked boolean

## RTX 5070 Match Target

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Preconditions For Future Observation

A future provider match observer may run only if:

- provider match readiness gate exists
- local entitlement status summary exists
- RTX 5070 target identity is retained
- fallback GPU substitution is false
- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked

## Current State

Current RTX 5070 Metal acceleration is not proven.

Current RTX 5070 UI smoothness is not proven.

Provider match observation is contract-only in this phase.

Provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR0 read remains blocked.

BAR0 write remains blocked.

GPU command submission remains blocked.

Framebuffer/display path remains blocked.

Metal compositor attribution remains blocked.

Dock/transparency/blur proof remains blocked.

## Safety Boundary

This phase does not run xcodebuild build.

This phase does not submit activation.

This phase does not submit deactivation.

This phase does not install anything.

This phase does not manually load a dext.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not read BAR0.

This phase does not write BAR0.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 62F should add a local provider match dry-run observer summary.

Phase 62F must still not open a provider.

## Classification

- CLASSIFICATION_PROVIDER_MATCH_DRYRUN_OBSERVER_CONTRACT
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_PROVIDER_MATCH_OBSERVER_NOT_PROVIDER_OPEN
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
