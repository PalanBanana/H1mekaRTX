# Activation Delegate Diagnostics Remediation Gate

## Purpose

Phase 60F summarizes local Phase 60E activation delegate diagnostics and chooses the next safe remediation path.

This phase may read:

- host-report-bundle/activation-delegate-diagnostics/activation-delegate-error-diagnostics-report.json

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

## Remediation Routing

If extension identifier is observed:

- rerun Phase 58
- rerun Phase 59
- rerun Phase 60A
- rerun Phase 60B
- proceed to Phase 61 only if provider_match_repair_bridge_ready is true

If delegate says needs user approval:

- open System Settings
- approve the system extension
- rerun Phase 60D
- rerun Phase 60E

If delegate did fail:

- inspect sanitized error domain/code
- go to Phase 60G activation error remediation plan

If delegate timed out:

- go to Phase 60H activation timeout / host lifecycle remediation

If delegate did finish but extension is still not visible:

- go to Phase 60I bundle identifier / app container / install location remediation

## Runtime Boundary

Even if this gate recommends the next step:

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI configuration writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_ACTIVATION_DELEGATE_DIAGNOSTICS_REMEDIATION_GATE
- CLASSIFICATION_ACTIVATION_DELEGATE_ERROR_DIAGNOSTICS
- CLASSIFICATION_REMEDIATION_GATE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
