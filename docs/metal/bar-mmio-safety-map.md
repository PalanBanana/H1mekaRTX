# BAR and MMIO Safety Map

## Purpose

Track BAR and MMIO safety requirements for long-term RTX 5070 acceleration research.

This stage is documentation-only.

## Background

PCI devices expose Base Address Registers, also called BARs, so the operating system can map device memory or register ranges into physical address space.

GPU drivers commonly interact with hardware through memory-mapped registers, but unsafe writes can cause hangs, resets, display loss, or kernel panics.

## Research Questions

- Which BARs are exposed by RTX 5070 on macOS?
- Which BARs are visible through IOPCIDevice?
- Which BARs are configuration-space only?
- Which BARs are MMIO register windows?
- Which BARs may expose VRAM aperture behavior?
- Which BAR regions are safe for read-only inspection?
- Which BAR regions must never be written during early research?
- Which register ranges are handled by GSP firmware on modern NVIDIA GPUs?

## Safety Policy

Phase 3 must stay read-only.

Allowed:

- PCI config-space reads
- BAR size discovery
- BAR metadata documentation
- IORegistry inspection
- system_profiler inspection
- log collection

Not allowed:

- MMIO writes
- BAR memory poking
- GPU reset
- firmware upload
- display engine initialization
- command queue submission
- framebuffer ownership
- Metal device exposure attempts

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Required Future Diagnostics

- Dump PCI config-space identity values
- Record BAR sizes
- Record BAR address ranges if safely exposed by the OS
- Record IORegistry provider tree
- Record system_profiler PCI output
- Record sysextd and DriverKit logs

## Hard Stop Conditions

Stop immediately if testing causes:

- boot failure
- display loss
- kernel panic
- GPU reset loop
- PCI bus instability
- storage corruption risk
- system freeze

## Boundary

This document does not enable DriverKit activation.

This document does not enable Metal acceleration.

This document does not perform MMIO writes, BAR memory poking, GPU reset logic, GSP initialization, display engine initialization, framebuffer support, or Metal support.
