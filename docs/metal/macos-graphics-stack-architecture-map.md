# macOS Graphics Stack Architecture Map

## Purpose

Stage 14 maps the research path from public Metal app APIs to the lower-level driver and hardware areas that would eventually be required for full RTX 5070 Metal graphics acceleration research.

This stage keeps the full Metal acceleration goal.

It does not claim RTX 5070 Metal acceleration is implemented.

## Goal

The long-term goal is full Metal graphics acceleration research for RTX 5070 on macOS.

Stage 14 defines the architecture layers and handoff blockers before any real hardware acceleration attempt.

## Decision

Current decision:

    GRAPHICS_STACK_RESEARCH_MAP_READY

## Layer Summary

- Application validation layer
- Metal API layer
- macOS graphics integration layer
- DriverKit PCI layer
- BAR and aperture layer
- GPU execution layer
- Memory manager layer
- Shader and compiler layer
- Firmware and GSP layer
- Display and framebuffer layer

## Key Boundary

Public Metal app code can be developed against an existing system Metal device.

That is allowed.

RTX 5070 Metal acceleration is not attempted in this stage.

## Research Gates

- Stage 15: public Metal validation harness
- Stage 16: DriverKit activation design
- Stage 17: BAR role research plan
- Stage 18: command processor and memory model placeholders
- Stage 19: shader and compiler research notes
- Stage 20: full Metal acceleration implementation decision gate

## Safety Boundary

This stage is read-only.

It allows public Metal app validation only on an existing system Metal device.

It does not perform:

- RTX 5070 Metal acceleration attempts
- ioreg collection
- system_profiler collection
- PCI config-space reads
- PCI config-space writes
- MMIO reads
- MMIO writes
- BAR memory mapping
- BAR memory poking
- GPU reset logic
- firmware loading
- GSP initialization
- display engine initialization
- framebuffer initialization
- DriverKit activation
- private graphics framework patching

## Notes

This map is intended to guide the project toward the full Metal graphics acceleration goal without skipping the required safety and architecture gates.
