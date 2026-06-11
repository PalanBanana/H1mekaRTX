# Apple Entitlement Request Template

## Purpose

Prepare the information needed before requesting Apple Developer entitlements for future signed DriverKit/System Extension activation.

This stage is documentation-only.

## Request Page

Apple System Extensions and DriverKit entitlement request page:

https://developer.apple.com/system-extensions/

## Requested Capabilities

Host App:

- System Extension install entitlement
- com.apple.developer.system-extension.install

DriverKit extension:

- DriverKit entitlement
- com.apple.developer.driverkit
- PCI transport entitlement
- com.apple.developer.driverkit.transport.pci

## Project

Project name:

- H1mekaRTX

Repository:

- https://github.com/PalanBanana/H1mekaRTX

## Hardware Target

GPU:

- NVIDIA GeForce RTX 5070

PCI identity:

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de

Subsystem:

- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Driver Purpose

The DriverKit extension is intended for a read-only PCI probe stage.

Current behavior:

- Match RTX 5070 PCI device
- Open IOPCIDevice
- Read PCI configuration space
- Log Vendor ID
- Log Device ID
- Log Subsystem Vendor ID
- Log Subsystem ID
- Log Revision ID
- Close IOPCIDevice

## Safety Boundary

The current DriverKit probe does not:

- write MMIO
- access BAR memory
- reset the GPU
- initialize GSP
- initialize display engines
- attempt framebuffer support
- attempt Metal support
- attempt graphics acceleration

## Request Notes Draft

H1mekaRTX is currently a read-only DriverKit PCI probe project for researching macOS DriverKit PCI enumeration behavior on an NVIDIA RTX 5070.

The current driver matches PCI device 0x2f04 from vendor 0x10de and only reads PCI configuration-space identity values. It does not write MMIO, access BAR memory, reset the GPU, initialize display engines, initialize firmware, or attempt graphics acceleration.

The requested entitlements are needed to test legitimate signed System Extension and DriverKit activation through macOS.
