# Provider Match Without Open Readiness Gate

## Purpose

Phase 60 adds a readiness gate for provider match evidence without opening the provider.

This phase may read sanitized Phase 59 evidence:

- release-readiness/dext-load-provider-match-status-summary.json

This phase does not run ioreg.

This phase does not run systemextensionsctl.

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

## Readiness Rule

Provider-open preflight may be considered ready only when:

- Phase 59 summary exists
- activation command completed is true
- extension identifier is observed in systemextensionsctl status
- RTX vendor 0x10de is observed in read-only ioreg status
- RTX device 0x2f04 is observed in read-only ioreg status
- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked

If any required evidence is missing, provider-open preflight remains blocked.

## Runtime Boundary

Even if provider-match readiness is true:

- provider open remains blocked until a separate hard opt-in preflight
- IOServiceOpen remains blocked until a separate hard opt-in preflight
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI config writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_PROVIDER_MATCH_WITHOUT_OPEN_READINESS_GATE
- CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
- CLASSIFICATION_PREFLIGHT_GATE_ONLY

## Current State

- PROVIDER_MATCH_WITHOUT_OPEN_READINESS_GATE_READY: True
- PREFLIGHT_GATE_ONLY: True
- PROVIDER_OPEN_ALLOWED_NOW: False
- IOSERVICEOPEN_ALLOWED_NOW: False
- BAR_MAPPING_ALLOWED_NOW: False
- GPU_COMMAND_SUBMISSION_ALLOWED_NOW: False
- ACTIVATION_SUBMITTED_BY_THIS_PHASE: False
- DEACTIVATION_SUBMITTED_BY_THIS_PHASE: False
- INSTALL_ATTEMPTED: False
- MANUAL_DEXT_LOAD_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- IOSERVICEOPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
