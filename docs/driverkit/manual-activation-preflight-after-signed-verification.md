# Manual Activation Preflight Gate After Signed Artifact Verification

## Purpose

Phase 56 adds a manual activation preflight gate that remains blocked until signed artifact verification is proven.

This phase does not submit an activation request.

This phase does not submit a deactivation request.

This phase does not install anything.

This phase does not load a dext.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Activation Preflight Rule

Activation preflight may be considered ready only when all are true:

- signed artifact verification summary exists
- signed artifact verification OK is true
- signed package created locally is true
- hard opt-in OK is true
- local scope OK is true
- activation still blocked is true
- provider open still blocked is true
- BAR mapping still blocked is true
- GPU command submission still blocked is true
- user approval allowed for future local test is true

If signed artifact verification OK is false or missing, activation remains blocked.

## Next Runtime Boundary

After this gate is ready, the next phase may add an actual local activation script with hard opt-in flags.

Even then:

- Provider open remains blocked.
- BAR mapping remains blocked.
- GPU command submission remains blocked.
- Dock/transparency/blur proof remains blocked.

## Classification

- CLASSIFICATION_MANUAL_ACTIVATION_PREFLIGHT_AFTER_SIGNED_VERIFICATION
- CLASSIFICATION_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER
- CLASSIFICATION_NO_INSTALL_NO_ACTIVATION
- CLASSIFICATION_PREFLIGHT_GATE_ONLY

## Current State

- MANUAL_ACTIVATION_PREFLIGHT_GATE_READY: True
- PREFLIGHT_GATE_ONLY: True
- ACTIVATION_ALLOWED_NOW: False
- DEACTIVATION_ALLOWED_NOW: False
- INSTALL_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_DEACTIVATION_ATTEMPTED: False
- DEXT_LOAD_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
