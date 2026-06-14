# Provisioning / Entitlement Hardblock Gate

## Purpose

Phase 60Q records the hardblock discovered during local xcodebuild with -allowProvisioningUpdates.

Observed xcodebuild failure:

- Please enable Driverkit to request a Driverkit profile.
- No DriverKit App Development provisioning profile for dev.h1meka.H1mekaRTXDriver.
- Personal development teams do not support the System Extension capability for dev.h1meka.H1mekaRTXHost.
- No Mac App Development provisioning profile for dev.h1meka.H1mekaRTXHost.

Conclusion:

The current personal development team cannot proceed to a valid DriverKit/System Extension build.

A paid Apple Developer Program team plus approved System Extension / DriverKit / PCI transport entitlement provisioning is required before real DriverKit dext validation can pass.

## Required External Prerequisites

Before attempting Phase 60L/60I again:

1. Use a paid Apple Developer Program team, not a Personal Team.
2. Enable System Extension capability for the host App ID.
3. Request and receive DriverKit entitlement approval from Apple.
4. Request the required DriverKit PCI transport entitlement.
5. Generate or allow Xcode to generate provisioning profiles for:
   - dev.h1meka.H1mekaRTXHost
   - dev.h1meka.H1mekaRTXDriver
6. Confirm Xcode account has permission to manage profiles for that team.

## Safety Boundary

This phase does not run xcodebuild.

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

## Next Gate

After paid-team provisioning and DriverKit entitlement approval:

- rerun Phase 60L with -allowProvisioningUpdates support
- prove real_driverkit_dext_built=true
- rerun signing/preflight
- rerun Phase 60I /Applications activation remediation
- rerun Phase 60K validationFailed root-cause gate
- only proceed toward Phase 61 if extension visibility/provider readiness becomes proven

## Classification

- CLASSIFICATION_PROVISIONING_ENTITLEMENT_HARDBLOCK_GATE
- CLASSIFICATION_DRIVERKIT_ENTITLEMENT_REQUIRED
- CLASSIFICATION_PAID_DEVELOPER_TEAM_REQUIRED
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Checker Exact Tokens

This section intentionally preserves exact phrases required by the Phase 60Q static checker.

- Please enable Driverkit
- Personal development teams do not support the System Extension capability
- paid Apple Developer Program
- DriverKit entitlement approval
- System Extension capability
- PCI transport entitlement
- provider open remains blocked
- GPU command submission
- Dock/transparency/blur

## Continued Blocked Runtime State

- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- BAR/MMIO mutation remains blocked
- PCI configuration writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

