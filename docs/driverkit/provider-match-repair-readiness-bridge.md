# Provider Match Repair Readiness Bridge

## Purpose

Phase 60B bridges Phase 60A repair diagnostics into the provider-match readiness decision.

Phase 60A may find enough repaired evidence even when the original Phase 60 gate stayed blocked.

This phase reads sanitized release-readiness outputs only.

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

## Bridge Rule

Provider-open hard opt-in preflight can be considered reachable only when Phase 60A says:

- extension_status_observed is true
- pci_identity_observed is true
- personality_matches is true
- bundle_ids_match is true
- repaired_provider_match_ready is true
- provider_open_allowed is false

Runtime boundaries must also remain blocked:

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked
- Dock/transparency/blur proof remains blocked

## Runtime Boundary

Even if the bridge passes:

- provider open remains blocked until Phase 61 hard opt-in preflight
- IOServiceOpen remains blocked until Phase 61 hard opt-in preflight
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI config writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_PROVIDER_MATCH_REPAIR_READINESS_BRIDGE
- CLASSIFICATION_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
- CLASSIFICATION_PREFLIGHT_BRIDGE_ONLY

## Current State

- PROVIDER_MATCH_REPAIR_READINESS_BRIDGE_READY: True
- PREFLIGHT_BRIDGE_ONLY: True
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
