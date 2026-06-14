# Provider Match Readiness Gate

## Purpose

Phase 62D adds a provider match readiness gate for RTX 5070 DriverKit / PCIDriverKit bring-up.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase does not attempt provider match.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 Metal acceleration.

## Provider Match Preconditions

Provider match work is allowed only when the local entitlement status collector reports:

- apple_developer_program_active
- apple_team_id_available
- driverkit_entitlement_request_submitted
- pcidriverkit_transport_entitlement_request_submitted
- system_extension_capability_requested
- host_app_id_configured
- driver_app_id_configured
- driverkit_entitlement_approved
- pcidriverkit_transport_entitlement_approved
- system_extension_capability_approved
- provisioning_profiles_regenerated_after_approval

If any field is false, provider match remains blocked.

## RTX 5070 Match Target

The provider match target remains:

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Ready State Meaning

`ready_for_provider_match = true` means only:

- the entitlement/provisioning path appears locally ready
- provider match dry-run planning may proceed

It does not mean:

- provider open is allowed
- IOServiceOpen is allowed
- BAR mapping is allowed
- BAR/MMIO mutation is allowed
- GPU command submission is allowed
- framebuffer/display path is allowed
- Metal acceleration is proven
- Dock/transparency/blur acceleration is proven

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Provider match is blocked until entitlement status is ready.

Provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR/MMIO mutation remains blocked.

PCI configuration writes remain blocked.

GPU command submission remains blocked.

Framebuffer/display path remains blocked.

Metal compositor attribution remains blocked.

Dock/transparency/blur acceleration proof remains blocked.

## Safety Boundary

This phase does not run xcodebuild build.

This phase does not submit activation.

This phase does not submit deactivation.

This phase does not install anything.

This phase does not manually load a dext.

This phase does not open a provider.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Next Gate

Phase 62E should add a provider match dry-run observer contract.

Phase 62E must still not open a provider unless entitlement readiness is true and hard opt-in is explicit.

## Classification

- CLASSIFICATION_PROVIDER_MATCH_READINESS_GATE
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_PROVIDER_MATCH_GATE_NOT_PROVIDER_OPEN
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
