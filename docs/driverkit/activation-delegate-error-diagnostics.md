# Activation Delegate / Error Diagnostics

## Purpose

Phase 60E adds hard opt-in activation diagnostics that capture OSSystemExtensionRequest delegate outcomes and local sysextd/kernelmanagerd status.

Phase 60D proved that activation was submitted, but the extension identifier was not observed in systemextensionsctl status.

This phase adds diagnostics for:

- request did finish result
- request did fail error
- request needs user approval
- replacement action path
- systemextensionsctl before and after
- sysextd/kernelmanagerd/syspolicyd local logs

This phase commits only scripts and sanitized checks.

Local raw diagnostic logs remain under host-report-bundle only.

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

## Required Runtime Flags

Actual local delegate diagnostics are allowed only when all flags are present:

- --i-understand-activation-delegate-diagnostics
- --submit-activation
- --signing-identity <IDENTITY_OR_SHA1>
- --output-under-host-report-bundle

Optional:

- --wait-seconds <N>
- --log-last <DURATION>

## Expected Identifier

- dev.h1meka.H1mekaRTXDriver

## Runtime Boundary

Even if activation diagnostics succeed:

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI config writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_ACTIVATION_DELEGATE_ERROR_DIAGNOSTICS
- CLASSIFICATION_ACTIVATION_WAIT_SYSTEM_EXTENSION_VISIBILITY_HARDENING
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
