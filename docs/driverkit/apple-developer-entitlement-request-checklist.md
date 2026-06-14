# Apple Developer Portal Entitlement Request Checklist

## Purpose

Phase 60R records the Apple Developer portal checklist required to unblock DriverKit/System Extension provisioning.

Phase 60Q established a hardblock:

- Personal Team cannot create the required System Extension provisioning profile.
- DriverKit profile request is blocked until DriverKit is enabled.
- DriverKit PCI transport entitlement approval is not proven.
- Host and dext provisioning profiles are missing.

This phase is a checklist and readiness gate only.

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

## Required Apple Developer Account State

Before continuing beyond Phase 60R:

1. Paid Apple Developer Program team exists.
2. Xcode account is signed into that paid team.
3. Team can manage certificates, identifiers, and profiles.
4. Personal Team is not used for the DriverKit/System Extension build path.

## Required Bundle IDs

Create or verify these App IDs / Bundle IDs in Apple Developer portal:

- Host App ID: `dev.h1meka.H1mekaRTXHost`
- DriverKit Dext ID: `dev.h1meka.H1mekaRTXDriver`

## Required Host App Capability

For `dev.h1meka.H1mekaRTXHost`:

- Enable System Extension capability.
- Required entitlement:
  - `com.apple.developer.system-extension.install`

## Required DriverKit Dext Capability

For `dev.h1meka.H1mekaRTXDriver`:

- Request DriverKit entitlement approval from Apple.
- Required entitlement:
  - `com.apple.developer.driverkit`

## Required PCI Transport Entitlement

For RTX 5070 / NVIDIA PCI matching:

- Request DriverKit PCI transport entitlement.
- Required entitlement:
  - `com.apple.developer.driverkit.transport.pci`
- Required PCI match:
  - vendor-id: `0x10de`
  - device-id: `0x2f04`
  - IOPCIMatch: `0x2f0410de`

## Required Provisioning Profiles

Create or allow Xcode to create:

- Mac App Development provisioning profile for:
  - `dev.h1meka.H1mekaRTXHost`
- DriverKit Development provisioning profile for:
  - `dev.h1meka.H1mekaRTXDriver`

## Required Local Verification After Approval

After entitlement/profile approval:

1. Run xcodebuild with `-allowProvisioningUpdates`.
2. Confirm `real_driverkit_dext_built=true` from Phase 60L.
3. Rerun local signing/preflight.
4. Rerun Phase 60I `/Applications` activation remediation.
5. Rerun Phase 60K validationFailed root-cause gate.
6. Only if extension visibility is proven, rerun:
   - Phase 58
   - Phase 59
   - Phase 60A
   - Phase 60B

## Continued Runtime Boundary

Even after Apple approval:

- provider open remains blocked until a later explicit gate
- IOServiceOpen remains blocked until a later explicit gate
- BAR mapping remains blocked until a later explicit gate
- BAR/MMIO mutation remains blocked
- PCI configuration writes remain blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_APPLE_DEVELOPER_ENTITLEMENT_REQUEST_CHECKLIST
- CLASSIFICATION_PROVISIONING_ENTITLEMENT_HARDBLOCK_GATE
- CLASSIFICATION_PORTAL_PREPARATION_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
