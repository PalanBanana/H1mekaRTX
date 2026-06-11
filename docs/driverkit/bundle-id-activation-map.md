# Bundle ID and Activation Map

## Purpose

Track the bundle identifiers required for future signed System Extension and DriverKit activation.

This stage is documentation-only.

## Host App

Current Host App role:

- Owns the SystemExtensions activation request UI
- Requests activation and deactivation
- Displays request status and result

Future Host App entitlement:

- com.apple.developer.system-extension.install

## DriverKit Extension

Current DriverKit extension role:

- Matches RTX 5070 PCI device
- Performs read-only PCI config-space probing
- Logs PCI identity values

Future DriverKit entitlements:

- com.apple.developer.driverkit
- com.apple.developer.driverkit.transport.pci

## Activation Flow

1. User opens Host App.
2. User clicks Request Activation.
3. Host App submits OSSystemExtensionRequest.
4. macOS sysextd validates signing, entitlements, and bundle identifiers.
5. User approval may be required in System Settings.
6. DriverKit extension starts only if signing and entitlements are valid.

## Boundary

This document does not enable real activation.

Real activation still requires valid Apple Developer signing, provisioning profiles, DriverKit entitlement approval, PCI transport entitlement configuration, and correct bundle identifier alignment.

## Not In Scope

- Real DriverKit activation
- Metal acceleration
- framebuffer support
- GSP initialization
- display engine initialization
- MMIO writes
- BAR memory poking
- GPU reset logic
