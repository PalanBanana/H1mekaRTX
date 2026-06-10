# Stage 1 Implementation Plan

## Target

H1mekaRTXProbe is a read-only macOS DriverKit/PCIDriverKit probe driver for NVIDIA RTX 5070.

## Target Device

- GPU: NVIDIA GB205 GeForce RTX 5070
- Vendor ID: 0x10de
- Device ID: 0x2f04
- Subsystem Vendor ID: 0x1458
- Subsystem Device ID: 0x417e
- Revision ID: 0xa1
- Class Code: 0x030000

## Allowed in Stage 1

- PCI device matching
- PCI config space reads
- BAR enumeration
- Read-only BAR mapping experiments
- IORegistry visibility checks
- Logging

## Forbidden in Stage 1

- MMIO writes
- VRAM writes
- GSP initialization
- Display engine programming
- Firmware upload
- Metal registration

## Success Criteria

- Driver matches 10de:2f04
- Driver logs PCI IDs
- Driver logs BAR0/BAR1/BAR3/BAR5
- Driver appears in IORegistry as H1mekaRTXProbe
