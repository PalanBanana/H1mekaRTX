# GSP Firmware Research Map

## Purpose

Track GSP firmware research requirements for long-term RTX 5070 acceleration research.

This stage is documentation-only.

## Background

NVIDIA documents GSP firmware as firmware used by supported GPUs to offload GPU initialization and management tasks.

NVIDIA open kernel modules depend on GSP for Turing and newer open module support.

## Research Questions

- Is RTX 5070 GSP firmware mandatory for initialization?
- Which firmware files are used by Linux NVIDIA drivers?
- Which initialization tasks are handled by GSP?
- Which tasks remain in the host driver?
- Can macOS DriverKit legally and safely load or communicate with this firmware path?
- What signing, licensing, and redistribution restrictions apply?

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Boundary

This document does not load firmware.

This document does not enable DriverKit activation or Metal acceleration.

No MMIO writes, BAR memory poking, GPU reset logic, display engine initialization, framebuffer support, or Metal support is attempted.
