# DriverKit Activation, Signing, and Entitlement Plan

## Purpose

This document describes the planned signing, entitlement, provisioning, and activation path for `H1mekaRTXProbe`.

The current DriverKit project is a read-only PCI visibility probe for NVIDIA RTX 5070.

This plan does not attempt graphics acceleration, framebuffer support, Metal support, GSP initialization, display engine support, or general RTX 5070 macOS acceleration.

## Current Status

Completed:

- macOS Sonoma boot confirmed on the test system.
- RTX 5070 is visible to macOS as a PCI device.
- Xcode 16.2 and DriverKit 24.2 SDK are installed.
- Initial DriverKit project skeleton exists.
- `IOPCIMatch = 0x2f0410de` has been added.
- `PCIDriverKit` is linked.
- Unsigned Debug build succeeds with code signing disabled.

Current build verification command:

```bash
xcodebuild \
  -project apps/H1mekaRTXProbeHost/H1mekaRTXProbeHost.xcodeproj \
  -scheme H1mekaRTXProbeHost \
  -configuration Debug \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  CODE_SIGN_IDENTITY="" \
  build
```

Expected result:

```text
** BUILD SUCCEEDED **
```

## Required Apple Capabilities and Entitlements

Actual DriverKit activation requires valid signing and provisioning.

Expected Host App entitlement:

- `com.apple.developer.system-extension.install`

Expected DriverKit extension entitlements:

- `com.apple.developer.driverkit`
- `com.apple.developer.driverkit.transport.pci`

Expected PCI transport descriptor:

```text
Vendor ID: 0x10de
Device ID: 0x2f04
IOPCIMatch: 0x2f0410de
```

## Provisioning Requirements

The following provisioning items are expected to be required:

- Apple Developer account
- App ID / Bundle ID for the System Extension Host App
- App ID / Bundle ID for the DriverKit extension
- DriverKit development provisioning profile
- System Extension capability for the host app
- DriverKit capability for the dext
- PCI transport entitlement for the dext

The current expected blocker is:

```text
No DriverKit App Development provisioning profile for:
com.palanbanana.H1mekaRTXProbeHost
```

## Activation Architecture

DriverKit drivers are installed and activated as system extensions from a containing app.

The future activation structure should be:

```text
H1mekaRTXProbeHost.app
└── Contents/Library/SystemExtensions/
    └── com.palanbanana.H1mekaRTXProbeHost.dext
```

The current project is focused on the DriverKit extension side.

A later step should add or restructure a proper Host App target that uses `SystemExtensions.framework` to request activation.

## Expected Activation Flow

Planned activation flow:

1. Build signed Host App and DriverKit extension.
2. Ensure the Host App has the System Extension entitlement.
3. Ensure the DriverKit extension has DriverKit and PCI transport entitlements.
4. Embed the dext inside the Host App.
5. Use `SystemExtensions.framework` from the Host App to request activation.
6. Approve the system extension in macOS System Settings if prompted.
7. Watch system logs for `H1mekaRTXProbe` messages.
8. Confirm that the probe only performs read-only PCI config-space logging.

## Expected Failure Modes

Expected failure modes before proper entitlement/provisioning is complete:

- Missing provisioning profile
- Missing DriverKit entitlement
- Missing PCI transport entitlement
- Missing System Extension entitlement on the host app
- Entitlement descriptor does not match the PCI provider
- System Extension activation denied or pending user approval
- DriverKit extension builds but cannot be activated
- DriverKit extension activates but does not match the RTX 5070 provider

## Log Collection Plan

When activation is eventually attempted, collect logs with:

```bash
log stream --style compact --predicate 'eventMessage CONTAINS "H1mekaRTXProbe"'
```

Additional useful checks:

```bash
systemextensionsctl list
system_profiler SPPCIDataType
ioreg -l | grep -i "10de"
ioreg -l | grep -i "2f04"
```

## Safety Boundary

This project stage is read-only.

Allowed:

- PCI visibility checking
- PCI config-space identifier reads
- DriverKit skeleton build validation
- Entitlement and activation planning

Not allowed in this stage:

- Graphics acceleration
- Metal support
- Framebuffer bring-up
- Display engine initialization
- GSP firmware initialization
- BAR memory poking
- MMIO writes
- GPU reset logic
- Kernel patching
- Production driver claims

## Next Steps

Recommended next implementation steps:

1. Add a proper Host App target.
2. Add `SystemExtensions.framework` activation request code.
3. Add entitlements files for host and dext.
4. Keep unsigned build path for CI-style validation.
5. Prepare a separate branch for signed local activation testing.
6. Document any signing or entitlement failure logs before attempting deeper driver behavior.
