# Apple Entitlement Request Packet

## Purpose

Prepare a ready-to-submit packet for requesting Apple Developer entitlements required for future signed DriverKit/System Extension activation.

This stage is documentation-only.

## Apple Request URL

https://developer.apple.com/system-extensions/

## Requested Entitlements

Host App:

- com.apple.developer.system-extension.install

DriverKit extension:

- com.apple.developer.driverkit
- com.apple.developer.driverkit.transport.pci

## Project Identity

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

Subsystem identity:

- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## DriverKit Extension Behavior

Current DriverKit probe behavior:

- Matches RTX 5070 PCI device
- Opens IOPCIDevice
- Reads PCI configuration-space identity values
- Logs Vendor ID
- Logs Device ID
- Logs Subsystem Vendor ID
- Logs Subsystem ID
- Logs Revision ID
- Closes IOPCIDevice

## Entitlement Request Text

H1mekaRTX is a read-only DriverKit PCI probe project for researching macOS DriverKit PCI enumeration and System Extension activation behavior on an NVIDIA GeForce RTX 5070.

The DriverKit extension currently matches PCI vendor ID 0x10de and device ID 0x2f04 using IOPCIMatch 0x2f0410de. The current implementation only opens the IOPCIDevice, reads PCI configuration-space identity values, logs the values, and closes the device.

The project requires the System Extension install entitlement for the Host App and DriverKit PCI transport entitlements for the DriverKit extension so signed activation can be tested through the supported macOS SystemExtensions and DriverKit path.

## Safety Boundary

The current probe does not write MMIO, access BAR memory, reset the GPU, initialize GSP, initialize display engines, provide framebuffer support, provide Metal support, or attempt graphics acceleration.
