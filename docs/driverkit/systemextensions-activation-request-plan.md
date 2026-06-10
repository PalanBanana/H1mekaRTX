# SystemExtensions Activation Request Plan

## Purpose

This document describes the next planned step for H1mekaRTXProbeInstaller.

The goal is to add Host App code that can eventually request DriverKit/System Extension activation.

This document does not attempt real activation yet.

## Current Scope

The current scope is limited to:

- Host App activation request planning
- SystemExtensions.framework integration planning
- expected signing and entitlement blockers
- read-only DriverKit probe workflow

## Current Project Status

Completed so far:

- macOS Sonoma boot confirmed on the test system.
- RTX 5070 is visible to macOS as a PCI device.
- Xcode 16.2 and DriverKit 24.2 SDK are installed.
- DriverKit project skeleton exists.
- IOPCIMatch = 0x2f0410de has been added.
- PCIDriverKit is linked.
- Unsigned Debug build succeeds with code signing disabled.
- Host App skeleton exists for future System Extension activation work.

## Planned Host App Role

H1mekaRTXProbeInstaller will eventually be responsible for requesting activation of the DriverKit extension.

Expected future structure:

    H1mekaRTXProbeInstaller.app
    └── Contents/Library/SystemExtensions/
        └── com.palanbanana.H1mekaRTXProbeHost.dext

## Required Future Entitlements

Host App:

- com.apple.developer.system-extension.install

DriverKit extension:

- com.apple.developer.driverkit
- com.apple.developer.driverkit.transport.pci

## RTX 5070 PCI Match

Expected PCI match values:

    Vendor ID: 0x10de
    Device ID: 0x2f04
    IOPCIMatch: 0x2f0410de

## Expected Future Activation Flow

1. Build signed Host App.
2. Build signed DriverKit extension.
3. Embed the dext into the Host App.
4. Use SystemExtensions.framework in the Host App.
5. Request activation for the DriverKit extension.
6. Approve the extension in macOS System Settings if prompted.
7. Check systemextensionsctl list.
8. Stream logs for H1mekaRTXProbe.
9. Confirm that only read-only PCI config-space logging occurs.

## Expected Log Commands

    log stream --style compact --predicate 'eventMessage CONTAINS "H1mekaRTXProbe"'
    systemextensionsctl list
    system_profiler SPPCIDataType
    ioreg -l | grep -i "10de"
    ioreg -l | grep -i "2f04"

## Expected Failure Modes

Expected failure modes before proper entitlement and provisioning are complete:

- Missing Host App provisioning profile
- Missing DriverKit provisioning profile
- Missing System Extension entitlement
- Missing DriverKit entitlement
- Missing PCI transport entitlement
- System Extension activation denied
- System Extension activation pending user approval
- DriverKit extension builds but cannot be activated
- DriverKit extension activates but does not match RTX 5070
- PCI entitlement descriptor does not match the provider

## Safety Boundary

This stage does not attempt:

- graphics acceleration
- Metal support
- framebuffer bring-up
- GSP initialization
- display engine initialization
- MMIO writes
- BAR memory poking
- GPU reset logic
- production driver behavior

The DriverKit probe remains read-only.

## Next Steps

Recommended next implementation steps:

1. Add SystemExtensions.framework to the Host App target.
2. Add a minimal activation request class.
3. Add placeholder Host App UI for activation status.
4. Keep unsigned build validation working.
5. Add entitlement files later in a separate signing-focused branch.
6. Do not attempt real activation until signing and entitlements are ready.
