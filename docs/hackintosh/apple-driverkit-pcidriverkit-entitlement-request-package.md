# Apple DriverKit / PCIDriverKit Entitlement Request Package

## Purpose

Phase 62B creates a submission-ready request package for Apple Developer DriverKit and PCIDriverKit entitlements.

This is the fastest safe next step toward real RTX 5070 Dock/transparency/blur acceleration.

The target remains RTX 5070 only.

Fallback GPU substitution is not accepted as RTX 5070 proof.

This phase does not submit anything to Apple.

This phase does not perform hardware mutation.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not submit GPU commands.

This phase does not claim RTX 5070 acceleration.

## Apple Request Targets

Request package target:

- DriverKit entitlement
- PCIDriverKit PCI transport entitlement
- System Extension capability
- DriverKit communicates with drivers capability
- DriverKit development provisioning profile
- Host app system extension provisioning profile

## Bundle Identifiers

Default planned identifiers:

- Host app bundle identifier: `dev.h1meka.H1mekaRTXHost`
- Driver extension bundle identifier: `dev.h1meka.H1mekaRTXDriver`
- Team ID: `<APPLE_TEAM_ID>`

The actual Team ID must be replaced with the paid Apple Developer Program team ID before submission.

## Target PCI Device

RTX 5070 target identity:

- Vendor ID: `0x10de`
- Device ID: `0x2f04`
- IOPCIMatch: `0x2f0410de`
- Subsystem Vendor ID: `0x1458`
- Subsystem ID: `0x417e`

## Request Justification

H1mekaRTX requires DriverKit / PCIDriverKit entitlement access to develop a user-space driver extension that can match and communicate with an NVIDIA RTX 5070 PCI device in a controlled research environment.

The initial access plan is default-deny and read-only.

The project does not request permission to bypass macOS security controls.

The project does not request permission to use kernel extensions.

The project does not request permission to patch WindowServer.

The project does not request permission to bypass SIP, AMFI, Gatekeeper, or code signing.

The project does not request permission to ship a production display driver at this phase.

## Safety Commitments

Initial entitlement usage will be limited to:

- provider match observation
- provider activation diagnostics
- PCI identity verification
- read-only BAR inventory correlation
- local-only diagnostics
- hard-opt-in captures

Initial entitlement usage will not include:

- BAR/MMIO writes
- PCI configuration writes
- firmware loading
- GPU reset
- GSP initialization
- framebuffer initialization
- display engine initialization
- GPU command submission
- Metal acceleration claims
- Dock/transparency/blur acceleration claims

## Current Proof State

Current RTX 5070 Metal acceleration is not claimed.

Current RTX 5070 UI smoothness is not claimed.

Current WindowServer attribution to RTX 5070 is not proven.

Current Core Animation attribution to RTX 5070 is not proven.

Current QuartzCore attribution to RTX 5070 is not proven.

Current Metal compositor attribution to RTX 5070 is not proven.

Current Dock/transparency/blur acceleration proof is not proven.

Phase 62C is not allowed now.

provider open remains blocked.

IOServiceOpen remains blocked.

BAR mapping remains blocked.

BAR/MMIO mutation remains blocked.

PCI configuration writes remain blocked.

GPU command submission remains blocked.

Metal proof remains blocked.

Dock/transparency/blur proof remains blocked.

## Manual Apple Portal Steps

1. Enroll in Apple Developer Program if not already paid/active.
2. Open Apple Developer account.
3. Go to Certificates, Identifiers & Profiles.
4. Create or verify Host App ID.
5. Create or verify Driver Extension App ID.
6. Request System Extension capability for the host app if missing.
7. Request DriverKit entitlement for the driver extension.
8. Request PCIDriverKit PCI transport entitlement for RTX 5070 vendor/device IDs.
9. Regenerate provisioning profiles after entitlement approval.
10. Re-run local provisioning hardblock gate.

## Next Gate

Phase 62C should add local entitlement request status collector.

Phase 62C must still not open a provider or submit GPU commands.

## Classification

- CLASSIFICATION_APPLE_DRIVERKIT_PCIDRIVERKIT_ENTITLEMENT_REQUEST_PACKAGE
- CLASSIFICATION_RTX5070_ONLY_TARGET
- CLASSIFICATION_ENTITLEMENT_PACKAGE_NOT_HARDWARE_ACCESS
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Exact Excluded Initial Usage Terms

The following exact terms are intentionally included for release-readiness validation and Apple request clarity:

- BAR/MMIO writes
- PCI configuration writes
- GPU command submission
- Metal acceleration claims
- Dock/transparency/blur acceleration claims

