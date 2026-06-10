# Entitlements Placeholder Plan

## Purpose

This document tracks placeholder entitlement files for the future signed DriverKit activation path.

This stage does not attempt real activation.

## Required Future Entitlements

Host App:

- com.apple.developer.system-extension.install

DriverKit extension:

- com.apple.developer.driverkit
- com.apple.developer.driverkit.transport.pci

## RTX 5070 PCI Transport Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

## Important Boundary

These placeholders are documentation and project-structure preparation only.

Actual activation still requires valid Apple Developer signing, provisioning profiles, DriverKit entitlement approval, and PCI transport entitlement configuration.

## Not In Scope

- Real DriverKit activation
- Metal acceleration
- framebuffer support
- GSP initialization
- display engine initialization
- MMIO writes
- BAR memory poking
- GPU reset logic
