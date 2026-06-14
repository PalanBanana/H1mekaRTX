# Dext Load + Provider Match Status Evidence

## Purpose

Phase 59 records dext load/status and provider match evidence using read-only local observations.

This phase may run:

- systemextensionsctl list
- ioreg read-only queries

This phase may read:

- host-report-bundle/local-activation/actual-local-activation-hard-optin-report.json

This phase commits only sanitized release-readiness outputs.

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

## Evidence Goals

- detect whether the system extension identifier appears in systemextensionsctl list
- detect sanitized status tokens such as activated, enabled, needs user approval, terminated
- detect whether RTX 5070 PCI identity appears in read-only I/O Registry output
- detect whether IOPCIDevice entries contain vendor/device/iopcimatch hints
- preserve raw local output under host-report-bundle only
- commit sanitized status summary only

## Expected RTX 5070 Identity

- vendor_id: 0x10de
- device_id: 0x2f04
- iopcimatch: 0x2f0410de
- extension_identifier: dev.h1meka.H1mekaRTXDriver

## Runtime Boundary

Even if dext/status evidence is observed:

- provider open remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI config writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE
- CLASSIFICATION_LOCAL_ACTIVATION_REPORT_STATUS_SANITIZER
- CLASSIFICATION_READ_ONLY_IOREG_STATUS
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Current State

- DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE_READY: True
- READ_ONLY_STATUS_EVIDENCE_ONLY: True
- RAW_STDOUT_NOT_COMMITTED: True
- RAW_STDERR_NOT_COMMITTED: True
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
