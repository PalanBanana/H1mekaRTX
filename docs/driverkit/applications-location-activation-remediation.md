# Applications Location Activation Remediation

## Purpose

Phase 60I remediates OSSystemExtensionErrorDomain code 3 by staging the host app into /Applications before submitting System Extension activation.

Observed Phase 60F/60G result:

- delegate_did_fail: true
- delegate_error_domain: OSSystemExtensionErrorDomain
- delegate_error_code: 3
- extension_identifier_observed: false

Code 3 is treated as unsupported parent bundle location. The host app containing the System Extension must be run from /Applications.

This phase adds a hard opt-in local remediation script.

Default behavior refuses staging and activation.

CI must not copy anything to /Applications.

CI must not submit activation.

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

Actual local /Applications staging is allowed only when all flags are present:

- --i-understand-applications-staging
- --stage-to-applications
- --submit-activation
- --signing-identity <IDENTITY_OR_SHA1>
- --output-under-host-report-bundle

Optional:

- --replace-existing
- --use-sudo
- --wait-seconds <N>
- --poll-interval-seconds <N>

## Runtime Behavior With Opt-In

The script may:

- verify Phase 56 activation_preflight_ready=true
- copy the local host app bundle to /Applications/H1mekaRTXHost.app
- build the activation diagnostics Swift host into the /Applications app bundle
- re-sign embedded dext
- re-sign host app
- submit activation from /Applications/H1mekaRTXHost.app
- poll systemextensionsctl list for dev.h1meka.H1mekaRTXDriver
- write local-only raw report under host-report-bundle

## Runtime Boundary

Even if /Applications activation succeeds:

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI config writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_APPLICATIONS_LOCATION_ACTIVATION_REMEDIATION
- CLASSIFICATION_ACTIVATION_ERROR_REMEDIATION_PLAN
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
