# PCI Config Space Map

## Purpose

Track PCI configuration-space registers relevant to long-term RTX 5070 acceleration research.

This stage is documentation-only and read-only.

## Background

PCI configuration space contains device identity, command/status registers, BAR registers, class code, subsystem identity, and capability pointers.

For H1mekaRTX, PCI config-space research must remain read-only until DriverKit signing, entitlement, and safe activation requirements are satisfied.

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e
- Revision ID: 0x00a1

## Standard PCI Config Offsets

| Offset | Width | Name | H1mekaRTX Use |
|---|---:|---|---|
| 0x00 | 16-bit | Vendor ID | Confirm NVIDIA vendor 0x10de |
| 0x02 | 16-bit | Device ID | Confirm RTX 5070 device 0x2f04 |
| 0x04 | 16-bit | Command | Inspect memory/bus-master enable state |
| 0x06 | 16-bit | Status | Inspect PCI status bits |
| 0x08 | 8-bit | Revision ID | Confirm revision |
| 0x09 | 8-bit | Programming Interface | Record class details |
| 0x0A | 8-bit | Subclass | Record class details |
| 0x0B | 8-bit | Base Class | Record GPU display controller class |
| 0x0C | 8-bit | Cache Line Size | Record only |
| 0x0D | 8-bit | Latency Timer | Record only |
| 0x0E | 8-bit | Header Type | Confirm standard header |
| 0x0F | 8-bit | BIST | Record only |
| 0x10 | 32-bit | BAR0 | Record BAR metadata only |
| 0x14 | 32-bit | BAR1 | Record BAR metadata only |
| 0x18 | 32-bit | BAR2 | Record BAR metadata only |
| 0x1C | 32-bit | BAR3 | Record BAR metadata only |
| 0x20 | 32-bit | BAR4 | Record BAR metadata only |
| 0x24 | 32-bit | BAR5 | Record BAR metadata only |
| 0x2C | 16-bit | Subsystem Vendor ID | Confirm 0x1458 |
| 0x2E | 16-bit | Subsystem ID | Confirm 0x417e |
| 0x34 | 8-bit | Capability Pointer | Locate PCI capabilities if safe |
| 0x3C | 8-bit | Interrupt Line | Record only |
| 0x3D | 8-bit | Interrupt Pin | Record only |

## Read-Only Research Rules

Allowed:

- Read Vendor ID
- Read Device ID
- Read Revision ID
- Read Class Code
- Read Subsystem IDs
- Read BAR registers as metadata
- Read Capability Pointer
- Document values

Not allowed:

- Writing PCI Command register
- Enabling bus mastering from experimental code
- Enabling memory decoding from experimental code
- Writing BAR registers
- MMIO writes
- BAR memory poking
- GPU reset
- GSP initialization
- display engine initialization
- framebuffer ownership
- Metal device exposure attempts

## Future DriverKit Probe Extension

Future signed DriverKit probe may add read-only config-space logging for:

- Command register
- Status register
- Class code
- BAR0-BAR5 raw values
- Capability pointer
- Interrupt line and pin

## Safety Boundary

This document does not enable DriverKit activation.

This document does not enable RTX 5070 Metal acceleration.

This document does not perform MMIO writes, BAR memory poking, GPU reset logic, GSP initialization, display engine initialization, framebuffer support, or Metal support.

## Hard Stop Conditions

Stop immediately if any future test causes:

- boot failure
- display loss
- kernel panic
- PCI bus instability
- GPU reset loop
- storage corruption risk
- system freeze
