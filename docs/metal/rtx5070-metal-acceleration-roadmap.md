# RTX 5070 Metal Acceleration Roadmap

## Goal

The long-term goal of H1mekaRTX is to research whether an NVIDIA GeForce RTX 5070 can ever be exposed to macOS as a Metal-capable accelerated graphics device.

## Reality Boundary

This is a long-term research goal, not a promised working driver.

DriverKit activation, PCI transport entitlement, GPU initialization, VRAM management, command submission, display engine initialization, and Metal device exposure are separate problems.

## RTX 5070 PCI Target

- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Subsystem Vendor ID: 0x1458
- Subsystem ID: 0x417e

## Phase 0

- Keep macOS boot stable
- Keep RTX 5070 visible as PCI device
- Keep current DriverKit read-only probe buildable
- Keep Host App buildable
- Keep diagnostics scripts working

## Phase 1

- Obtain Apple Developer Program access
- Request DriverKit entitlement
- Request PCI transport entitlement
- Build signed Host App
- Build signed DriverKit extension
- Attempt supported SystemExtensions activation

## Phase 2

- Confirm DriverKit extension attaches to RTX 5070
- Confirm PCI config-space reads
- Confirm stable start and stop lifecycle
- Confirm no GPU reset, no MMIO writes, and no BAR access yet

## Phase 3

- Research RTX 5070 BAR layout
- Research safe MMIO read-only inspection
- Research VRAM aperture behavior
- Research GSP firmware initialization requirements
- Research command queue initialization requirements

## Phase 4

- Research display engine initialization
- Research framebuffer ownership
- Research memory manager requirements
- Research synchronization and fence requirements
- Research user client interface design

## Phase 5

- Research whether macOS can expose a third-party custom DriverKit GPU as a Metal device
- Research private graphics stack boundaries
- Research required IOKit service classes
- Research why DriverKit PCI access alone is insufficient for Metal acceleration

## Hard Stop Conditions

Stop immediately if testing causes boot failure, display loss, PCI instability, kernel panic, GPU reset loops, firmware faults, or storage corruption risk.

## Not Promised

- Working Metal acceleration
- Working display output
- Working framebuffer
- Working game acceleration
- Working Blender acceleration
- Working general macOS UI acceleration

