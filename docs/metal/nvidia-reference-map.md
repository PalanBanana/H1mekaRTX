# NVIDIA Reference Map

## Purpose

Track public NVIDIA-related reference projects for long-term RTX 5070 Metal acceleration research.

This stage is documentation-only.

## Reference Sources

### NVIDIA Open GPU Kernel Modules

Repository:

- https://github.com/NVIDIA/open-gpu-kernel-modules

Use:

- Study Linux NVIDIA kernel module structure
- Study PCI device handling patterns
- Study memory management boundaries
- Study firmware and GSP-related structure references

Boundary:

- Linux-only reference
- Not a macOS DriverKit implementation
- Not a Metal implementation

### Nouveau

Project:

- https://nouveau.freedesktop.org/

Use:

- Study open-source NVIDIA GPU driver architecture
- Study Linux DRM integration concepts
- Study historical NVIDIA GPU reverse-engineering notes

Boundary:

- Linux DRM/Mesa stack
- Not macOS IOKit
- Not macOS DriverKit
- Not Metal

### Mesa NVK

Documentation:

- https://docs.mesa3d.org/drivers/nvk.html

Use:

- Study modern open-source NVIDIA Vulkan driver architecture
- Study command submission concepts
- Study user-space graphics driver design patterns

Boundary:

- Vulkan, not Metal
- Mesa/Linux stack, not macOS graphics stack
- Not directly portable to macOS

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Research Rule

These projects are references only.

H1mekaRTX must not copy incompatible code blindly.

H1mekaRTX must keep the current macOS path focused on DriverKit, SystemExtensions, diagnostics, and read-only PCI probing until signing and entitlement requirements are satisfied.

## Boundary

This document does not enable real DriverKit activation.

This document does not enable Metal acceleration.

No MMIO writes, BAR memory poking, GPU reset logic, GSP initialization, display engine initialization, framebuffer support, or general RTX 5070 macOS acceleration is attempted by this stage.
