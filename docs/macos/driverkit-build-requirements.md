# DriverKit Build Requirements

This document tracks the expected macOS/Xcode requirements for building H1mekaRTXProbe.

## Target

H1mekaRTXProbe is planned as a read-only DriverKit/PCIDriverKit probe driver for NVIDIA RTX 5070.

## Required Apple Components

* macOS development machine
* Xcode
* Apple Developer account
* DriverKit capability
* PCI DriverKit transport entitlement
* System Extension host app
* Driver Extension target

## Required Frameworks

* DriverKit
* PCIDriverKit
* SystemExtensions

## Apple Entitlements

Expected entitlements:

* `com.apple.developer.driverkit`
* `com.apple.developer.driverkit.transport.pci`

The PCI transport entitlement must describe the supported PCI device descriptors for the custom driver.

## Target PCI Device

* Vendor ID: `0x10de`
* Device ID: `0x2f04`
* Subsystem Vendor ID: `0x1458`
* Subsystem Device ID: `0x417e`
* Revision ID: `0xa1`
* Class Code: `0x030000`

## Planned Bundle Layout

The real implementation is expected to use:

```text
H1mekaRTXProbe.app
└── Contents/
    └── Library/
        └── SystemExtensions/
            └── com.h1meka.H1mekaRTXProbe.Driver.dext
```

## Stage 1 Safety Policy

Allowed:

* PCI matching
* PCI config space reads
* BAR enumeration
* read-only logging
* IORegistry visibility checks

Forbidden:

* MMIO writes
* VRAM writes
* GSP initialization
* firmware upload
* display engine programming
* Metal registration

## First Build Goal

The first build does not need GPU acceleration.

Success means:

* the dext builds
* the host app builds
* the dext can be activated
* the RTX 5070 PCI device matches `10de:2f04`
* logs show PCI IDs and BAR information
