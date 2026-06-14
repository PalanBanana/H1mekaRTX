# Codesign Identity + Entitlement Dry-Run Evidence

## Purpose

Phase 50 records local codesign identity and entitlement readiness without signing anything.

This phase is dry-run evidence only.

This phase may run read-only local commands such as security find-identity.

This phase may parse entitlement plist templates.

This phase may compare bundle IDs and expected entitlement keys.

This phase does not run codesign signing.

This phase does not create signed artifacts.

This phase does not install anything.

This phase does not submit an activation request.

This phase does not submit a deactivation request.

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

## Checked Items

- security find-identity -v -p codesigning
- host app entitlement plist parse
- dext entitlement plist parse
- host bundle ID expected value
- dext bundle ID expected value
- system-extension install entitlement key
- DriverKit entitlement key
- DriverKit PCI transport entitlement key
- future signing requirements are still blocked until explicit local signing step

## Classification

- CLASSIFICATION_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_EVIDENCE
- CLASSIFICATION_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT
- CLASSIFICATION_NO_SIGNING_NO_INSTALL_NO_ACTIVATION
- CLASSIFICATION_LOCAL_EVIDENCE_ONLY

## Current State

- CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_READY: True
- DRYRUN_EVIDENCE_ONLY: True
- LOCAL_EVIDENCE_ONLY: True
- CODESIGN_IDENTITY_DISCOVERY_ATTEMPTED: True
- CODESIGN_SIGNING_ATTEMPTED: False
- SIGNED_PACKAGE_CREATED: False
- INSTALL_ATTEMPTED: False
- SUBMIT_ACTIVATION_ALLOWED_NOW: False
- SUBMIT_DEACTIVATION_ALLOWED_NOW: False
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
