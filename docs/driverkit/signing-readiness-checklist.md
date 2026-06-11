# Signing Readiness Checklist

## Purpose

Track the signing requirements needed before attempting real System Extension and DriverKit activation.

This stage is documentation-only.

## Current State

- Host App UI exists
- SystemExtensions activation request code exists
- DriverKit PCI probe code exists
- RTX 5070 PCI match is documented
- Diagnostics collection script exists

## Required Before Real Activation

Host App:

- Valid Apple Developer Team ID
- Valid bundle identifier
- com.apple.developer.system-extension.install entitlement
- Provisioning profile including System Extension install entitlement

DriverKit extension:

- Valid DriverKit-capable signing identity
- Valid bundle identifier
- com.apple.developer.driverkit entitlement
- com.apple.developer.driverkit.transport.pci entitlement
- Provisioning profile including DriverKit and PCI transport entitlements

Project alignment:

- Host App must embed the System Extension
- Host App activation identifier must match the System Extension bundle identifier
- System Extension bundle identifier must match provisioning profile
- DriverKit target must keep IOPCIMatch set to 0x2f0410de

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## First Real Activation Test

Only after signing is valid:

1. Build signed Debug app.
2. Run Host App.
3. Click Request Activation.
4. Approve System Extension in System Settings if prompted.
5. Run diagnostics script.
6. Check systemextensionsctl list.
7. Check sysextd and DriverKit logs.

## Boundary

This document does not enable real activation.

Real activation still requires Apple entitlement approval and valid provisioning.

## Not In Scope

- Real DriverKit activation
- Metal acceleration
- framebuffer support
- GSP initialization
- display engine initialization
- MMIO writes
- BAR memory poking
- GPU reset logic
