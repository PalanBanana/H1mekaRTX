# BAR Inventory Diagnostics

## Purpose

Add a read-only diagnostics script for collecting RTX 5070 PCI and BAR-related OS inventory.

This stage is diagnostics-only.

## Script

Run:

    ./scripts/collect-bar-inventory.sh

Optional output path:

    ./scripts/collect-bar-inventory.sh ~/Desktop/H1mekaRTX-bar-inventory-test

## Captured Data

- macOS version
- kernel version
- PCI device report
- display report
- IODeviceTree snapshot
- IOService snapshot
- RTX 5070 filtered IORegistry hints
- recent H1mekaRTX, IOPCIDevice, DriverKit, and sysextd logs

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Safety Boundary

This script is read-only.

It does not perform:

- MMIO writes
- BAR memory poking
- GPU reset logic
- GSP initialization
- display engine initialization
- framebuffer initialization
- Metal acceleration attempts

## Use

Use this script before any future BAR/MMIO research to archive the OS-visible PCI inventory state.
