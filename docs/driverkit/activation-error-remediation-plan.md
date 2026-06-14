# Activation Error Remediation Plan

## Purpose

Phase 60G records the remediation plan for Phase 60F delegate failure.

Observed Phase 60F result:

- delegate_did_fail: true
- delegate_needs_user_approval: false
- delegate_timeout: false
- extension_identifier_observed: false
- next_gate: phase60g_activation_error_remediation_plan

The current diagnostics host printed escaped Swift interpolation placeholders for NSError domain/code.

Therefore, Phase 60G must fix diagnostics first so the next runtime attempt captures real NSError domain and code.

This phase is a remediation plan plus diagnostics-host patch only.

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

## Fix Required

Patch the Swift activation diagnostics host so didFailWithError prints real interpolation values:

- H1MEKARTX_SYSEXT_ERROR_DOMAIN=<real NSError domain>
- H1MEKARTX_SYSEXT_ERROR_CODE=<real NSError code>
- H1MEKARTX_SYSEXT_ERROR_DESCRIPTION=<real localized description>
- H1MEKARTX_SYSEXT_ERROR_TEXT=<real combined text>

The host must not print literal placeholders such as:

- \(nsError.domain)
- \(nsError.code)

## Next Runtime Step

After Phase 60G merges:

1. rerun activation-delegate-error-diagnostics.py with hard opt-in flags
2. rerun Phase 60F remediation gate
3. route based on real NSError domain/code

## Possible Remediation Routes After Real Error Capture

- needs user approval → approve in System Settings, rerun Phase 60D/60E
- entitlement/provisioning error → fix entitlements/provisioning/signing
- bundle/location error → fix bundle embedding and app location
- unsupported extension type / DriverKit entitlement error → fix DriverKit entitlement approval
- timeout/no callback → fix host lifecycle and run loop

## Runtime Boundary

Even if real error capture succeeds:

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI configuration writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_ACTIVATION_ERROR_REMEDIATION_PLAN
- CLASSIFICATION_ACTIVATION_DELEGATE_DIAGNOSTICS_REMEDIATION_GATE
- CLASSIFICATION_DIAGNOSTICS_PATCH_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
