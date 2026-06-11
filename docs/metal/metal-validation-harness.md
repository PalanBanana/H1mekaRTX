# Metal Validation Harness

## Purpose

Stage 15 adds the first practical Metal-related code for the full Metal graphics acceleration research track.

This harness uses the existing system Metal device only.

It does not attempt RTX 5070 Metal acceleration.

## Goal

The long-term project goal remains full Metal graphics acceleration research for RTX 5070 on macOS.

This stage validates the public Metal app-layer harness and reporting pipeline before any RTX 5070 hardware acceleration attempt.

## Harness

Location:

    tools/metal-validation-harness

Package:

    H1mekaMetalValidation

The harness performs a simple Metal compute validation:

- obtains the default system Metal device
- creates a command queue
- loads a small Metal shader
- creates a compute pipeline
- creates input and output buffers
- dispatches a vector-add compute kernel
- verifies the result
- prints a JSON runtime report

## Run

From the repository root:

    cd tools/metal-validation-harness
    swift run

## Static Check

From the repository root:

    ./scripts/check-metal-validation-harness.py --root . --out-dir .

Optional build check on macOS:

    ./scripts/check-metal-validation-harness.py --root . --out-dir . --build

## Safety Boundary

This harness is limited to the existing system Metal device.

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

This harness proves the project can build and run Metal validation workloads.

It does not prove RTX 5070 acceleration.

It does not expose the RTX 5070 as a macOS Metal device.
