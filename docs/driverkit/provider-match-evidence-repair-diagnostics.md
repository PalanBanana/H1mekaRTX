# Provider Match Evidence Repair Diagnostics

## Purpose

Phase 60A adds focused read-only diagnostics to repair missing provider-match evidence.

Phase 60 was merged successfully but the readiness decision can still be blocked when provider-match evidence is incomplete.

This phase may run read-only local status commands:

- systemextensionsctl list
- ioreg read-only queries
- system_profiler read-only queries
- codesign display read-only queries on the local app/dext bundle
- plutil read-only parsing of Info.plist files

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

## Repair Focus

The diagnostics try to explain which evidence is missing:

- system extension identifier missing from systemextensionsctl
- system extension active/enabled token missing
- RTX vendor 0x10de missing from ioreg
- RTX device 0x2f04 missing from ioreg
- IOPCIMatch 0x2f0410de missing from ioreg
- dext bundle ID mismatch
- host bundle ID mismatch
- IOKit personality mismatch
- IOProviderClass mismatch
- IOPCIMatch mismatch
- entitlement evidence mismatch

## Expected Identity

- host_bundle_id: dev.h1meka.H1mekaRTXHost
- dext_bundle_id: dev.h1meka.H1mekaRTXDriver
- extension_identifier: dev.h1meka.H1mekaRTXDriver
- vendor_id: 0x10de
- device_id: 0x2f04
- iopcimatch: 0x2f0410de
- provider_class: IOPCIDevice

## Runtime Boundary

Even if repair diagnostics become complete:

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI config writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS
- CLASSIFICATION_PROVIDER_MATCH_WITHOUT_OPEN_READINESS_GATE
- CLASSIFICATION_READ_ONLY_STATUS_EVIDENCE
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Current State

- PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS_READY: True
- READ_ONLY_DIAGNOSTICS_ONLY: True
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
